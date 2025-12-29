"""
Assistant Builder Shared Library

Provides common utilities for the assistant-builder skill:
- template_engine: Template loading and placeholder replacement
- project_detector: Detect and analyze Assistant Skills projects
- formatters: Output formatting (tables, trees, JSON)
- validators: Input validation utilities
"""

__version__ = "0.1.0"

from .template_engine import load_template, render_template, list_placeholders
from .project_detector import detect_project, list_skills, get_topic_prefix
from .formatters import format_table, format_tree, format_json, print_success, print_error
from .validators import validate_required, validate_path, validate_name
