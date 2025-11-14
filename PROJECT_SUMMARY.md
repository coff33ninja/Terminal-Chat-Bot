# Terminal Chat Bot - Project Summary

## 🎯 Project Overview

A sophisticated terminal-based AI chatbot that automatically learns about users through conversation, with the ability to train custom AI models for completely offline, personalized assistance.

**Repository:** https://github.com/coff33ninja/Terminal-Chat-Bot

## 🌟 Key Features

### 1. Auto-Memory System
- AI automatically extracts and stores facts from conversations
- Learns about user preferences, background, and interests
- Remembers conversation topics and what it explained
- No manual input required - just chat naturally

### 2. Dual-Layer Learning
- **Structured Memories:** Quick facts for immediate context
- **Full Conversation Logs:** Complete history for training custom models

### 3. Easy Setup
- One-click launcher scripts (`.bat` and `.ps1`)
- Auto-installs Python 3.13 via `uv`
- Auto-creates virtual environment
- Auto-installs all dependencies

### 4. Two Interface Modes
- **Terminal Mode:** Simple, fast, classic CLI
- **TUI Mode:** Modern, beautiful terminal UI (Textual)

### 5. Custom Model Training
- Collect conversations automatically
- Export in multiple formats (OpenAI, Llama, Alpaca)
- Train your own AI model
- Run completely offline once trained

### 6. Rich Features
- Web search with AI analysis
- Games (trivia, guessing, RPS, 8-ball)
- Utilities (calculator, weather, time, dice)
- Personality and mood system
- Relationship tracking (5 levels)

## 📁 Project Structure

```
Terminal-Chat-Bot/
├── main.py                 # Entry point
├── run_terminal.bat        # Windows CMD launcher
├── run_terminal.ps1        # PowerShell launcher
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git exclusions
├── LICENSE                 # MIT License
├── README.md               # Main documentation
├── CONTRIBUTING.md         # Contribution guide
├── GITHUB_UPLOAD_CHECKLIST.md  # Upload checklist
│
├── modules/                # Core modules
│   ├── terminal_bot.py     # Terminal mode bot
│   ├── tui_bot.py          # TUI mode bot
│   ├── terminal_interface.py  # Terminal UI
│   ├── tui_interface.py    # Modern TUI
│   ├── command_handlers.py # Command implementations
│   ├── command_parser.py   # Command parsing
│   ├── auto_memory.py      # Auto-learning system
│   ├── ai_database.py      # Database & memory storage
│   ├── api_manager.py      # Gemini API wrapper
│   ├── persona_manager.py  # Personality system
│   ├── training_data_collector.py  # Data collection
│   ├── model_trainer.py    # Model training
│   ├── model_tester.py     # Model testing
│   ├── utilities.py        # Utility commands
│   ├── games.py            # Game commands
│   ├── search.py           # Web search
│   ├── social.py           # Relationship tracking
│   ├── knowledge_manager.py # Knowledge base
│   ├── config_manager.py   # Configuration
│   ├── response_formatter.py # Response formatting
│   ├── bot_name_service.py # Bot naming
│   └── logger.py           # Logging system
│
├── .github/
│   └── workflows/
│       └── python-app.yml  # CI/CD workflow
│
└── docs/
    └── TRAINING.md         # Training guide
```

## 🚀 Quick Start for Users

1. **Clone repository:**
   ```bash
   git clone https://github.com/coff33ninja/Terminal-Chat-Bot.git
   cd Terminal-Chat-Bot
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY
   ```

3. **Run launcher:**
   ```bash
   run_terminal.bat  # Windows CMD
   # or
   .\run_terminal.ps1  # PowerShell
   ```

That's it! The launcher handles everything else.

## 🔧 Technical Details

### Requirements
- Python 3.10+ (launcher auto-installs 3.13)
- Internet connection (for Gemini API)
- ~500MB disk space

### Dependencies
- `google-generativeai` - Gemini API
- `aiohttp` - Async HTTP
- `aiosqlite` - Async database
- `colorama` - Terminal colors
- `textual` - Modern TUI (optional)
- `python-dotenv` - Environment variables

### Training Dependencies (Optional)
- `transformers` - Model training
- `datasets` - Data handling
- `torch` - PyTorch
- `peft` - LoRA training
- `accelerate` - Training acceleration

### Database Schema
- **conversations** - Full conversation logs
- **ai_memory** - Extracted structured memories
- **user_ai_preferences** - User settings
- **knowledge_base** - Knowledge entries
- **model_performance** - API usage tracking
- **ai_feedback** - User feedback

## 🎓 How It Works

### 1. User Chats
User types messages naturally or uses commands like `!ai <question>`

### 2. AI Responds
Gemini API generates response with streaming output

### 3. Auto-Learning
- Full conversation saved to `training_data/conversations.jsonl`
- AI analyzes conversation and extracts key facts
- Facts stored in database with importance ratings
- Memories categorized as "user" or "conversation" type

### 4. Context Building
Next conversation:
- AI loads stored memories from database
- Adds to prompt: "Things you know about this user..."
- Includes recent conversation snippets
- Generates personalized response

### 5. Training (Future)
When enough data collected:
- Export conversations in training format
- Train custom model (Phi, Llama, etc.)
- Use trained model instead of Gemini
- Continue collecting data to improve model

## 📊 Data Flow

```
User Input
    ↓
Command Parser
    ↓
Command Handler
    ↓
[Load Memories] → AI API (Gemini) → [Generate Response]
    ↓                                        ↓
[Save Full Log]                    [Extract Memories]
    ↓                                        ↓
training_data/                          ai_database.db
conversations.jsonl                     (ai_memory table)
```

## 🔒 Privacy & Security

### What's Stored Locally
- All conversations (for training)
- Extracted memories
- User preferences
- Relationship data
- Training data exports

### What's Sent to Gemini
- Current message
- Loaded memories (as context)
- Recent conversation snippets
- Persona/personality instructions

### What's NOT Stored in Git
- `.env` file (API keys)
- `data/` directory (databases)
- `training_data/` (conversations)
- `trained_models/` (models)
- `bot.log` (logs)
- `.venv/` (virtual environment)

## 🎯 Future Roadmap

### Phase 1: Bootstrap (Current)
- ✅ Use Gemini API for responses
- ✅ Collect conversation data
- ✅ Auto-extract memories
- ✅ Build training dataset

### Phase 2: Custom Model
- Train first custom model
- Implement model switching
- Offline mode support
- Continuous learning

### Phase 3: Advanced Features
- Voice input/output
- Multi-language support
- Plugin system
- Web interface option
- Mobile app

### Phase 4: Community
- Model sharing platform
- Persona card marketplace
- Community training datasets
- Collaborative improvements

## 📈 Success Metrics

### For Users
- Easy setup (< 5 minutes)
- Natural conversations
- Accurate memory recall
- Useful responses
- Privacy maintained

### For Project
- GitHub stars
- Active users
- Contributions
- Training data quality
- Model performance

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Priority areas:**
- Bug fixes
- Performance improvements
- New commands/features
- Documentation
- Testing
- Training improvements

## 📞 Support & Community

- **Issues:** https://github.com/coff33ninja/Terminal-Chat-Bot/issues
- **Discussions:** https://github.com/coff33ninja/Terminal-Chat-Bot/discussions
- **Documentation:** [README.md](README.md) and [docs/](docs/)

## 🙏 Acknowledgments

- **Google Gemini** - AI API during bootstrap
- **Hugging Face** - Training infrastructure
- **Astral (uv)** - Fast Python package management
- **Textual** - Modern TUI framework
- **Open Source Community** - Models and tools

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

**Built with ❤️ by coff33ninja**

**Star the project:** https://github.com/coff33ninja/Terminal-Chat-Bot ⭐
