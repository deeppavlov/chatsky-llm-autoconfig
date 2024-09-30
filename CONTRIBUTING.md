# Contributing to dff-llm-integration

Thank you for your interest in contributing to the dff-llm-integration project! We welcome contributions from the community to help improve and expand this Chatsky LLM-Autoconfig tool.

## Getting Started

1. Fork the repository on GitHub
2. Clone your forked repository to your local machine
3. Set up the development environment:
```bash
poetry install
```

## How to Contribute
1. Make your changes and test hypothesis in the `./experiments` folder
2. Write if needed and run the tests from the `./tests` folder
3. If tests run smoothly create a pull request with clear description of fixed and features

## Coding Guidelines

- Follow PEP 8 style guide for Python code
- Write clear and concise comments
- Include docstrings for functions and classes
- Write unit tests for new features or bug fixes

## Reporting Issues

If you encounter any bugs or have feature requests, please open an issue on the GitHub repository. Provide as much detail as possible, including:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Graph visulisation if possible

## Current Focus Areas

We are currently working on supporting various types of graphs. Here's the current status:

Supported types of graphs:
- [x] chain
- [x] single cycle

Currently unsupported types:
- [ ] single node cycle
- [ ] multi-cycle graph
- [ ] incomplete graph
- [ ] complex graph with cycles