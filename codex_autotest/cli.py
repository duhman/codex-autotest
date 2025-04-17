import os
import sys
import click
from pathlib import Path
from string import Template
from .config import write_default_config, load_config
from .openai_client import chat_completion

@click.group()
def main():
    """codex-autotest: Generate and review tests using OpenAI Codex."""
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

if __name__ == '__main__':
    main()