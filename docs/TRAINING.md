# AI Model Training Guide

Complete guide for training custom AI models using your conversation data.

## Table of Contents
- [Quick Start](#quick-start)
- [Data Collection](#data-collection)
- [Training Models](#training-models)
- [Available Models](#available-models)
- [Commands Reference](#commands-reference)
- [Hardware Requirements](#hardware-requirements)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies
```bash
pip install transformers datasets accelerate peft torch
```

For GPU support (recommended):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Collect Data
Chat with your bot normally - conversations are saved automatically.

### 3. Train a Model
```bash
# Using main.py
python main.py train --size tiny --epochs 3

# Or in the bot
!train_model tiny 3
```

### 4. Test Your Model
```bash
python main.py test
```

## Data Collection

### Automatic Collection
Every AI conversation is automatically saved to `training_data/conversations.jsonl` with:
- User input
- Bot response
- Timestamp
- User ID
- Context (relationship level, etc.)

### View Statistics
```bash
# In bot
!training_stats

# Command line
python main.py stats
```

### Export Data
```bash
# In bot
!training_export openai   # OpenAI format
!training_export llama    # Llama/Mistral format
!training_export alpaca   # Alpaca format

# Command line exports are automatic during training
```

## Training Models

### Using Command Line
```bash
# Basic training
python main.py train --size tiny --epochs 3

# Advanced options
python main.py train \
  --size small \
  --epochs 5 \
  --batch-size 2 \
  --learning-rate 1e-5 \
  --output-name my_custom_bot

# Without LoRA (not recommended)
python main.py train --size tiny --no-lora
```

### Using Bot Commands
```bash
!training_requirements tiny  # Check requirements
!train_model tiny 3          # Train model
!list_models                 # List trained models
```

### Training Process
1. **Load Data** - Reads conversations from training_data/
2. **Prepare Dataset** - Formats for training
3. **Load Model** - Downloads base model (first time only)
4. **Apply LoRA** - Adds efficient trainable parameters
5. **Train** - Runs through data for specified epochs
6. **Save** - Saves to trained_models/

## Available Models

| Size | Model | VRAM | RAM | Time/Epoch | Best For |
|------|-------|------|-----|------------|----------|
| **tiny** | Phi-2 (2.7B) | 6 GB | 8 GB | 5-10 min | Testing, learning |
| **small** | Phi-3 Mini (3.8B) | 8 GB | 16 GB | 10-20 min | Good balance |
| **medium** | Llama 3.2 (3B) | 12 GB | 16 GB | 15-30 min | Better quality |
| **large** | Llama 3.2 (8B) | 16 GB | 32 GB | 30-60 min | Production use |
| **mistral** | Mistral 7B | 16 GB | 32 GB | 30-60 min | High quality |

### Check Requirements
```bash
# Specific model
python main.py requirements tiny

# All models
python main.py requirements
```

## Commands Reference

### Main.py Commands
```bash
python main.py                    # Start chat bot (default)
python main.py --user myname      # Start with custom user ID
python main.py train --size tiny  # Train a model
python main.py test               # Test trained model
python main.py stats              # Show data statistics
python main.py list               # List trained models
python main.py requirements       # Show requirements
```

### Bot Commands
```bash
# Data Collection
!training_stats              # View statistics
!training_export <format>    # Export data

# Training
!training_requirements <size> # Check requirements
!train_model <size> [epochs] # Train model
!list_models                 # List trained models

# AI Chat
!ai <question>               # Ask AI
!chat <question>             # Same as !ai
!search <query>              # Web search
!help                        # Show all commands
```

## Hardware Requirements

### Minimum (CPU Only)
- Modern multi-core CPU
- 16 GB RAM
- 20 GB storage
- ⚠️ Very slow (hours per epoch)

### Recommended (GPU)
- NVIDIA GPU with 8+ GB VRAM
- 16 GB RAM
- 20 GB storage
- ✅ Fast (minutes per epoch)

### Optimal (High-End)
- NVIDIA GPU with 16+ GB VRAM
- 32 GB RAM
- 50 GB storage
- ⚡ Very fast, larger models

## Best Practices

### Data Quality
- Aim for 100+ conversations
- Cover diverse topics
- Maintain consistent personality
- Quality over quantity

### Training Settings
- Start with "tiny" model
- Use 3-5 epochs
- Keep LoRA enabled
- Monitor loss values

### Testing
- Test after training
- Compare with original
- Iterate and improve
- Collect more data if needed

## Troubleshooting

### Out of Memory
- Use smaller model size
- Reduce batch size: `--batch-size 2`
- Enable LoRA (default)
- Close other programs

### Slow Training
- Use GPU instead of CPU
- Increase batch size if VRAM allows
- Use smaller model for testing

### Model Not Learning
- Need more data (100+ conversations)
- Increase epochs: `--epochs 5`
- Check data quality
- Try different learning rate

### GPU Not Detected
```bash
# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Technical Details

### What is Fine-Tuning?
Teaching a pre-trained model your specific conversation style.

### What is LoRA?
Low-Rank Adaptation - efficient fine-tuning that:
- Trains only small part of model
- Uses less memory
- Often produces better results

### Data Format
```json
{
  "timestamp": "2024-11-14T12:00:00",
  "user_id": "user@host",
  "user_input": "Hello!",
  "bot_response": "Hi there!",
  "context": {"relationship_level": "friend"}
}
```

## Using Trained Models

### Test Interactively
```bash
python main.py test
```

### Load in Python
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("trained_models/tiny_model_...")
tokenizer = AutoTokenizer.from_pretrained("trained_models/tiny_model_...")

inputs = tokenizer("Hello!", return_tensors="pt")
outputs = model.generate(**inputs, max_length=100)
response = tokenizer.decode(outputs[0])
```

### Replace Gemini API
Modify `modules/api_manager.py` to use your trained model instead of Gemini for free, local AI.

## File Structure

```
training_data/
├── conversations.jsonl       # Raw data
├── metadata.json            # Statistics
└── export_*.jsonl           # Exports

trained_models/
├── tiny_model_20241114/     # Trained models
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   └── training_info.json
└── ...

bot.log                      # Training logs
```

## Resources

- **Hugging Face**: https://huggingface.co/docs
- **Transformers**: https://huggingface.co/docs/transformers
- **PEFT/LoRA**: https://huggingface.co/docs/peft
- **PyTorch**: https://pytorch.org/docs

## FAQ

**Q: Can I train Gemini?**
A: No, but you can train open-source models like Llama and Phi.

**Q: How much data do I need?**
A: Minimum 50, recommended 100+ conversations.

**Q: Do I need a GPU?**
A: No, but it's MUCH faster with a GPU.

**Q: How long does training take?**
A: Tiny model: 15-30 minutes total (3 epochs on GPU)

**Q: Is it free?**
A: Yes! After training, usage is completely free.

**Q: Can I use commercially?**
A: Check the license of the base model you use.
