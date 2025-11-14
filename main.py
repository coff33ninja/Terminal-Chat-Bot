"""
Terminal Chat Bot - Main Entry Point
Run with: python main.py
"""
import sys
import argparse


def main():
    """Main entry point with command routing"""
    parser = argparse.ArgumentParser(
        description="Terminal Chat Bot - AI chat interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start the chat bot
  python main.py --user myname      # Start with custom user ID
  python main.py train --size tiny  # Train a model
  python main.py test               # Test a trained model
  python main.py stats              # Show training data stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Chat bot command (default)
    chat_parser = subparsers.add_parser('chat', help='Start the chat bot (default)')
    chat_parser.add_argument('--user', type=str, help='User identifier')
    chat_parser.add_argument('--tui', action='store_true', help='Use modern TUI interface')
    
    # Training command
    train_parser = subparsers.add_parser('train', help='Train a custom model')
    train_parser.add_argument('--size', type=str, default='tiny',
                             choices=['tiny', 'small', 'medium', 'large', 'mistral'],
                             help='Model size (default: tiny)')
    train_parser.add_argument('--epochs', type=int, default=3,
                             help='Number of epochs (default: 3)')
    train_parser.add_argument('--batch-size', type=int, default=4,
                             help='Batch size (default: 4)')
    train_parser.add_argument('--learning-rate', type=float, default=2e-5,
                             help='Learning rate (default: 2e-5)')
    train_parser.add_argument('--output-name', type=str,
                             help='Custom output name')
    train_parser.add_argument('--no-lora', action='store_true',
                             help='Disable LoRA')
    
    # Test command
    _ = subparsers.add_parser('test', help='Test a trained model')
    
    # Stats command
    _ = subparsers.add_parser('stats', help='Show training data statistics')
    
    # List models command
    _ = subparsers.add_parser('list', help='List trained models')
    
    # Requirements command
    req_parser = subparsers.add_parser('requirements', help='Show training requirements')
    req_parser.add_argument('size', type=str, nargs='?',
                           choices=['tiny', 'small', 'medium', 'large', 'mistral'],
                           help='Model size')
    
    args = parser.parse_args()
    
    # Default to chat if no command specified
    if args.command is None:
        args.command = 'chat'
    
    # Route to appropriate handler
    if args.command == 'chat':
        # Check if TUI mode is requested
        if hasattr(args, 'tui') and args.tui:
            from modules.tui_bot import run_tui_bot
            run_tui_bot(args.user if hasattr(args, 'user') else None)
        else:
            from modules.terminal_bot import run_chat_bot
            run_chat_bot(args.user if hasattr(args, 'user') else None)
    
    elif args.command == 'train':
        from modules.model_trainer import get_trainer
        from modules.training_data_collector import training_collector
        
        trainer = get_trainer()
        if trainer is None:
            print("❌ Model trainer not available!")
            print("\nInstall required packages:")
            print("pip install transformers datasets accelerate torch peft")
            sys.exit(1)
        
        # Check training data
        stats = training_collector.get_statistics()
        if stats['total_conversations'] < 10:
            print(f"❌ Not enough training data! You have {stats['total_conversations']} conversations.")
            print("Minimum: 10 conversations (50+ recommended)")
            sys.exit(1)
        
        # Show info and confirm
        print(f"\n🚀 Training {args.size} model on {stats['total_conversations']} conversations")
        print(f"Epochs: {args.epochs}, Batch Size: {args.batch_size}")
        
        response = input("\nContinue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            sys.exit(0)
        
        # Train
        try:
            output_path = trainer.train_model(
                model_size=args.size,
                epochs=args.epochs,
                batch_size=args.batch_size,
                learning_rate=args.learning_rate,
                output_name=args.output_name,
                use_lora=not args.no_lora
            )
            print(f"\n✅ Training complete! Model saved to: {output_path}")
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            sys.exit(1)
    
    elif args.command == 'test':
        from modules.model_tester import run_model_test
        run_model_test()
    
    elif args.command == 'stats':
        from modules.training_data_collector import training_collector
        stats = training_collector.get_statistics()
        print("\n📊 Training Data Statistics")
        print("=" * 50)
        print(f"Total Conversations: {stats['total_conversations']}")
        print(f"Unique Users: {stats['unique_users']}")
        print(f"Avg User Input: {stats['avg_user_input_length']:.0f} chars")
        print(f"Avg Bot Response: {stats['avg_bot_response_length']:.0f} chars")
        if stats['date_range']:
            print(f"First: {stats['date_range']['first'][:10]}")
            print(f"Last: {stats['date_range']['last'][:10]}")
        print()
    
    elif args.command == 'list':
        from modules.model_trainer import get_trainer
        trainer = get_trainer()
        if trainer is None:
            print("❌ Model trainer not available. Install dependencies first.")
            sys.exit(1)
        
        models = trainer.list_trained_models()
        if not models:
            print("\n📁 No trained models found.")
            print("\nTrain your first model with:")
            print("python main.py train --size tiny")
        else:
            print(f"\n📁 Trained Models ({len(models)} total)")
            print("=" * 50)
            for i, model in enumerate(models, 1):
                print(f"\n{i}. {model['name']}")
                print(f"   Size: {model.get('model_size', 'unknown')}")
                print(f"   Conversations: {model.get('num_conversations', 0)}")
                print(f"   Trained: {model.get('trained_at', 'unknown')[:10]}")
                print(f"   Path: {model['path']}")
        print()
    
    elif args.command == 'requirements':
        from modules.model_trainer import get_trainer
        trainer = get_trainer()
        if trainer is None:
            print("❌ Model trainer not available.")
            sys.exit(1)
        
        if args.size:
            reqs = trainer.estimate_requirements(args.size)
            print(f"\n💻 Requirements for {args.size} model:")
            print("=" * 50)
            print(f"VRAM: {reqs.get('vram_gb', 'N/A')} GB (GPU)")
            print(f"RAM: {reqs.get('ram_gb', 'N/A')} GB")
            print(f"Storage: ~{reqs.get('storage_gb', '10-20')} GB")
            print(f"Time per Epoch: {reqs.get('time_per_epoch', 'N/A')}")
            print(f"Recommended: {reqs.get('recommended_epochs', '3-5')} epochs")
            print(f"\nBest For: {reqs.get('recommended_for', 'General use')}")
            print(f"Model: {trainer.COMPATIBLE_MODELS[args.size]}")
        else:
            print("\n💻 Training Requirements")
            print("=" * 50)
            for size in trainer.COMPATIBLE_MODELS.keys():
                reqs = trainer.estimate_requirements(size)
                print(f"\n{size.upper()} - {reqs.get('vram_gb', 'N/A')} GB VRAM")
                print(f"  {reqs.get('recommended_for', 'General use')}")
        print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
