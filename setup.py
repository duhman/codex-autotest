from setuptools import setup, find_packages

setup(
    name='codex-autotest',
    version='0.2.0',
    description='CLI tool to generate and review tests using OpenAI Codex',
    author='Adrian Marten',
    packages=find_packages(),
    install_requires=[
        'click',
        'openai',
        'PyYAML',
    ],
    extras_require={
        'dev': ['mutmut', 'hypothesis'],
    },
    entry_points={
        'console_scripts': [
            'codex-autotest=codex_autotest.cli:main',
        ],
    },
)