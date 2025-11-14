# GitHub Upload Checklist

Use this checklist before uploading to https://github.com/coff33ninja/Terminal-Chat-Bot

## ✅ Pre-Upload Checklist

### 1. Files to Include
- [x] `README.md` - Complete documentation
- [x] `LICENSE` - MIT License
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `.gitignore` - Excludes sensitive data
- [x] `.env.example` - Template for users
- [x] `requirements.txt` - Python dependencies
- [x] `main.py` - Entry point
- [x] `run_terminal.bat` - Windows CMD launcher
- [x] `run_terminal.ps1` - PowerShell launcher
- [x] `modules/` - All Python modules
- [x] `docs/` - Documentation (if exists)
- [x] `.github/workflows/` - CI/CD (optional)

### 2. Files to EXCLUDE (Handled by .gitignore)
- [ ] `.env` - **CRITICAL: Contains API key!**
- [ ] `data/` - User databases
- [ ] `training_data/` - User conversations
- [ ] `trained_models/` - Trained models
- [ ] `bot.log` - Log files
- [ ] `.venv/` - Virtual environment
- [ ] `__pycache__/` - Python cache
- [ ] `*.pyc` - Compiled Python files

### 3. Verify Sensitive Data
- [ ] Check `.env` is NOT in git: `git status` should not show it
- [ ] Verify `.gitignore` is working
- [ ] Search for hardcoded API keys in code
- [ ] Check no personal data in commits

### 4. Documentation
- [ ] README.md is complete and accurate
- [ ] Installation instructions are clear
- [ ] All features are documented
- [ ] GitHub repository URL is correct
- [ ] Links work (API key, docs, etc.)

### 5. Code Quality
- [ ] No syntax errors
- [ ] All imports work
- [ ] Launcher scripts tested
- [ ] Both terminal and TUI modes work
- [ ] Commands are functional

## 🚀 Upload Steps

### First Time Setup

1. **Create GitHub Repository**
   ```bash
   # On GitHub.com:
   # - Go to https://github.com/coff33ninja
   # - Click "New Repository"
   # - Name: Terminal-Chat-Bot
   # - Description: "AI chatbot with auto-learning memory and custom model training"
   # - Public repository
   # - Do NOT initialize with README (we have one)
   ```

2. **Initialize Local Git**
   ```bash
   cd E:\SCRIPTS\ai
   git init
   git add .
   git commit -m "Initial commit: Terminal Chat Bot with auto-memory system"
   ```

3. **Connect to GitHub**
   ```bash
   git remote add origin https://github.com/coff33ninja/Terminal-Chat-Bot.git
   git branch -M main
   git push -u origin main
   ```

### Updating Existing Repository

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Update: description of changes"

# Push to GitHub
git push origin main
```

## 📋 Post-Upload Checklist

### On GitHub.com

1. **Repository Settings**
   - [ ] Add description: "AI chatbot with auto-learning memory and custom model training"
   - [ ] Add topics: `ai`, `chatbot`, `python`, `gemini`, `machine-learning`, `terminal`, `tui`
   - [ ] Set website: (if you have one)
   - [ ] Enable Issues
   - [ ] Enable Discussions (optional)

2. **README Display**
   - [ ] README.md displays correctly
   - [ ] Badges show properly
   - [ ] Links work
   - [ ] Code blocks format correctly

3. **Repository Files**
   - [ ] All files uploaded
   - [ ] No sensitive data visible
   - [ ] .gitignore working
   - [ ] LICENSE visible

4. **Create Releases** (Optional)
   - [ ] Tag version: v1.0.0
   - [ ] Release title: "Initial Release"
   - [ ] Release notes with features

## 🔒 Security Checks

### Before Every Push

```bash
# Check what will be committed
git status

# Check for sensitive data
git diff

# Verify .env is ignored
git check-ignore .env
# Should output: .env

# Search for API keys in code (should find none)
grep -r "GEMINI_API_KEY" --exclude-dir=.venv --exclude=.env.example .
```

### If You Accidentally Commit Sensitive Data

```bash
# Remove from git history (BEFORE pushing)
git rm --cached .env
git commit -m "Remove .env from tracking"

# If already pushed, you MUST:
# 1. Revoke the API key immediately
# 2. Get a new API key
# 3. Use git filter-branch or BFG Repo-Cleaner to remove from history
```

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

```bash
# Good examples:
git commit -m "Add: Auto-memory system for AI learning"
git commit -m "Fix: Memory extraction JSON parsing error"
git commit -m "Update: README with installation instructions"
git commit -m "Refactor: Command handler structure"
git commit -m "Docs: Add contributing guidelines"

# Bad examples:
git commit -m "updates"
git commit -m "fix stuff"
git commit -m "changes"
```

## 🎯 Final Verification

Before pushing to GitHub:

```bash
# 1. Clean test
rm -rf .venv data/ training_data/ bot.log

# 2. Fresh install test
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Run the bot
python main.py

# 4. Test launcher
run_terminal.bat  # or run_terminal.ps1

# 5. If everything works, push!
git push origin main
```

## ✨ Post-Upload Promotion

After uploading:

1. **Share on social media**
   - Reddit: r/Python, r/learnpython, r/MachineLearning
   - Twitter/X with hashtags: #Python #AI #OpenSource
   - Dev.to or Medium article

2. **Add to lists**
   - Awesome Python lists
   - AI/ML project collections

3. **Engage with users**
   - Respond to issues
   - Accept pull requests
   - Update documentation based on feedback

## 🆘 Troubleshooting

### Git Issues

**Large files error:**
```bash
# Check file sizes
git ls-files | xargs ls -lh | sort -k5 -h

# Remove large files
git rm --cached large_file.bin
```

**Merge conflicts:**
```bash
# Pull latest changes
git pull origin main

# Resolve conflicts in files
# Then commit
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

---

## ✅ Ready to Upload!

Once all checkboxes are complete, you're ready to upload to GitHub!

```bash
git push origin main
```

**Repository URL:** https://github.com/coff33ninja/Terminal-Chat-Bot

Good luck! 🚀
