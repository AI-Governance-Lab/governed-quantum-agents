# Contributing to Venus: Governed Quantum Agents (GQA)

First off, thank you for considering contributing to Venus (GQA)! We value community contributions and are excited to see what we can build together.

## Code of Conduct
By participating in this project, you agree to abide by our Code of Conduct. Please be respectful, inclusive, and constructive in your communications.

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please open an issue in the issue tracker. Include as much detail as possible:
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your operating system and Python version

### Suggesting Enhancements
Have an idea for a new feature? We'd love to hear it! Open an issue describing the feature, why it would be useful, and how you envision it working.

### Contributing Code
1. **Fork the repository** and create your branch from `main`.
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
2. **Install dependencies** (preferably in a virtual environment).
   ```bash
   pip install -r requirements.txt
   ```
3. **Make your changes**. Write clear, concise commit messages.
4. **Run tests and linting**. Ensure your code passes the CI checks locally before pushing.
   ```bash
   pytest tests/
   flake8 src tests
   ```
5. **Push your branch** to your fork.
   ```bash
   git push origin feature/my-awesome-feature
   ```
6. **Open a Pull Request** against the `main` branch. Provide a detailed description of your changes in the PR template.

## Coding Standards
- We follow PEP 8 for Python code style.
- Please use type hints (`typing`) wherever possible to make the codebase easier to understand and maintain.
- Ensure that any new quantum algorithms or agent logic are well-documented and covered by unit tests.

## Adding Support for New Quantum Algorithms
If you are adding a new quantum algorithm to the `Classical-Quantum Bridge`:
1. Add the implementation in `src/bridge/circuit_generator.py` or create a new module.
2. Update the `Algorithm Selector` logic to recognize when this algorithm is applicable.
3. Write unit tests simulating the circuit execution using `Cirq`.

Thank you for contributing to the future of Governed AI and Quantum Computing!
