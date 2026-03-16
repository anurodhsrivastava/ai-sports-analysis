# Contributing

Thanks for your interest in contributing!

## Getting Started

1. Fork the repo and clone your fork
2. Create a feature branch: `git checkout -b my-feature`
3. Install dependencies:
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt

   # Frontend
   cd frontend && npm install
   ```
4. Make your changes
5. Run tests:
   ```bash
   cd backend && python -m pytest tests/ -v
   ```
6. Commit with a clear message and open a PR against `main`

## Guidelines

- Keep PRs focused — one feature or fix per PR
- Add tests for new backend functionality
- Follow existing code style (Ruff for Python, ESLint for TypeScript)
- Update the README if your change affects the API or setup steps

## Reporting Issues

Open a GitHub issue with steps to reproduce, expected vs. actual behavior, and any relevant logs.
