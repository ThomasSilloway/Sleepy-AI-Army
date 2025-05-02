# Prompt for the TaskSetupAgent
from ...shared_libraries import constants

TASK_SETUP_AGENT_PROMPT = f"""
Analyze task description. Infer prefix from {constants.ALLOWED_PREFIXES} (default: {constants.DEFAULT_PREFIX}). Generate short (<=5 words) hyphenated slug.
Output ONLY JSON: {{"prefix": "...", "slug": "..."}}
Task: {{user_content}}
"""