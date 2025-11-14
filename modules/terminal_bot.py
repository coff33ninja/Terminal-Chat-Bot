"""
Terminal Chat Bot - Main application for terminal-based AI chat
"""
import asyncio
import sys
import signal
from dotenv import load_dotenv

from modules.terminal_interface import TerminalInterface
from modules.command_parser import CommandParser
from modules.command_handlers import CommandHandlers
from modules.persona_manager import PersonaManager
from modules.api_manager import GeminiAPIManager
from modules.ai_database import ai_db, initialize_ai_database
from modules.config_manager import ConfigManager
from modules.utilities import TsundereUtilities
from modules.games import TsundereGames
from modules.search import TsundereSearch
from modules.social import TsundereSocial
from modules.knowledge_manager import knowledge_manager
from modules.logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)


class TerminalChatBot:
    """Main terminal chat bot application"""
    
    def __init__(self, user_id: str = None):
        """Initialize terminal chat bot
        
        Args:
            user_id: User identifier (generated if not provided)
        """
        # Load environment variables
        load_dotenv()
        
        # Generate user ID if not provided
        if not user_id:
            import socket
            import getpass
            try:
                username = getpass.getuser()
                hostname = socket.gethostname()
                user_id = f"{username}@{hostname}"
            except Exception:
                user_id = "terminal_user"
        
        self.user_id = user_id
        self.running = False
        
        # Initialize configuration
        self.config = ConfigManager(validate=False)
        
        # Initialize modules (will be fully set up in initialize())
        self.persona_manager = None
        self.api_manager = None
        self.utilities = None
        self.games = None
        self.search = None
        self.social = None
        
        # Initialize interface and parser
        self.interface = None
        self.parser = None
        self.handlers = None
        
        logger.info(f"TerminalChatBot created for user: {self.user_id}")
    
    async def initialize(self):
        """Async initialization of database and modules"""
        try:
            logger.info("Starting async initialization")
            
            # Validate configuration
            try:
                self.config.validate_config()
                logger.info("Configuration validated")
            except ValueError as e:
                logger.error(f"Configuration validation failed: {e}")
                print(f"❌ Configuration Error: {e}")
                print("Please check your .env file and ensure GEMINI_API_KEY is set.")
                return False
            
            # Initialize API manager
            logger.info("Initializing API manager")
            self.api_manager = GeminiAPIManager()
            model = self.api_manager.get_current_model()
            
            if model is None:
                logger.error("Failed to initialize API model")
                print("❌ Failed to initialize AI model")
                return False
            
            # Initialize persona manager
            logger.info("Initializing persona manager")
            self.persona_manager = PersonaManager()
            bot_name = self.persona_manager.get_name()
            
            # Initialize terminal interface with bot name
            self.interface = TerminalInterface(self.user_id, bot_name)
            
            # Initialize AI database
            logger.info("Initializing AI database")
            await initialize_ai_database()
            
            # Wire knowledge manager
            try:
                knowledge_manager.set_ai_db(ai_db)
                self.persona_manager.set_knowledge_manager(knowledge_manager)
                logger.info("Knowledge manager wired to database")
            except Exception as e:
                logger.warning(f"Failed to wire knowledge manager: {e}")
            
            # Initialize modules
            logger.info("Initializing utility modules")
            self.utilities = TsundereUtilities(model)
            self.games = TsundereGames(api_manager=self.api_manager, search=None, ai_db=ai_db)
            self.search = TsundereSearch(model)
            self.social = TsundereSocial()
            
            # Wire dependencies
            try:
                self.games.set_api_manager(self.api_manager)
                self.games.set_ai_db(ai_db)
                self.games.set_knowledge_manager(knowledge_manager)
                logger.info("Game module dependencies wired")
            except Exception as e:
                logger.warning(f"Failed to wire game dependencies: {e}")
            
            try:
                self.search.set_knowledge_manager(knowledge_manager)
                logger.info("Search module dependencies wired")
            except Exception as e:
                logger.warning(f"Failed to wire search dependencies: {e}")
            
            # Initialize command parser and handlers
            self.parser = CommandParser()
            self.handlers = CommandHandlers(self)
            
            # Register command handlers
            self.register_command_handlers()
            
            logger.info("Initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            print(f"❌ Initialization error: {e}")
            return False
    
    def register_command_handlers(self):
        """Register all command handlers"""
        # AI commands
        self.parser.register_handler('ai', self.handlers.handle_ai)
        self.parser.register_handler('chat', self.handlers.handle_ai)
        
        # Search commands
        self.parser.register_handler('search', self.handlers.handle_search)
        
        # Utility commands
        self.parser.register_handler('time', self.handlers.handle_time)
        self.parser.register_handler('calc', self.handlers.handle_calc)
        self.parser.register_handler('dice', self.handlers.handle_dice)
        self.parser.register_handler('flip', self.handlers.handle_flip)
        self.parser.register_handler('weather', self.handlers.handle_weather)
        self.parser.register_handler('fact', self.handlers.handle_fact)
        self.parser.register_handler('joke', self.handlers.handle_joke)
        self.parser.register_handler('catfact', self.handlers.handle_catfact)
        
        # Game commands
        self.parser.register_handler('game', self.handlers.handle_game)
        self.parser.register_handler('guess', self.handlers.handle_guess)
        self.parser.register_handler('rps', self.handlers.handle_rps)
        self.parser.register_handler('8ball', self.handlers.handle_8ball)
        self.parser.register_handler('trivia', self.handlers.handle_trivia)
        self.parser.register_handler('answer', self.handlers.handle_answer)
        
        # System commands
        self.parser.register_handler('help', self.handlers.handle_help)
        self.parser.register_handler('memory', self.handlers.handle_memory)
        self.parser.register_handler('stats', self.handlers.handle_stats)
        self.parser.register_handler('mood', self.handlers.handle_mood)
        self.parser.register_handler('relationship', self.handlers.handle_relationship)
        self.parser.register_handler('compliment', self.handlers.handle_compliment)
        
        # Training data commands
        self.parser.register_handler('training_stats', self.handlers.handle_training_stats)
        self.parser.register_handler('training_export', self.handlers.handle_training_export)
        self.parser.register_handler('train_model', self.handlers.handle_train_model)
        self.parser.register_handler('list_models', self.handlers.handle_list_models)
        self.parser.register_handler('training_requirements', self.handlers.handle_training_requirements)
        
        # Memory commands
        self.parser.register_handler('remember', self.handlers.handle_remember)
        self.parser.register_handler('recall', self.handlers.handle_recall)
        self.parser.register_handler('forget', self.handlers.handle_forget)
        self.parser.register_handler('memories', self.handlers.handle_memories)
        
        logger.info("Command handlers registered")
    
    async def run(self):
        """Main event loop"""
        try:
            # Initialize
            if not await self.initialize():
                return
            
            self.running = True
            
            # Display welcome message
            self.interface.display_welcome()
            
            # Main loop
            while self.running:
                try:
                    # Display prompt and get input
                    self.interface.display_prompt()
                    user_input = self.interface.get_input()
                    
                    # Check for exit commands
                    if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                        self.interface.display_message("Goodbye! Thanks for chatting!", "success")
                        break
                    
                    # Skip empty input
                    if not user_input.strip():
                        continue
                    
                    # Process input
                    await self.process_input(user_input)
                    
                except KeyboardInterrupt:
                    print()  # New line after ^C
                    self.interface.display_message("Use 'exit' or 'quit' to leave.", "info")
                    continue
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.interface.display_message(f"An error occurred: {e}", "error")
                    continue
            
            # Shutdown
            await self.shutdown()
            
        except Exception as e:
            logger.error(f"Fatal error in run(): {e}")
            print(f"❌ Fatal error: {e}")
            await self.shutdown()
    
    async def process_input(self, user_input: str):
        """Process user input
        
        Args:
            user_input: User input string
        """
        try:
            # Parse input
            command, args, kwargs = self.parser.parse(user_input)
            
            # Show typing indicator
            self.interface.display_typing()
            
            # Get handler
            handler = self.parser.get_command_handler(command)
            
            if handler:
                # Execute command
                response = await handler(args)
                
                # Clear typing indicator
                self.interface.clear_typing()
                
                # Handle special responses
                if response == "SHOW_HELP":
                    self.interface.display_help()
                elif response == "STREAMING_COMPLETE":
                    # Streaming was already handled in the command handler
                    pass
                else:
                    # Display response
                    self.interface.display_message(response, "bot")
                
                # Track interaction
                self.social.update_interaction(self.user_id)
                
            else:
                # Unknown command
                self.interface.clear_typing()
                
                # Suggest similar command
                suggestion = self.parser.suggest_command(command)
                if suggestion:
                    self.interface.display_message(
                        f"Unknown command '{command}'. Did you mean '!{suggestion}'?",
                        "error"
                    )
                else:
                    self.interface.display_message(
                        f"Unknown command '{command}'. Type !help for available commands.",
                        "error"
                    )
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            self.interface.clear_typing()
            self.interface.display_message(f"Error processing command: {e}", "error")
    
    async def shutdown(self):
        """Graceful shutdown"""
        try:
            logger.info("Shutting down terminal bot")
            
            # Save social data
            if self.social:
                self.social.save_user_data()
                logger.info("Social data saved")
            
            # Close database
            try:
                await ai_db.close()
                logger.info("Database closed")
            except Exception as e:
                logger.warning(f"Error closing database: {e}")
            
            # Close search session
            if self.search:
                try:
                    await self.search.close_session()
                    logger.info("Search session closed")
                except Exception as e:
                    logger.warning(f"Error closing search session: {e}")
            
            logger.info("Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def run_chat_bot(user_id=None):
    """Run the chat bot (called from main.py)"""
    async def run():
        # Create and run bot
        bot = TerminalChatBot(user_id)
        
        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            print("\n\n🛑 Interrupted by user")
            bot.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Run bot
        await bot.run()
    
    # Run the async function
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


# Legacy support - can still run directly
if __name__ == '__main__':
    user_id = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("""
Terminal Chat Bot - AI chat interface for terminal

Usage:
    python terminal_bot.py [user_id]
    python main.py [--user user_id]  # Recommended
    
Arguments:
    user_id    Optional user identifier (default: auto-generated)
    
Examples:
    python main.py
    python main.py --user myusername
    
Commands:
    Type !help in the chat for available commands
    Type 'exit' or 'quit' to leave
""")
            sys.exit(0)
        else:
            user_id = sys.argv[1]
    
    run_chat_bot(user_id)
