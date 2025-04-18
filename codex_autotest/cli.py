import os
import sys
import click
from pathlib import Path
from string import Template
from .config import write_default_config, load_config, DEFAULT_CONFIG
from .openai_client import chat_completion
import ast
import difflib
import subprocess
import re

@click.group()
def main():
    """codex-autotest: AI-assisted development commands (explain, test generation, docstrings, refactoring, commits, security audits)"""
    pass

@main.command()
@click.option('--template', default=None, help='Optional template name')
def init(template):
    """Initialize codex-autotest in the current repository."""
    config_path = '.codex-autotest.yaml'
    try:
        write_default_config(config_path)
        os.makedirs('tests', exist_ok=True)
        click.echo(f'Initialized codex-autotest with config at {config_path} and tests/ directory.')
    except FileExistsError:
        click.echo(f'Config file {config_path} already exists. Aborting.', err=True)

@main.command()
@click.option('--path', 'src_path', default=None, help='Source path to scan for files')
@click.option('--language', default=None, help='Language override')
@click.option('--framework', default=None, help='Framework override')
def generate(src_path, language, framework):
    """Generate tests for source code files."""
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError:
        click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
        return
    # Determine source path (flag overrides config)
    path = src_path or config.get('src_path', None)
    if not path:
        click.echo('Source path must be provided or defined in config.', err=True)
        return
    lang = language or config.get('language', 'python')
    fw = framework or config.get('framework', '')
    prompts = config.get('prompts', {})
    unit_prompt_tpl = prompts.get('unit_test', '')
    # Check API key
    try:
        os.environ['OPENAI_API_KEY'] and None
    except Exception:
        click.echo('OPENAI_API_KEY is not set. Please export your API key.', err=True)
        return
    # Clear ChatCompletion cache and prepare templating
    chat_completion.cache_clear()
    use_str_template = '$' in unit_prompt_tpl
    if use_str_template:
        str_tpl = Template(unit_prompt_tpl)
    ext_map = {'python': '.py', 'javascript': '.js'}
    ext = ext_map.get(lang.lower(), '.py')
    files = Path(path).rglob(f'*{ext}')
    for f in files:
        code = f.read_text()
        if use_str_template:
            prompt = str_tpl.safe_substitute(language=lang, framework=fw, code=code)
        else:
            prompt = unit_prompt_tpl.format(language=lang, framework=fw, code=code)
        click.echo(f'Generating tests for {f}')
        try:
            test_code = chat_completion(prompt)
        except Exception as e:
            click.echo(f'Error generating tests for {f}: {e}', err=True)
            continue
        rel_path = f.relative_to(src_path)
        # Determine test file path with matching extension
        test_file = Path('tests') / rel_path.parent / f'test_{f.stem}{ext}'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code)
        click.echo(f'Wrote tests to {test_file}')

@main.command()
@click.argument('test_file')
def review(test_file):
    """Review and regenerate tests interactively."""
    try:
        config = load_config()
    except FileNotFoundError:
        click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
        return
    src_path = config.get('src_path', None)
    if not src_path:
        click.echo('src_path is not configured in .codex-autotest.yaml', err=True)
        return
    lang = config.get('language', '')
    fw = config.get('framework', '')
    prompts = config.get('prompts', {})
    unit_prompt_tpl = prompts.get('unit_test', '')
    ext_map = {'python': '.py', 'javascript': '.js'}
    ext = ext_map.get(lang.lower(), '.py')

    test_path = Path(test_file)
    if not test_path.exists():
        click.echo(f'Test file {test_file} not found.', err=True)
        return
    try:
        rel = test_path.relative_to('tests')
    except Exception:
        click.echo('Please provide a test file under the "tests/" directory.', err=True)
        return
    name = rel.name
    if name.startswith('test_'):
        src_name = name[len('test_'):]
    else:
        src_name = name
    if not src_name.endswith(ext):
        src_name = Path(src_name).stem + ext
    code_path = Path(src_path) / rel.parent / src_name
    if not code_path.exists():
        click.echo(f'Could not find source file {code_path} for test {test_file}.', err=True)
        return
    code = code_path.read_text()

    click.echo(f'Current test code for {test_file}:\n')
    click.echo(test_path.read_text())

    # Interactive prompt editing and regeneration loop using multi-line editor
    prompt_template = unit_prompt_tpl
    # Ensure API key and clear cache
    try:
        os.environ['OPENAI_API_KEY'] and None
    except Exception:
        click.echo('OPENAI_API_KEY is not set. Please export your API key.', err=True)
        return
    chat_completion.cache_clear()
    while True:
        # Use editor for interactive TTY sessions, else fallback to prompt input
        if sys.stdin.isatty():
            click.echo('\nOpening editor to customize the prompt. Save to apply changes, or exit without saving to keep existing prompt.')
            edited = click.edit(text=prompt_template, require_save=True)
            if edited is not None:
                prompt_template = edited.rstrip('\n')
        else:
            click.echo('\nEnter a new prompt (or leave empty to use previous/default):')
            new_prompt = click.prompt('Prompt', default=prompt_template)
            prompt_template = new_prompt
        click.echo('\nUsing prompt:\n' + prompt_template)
        # Render prompt using templating
        if '$' in prompt_template:
            prompt = Template(prompt_template).safe_substitute(language=lang, framework=fw, code=code)
        else:
            try:
                prompt = prompt_template.format(language=lang, framework=fw, code=code)
            except Exception as e:
                click.echo(f'Error formatting prompt: {e}', err=True)
                return
        try:
            new_test_code = chat_completion(prompt)
        except Exception as e:
            click.echo(f'Error regenerating tests: {e}', err=True)
            return

        click.echo('\nGenerated new test code:\n')
        click.echo(new_test_code)
        if click.confirm(f'Overwrite {test_file}?'):
            test_path.write_text(new_test_code)
            click.echo(f'Wrote updated tests to {test_file}')
            break
        elif click.confirm('Edit prompt and regenerate?', default=True):
            continue
        else:
            click.echo('Aborted. No changes written.')
            break

@main.command()
@click.option('--path', 'src_path', default=None, help='Source path to mutate and generate kill tests')
@click.option('--language', default=None, help='Language override')
@click.option('--framework', default=None, help='Framework override')
def mutate(src_path, language, framework):
    """Run mutation-driven test amplification to kill surviving mutants."""
    try:
        config = load_config()
    except FileNotFoundError:
        click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
        return
    # Determine language/framework
    lang = language or config.get('language', 'python')
    fw = framework or config.get('framework', '')
    prompts = config.get('prompts', {})
    kill_prompt_tpl = prompts.get('kill_mutant', '')
    if not kill_prompt_tpl:
        click.echo('No kill_mutant prompt configured.', err=True)
        return
    import shutil, subprocess, json
    # Determine source path (flag overrides config)
    path = src_path or config.get('src_path', None)
    if not path:
        click.echo('Source path must be provided or defined in config.', err=True)
        return
    # Ensure mutmut is installed
    if shutil.which('mutmut') is None:
        click.echo('mutmut not found. Please install mutmut to use the mutate command.', err=True)
        return
    # Run mutation testing
    click.echo(f'Running mutmut on {path}...')
    run_res = subprocess.run(['mutmut', 'run', '--paths-to-mutate', path],
                             capture_output=True, text=True)
    if run_res.returncode != 0:
        click.echo(f'Error running mutmut: {run_res.stderr}', err=True)
        return
    # Get JSON results
    res_res = subprocess.run(['mutmut', 'results', '--json'],
                              capture_output=True, text=True)
    if res_res.returncode != 0:
        click.echo(f'Error getting mutmut results: {res_res.stderr}', err=True)
        return
    try:
        results = json.loads(res_res.stdout)
    except Exception as e:
        click.echo(f'Error parsing mutmut results: {e}', err=True)
        return
    # Filter surviving mutants
    survived = [m for m in results if m.get('status') == 'survived']
    if not survived:
        click.echo('No surviving mutants. All mutants are killed by existing tests!')
        return
    # Ensure API key and clear cache
    try:
        os.environ['OPENAI_API_KEY'] and None
    except Exception:
        click.echo('OPENAI_API_KEY is not set. Please export your API key.', err=True)
        return
    chat_completion.cache_clear()
    # Process each surviving mutant
    for m in survived:
        mutation_id = m.get('id')
        filename = m.get('filename')
        click.echo(f'Processing surviving mutant {mutation_id} in {filename}...')
        show_res = subprocess.run(['mutmut', 'show', str(mutation_id)],
                                  capture_output=True, text=True)
        if show_res.returncode != 0:
            click.echo(f'Error showing mutant {mutation_id}: {show_res.stderr}', err=True)
            continue
        diff = show_res.stdout
        # Prepare prompt
        # Prepare prompt
        if '$' in kill_prompt_tpl:
            prompt = Template(kill_prompt_tpl).safe_substitute(language=lang, framework=fw, diff=diff)
        else:
            try:
                prompt = kill_prompt_tpl.format(language=lang, framework=fw, diff=diff)
            except Exception as e:
                click.echo(f'Error formatting kill prompt: {e}', err=True)
                continue
        click.echo(f'Generating test to kill mutant {mutation_id}...')
        try:
            test_code = chat_completion(prompt)
        except Exception as e:
            click.echo(f'Error generating kill test: {e}', err=True)
            continue
        # Write test file
        module = Path(filename).stem
        test_file = Path('tests') / f'test_mutant_{module}_{mutation_id}.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code)
        click.echo(f'Wrote kill test to {test_file}')

@main.command()
@click.argument('target')
@click.option('--language', default=None, help='Language override for code explanation')
@click.option('--model', default=None, help='OpenAI model to use for explanation')
@click.option('--max-tokens', 'max_tokens', default=None, type=int, help='Maximum tokens for the explanation')
def explain(target, language, model, max_tokens):
    """Explain what the given code snippet or file does using OpenAI Codex."""
    path_str = target
    start = end = None
    if ':' in target:
        path_str, rng = target.split(':', 1)
        if '-' in rng:
            s, e = rng.split('-', 1)
            try:
                start, end = int(s), int(e)
            except ValueError:
                click.echo(f'Invalid range spec "{rng}"; use start-end', err=True)
                return
        else:
            click.echo(f'Invalid range spec "{rng}"; use start-end', err=True)
            return
    path = Path(path_str)
    if not path.exists():
        click.echo(f'File not found: {path_str}', err=True)
        return
    content = path.read_text()
    if start is not None and end is not None:
        lines = content.splitlines()
        if start < 1 or end > len(lines) or start > end:
            click.echo(f'Invalid line range {start}-{end} for file with {len(lines)} lines', err=True)
            return
        snippet = '\n'.join(lines[start-1:end])
    else:
        snippet = content
    ext_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.java': 'java',
               '.go': 'go', '.rb': 'ruby'}
    ext = path.suffix.lower()
    lang = language or ext_map.get(ext)
    if not lang:
        click.echo(f'Could not infer language from extension "{ext}"; specify --language', err=True)
        return
    prompt = (
        f"Explain what the following {lang} code does, providing a detailed, step-by-step "
        f"explanation:\n\n{snippet}"
    )
    try:
        chat_completion.cache_clear()
    except Exception:
        pass
    kwargs = {}
    if model:
        kwargs['model'] = model
    if max_tokens:
        kwargs['max_tokens'] = max_tokens
    try:
        explanation = chat_completion(prompt, **kwargs)
    except Exception as e:
        click.echo(f'Error generating explanation: {e}', err=True)
        return
    click.echo(explanation)

@main.command()
@click.option('--path', 'src_path', default=None, help='Source path to scan for Python files')
@click.option('--apply', 'apply_changes', is_flag=True, default=False, help='Apply changes to files')
def docstring(src_path, apply_changes):
    """Generate or preview docstring insertions for functions, classes, and methods."""
    # Load config only if no explicit path provided
    if src_path:
        config = {}
    else:
        try:
            config = load_config()
        except FileNotFoundError:
            click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
            return
    path = src_path or config.get('src_path')
    if not path:
        click.echo('Source path must be provided or defined in config.', err=True)
        return
    files = Path(path).rglob('*.py')
    default_prompt = (
        'Write a Python docstring for the following {object_type} in {language} code, '
        'including descriptions of parameters and return values where applicable:\n\n'
        '{code}'
    )
    prompts = config.get('prompts', {})
    prompt_tpl = prompts.get('docstring', default_prompt)
    error_files = False
    for f in files:
        content = f.read_text()
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            click.echo(f'SyntaxError parsing {f}: {e}', err=True)
            error_files = True
            continue
        lines = content.splitlines()
        insertions = []
        for node in tree.body:
            # Top-level functions and classes
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node, clean=False) is None:
                    body = node.body
                    if body:
                        first = body[0]
                        insertions.append((first.lineno, node, 'class' if isinstance(node, ast.ClassDef) else 'function'))
            # Methods inside classes
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if ast.get_docstring(child, clean=False) is None:
                            body = child.body
                            if body:
                                first = body[0]
                                insertions.append((first.lineno, child, 'method'))
        if not insertions:
            continue
        # Process from bottom up
        insertions.sort(key=lambda x: x[0], reverse=True)
        new_lines = lines.copy()
        for lineno, node, obj_type in insertions:
            # Extract code snippet for context
            snippet = '\n'.join(lines[node.lineno - 1: getattr(node, 'end_lineno', node.lineno) ])
            # Build prompt
            if '$' in prompt_tpl:
                prompt = Template(prompt_tpl).safe_substitute(language='python', object_type=obj_type, code=snippet)
            else:
                try:
                    prompt = prompt_tpl.format(language='python', object_type=obj_type, code=snippet)
                except Exception as e:
                    click.echo(f'Error formatting prompt for {f}: {e}', err=True)
                    continue
            # Generate docstring
            try:
                chat_completion.cache_clear()
            except Exception:
                pass
            try:
                doc = chat_completion(prompt)
            except Exception as e:
                click.echo(f'Error generating docstring for {f}: {e}', err=True)
                continue
            doc = doc.strip()
            if not (doc.startswith('"""') and doc.endswith('"""')):
                doc = f'"""{doc}"""'
            # Determine indentation from first statement line
            orig = lines[lineno - 1]
            indent = re.match(r'\s*', orig).group(0)
            # Prepare indented docstring lines
            doc_lines = doc.splitlines()
            indented = [indent + dl for dl in doc_lines]
            # Insert before the first statement
            new_lines[lineno - 1:lineno - 1] = indented
        result = '\n'.join(new_lines) + '\n'
        if apply_changes:
            f.write_text(result)
            click.echo(f'Applied docstrings to {f}')
        else:
            diff = difflib.unified_diff(lines, new_lines, fromfile=str(f), tofile=str(f), lineterm='')
            for d in diff:
                click.echo(d)
    if error_files:
        return

@main.command(name='generate-tests')
@click.option('--path', 'src_path', default=None, help='Source path to scan for files')
@click.option('--language', default=None, help='Language override')
@click.option('--framework', default=None, help='Framework override')
@click.option('--apply', 'apply_changes', is_flag=True, default=False, help='Apply generated tests instead of showing diff')
def generate_tests(src_path, language, framework, apply_changes):
    """Generate or preview test files for source code functions and classes."""
    # Load configuration unless path explicitly provided
    if src_path:
        config = {}
    else:
        try:
            config = load_config()
        except FileNotFoundError:
            click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
            return
    path = src_path or config.get('src_path')
    if not path:
        click.echo('Source path must be provided or defined in config.', err=True)
        return
    lang = language or config.get('language', 'python')
    fw = framework or config.get('framework', '')
    prompts = config.get('prompts', {})
    default_prompt = DEFAULT_CONFIG['prompts'].get('unit_test', '')
    prompt_tpl = prompts.get('unit_test', default_prompt)
    use_str_template = '$' in prompt_tpl
    if use_str_template:
        str_tpl = Template(prompt_tpl)
    ext_map = {'python': '.py', 'javascript': '.js'}
    ext = ext_map.get(lang.lower(), '.py')
    path_obj = Path(path)
    files = path_obj.rglob(f'*{ext}')
    for f in files:
        if f.name == '__init__.py':
            continue
        code = f.read_text()
        if use_str_template:
            prompt = str_tpl.safe_substitute(language=lang, framework=fw, code=code)
        else:
            prompt = prompt_tpl.format(language=lang, framework=fw, code=code)
        click.echo(f'Generating tests for {f}')
        try:
            chat_completion.cache_clear()
        except Exception:
            pass
        try:
            test_code = chat_completion(prompt)
        except Exception as e:
            click.echo(f'Error generating tests for {f}: {e}', err=True)
            continue
        rel_path = f.relative_to(path_obj)
        test_file = Path('tests') / rel_path.parent / f'test_{f.stem}{ext}'
        existing = test_file.read_text().splitlines() if test_file.exists() else []
        new_lines = test_code.splitlines()
        if apply_changes:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(test_code)
            click.echo(f'Wrote tests to {test_file}')
        else:
            diff = difflib.unified_diff(existing, new_lines, fromfile=str(test_file), tofile=str(test_file), lineterm='')
            for line in diff:
                click.echo(line)
        
@main.command()
@click.option('--path', 'src_path', default=None, help='Source path to scan for files')
@click.option('--focus', default=None, help='Refactoring focus (e.g., performance, readability)')
@click.option('--language', default=None, help='Language override')
@click.option('--apply', 'apply_changes', is_flag=True, default=False, help='Apply refactored code instead of showing diff')
def refactor(src_path, focus, language, apply_changes):
    """Refactor source code files based on the given focus (e.g., performance, readability)."""
    # Load configuration unless path explicitly provided
    if src_path:
        config = {}
    else:
        try:
            config = load_config()
        except FileNotFoundError:
            click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
            return
    path = src_path or config.get('src_path')
    if not path:
        click.echo('Source path must be provided or defined in config.', err=True)
        return
    lang = language or config.get('language', 'python')
    prompts = config.get('prompts', {})
    # default refactor prompt
    default_prompt = DEFAULT_CONFIG['prompts'].get('refactor',
        'Refactor the following {language} code focusing on {focus}. '
        'Provide the entire updated code without extra commentary:\n\n{code}'
    )
    prompt_tpl = prompts.get('refactor', default_prompt)
    use_str_template = '$' in prompt_tpl
    if use_str_template:
        str_tpl = Template(prompt_tpl)
    ext_map = {'python': '.py', 'javascript': '.js'}
    ext = ext_map.get(lang.lower(), '.py')
    path_obj = Path(path)
    files = path_obj.rglob(f'*{ext}')
    for f in files:
        if f.name == '__init__.py':
            continue
        code = f.read_text()
        # Render prompt
        if use_str_template:
            prompt = str_tpl.safe_substitute(language=lang, focus=focus or '', code=code)
        else:
            try:
                prompt = prompt_tpl.format(language=lang, focus=focus or '', code=code)
            except Exception as e:
                click.echo(f'Error formatting prompt for {f}: {e}', err=True)
                continue
        click.echo(f'Refactoring {f}')
        try:
            chat_completion.cache_clear()
        except Exception:
            pass
        try:
            new_code = chat_completion(prompt)
        except Exception as e:
            click.echo(f'Error refactoring {f}: {e}', err=True)
            continue
        original_lines = code.splitlines()
        new_lines = new_code.splitlines()
        if apply_changes:
            f.write_text(new_code)
            click.echo(f'Wrote refactored code to {f}')
        else:
            diff = difflib.unified_diff(original_lines, new_lines,
                                        fromfile=str(f), tofile=str(f), lineterm='')
            for line in diff:
                click.echo(line)
        
@main.command()
@click.option('--staged', is_flag=True, default=False, help='Generate commit message for staged changes')
@click.option('--model', default=None, help='OpenAI model to use for commit message')
@click.option('--max-tokens', 'max_tokens', default=None, type=int, help='Maximum tokens for the commit message')
def commit(staged, model, max_tokens):
    """Generate a conventional commit message using OpenAI Codex."""
    if not staged:
        click.echo('Please specify --staged to generate commit message for staged changes.', err=True)
        return
    import subprocess
    run = subprocess.run(['git', 'diff', '--staged'], capture_output=True, text=True)
    if run.returncode != 0:
        click.echo(f'Error getting staged diff: {run.stderr}', err=True)
        return
    diff = run.stdout
    if not diff.strip():
        click.echo('No staged changes detected.', err=True)
        return
    try:
        config = load_config()
    except FileNotFoundError:
        config = {}
    prompts = config.get('prompts', {})
    default_prompt = DEFAULT_CONFIG.get('prompts', {}).get('commit', '')
    prompt_tpl = prompts.get('commit', default_prompt)
    # Build prompt
    if '$' in prompt_tpl:
        from string import Template as _Tpl
        prompt = _Tpl(prompt_tpl).safe_substitute(diff=diff)
    else:
        try:
            prompt = prompt_tpl.format(diff=diff)
        except Exception as e:
            click.echo(f'Error formatting commit prompt: {e}', err=True)
            return
    try:
        chat_completion.cache_clear()
    except Exception:
        pass
    kwargs = {}
    if model:
        kwargs['model'] = model
    if max_tokens:
        kwargs['max_tokens'] = max_tokens
    try:
        msg = chat_completion(prompt, **kwargs)
    except Exception as e:
        click.echo(f'Error generating commit message: {e}', err=True)
        return
    click.echo(msg)
    
@main.command(name='audit-security')
@click.option('--path', 'src_path', default=None, help='Source path to scan for security audit')
@click.option('--language', default=None, help='Language override (e.g., python, javascript)')
@click.option('--output', default='security_audit_report.md', help='Path to write the audit report')
@click.option('--apply-fixes', is_flag=True, default=False, help='Apply suggested fixes to source files')
def audit_security(src_path, language, output, apply_fixes):
    """Perform a security audit using OpenAI Codex and optionally apply fixes."""
    # Load configuration unless path explicitly provided
    if src_path:
        config = {}
    else:
        try:
            config = load_config()
        except FileNotFoundError:
            click.echo('Configuration not found. Please run "codex-autotest init" first.', err=True)
            return
    path = src_path or config.get('src_path')
    if not path:
        click.echo('Source path must be provided or defined in config.', err=True)
        return
    lang = language or config.get('language', 'python')
    # Determine file extension for scanning
    ext_map = {'python': '.py', 'javascript': '.js', 'typescript': '.ts'}
    ext = ext_map.get(lang.lower(), '.py')
    base = Path(path)
    files = list(base.rglob(f'*{ext}'))
    if not files:
        click.echo(f'No {ext} files found under {path}.', err=True)
        return
    # Default audit prompt
    default_prompt = (
        'Audit the following {language} code for security vulnerabilities. '
        'List each issue with line numbers, a description, and a suggested fix:\n\n'
        '{code}'
    )
    prompts = config.get('prompts', {})
    prompt_tpl = prompts.get('audit_security', default_prompt)
    use_str_template = '$' in prompt_tpl
    report_lines = []
    fixes = {}
    for f in files:
        code = f.read_text()
        # Build prompt
        if use_str_template:
            prompt = Template(prompt_tpl).safe_substitute(language=lang, code=code)
        else:
            try:
                prompt = prompt_tpl.format(language=lang, code=code)
            except Exception as e:
                click.echo(f'Error formatting audit prompt for {f}: {e}', err=True)
                continue
        # Invoke Codex for audit
        try:
            chat_completion.cache_clear()
        except Exception:
            pass
        try:
            audit = chat_completion(prompt)
        except Exception as e:
            click.echo(f'Error auditing {f}: {e}', err=True)
            continue
        report_lines.append(f'## File: {f}\n')
        report_lines.append(audit)
        report_lines.append('\n')
        if apply_fixes:
            # Ask for fixes
            fix_prompt = (
                'Apply the security fixes suggested below to the {language} code. '
                'Return only the full updated code without commentary.\n\n'
                'Issues:\n{audit}\n\n'
                'Code:\n{code}'
            )
            if '$' in fix_prompt:
                fix_tpl = Template(fix_prompt)
                fp = fix_tpl.safe_substitute(language=lang, audit=audit, code=code)
            else:
                fp = fix_prompt.format(language=lang, audit=audit, code=code)
            try:
                chat_completion.cache_clear()
            except Exception:
                pass
            try:
                new_code = chat_completion(fp)
            except Exception as e:
                click.echo(f'Error generating fixes for {f}: {e}', err=True)
                continue
            fixes[str(f)] = new_code
    # Write report
    report_text = '\n'.join(report_lines)
    try:
        Path(output).write_text(report_text)
        click.echo(f'Wrote security audit report to {output}')
    except Exception as e:
        click.echo(f'Error writing report to {output}: {e}', err=True)
        return
    # Apply fixes if requested
    if apply_fixes:
        for fp, code in fixes.items():
            try:
                Path(fp).write_text(code)
                click.echo(f'Applied security fixes to {fp}')
            except Exception as e:
                click.echo(f'Error writing fixes to {fp}: {e}', err=True)

if __name__ == '__main__':
    main()