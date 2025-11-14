"""
Model Tester - Interactive testing of trained models
"""
import sys
import os

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


def list_models():
    """List available trained models"""
    models_dir = "trained_models"
    
    if not os.path.exists(models_dir):
        return []
    
    models = []
    for item in os.listdir(models_dir):
        model_path = os.path.join(models_dir, item)
        if os.path.isdir(model_path):
            models.append((item, model_path))
    
    return models


def load_model(model_path):
    """Load a trained model"""
    print(f"Loading model from: {model_path}")
    
    # Check device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # Load model
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None
    )
    
    if device == "cpu":
        model = model.to(device)
    
    print("✅ Model loaded successfully!")
    return model, tokenizer, device


def generate_response(model, tokenizer, device, prompt, max_length=200):
    """Generate a response using the model"""
    # Format prompt
    formatted_prompt = f"### User: {prompt}\n### Assistant:"
    
    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the assistant's response
    if "### Assistant:" in response:
        response = response.split("### Assistant:")[-1].strip()
    
    return response


def interactive_chat(model, tokenizer, device):
    """Interactive chat with the model"""
    print("\n" + "=" * 50)
    print("Interactive Chat with Your Trained Model")
    print("=" * 50)
    print("Type 'exit' or 'quit' to leave")
    print("=" * 50 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nGoodbye!")
                break
            
            print("Bot: ", end="", flush=True)
            response = generate_response(model, tokenizer, device, user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


def run_model_test():
    """Run the model tester"""
    if not TRANSFORMERS_AVAILABLE:
        print("❌ Required packages not installed!")
        print("\nInstall with:")
        print("pip install transformers torch")
        sys.exit(1)
    
    print("\n🤖 Trained Model Tester")
    print("=" * 50)
    
    # List available models
    models = list_models()
    
    if not models:
        print("\n❌ No trained models found!")
        print("\nTrain a model first:")
        print("python main.py train --size tiny")
        sys.exit(1)
    
    print(f"\nFound {len(models)} trained model(s):\n")
    for i, (name, path) in enumerate(models, 1):
        print(f"{i}. {name}")
    
    # Select model
    if len(models) == 1:
        selected_idx = 0
        print(f"\nUsing: {models[0][0]}")
    else:
        try:
            choice = input(f"\nSelect model (1-{len(models)}): ").strip()
            selected_idx = int(choice) - 1
            if selected_idx < 0 or selected_idx >= len(models):
                print("❌ Invalid selection")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid input")
            sys.exit(1)
    
    model_name, model_path = models[selected_idx]
    
    # Load model
    print()
    try:
        model, tokenizer, device = load_model(model_path)
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        sys.exit(1)
    
    # Start interactive chat
    interactive_chat(model, tokenizer, device)
