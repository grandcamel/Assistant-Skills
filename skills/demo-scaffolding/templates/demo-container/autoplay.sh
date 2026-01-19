#!/bin/bash
# =============================================================================
# {{PRODUCT}} Demo Auto-Play Script
# =============================================================================
# Plays through scenario prompts with Claude's streaming API.
#
# Usage:
#   ./autoplay.sh <scenario>                    # Press-key to advance
#   ./autoplay.sh --auto-advance <scenario>     # Auto-advance with 3s delay
#   ./autoplay.sh --auto-advance --delay 5 <scenario>  # Custom delay
# =============================================================================

set -euo pipefail

SCENARIOS_DIR="${SCENARIOS_DIR:-/workspace/scenarios}"
PACING_MODE="keypress"
AUTO_DELAY=3
SCENARIO=""

# Colors
C_RESET='\033[0m'
C_BOLD='\033[1m'
C_DIM='\033[2m'
C_USER_BORDER='\033[1;34m'
C_CLAUDE_BORDER='\033[1;32m'
C_RED='\033[0;31m'
C_YELLOW='\033[1;33m'
C_GREEN='\033[0;32m'
C_CYAN='\033[0;36m'

# Box characters
BOX_TL='+'
BOX_TR='+'
BOX_BL='+'
BOX_BR='+'
BOX_H='-'
BOX_V='|'

TERMINAL_WIDTH=80
declare -a PROMPTS=()

get_terminal_width() {
    TERMINAL_WIDTH=$(tput cols 2>/dev/null || echo 80)
    if [[ $TERMINAL_WIDTH -gt 100 ]]; then
        TERMINAL_WIDTH=100
    fi
}

repeat_char() {
    local char="$1"
    local count="$2"
    printf "%${count}s" | tr ' ' "$char"
}

draw_box_top() {
    local color="$1"
    local width=$((TERMINAL_WIDTH - 2))
    echo -e "${color}${BOX_TL}$(repeat_char "$BOX_H" "$width")${BOX_TR}${C_RESET}"
}

draw_box_line() {
    local color="$1"
    local content="$2"
    local width=$((TERMINAL_WIDTH - 4))
    printf "${color}${BOX_V}${C_RESET} %-${width}s ${color}${BOX_V}${C_RESET}\n" "$content"
}

draw_box_bottom() {
    local color="$1"
    local width=$((TERMINAL_WIDTH - 2))
    echo -e "${color}${BOX_BL}$(repeat_char "$BOX_H" "$width")${BOX_BR}${C_RESET}"
}

display_user_bubble() {
    local prompt="$1"
    echo ""
    draw_box_top "$C_USER_BORDER"
    draw_box_line "$C_USER_BORDER" "USER"
    echo -e "${C_USER_BORDER}|$(repeat_char "$BOX_H" $((TERMINAL_WIDTH - 2)))|${C_RESET}"
    while IFS= read -r line; do
        draw_box_line "$C_USER_BORDER" "$line"
    done <<< "$prompt"
    draw_box_bottom "$C_USER_BORDER"
    echo ""
}

parse_prompts_file() {
    local file="$1"
    local current_prompt=""
    local in_prompt=false

    PROMPTS=()

    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ "$line" =~ ^# ]] && continue

        if [[ "$line" == "---" ]]; then
            if [[ -n "$current_prompt" ]]; then
                current_prompt="${current_prompt#"${current_prompt%%[![:space:]]*}"}"
                current_prompt="${current_prompt%"${current_prompt##*[![:space:]]}"}"
                [[ -n "$current_prompt" ]] && PROMPTS+=("$current_prompt")
            fi
            current_prompt=""
            in_prompt=false
            continue
        fi

        if [[ "$line" =~ ^prompt:\ *\|\ *$ ]]; then
            in_prompt=true
            continue
        fi

        if [[ "$line" =~ ^prompt:\ +(.+)$ ]]; then
            current_prompt="${BASH_REMATCH[1]}"
            in_prompt=false
            continue
        fi

        if [[ "$in_prompt" == true ]] && [[ "$line" =~ ^[a-z_]+: ]]; then
            in_prompt=false
            continue
        fi

        if [[ "$in_prompt" == true ]]; then
            local content="${line#  }"
            [[ -n "$current_prompt" ]] && current_prompt+=$'\n'
            current_prompt+="$content"
        fi
    done < "$file"

    if [[ -n "$current_prompt" ]]; then
        current_prompt="${current_prompt#"${current_prompt%%[![:space:]]*}"}"
        current_prompt="${current_prompt%"${current_prompt##*[![:space:]]}"}"
        [[ -n "$current_prompt" ]] && PROMPTS+=("$current_prompt")
    fi
}

run_claude_prompt() {
    local prompt="$1"
    echo -e "${C_DIM}  Running Claude...${C_RESET}"
    claude -p "$prompt" --dangerously-skip-permissions 2>&1
}

wait_for_advance() {
    local current="$1"
    local total="$2"

    echo ""
    if [[ "$PACING_MODE" == "keypress" ]]; then
        echo -en "${C_DIM}[Press any key to continue... (${current}/${total})]${C_RESET}"
        read -rsn1
        echo ""
    else
        echo -en "${C_DIM}[Auto-advancing in ${AUTO_DELAY}s... (${current}/${total})]${C_RESET}"
        sleep "$AUTO_DELAY"
        echo ""
    fi
}

show_usage() {
    echo "Usage: $0 [options] <scenario>"
    echo ""
    echo "Options:"
    echo "  --auto-advance, -a    Auto-advance instead of waiting for keypress"
    echo "  --delay, -d <secs>    Delay between prompts in auto mode (default: 3)"
    echo "  --help, -h            Show this help message"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --auto-advance|-a)
                PACING_MODE="auto"
                shift
                ;;
            --delay|-d)
                AUTO_DELAY="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                echo -e "${C_RED}Unknown option: $1${C_RESET}"
                show_usage
                exit 1
                ;;
            *)
                SCENARIO="$1"
                shift
                ;;
        esac
    done

    if [[ -z "$SCENARIO" ]]; then
        echo -e "${C_RED}Error: No scenario specified${C_RESET}"
        show_usage
        exit 1
    fi
}

run_scenario() {
    local prompts_file="${SCENARIOS_DIR}/${SCENARIO}.prompts"

    if [[ ! -f "$prompts_file" ]]; then
        echo -e "${C_RED}Error: Scenario file not found: $prompts_file${C_RESET}"
        exit 1
    fi

    parse_prompts_file "$prompts_file"

    local total=${#PROMPTS[@]}
    if [[ $total -eq 0 ]]; then
        echo -e "${C_RED}Error: No prompts found in scenario file${C_RESET}"
        exit 1
    fi

    echo ""
    echo -e "${C_CYAN}Starting scenario: ${C_BOLD}${SCENARIO}${C_RESET}"
    echo -e "${C_CYAN}Total steps: ${total}${C_RESET}"
    echo ""

    if [[ "$PACING_MODE" == "keypress" ]]; then
        echo -en "${C_DIM}[Press any key to start...]${C_RESET}"
        read -rsn1
        echo ""
    else
        sleep 2
    fi

    for ((i=0; i<total; i++)); do
        local step=$((i + 1))
        local prompt="${PROMPTS[$i]}"

        get_terminal_width

        echo ""
        echo -e "${C_BOLD}$(repeat_char '=' "$TERMINAL_WIDTH")${C_RESET}"
        echo -e "${C_YELLOW}Step ${step}/${total}${C_RESET}"
        echo -e "${C_BOLD}$(repeat_char '=' "$TERMINAL_WIDTH")${C_RESET}"

        display_user_bubble "$prompt"
        run_claude_prompt "$prompt"

        if [[ $step -lt $total ]]; then
            wait_for_advance "$step" "$total"
        fi
    done

    echo ""
    echo -e "${C_GREEN}$(repeat_char '=' "$TERMINAL_WIDTH")${C_RESET}"
    echo -e "${C_GREEN}${C_BOLD}  Scenario complete!${C_RESET}"
    echo -e "${C_GREEN}$(repeat_char '=' "$TERMINAL_WIDTH")${C_RESET}"
    echo ""
}

main() {
    if ! command -v claude &>/dev/null; then
        echo -e "${C_RED}Error: claude CLI is required but not installed${C_RESET}"
        exit 1
    fi

    parse_arguments "$@"
    get_terminal_width
    run_scenario
}

main "$@"
