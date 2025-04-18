import os
import yaml

DEFAULT_CONFIG = {
    'src_path': 'src',
    'language': 'python',
    'framework': 'pytest',
    'prompts': {
        'unit_test': (
            'Write {framework} tests for the following {language} function, '
            'including edge cases:\n\n'
            '{code}'
        ),
        # Template for generating tests to kill surviving mutants
        'kill_mutant': (
            'Write {framework} tests to kill the following mutant in {language} code:\n\n'
            '{diff}'
        ),
        'commit': (
            'Write a conventional commit message (type, scope, subject) '
            'for the following diff, following Conventional Commits format:\n\n'
            '{diff}'
        ),
        'refactor': (
            'Refactor the following {language} code focusing on {focus}. '
            'Provide the entire updated code without extra commentary:\n\n'
            '{code}'
        ),
        'audit_security': (
            'Audit the following {language} code for security vulnerabilities. '
            'List each issue with line numbers, a description, and a suggested fix:\n\n'
            '{code}'
        ),
        # Default prompt for generating docstrings
        'docstring': (
            'Write a Python docstring for the following {object_type} in {language} code, '
            'including descriptions of parameters and return values where applicable:\n\n'
            '{code}'
        ),
        # Default prompt for explaining code snippets
        'explain': (
            'Explain what the following {language} code does, providing a detailed, step-by-step explanation:\n\n'
            '{code}'
        )
    }
}

def write_default_config(path='.codex-autotest.yaml'):
    """Write the default configuration to the given path."""
    if os.path.exists(path):
        raise FileExistsError(f'{path} already exists')
    with open(path, 'w') as f:
        yaml.dump(DEFAULT_CONFIG, f)

def load_config(path='.codex-autotest.yaml'):
    """Load configuration from the given path."""
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} not found')
    with open(path) as f:
        return yaml.safe_load(f)