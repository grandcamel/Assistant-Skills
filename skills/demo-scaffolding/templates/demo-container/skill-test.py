#!/usr/bin/env python3
"""
Skill Test Runner - Tests Claude Code skills against expected patterns.

Runs prompts through Claude, captures tool usage and response text,
asserts against deterministic patterns, and uses LLM-as-judge for
semantic quality evaluation.

Usage:
    python skill-test.py scenarios/search.prompts
    python skill-test.py scenarios/search.prompts --model sonnet --judge-model haiku
    python skill-test.py scenarios/search.prompts --verbose
    python skill-test.py scenarios/search.prompts --prompt-index 0  # Single prompt

Environment Variables:
    OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint for traces (default: http://localhost:4318)
    LOKI_ENDPOINT: Loki endpoint for logs (default: http://localhost:3100)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

# OpenTelemetry imports - optional dependency
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Module-level tracer and config
_tracer: Any | None = None
_loki_endpoint: str | None = None
_debug_enabled: bool = True
_scenario_name: str = "unknown"
_trace_provider: Any | None = None


def init_telemetry(
    service_name: str = "skill-test",
    scenario: str = "unknown",
    debug: bool = True,
) -> Any | None:
    """Initialize OpenTelemetry tracing and Loki logging."""
    global _tracer, _loki_endpoint, _debug_enabled, _scenario_name, _trace_provider

    _debug_enabled = debug
    _scenario_name = scenario

    if not debug:
        print("[OTEL] Debug mode disabled, telemetry off", file=sys.stderr)
        return None

    otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    _loki_endpoint = os.environ.get("LOKI_ENDPOINT", "http://localhost:3100")

    if os.path.exists("/.dockerenv"):
        otel_endpoint = os.environ.get(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://host.docker.internal:4318"
        )
        _loki_endpoint = os.environ.get(
            "LOKI_ENDPOINT", "http://host.docker.internal:3100"
        )

    if OTEL_AVAILABLE:
        try:
            resource = Resource.create({
                "service.name": service_name,
                "service.version": "1.0.0",
                "scenario": scenario,
            })

            _trace_provider = TracerProvider(resource=resource)
            exporter = OTLPSpanExporter(endpoint=f"{otel_endpoint}/v1/traces")
            _trace_provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(_trace_provider)
            _tracer = trace.get_tracer(service_name)

            print(f"[OTEL] Tracing initialized -> {otel_endpoint}", file=sys.stderr)
        except Exception as e:
            print(f"[OTEL] Failed to initialize tracing: {e}", file=sys.stderr)
            _tracer = None
    else:
        print("[OTEL] OpenTelemetry not installed, tracing disabled", file=sys.stderr)

    print(f"[OTEL] Loki logging -> {_loki_endpoint}", file=sys.stderr)
    return _tracer


def shutdown_telemetry() -> None:
    """Shutdown telemetry and flush all pending spans."""
    global _trace_provider
    if _trace_provider is not None:
        try:
            _trace_provider.force_flush(timeout_millis=5000)
            _trace_provider.shutdown()
            print("[OTEL] Telemetry shutdown complete", file=sys.stderr)
        except Exception as e:
            print(f"[OTEL] Shutdown error: {e}", file=sys.stderr)


@contextmanager
def trace_span(
    name: str,
    attributes: dict | None = None,
    record_exception: bool = True,
):
    """Context manager for creating trace spans with timing."""
    start_time = time.time()

    if _tracer is None:
        yield None
        return

    with _tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(key, str(value) if not isinstance(value, (int, float, bool)) else value)
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            if record_exception:
                span.record_exception(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            span.set_attribute("duration_ms", duration_ms)


@dataclass
class ToolExpectations:
    must_call: list[str] = field(default_factory=list)
    must_not_call: list[str] = field(default_factory=list)
    match_mode: str = "all"


@dataclass
class TextExpectations:
    must_contain: list[str] = field(default_factory=list)
    must_not_contain: list[str] = field(default_factory=list)


@dataclass
class Expectations:
    tools: ToolExpectations = field(default_factory=ToolExpectations)
    text: TextExpectations = field(default_factory=TextExpectations)
    semantic: str = ""


@dataclass
class PromptSpec:
    prompt: str
    expect: Expectations
    index: int = 0


@dataclass
class ToolCall:
    name: str
    input: dict[str, Any]
    output: str = ""


@dataclass
class PromptResult:
    spec: PromptSpec
    response_text: str
    tools_called: list[ToolCall]
    exit_code: int
    tool_assertions: list[tuple[str, bool, str]]
    text_assertions: list[tuple[str, bool, str]]
    quality: str = ""
    tool_accuracy: str = ""
    reasoning: str = ""
    passed: bool = False


def parse_prompts_file(filepath: Path) -> list[PromptSpec]:
    """Parse prompts file with YAML expectations."""
    content = filepath.read_text()
    documents = content.split("\n---\n")

    specs: list[PromptSpec] = []
    for i, doc in enumerate(documents):
        doc = doc.strip()
        if not doc or doc == "---":
            continue

        if doc.startswith("---\n"):
            doc = doc[4:]

        try:
            data = yaml.safe_load(doc)
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse YAML block {i}: {e}")
            continue

        if not data or "prompt" not in data:
            continue

        expect_data = data.get("expect", {})
        tools_data = expect_data.get("tools", {})
        text_data = expect_data.get("text", {})

        tool_exp = ToolExpectations(
            must_call=tools_data.get("must_call", []),
            must_not_call=tools_data.get("must_not_call", []),
            match_mode=tools_data.get("match_mode", "all"),
        )

        text_exp = TextExpectations(
            must_contain=text_data.get("must_contain", []),
            must_not_contain=text_data.get("must_not_contain", []),
        )

        expectations = Expectations(
            tools=tool_exp,
            text=text_exp,
            semantic=expect_data.get("semantic", ""),
        )

        specs.append(PromptSpec(
            prompt=data["prompt"].strip(),
            expect=expectations,
            index=len(specs),
        ))

    return specs


def run_claude_prompt(
    prompt: str,
    model: str = "sonnet",
    verbose: bool = False,
    prompt_index: int = 0,
) -> tuple[str, list[ToolCall], int, float]:
    """Run a prompt through Claude and capture output."""
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
        "--dangerously-skip-permissions",
    ]

    if verbose:
        print(f"  Running: claude -p '...' --model {model}")

    start_time = time.time()

    with trace_span(
        "claude.prompt",
        attributes={
            "prompt_index": prompt_index,
            "model": model,
            "prompt_length": len(prompt),
        },
    ):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            return "", [], 1, time.time() - start_time
        except Exception as e:
            print(f"  Error running Claude: {e}")
            return "", [], 1, time.time() - start_time

        duration = time.time() - start_time
        response_text = ""
        tools_called = []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "")

            if event_type == "assistant":
                message = event.get("message", {})
                content_blocks = message.get("content", [])

                for block in content_blocks:
                    block_type = block.get("type", "")

                    if block_type == "text":
                        response_text += block.get("text", "")

                    elif block_type == "tool_use":
                        tool = ToolCall(
                            name=block.get("name", ""),
                            input=block.get("input", {}),
                        )
                        tools_called.append(tool)

            elif event_type == "result":
                if not response_text:
                    response_text = event.get("result", "")

        return response_text, tools_called, result.returncode, duration


def run_tool_assertions(
    tools_called: list[ToolCall],
    expectations: ToolExpectations,
) -> list[tuple[str, bool, str]]:
    """Run tool assertions."""
    results = []
    called_names = [t.name for t in tools_called]

    if expectations.match_mode == "all":
        for tool in expectations.must_call:
            passed = tool in called_names
            results.append((
                f"must_call: {tool}",
                passed,
                f"called: {called_names}" if not passed else "",
            ))
    elif expectations.match_mode == "any":
        if expectations.must_call:
            any_called = any(t in called_names for t in expectations.must_call)
            results.append((
                f"must_call (any): {expectations.must_call}",
                any_called,
                f"called: {called_names}" if not any_called else "",
            ))

    for tool in expectations.must_not_call:
        passed = tool not in called_names
        results.append((
            f"must_not_call: {tool}",
            passed,
            "but was called" if not passed else "",
        ))

    return results


def run_text_assertions(
    response_text: str,
    expectations: TextExpectations,
) -> list[tuple[str, bool, str]]:
    """Run text assertions."""
    results = []
    text_lower = response_text.lower()

    for pattern in expectations.must_contain:
        pattern = str(pattern)
        passed = pattern.lower() in text_lower
        results.append((
            f"must_contain: '{pattern}'",
            passed,
            "" if passed else "not found in response",
        ))

    for pattern in expectations.must_not_contain:
        pattern = str(pattern)
        passed = pattern.lower() not in text_lower
        results.append((
            f"must_not_contain: '{pattern}'",
            passed,
            "found in response" if not passed else "",
        ))

    return results


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_report(results: list[PromptResult], scenario_name: str) -> None:
    """Print formatted test report."""
    c = Colors

    print()
    print(f"{c.BOLD}{'=' * 70}{c.RESET}")
    print(f"{c.BOLD} SKILL TEST REPORT: {scenario_name}{c.RESET}")
    print(f"{c.BOLD}{'=' * 70}{c.RESET}")
    print()

    for result in results:
        status_icon = f"{c.GREEN}PASS{c.RESET}" if result.passed else f"{c.RED}FAIL{c.RESET}"
        print(f"{c.BOLD}Prompt {result.spec.index + 1}/{len(results)}: {result.spec.prompt[:60]}...{c.RESET}")

        for desc, passed, detail in result.tool_assertions:
            icon = f"{c.GREEN}+{c.RESET}" if passed else f"{c.RED}x{c.RESET}"
            detail_str = f" {c.DIM}({detail}){c.RESET}" if detail else ""
            print(f"  {icon} Tool: {desc}{detail_str}")

        for desc, passed, detail in result.text_assertions:
            icon = f"{c.GREEN}+{c.RESET}" if passed else f"{c.RED}x{c.RESET}"
            detail_str = f" {c.DIM}({detail}){c.RESET}" if detail else ""
            print(f"  {icon} Text: {desc}{detail_str}")

        print(f"  {c.BOLD}Status:{c.RESET} {status_icon}")
        print()

    print(f"{c.BOLD}{'=' * 70}{c.RESET}")
    passed_count = sum(1 for r in results if r.passed)
    total = len(results)
    print(f" Passed: {passed_count}/{total}")
    print(f"{c.BOLD}{'=' * 70}{c.RESET}")


def run_skill_test(
    prompts_file: Path,
    model: str = "sonnet",
    verbose: bool = False,
    prompt_index: int | None = None,
) -> list[PromptResult]:
    """Run skill test for a scenario."""
    scenario_name = prompts_file.stem

    specs = parse_prompts_file(prompts_file)
    if not specs:
        print(f"Error: No prompts found in {prompts_file}")
        return []

    if prompt_index is not None:
        if prompt_index < 0 or prompt_index >= len(specs):
            print(f"Error: prompt_index {prompt_index} out of range (0-{len(specs)-1})")
            return []
        specs = [specs[prompt_index]]
        print(f"Running prompt {prompt_index} from {prompts_file.name}")
    else:
        print(f"Running {len(specs)} prompts from {prompts_file.name}")

    print(f"Model: {model}")
    print()

    results: list[PromptResult] = []

    with trace_span(
        "skill_test.run",
        attributes={
            "scenario": scenario_name,
            "prompt_count": len(specs),
            "model": model,
        },
    ):
        for spec in specs:
            print(f"[{spec.index + 1}/{len(specs)}] {spec.prompt[:50]}...")

            response_text, tools_called, exit_code, duration = run_claude_prompt(
                spec.prompt, model=model, verbose=verbose, prompt_index=spec.index
            )

            if verbose:
                print(f"  Response length: {len(response_text)} chars")
                print(f"  Tools called: {[t.name for t in tools_called]}")

            tool_assertions = run_tool_assertions(tools_called, spec.expect.tools)
            text_assertions = run_text_assertions(response_text, spec.expect.text)

            result = PromptResult(
                spec=spec,
                response_text=response_text,
                tools_called=tools_called,
                exit_code=exit_code,
                tool_assertions=tool_assertions,
                text_assertions=text_assertions,
            )

            all_tool_passed = all(a[1] for a in tool_assertions)
            all_text_passed = all(a[1] for a in text_assertions)
            result.passed = all_tool_passed and all_text_passed

            results.append(result)
            print(f"  -> {'PASS' if result.passed else 'FAIL'}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Skill Test Runner - Test Claude Code skills against expectations"
    )
    parser.add_argument("prompts_file", type=Path, help="Path to .prompts file")
    parser.add_argument("--model", default="sonnet", help="Model for running prompts")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--prompt-index", type=int, help="Run only specific prompt (0-based)")
    parser.add_argument("--no-debug", action="store_true", help="Disable telemetry")
    args = parser.parse_args()

    if not args.prompts_file.exists():
        print(f"Error: File not found: {args.prompts_file}")
        sys.exit(1)

    scenario_name = args.prompts_file.stem

    init_telemetry(
        service_name="skill-test",
        scenario=scenario_name,
        debug=not args.no_debug,
    )

    results = run_skill_test(
        prompts_file=args.prompts_file,
        model=args.model,
        verbose=args.verbose,
        prompt_index=args.prompt_index,
    )

    if not results:
        sys.exit(1)

    print_report(results, scenario_name)
    shutdown_telemetry()

    if not all(r.passed for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
