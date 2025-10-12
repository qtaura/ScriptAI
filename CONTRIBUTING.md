# Contributing to ScriptAI

Thank you for considering contributing to ScriptAI! This document outlines the process for contributing to the project and how to report issues.

## Professional Conduct

By participating in this project, you agree to maintain professional conduct and respect all contributors. We are committed to providing a welcoming and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ScriptAI. Following these guidelines helps maintainers understand your report, reproduce the issue, and find related reports.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report).

#### Before Submitting A Bug Report

* **Check the [FAQs](https://github.com/jailk123/ScriptAI/wiki/FAQ)** for a list of common questions and problems.
* **Perform a [search](https://github.com/jailk123/ScriptAI/issues)** to see if the problem has already been reported. If it has and the issue is still open, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem.
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for ScriptAI, including completely new features and minor improvements to existing functionality.

#### Before Submitting An Enhancement Suggestion

* **Perform a [search](https://github.com/jailk123/ScriptAI/issues)** to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** to most ScriptAI users.
* **List some other applications where this enhancement exists.**

### Pull Requests

The process described here has several goals:

- Maintain ScriptAI's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible ScriptAI
- Enable a sustainable system for ScriptAI's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 🚱 `:non-potable_water:` when plugging memory leaks
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * 💚 `:green_heart:` when fixing the CI build
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security
    * ⬆️ `:arrow_up:` when upgrading dependencies
    * ⬇️ `:arrow_down:` when downgrading dependencies
    * 👕 `:shirt:` when removing linter warnings

### Python Styleguide

All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### JavaScript Styleguide

All JavaScript code must adhere to the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Reference methods and classes in markdown with the custom `{.method}` syntax:
    * Reference classes with `{ClassName}`
    * Reference instance methods with `{ClassName.methodName}`
    * Reference class methods with `{ClassName.methodName}`

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

[GitHub search](https://help.github.com/articles/searching-issues/) makes it easy to use labels for finding groups of issues or pull requests you're interested in.

The labels are loosely grouped by their purpose, but it's not required that every issue has a label from every group or that an issue can't have more than one label from the same group.

Please open an issue if you have suggestions for new labels.

#### Type of Issue and Issue State

* `enhancement`: Feature requests.
* `bug`: Confirmed bugs or reports that are very likely to be bugs.
* `question`: Questions more than bug reports or feature requests (e.g. how do I do X).
* `feedback`: General feedback more than bug reports or feature requests.
* `help-wanted`: The ScriptAI core team would appreciate help from the community in resolving these issues.
* `beginner`: Less complex issues which would be good first issues to work on for users who want to contribute to ScriptAI.
* `more-information-needed`: More information needs to be collected about these problems or feature requests (e.g. steps to reproduce).
* `needs-reproduction`: Likely bugs, but haven't been reliably reproduced.
* `blocked`: Issues blocked on other issues.
* `duplicate`: Issues which are duplicates of other issues, i.e. they have been reported before.
* `wontfix`: The ScriptAI core team has decided not to fix these issues for now, either because they're working as intended or for some other reason.
* `invalid`: Issues which aren't valid (e.g. user errors).

#### Topic Categories

* `documentation`: Related to any type of documentation.
* `performance`: Related to performance.
* `security`: Related to security.
* `ui`: Related to visual design.
* `api`: Related to ScriptAI's public APIs.

#### Pull Request Labels

* `work-in-progress`: Pull requests which are still being worked on, more changes will follow.
* `needs-review`: Pull requests which need code review, and approval from maintainers or ScriptAI core team.
* `under-review`: Pull requests being reviewed by maintainers or ScriptAI core team.
* `requires-changes`: Pull requests which need to be updated based on review comments and then reviewed again.
* `needs-testing`: Pull requests which need manual testing.

## Attribution

This Contributing guide is adapted from the [Atom Contributing guide](https://github.com/atom/atom/blob/master/CONTRIBUTING.md).