# Contributing to Terminal Chat Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- A GitHub account

### Setting Up Development Environment

1. **Fork the repository**
   - Click the "Fork" button on GitHub
   - Clone your fork: `git clone https://github.com/YOUR_USERNAME/Terminal-Chat-Bot.git`

2. **Set up the project**
   ```bash
   cd Terminal-Chat-Bot
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Create a .env file**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY
   ```

4. **Test the setup**
   ```bash
   python main.py
   ```

## 🔧 Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. **Write clean, documented code**
   - Follow PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Comment complex logic

2. **Test your changes**
   - Test in both terminal and TUI modes
   - Test with different commands
   - Check for errors in `bot.log`

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

   Commit message prefixes:
   - `Add:` - New features
   - `Fix:` - Bug fixes
   - `Update:` - Updates to existing features
   - `Refactor:` - Code refactoring
   - `Docs:` - Documentation changes
   - `Test:` - Test additions or changes

### Submitting a Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with:
     - Description of changes
     - Why the change is needed
     - How to test it
     - Screenshots (if UI changes)

3. **Wait for review**
   - Address any feedback
   - Make requested changes
   - Push updates to the same branch

## 📝 Code Guidelines

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names

### Documentation
- Add docstrings to all functions and classes
- Update README.md if adding features
- Comment complex algorithms

### Error Handling
- Use try-except blocks appropriately
- Log errors with the logger module
- Provide helpful error messages to users

### Example Code Style

```python
async def handle_new_command(self, args: List[str]) -> str:
    """
    Handle the new command
    
    Args:
        args: List of command arguments
        
    Returns:
        Response message to display to user
    """
    try:
        # Your code here
        logger.info(f"New command executed with args: {args}")
        return "Success message"
        
    except Exception as e:
        logger.error(f"Error in new command: {e}")
        return f"Error: {e}"
```

## 🐛 Reporting Bugs

### Before Reporting
1. Check existing issues
2. Check `bot.log` for error details
3. Try to reproduce the bug

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Enter input '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.11.5]
- Bot version/commit: [e.g., main branch, commit abc123]

**Logs**
```
Paste relevant logs from bot.log
```

**Screenshots**
If applicable, add screenshots.
```

## 💡 Suggesting Features

### Feature Request Template
```markdown
**Feature Description**
Clear description of the feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other ways to solve this problem.

**Additional Context**
Any other information, mockups, or examples.
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Test in terminal mode
- [ ] Test in TUI mode
- [ ] Test with various commands
- [ ] Test error handling
- [ ] Check logs for errors
- [ ] Test with fresh database
- [ ] Test with existing data

### Areas to Test
1. **Commands** - All command variations
2. **Memory System** - Auto-learning and recall
3. **Training** - Data collection and export
4. **UI** - Both terminal and TUI interfaces
5. **Error Handling** - Invalid inputs, API failures
6. **Database** - Data persistence and retrieval

## 📚 Documentation

### What to Document
- New features in README.md
- New commands in help text
- API changes in docstrings
- Configuration options in .env.example

### Documentation Style
- Clear and concise
- Include examples
- Use proper markdown formatting
- Add code blocks with syntax highlighting

## 🎯 Priority Areas

We especially welcome contributions in:
- **Bug fixes** - Always appreciated!
- **Performance improvements** - Make it faster
- **New commands** - Useful utilities or games
- **UI improvements** - Better user experience
- **Documentation** - Clearer guides and examples
- **Testing** - More comprehensive tests
- **Training features** - Better model training tools

## ❓ Questions?

- Open a [Discussion](https://github.com/coff33ninja/Terminal-Chat-Bot/discussions)
- Comment on an existing issue
- Check the [README](README.md) and [docs/](docs/)

## 🙏 Thank You!

Every contribution helps make this project better. Whether it's code, documentation, bug reports, or feature suggestions - thank you for your time and effort!

---

**Happy Coding!** 🚀
