 # Product Requirements Document (PRD)
 **Project Name**: codex-autotest
 **Author**: Adrian Marten
 **Version**: 0.2

 ---

 ## 1. Purpose
The purpose of this document is to define the product requirements for `codex-autotest`, an open-source CLI tool that leverages OpenAI Codex to automatically generate, review, and maintain test suites for codebases. This PRD outlines the problem statement, goals, features, user stories, and roadmap to guide the development of the v0.2 release and beyond.

 ## 2. Background & Problem Statement
 - Writing tests is time-consuming and often deferred, leading to lower code quality and more bugs in production.
 - Developers lack a standardized, automated way to generate meaningful tests (including edge cases) across different languages and frameworks.
 - Existing test-generation tools are limited in scope or require extensive manual configuration.

 ## 3. Goals & Objectives
 ### 3.1 Goals
 - Accelerate the creation of unit and integration tests.
 - Improve test coverage and code quality across diverse tech stacks.
 - Provide an extensible, community-driven framework for test automation.

 ### 3.2 Objectives (SMART)
 - Generate test skeletons with >=70% code coverage for simple modules in a single command.
 - Support at least 2 languages (Python, JavaScript) and 2 frameworks (pytest, Mocha).

 ## 4. Success Metrics
 - **Adoption**: Number of repositories using `codex-autotest` (tracked via CLI opt-in telemetry).
 - **Coverage Improvement**: Average increase in code coverage per project after running `generate`.
 - **Community Engagement**: Stars, forks, PRs, and issues filed on GitHub.
 - **Performance**: Average test generation time per file < 10 seconds.

 ## 5. User Personas & Stories
 ### 5.1 Personas
 - **Backend Developer**: Python/Node.js engineer aiming to ship reliable APIs.
 - **Full-Stack Engineer**: Maintains both frontend and backend, wants consistency in test practices.
 - **Team Lead/QA**: Wants to enforce test coverage standards across teams.

 ### 5.2 User Stories
 | ID   | As a            | I want to...                                                    | So that...                                         |
 |------|-----------------|-----------------------------------------------------------------|----------------------------------------------------|
 | US-1 | Developer       | scaffold test config & directories in an existing repo          | I don’t have to set up boilerplate manually       |
 | US-2 | Developer       | automatically generate test cases for my functions              | I catch bugs early with minimal effort             |
 | US-3 | Developer       | review and customize generated tests interactively              | tests match my coding standards and edge cases     |
 | US-4 | Team Lead       | integrate with CI to enforce test generation in pipelines       | all new code gets tested automatically             |

 ## 6. Functional Requirements
 ### 6.1 codex-autotest init
 - Command: `codex-autotest init [--template <lang>]`
 - Creates `.codex-autotest.yaml`, `tests/` directory, and CLI scaffolding.
 - Prompts user for language, framework, and CI integration options.

 ### 6.2 codex-autotest generate
 - Command: `codex-autotest generate --path <src_path> [--language <lang>] [--framework <fw>]`
 - Scans source files, extracts functions and classes.
 - Calls OpenAI API with templated prompts to propose tests (unit & edge cases).
 - Writes tests into `tests/` following existing directory structure.

 ### 6.3 codex-autotest review
 - Command: `codex-autotest review <test_file>`
 - Opens an interactive REPL where user can edit prompts and regenerate tests in real time.

 ### 6.4 Configuration Management
 - `.codex-autotest.yaml` supports user overrides for prompts, API keys, output paths, and generation styles (BDD vs TDD).

 ### 6.5 Plugin & Extensibility System
 - Plugin interface to add new languages, frameworks, or CI snippets without core changes.

### 6.6 codex-autotest mutate
 - Command: `codex-autotest mutate --path <src_path> [--language <lang>] [--framework <fw>]`
 - Runs mutation testing (e.g., mutmut) on the specified source files.
 - Parses surviving mutants, extracts diffs, and prompts Codex to generate tests that kill each mutant.
 - Writes generated kill tests to `tests/test_mutant_<module>_<id>.py`.

 ## 7. Non-Functional Requirements
 - **Performance**: Total test generation time < 10s/file under normal network conditions.
 - **Scalability**: Handle large codebases (100+ files) via batching and parallel API calls.
 - **Reliability**: Retry logic for transient API failures.
 - **Security**: Do not log or store source code or API keys insecurely.
 - **Usability**: CLI help, clear error messages, and sensible defaults.

 ## 8. Current Implementation Scope (v0.2)
 - Core CLI commands: init, generate, review, mutate.
 - Support Python+pytest, JavaScript+Mocha.
 - Built-in retry/backoff and LRU caching for OpenAI API calls.
 - Basic `.codex-autotest.yaml` configuration file with `unit_test` and `kill_mutant` templates.
 - Developer extras via `dev-requirements.txt` (mutmut, hypothesis).
 - GitHub Actions CI pipeline and PyPI release workflow.

 ## 9. Future Enhancements (v1.0+)
 - Additional languages: Java, Go, TypeScript.
 - CI integrations: GitHub Actions, GitLab CI templates.
 - Coverage analysis and gap-filling suggestions (`coverage` command).
 - Community prompt library and sharing marketplace.
 - Mutation-driven test amplification (`mutate` command) using mutation testing tools (e.g., mutmut) to automatically generate tests that kill surviving mutants.

 ## 10. Dependencies
 - OpenAI SDK (`openai` npm/PyPI package).
 - CLI framework: Python Click or JavaScript Commander.js.
 - YAML parser (PyYAML or js-yaml).

 ## 11. Assumptions
 - Users have valid OpenAI API keys and internet connectivity.
 - Developers are familiar with basic CLI usage.

 ## 12. Risks & Mitigations
 - **API Rate Limits**: Implement caching and respect rate limits. Provide fallback messaging.
 - **Low-Quality Tests**: Allow user feedback loop via `review` to refine prompts.
 - **Community Adoption**: Provide clear docs, quickstart, and onboarding templates.

## 13. Timeline & Milestones
- *Removed — timelines are now part of ongoing roadmap in GitHub issues.*

 ## 14. Stakeholders
 - **Product Owner**: Adrian Marten
 - **Maintainers**: Core Open-Source Contributors
 - **Community**: Open-Source Developers

 ---
 *End of Document*