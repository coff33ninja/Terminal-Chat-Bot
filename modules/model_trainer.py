"""
Model Trainer - Fine-tune compatible AI models on collected conversation data
"""
import os
import json
import torch
from typing import Optional, Dict, List
from datetime import datetime
from modules.logger import BotLogger

logger = BotLogger.get_logger(__name__)

# Check if transformers is available
try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers library not available. Install with: pip install transformers datasets accelerate")


class ModelTrainer:
    """Train compatible AI models on conversation data"""
    
    # Recommended models for fine-tuning (sorted by size)
    COMPATIBLE_MODELS = {
        "tiny": "microsoft/phi-2",  # 2.7B params - Fast, good for testing
        "small": "microsoft/Phi-3-mini-4k-instruct",  # 3.8B params
        "medium": "meta-llama/Llama-3.2-3B-Instruct",  # 3B params
        "large": "meta-llama/Llama-3.2-8B-Instruct",  # 8B params
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3",  # 7B params
    }
    
    def __init__(self, training_data_dir: str = "training_data"):
        """
        Initialize model trainer
        
        Args:
            training_data_dir: Directory containing training data
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers library required. Install with:\n"
                "pip install transformers datasets accelerate torch"
            )
        
        self.training_data_dir = training_data_dir
        self.conversations_file = os.path.join(training_data_dir, "conversations.jsonl")
        self.models_dir = "trained_models"
        
        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Check for GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Model trainer initialized on device: {self.device}")
    
    def load_training_data(self) -> List[Dict]:
        """Load conversation data from file"""
        if not os.path.exists(self.conversations_file):
            raise FileNotFoundError(f"No training data found at {self.conversations_file}")
        
        conversations = []
        with open(self.conversations_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    conversations.append(json.loads(line))
        
        logger.info(f"Loaded {len(conversations)} conversations")
        return conversations
    
    def prepare_dataset(
        self,
        conversations: List[Dict],
        model_name: str,
        max_length: int = 512
    ) -> Dataset:
        """
        Prepare dataset for training
        
        Args:
            conversations: List of conversation dictionaries
            model_name: Name of the model to use for tokenization
            max_length: Maximum sequence length
            
        Returns:
            Hugging Face Dataset object
        """
        logger.info(f"Preparing dataset with {len(conversations)} conversations")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Add padding token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Format conversations for training
        formatted_data = []
        for conv in conversations:
            # Create instruction-response format
            text = f"### User: {conv['user_input']}\n### Assistant: {conv['bot_response']}"
            formatted_data.append({"text": text})
        
        # Create dataset
        dataset = Dataset.from_list(formatted_data)
        
        # Tokenize
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=max_length,
                padding="max_length"
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        logger.info(f"Dataset prepared: {len(tokenized_dataset)} examples")
        return tokenized_dataset, tokenizer
    
    def train_model(
        self,
        model_size: str = "tiny",
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5,
        output_name: Optional[str] = None,
        use_lora: bool = True
    ) -> str:
        """
        Train a model on conversation data
        
        Args:
            model_size: Size of model to train (tiny, small, medium, large, mistral)
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            output_name: Custom output name (default: auto-generated)
            use_lora: Use LoRA for efficient fine-tuning (recommended)
            
        Returns:
            Path to trained model
        """
        if model_size not in self.COMPATIBLE_MODELS:
            raise ValueError(
                f"Invalid model size. Choose from: {list(self.COMPATIBLE_MODELS.keys())}"
            )
        
        model_name = self.COMPATIBLE_MODELS[model_size]
        logger.info(f"Starting training with model: {model_name}")
        
        # Load training data
        conversations = self.load_training_data()
        
        if len(conversations) < 50:
            logger.warning(f"Only {len(conversations)} conversations. Recommend at least 100 for good results.")
        
        # Prepare dataset
        dataset, tokenizer = self.prepare_dataset(conversations, model_name)
        
        # Load model
        logger.info("Loading base model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        
        # Apply LoRA if requested
        if use_lora:
            try:
                from peft import LoraConfig, get_peft_model, TaskType
                
                logger.info("Applying LoRA configuration...")
                lora_config = LoraConfig(
                    task_type=TaskType.CAUSAL_LM,
                    r=8,  # LoRA rank
                    lora_alpha=32,
                    lora_dropout=0.1,
                    target_modules=["q_proj", "v_proj"]  # Common for most models
                )
                model = get_peft_model(model, lora_config)
                model.print_trainable_parameters()
            except ImportError:
                logger.warning("PEFT not available. Install with: pip install peft")
                logger.warning("Training without LoRA (will use more memory)")
                use_lora = False
        
        # Set up output directory
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{model_size}_model_{timestamp}"
        
        output_dir = os.path.join(self.models_dir, output_name)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=100,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            fp16=self.device == "cuda",
            report_to="none",  # Disable wandb/tensorboard
            remove_unused_columns=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # Causal LM, not masked LM
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting training...")
        print(f"\n🚀 Training {model_size} model on {len(conversations)} conversations...")
        print(f"📊 Epochs: {epochs}, Batch Size: {batch_size}, Learning Rate: {learning_rate}")
        print(f"💾 Output: {output_dir}")
        print(f"⚡ Device: {self.device}")
        print(f"🔧 LoRA: {'Enabled' if use_lora else 'Disabled'}\n")
        
        trainer.train()
        
        # Save model and tokenizer
        logger.info("Saving model...")
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        # Save training info
        training_info = {
            "model_name": model_name,
            "model_size": model_size,
            "trained_at": datetime.now().isoformat(),
            "num_conversations": len(conversations),
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "use_lora": use_lora,
            "device": self.device
        }
        
        with open(os.path.join(output_dir, "training_info.json"), 'w') as f:
            json.dump(training_info, f, indent=2)
        
        logger.info(f"Training complete! Model saved to: {output_dir}")
        print(f"\n✅ Training complete! ({model_size} model)")
        print(f"📁 Model saved to: {output_dir}")
        
        return output_dir
    
    def list_trained_models(self) -> List[Dict]:
        """List all trained models"""
        models = []
        
        if not os.path.exists(self.models_dir):
            return models
        
        for model_dir in os.listdir(self.models_dir):
            model_path = os.path.join(self.models_dir, model_dir)
            info_file = os.path.join(model_path, "training_info.json")
            
            if os.path.isdir(model_path) and os.path.exists(info_file):
                try:
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                        info['path'] = model_path
                        info['name'] = model_dir
                        models.append(info)
                except Exception as e:
                    logger.error(f"Error reading model info: {e}")
        
        return models
    
    def estimate_requirements(self, model_size: str) -> Dict:
        """
        Estimate hardware requirements for training
        
        Args:
            model_size: Model size to estimate for
            
        Returns:
            Dictionary with requirements
        """
        requirements = {
            "tiny": {
                "vram_gb": 6,
                "ram_gb": 8,
                "time_per_epoch": "5-10 minutes",
                "recommended_for": "Testing, quick iterations"
            },
            "small": {
                "vram_gb": 8,
                "ram_gb": 16,
                "time_per_epoch": "10-20 minutes",
                "recommended_for": "Good balance of quality and speed"
            },
            "medium": {
                "vram_gb": 12,
                "ram_gb": 16,
                "time_per_epoch": "15-30 minutes",
                "recommended_for": "Better quality responses"
            },
            "large": {
                "vram_gb": 16,
                "ram_gb": 32,
                "time_per_epoch": "30-60 minutes",
                "recommended_for": "Best quality, production use"
            },
            "mistral": {
                "vram_gb": 16,
                "ram_gb": 32,
                "time_per_epoch": "30-60 minutes",
                "recommended_for": "High quality, good reasoning"
            }
        }
        
        return requirements.get(model_size, {})


# Global instance
model_trainer = None

def get_trainer():
    """Get or create model trainer instance"""
    global model_trainer
    if model_trainer is None:
        if TRANSFORMERS_AVAILABLE:
            model_trainer = ModelTrainer()
    return model_trainer
