# 🤖 Terminal AI Chat Bot

A powerful terminal-based AI chatbot with automatic memory learning, personality system, and custom model training capabilities.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-coff33ninja%2FTerminal--Chat--Bot-black)](https://github.com/coff33ninja/Terminal-Chat-Bot)

**🎯 One-Click Setup** | **🧠 Auto-Learning AI** | **🔒 100% Local & Private** | **🎓 Train Your Own Model**

---

## 📖 What is This?

An intelligent terminal chatbot that **learns about you automatically** as you chat. It remembers your preferences, tracks conversation topics, and can be trained to become your own personalized AI assistant - completely free and offline!

### Why Use This?

- **🚀 Easy Setup**: Just run the launcher script - it handles everything
- **🧠 Smart Memory**: AI automatically learns and remembers facts about you
- **💬 Natural Conversations**: Chat naturally, no complex commands needed
- **🎓 Train Your Own AI**: Collect conversations to train a custom model
- **🔒 Privacy First**: All data stays on your computer
- **💰 Free Forever**: Use Gemini now, train your own model later
- **🎨 Customizable**: Personality, mood, relationship system
- **🎮 Fun Features**: Games, utilities, web search, and more

### Perfect For

- Personal AI assistant that learns your preferences
- Experimenting with AI and machine learning
- Building a custom AI trained on your conversations
- Privacy-conscious users who want local AI
- Developers learning about chatbots and NLP
- Anyone who wants a smart, personalized chat companion

## ✨ Features

### Core AI Features
- **AI Chat** - Powered by Google Gemini API with streaming responses
- **Auto-Memory System** - AI automatically learns and remembers facts about you
- **Dual-Layer Learning** - Structured memories + full conversation logs for training
- **Unlimited Memory** - Configurable conversation history (0 = unlimited)
- **Conversation Context** - AI remembers what it told you and previous discussions

### Personality & Social
- **Personality System** - Customizable bot personality via persona cards
- **Relationship Tracking** - Builds relationship with users over time (5 levels)
- **Mood System** - Bot has dynamic moods that affect responses
- **Social Interactions** - Compliments, relationship status, and more

### Utilities & Fun
- **Web Search** - DuckDuckGo integration with AI-powered analysis
- **Games** - Number guessing, rock-paper-scissors, trivia, magic 8-ball
- **Utilities** - Calculator, dice roller, coin flip, time, weather
- **Random Content** - Facts, jokes, cat facts

### Training & Data
- **Training System** - Train custom AI models on your conversations
- **Data Collection** - Automatic conversation logging for model training
- **Multiple Export Formats** - OpenAI, Llama, Alpaca formats
- **Model Management** - List, test, and manage trained models

### Interface Options
- **Terminal Mode** - Simple, fast command-line interface
- **TUI Mode** - Modern, beautiful terminal UI (requires textual)
- **Cross-Platform** - Windows, Linux, macOS support

### Privacy & Control
- **Local & Private** - All data stored locally on your machine
- **No Tracking** - Your conversations stay on your computer
- **Full Control** - Export, delete, or manage all your data

## 🚀 Quick Start

### Prerequisites

- **Python 3.10 or higher** installed on your system
- Internet connection (for initial setup and Gemini API)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/coff33ninja/Terminal-Chat-Bot.git
cd Terminal-Chat-Bot
```

2. **Set up your API key**
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

Get your free API key from: https://makersuite.google.com/app/apikey

3. **Run the launcher (Recommended - Auto Setup!)**

The launcher scripts will automatically:
- Install `uv` package manager (if not present)
- Create a Python 3.13 virtual environment
- Install all required dependencies
- Launch the bot

**Windows CMD:**
```bash
run_terminal.bat
```

**Windows PowerShell:**
```bash
.\run_terminal.ps1
```

That's it! The scripts handle everything automatically.

### Manual Installation (Alternative)

If you prefer manual setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

### First Run

On first run, you'll see a menu:
```
1. Terminal Mode (Simple, Fast)
2. TUI Mode (Modern, Beautiful)
3. Exit
```

Choose your preferred interface and start chatting!

## 📖 Usage

### Starting the Bot

```bash
# Default start (simple terminal)
python main.py

# Modern TUI interface (requires textual)
python main.py --tui

# With custom user ID
python main.py --user myname

# TUI with custom user
python main.py --user myname --tui

# Show help
python main.py --help
```

### Basic Commands

```bash
# AI Chat
!ai <question>              # Ask the AI anything
!ask <question>             # Alias for !ai
!chat <question>            # Same as !ai
hello                       # Just type naturally!

# Search
!search <query>             # Web search with AI analysis
!find <query>               # Alias for !search

# Utilities
!time                       # Current time
!calc 2+2                   # Calculator
!dice 6                     # Roll dice
!flip                       # Flip coin
!weather Tokyo              # Weather info
!fact                       # Random fact
!joke                       # Random joke
!catfact                    # Random cat fact

# Games
!game guess 100             # Number guessing game
!guess <number>             # Make a guess in active game
!rps rock                   # Rock-paper-scissors
!8ball <question>           # Magic 8-ball
!trivia                     # Trivia questions
!answer <answer>            # Answer trivia or game

# AI Memory (Auto-learns about you!)
!memories                   # View what AI remembers
!recall <key>               # Retrieve specific memory
!remember <key> <value>     # Manually add a memory
!forget <key>               # Delete a memory

# System
!help                       # Show all commands
!memory [number]            # Set conversation memory (0=unlimited)
!stats                      # Usage statistics
!mood                       # Bot's current mood
!relationship               # Your relationship status
!compliment                 # Give the bot a compliment

# Training & Data
!training_stats             # View training data statistics
!training_export <format>   # Export data (openai/llama/alpaca)
!train_model <size>         # Train custom model
!list_models                # List your trained models
!training_requirements      # Show hardware requirements
```

### Training Custom Models

Train your own AI model on your conversations:

```bash
# Check your training data
python main.py stats

# Train a model
python main.py train --size tiny --epochs 3

# Test your trained model
python main.py test

# List trained models
python main.py list
```

See [docs/TRAINING.md](docs/TRAINING.md) for complete training guide.

## 📁 Project Structure

```
ai/
├── main.py                 # Main entry point
├── run_terminal.bat        # Windows launcher
├── requirements.txt        # Dependencies
├── .env                    # API keys (create this)
├── persona_card.json       # Bot personality
│
├── modules/                # Core modules
│   ├── terminal_bot.py     # Main bot logic (terminal mode)
│   ├── tui_bot.py          # TUI bot logic (modern UI)
│   ├── terminal_interface.py  # Terminal UI handling
│   ├── tui_interface.py    # Modern TUI interface
│   ├── command_parser.py   # Command parsing
│   ├── command_handlers.py # Command implementations
│   ├── api_manager.py      # Gemini API wrapper
│   ├── persona_manager.py  # Personality system
│   ├── ai_database.py      # Conversation & memory storage
│   ├── auto_memory.py      # Automatic memory extraction
│   ├── config_manager.py   # Configuration
│   ├── utilities.py        # Utility commands
│   ├── games.py            # Game commands
│   ├── search.py           # Web search
│   ├── social.py           # Relationship tracking
│   ├── knowledge_manager.py # Knowledge base
│   ├── training_data_collector.py # Data collection
│   ├── model_trainer.py    # Model training
│   ├── model_tester.py     # Model testing
│   ├── response_formatter.py # Response formatting
│   ├── bot_name_service.py # Bot naming service
│   └── logger.py           # Logging system
│
├── docs/                   # Documentation
│   └── TRAINING.md         # Training guide
│
├── data/                   # Database files
├── training_data/          # Training data
├── trained_models/         # Your trained models
└── bot.log                 # Log file
```

## 🎨 Customization

### Persona Card

Edit `persona_card.json` to customize your bot's personality:

```json
{
  "name": "YourBotName",
  "personality": "Your bot's personality description",
  "speaking_style": "How your bot speaks",
  "responses": {
    "greeting": ["Hello!", "Hi there!"],
    "farewell": ["Goodbye!", "See you!"]
  }
}
```

### Environment Variables

Create `.env` file:

```env
# Required
GEMINI_API_KEY=your_key_here

# Optional
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

## 🔧 Advanced Features

### Auto-Memory System

The bot automatically learns about you as you chat:

**Automatic Learning:**
- AI extracts important facts from every conversation
- Remembers personal information (name, preferences, hobbies, etc.)
- Tracks conversation topics and what it explained to you
- No manual input needed - just chat naturally!

**Two Types of Memories:**
1. **About You** - Personal facts, preferences, background
2. **Conversation History** - Topics discussed, things AI explained/recommended

**Managing Memories:**
```bash
!memories           # View everything AI remembers
!recall name        # Check specific memory
!remember job developer  # Manually add a fact
!forget old_hobby   # Delete a memory
```

**Conversation Memory Settings:**
```bash
!memory 0   # Unlimited conversation history (default)
!memory 10  # Remember last 10 conversations
!memory 50  # Remember last 50 conversations
```

The AI uses both structured memories and conversation history to provide personalized, context-aware responses!

### Relationship System

Build a relationship with your bot:
- **Stranger** → **Acquaintance** → **Friend** → **Close Friend** → **Best Friend**

Check your status:
```bash
!relationship
```

### Training Custom Models

Train AI models on your conversation style:

1. Chat normally to collect data
2. Check progress: `python main.py stats`
3. Train: `python main.py train --size tiny`
4. Test: `python main.py test`

Benefits:
- Free usage after training
- Works offline
- Learns your style
- Complete privacy

See [docs/TRAINING.md](docs/TRAINING.md) for details.

## 📊 Data & Privacy

- All data stored locally
- No data sent to third parties (except Gemini API for responses)
- Training data stays on your machine
- You control all exports and backups

## 🛠️ Development

### Requirements

- Python 3.8+
- Windows/Linux/Mac
- Internet connection (for Gemini API)
- Optional: NVIDIA GPU (for training)

### Dependencies

Core:
- `google-generativeai` - Gemini API
- `aiohttp` - Async HTTP
- `aiosqlite` - Async database
- `colorama` - Terminal colors

Training (optional):
- `transformers` - Model training
- `datasets` - Data handling
- `torch` - PyTorch
- `peft` - LoRA training

### Running Tests

```bash
# Test the bot (terminal mode)
python main.py

# Test with TUI interface
python main.py --tui

# Test trained model
python main.py test

# Check training data
python main.py stats

# List trained models
python main.py list
```

### Key Features to Test

1. **Auto-Memory System**
   - Chat naturally and mention personal facts
   - Use `!memories` to see what AI learned
   - AI will use these facts in future conversations

2. **Conversation Context**
   - Ask AI to explain something
   - Later ask "what did you tell me about X?"
   - AI remembers what it explained

3. **Relationship Building**
   - Chat regularly to build relationship
   - Use `!relationship` to check progress
   - Bot personality changes as relationship grows

4. **Training Data Collection**
   - All conversations automatically saved
   - Use `!training_stats` to see progress
   - Export with `!training_export openai`

## 🐛 Troubleshooting

### Launcher Scripts (run_terminal.bat / run_terminal.ps1)

**Python not found:**
- Ensure Python 3.10+ is installed and in your PATH
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

**uv installation fails:**
- The script will try to install `uv` using pip
- If it fails, install manually: `pip install uv`
- Or download from: https://docs.astral.sh/uv/

**Virtual environment creation fails:**
- Ensure you have write permissions in the directory
- Try running the script as administrator
- Check available disk space

### Bot Issues

**Bot won't start:**
- Check `.env` file exists with valid API key
- Verify Python 3.10+ installed: `python --version`
- Try manual installation: `pip install -r requirements.txt`

**API errors:**
- Verify API key is correct in `.env`
- Check internet connection
- Ensure API key has quota remaining
- Get new key: https://makersuite.google.com/app/apikey

**Training issues:**
- Install training dependencies
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`
- See [docs/TRAINING.md](docs/TRAINING.md) troubleshooting section

**Memory/Database errors:**
- Check `data/` directory exists and is writable
- Delete `data/ai_database.db` to reset (loses history)
- Check disk space

### Logs
Check `bot.log` for detailed error messages and debugging info.

### Getting Help

1. Check the logs: `bot.log`
2. Review this troubleshooting section
3. Check [Issues](https://github.com/coff33ninja/Terminal-Chat-Bot/issues) on GitHub
4. Open a new issue with:
   - Error message from `bot.log`
   - Python version: `python --version`
   - Operating system
   - Steps to reproduce

## 📚 Documentation

- [Training Guide](docs/TRAINING.md) - Complete model training guide
- [API Documentation](https://ai.google.dev/docs) - Gemini API docs
- [Transformers](https://huggingface.co/docs/transformers) - Model training docs

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues
- Check existing [Issues](https://github.com/coff33ninja/Terminal-Chat-Bot/issues)
- Create a new issue with detailed information
- Include logs, error messages, and steps to reproduce

### Suggesting Features
- Open an issue with the `enhancement` label
- Describe the feature and use case
- Explain how it would benefit users

### Pull Requests
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/coff33ninja/Terminal-Chat-Bot.git
cd Terminal-Chat-Bot
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 📝 License

This project is open source. Check individual model licenses when training custom models.

## 🙏 Acknowledgments

- **Google Gemini API** - For AI responses during bootstrap phase
- **Hugging Face** - For training infrastructure and model hosting
- **Microsoft & Meta** - For open-source models (Phi, Llama)
- **DuckDuckGo** - For privacy-respecting search functionality
- **Astral (uv)** - For fast Python package management

## 🔗 Links

- **GitHub Repository**: https://github.com/coff33ninja/Terminal-Chat-Bot
- **Report Issues**: https://github.com/coff33ninja/Terminal-Chat-Bot/issues
- **Gemini API**: https://makersuite.google.com/app/apikey
- **Training Guide**: [docs/TRAINING.md](docs/TRAINING.md)

## 📞 Support

- **Logs**: Check `bot.log` for detailed error messages
- **Training Help**: See [docs/TRAINING.md](docs/TRAINING.md)
- **Command Help**: Type `!help` in the bot
- **Issues**: Open an issue on [GitHub](https://github.com/coff33ninja/Terminal-Chat-Bot/issues)
- **Discussions**: Use GitHub Discussions for questions and ideas

---

## 🌟 Star This Project!

If you find this project useful, please consider giving it a ⭐ on GitHub! It helps others discover the project and motivates continued development.

**Ready to chat? Just run the launcher script and start chatting!** 🚀

```bash
# Windows CMD
run_terminal.bat

# Windows PowerShell  
.\run_terminal.ps1
```

---

### 📦 Repository Structure for GitHub

Before uploading to GitHub, ensure you have:
- ✅ `.env.example` (template for users)
- ✅ `.gitignore` (excludes sensitive data)
- ✅ `LICENSE` (MIT License)
- ✅ `README.md` (this file)
- ✅ `CONTRIBUTING.md` (contribution guidelines)
- ✅ `requirements.txt` (Python dependencies)
- ✅ All source code in `modules/`
- ✅ Launcher scripts (`run_terminal.bat`, `run_terminal.ps1`)

**Do NOT commit:**
- ❌ `.env` (contains your API key!)
- ❌ `data/` directory (user databases)
- ❌ `training_data/` (user conversations)
- ❌ `trained_models/` (trained models)
- ❌ `bot.log` (log files)
- ❌ `.venv/` (virtual environment)

The `.gitignore` file handles this automatically!

---

## ⚡ Powered By

**Currently powered by Google Gemini API** - This bot uses Gemini for AI responses while collecting conversation data. Once sufficient training data is gathered, you can train your own custom model that runs independently, making Gemini optional for future use.

**Future: Your Own Custom Model** - The bot collects all conversations to train a personalized AI model that:
- Learns your conversation style and preferences
- Runs completely offline and free
- Maintains full privacy with no external API calls
- Can be continuously improved with more conversations

The transition from Gemini to your custom model is seamless - the bot will automatically use your trained model once available, while still collecting data to improve it further.
