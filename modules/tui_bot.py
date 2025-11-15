"""
TUI Bot - Terminal bot with Textual UI
"""
import asyncio
import signal
from modules.tui_interface import is_textual_available, create_tui_app
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
from modules.command_parser import CommandParser
from modules.command_handlers import CommandHandlers

logger = BotLogger.get_logger(__name__)


class TUIBot:
    """Terminal bot with Textual TUI"""
    
    def __init__(self, user_id: str = None):
        """Initialize TUI bot"""
        if not is_textual_available():
            raise ImportError("Textual is not installed. Install with: pip install textual")
        
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
        
        # Initialize modules
        self.persona_manager = None
        self.api_manager = None
        self.utilities = None
        self.games = None
        self.search = None
        self.social = None
        
        # Initialize parser and handlers
        self.parser = None
        self.handlers = None
        
        # TUI app
        self.app = None
        
        logger.info(f"TUIBot created for user: {self.user_id}")
    
    async def initialize(self):
        """Async initialization"""
        try:
            logger.info("Starting TUI bot initialization")
            
            # Validate configuration
            try:
                self.config.validate_config()
                logger.info("Configuration validated")
            except ValueError as e:
                logger.error(f"Configuration validation failed: {e}")
                return False
            
            # Initialize API manager
            self.api_manager = GeminiAPIManager()
            model = self.api_manager.get_current_model()
            
            if model is None:
                logger.error("Failed to initialize API model")
                return False
            
            # Initialize persona manager
            self.persona_manager = PersonaManager()
            bot_name = self.persona_manager.get_name()
            
            # Initialize AI database
            await initialize_ai_database()
            
            # Wire knowledge manager
            try:
                knowledge_manager.set_ai_db(ai_db)
                self.persona_manager.set_knowledge_manager(knowledge_manager)
            except Exception as e:
                logger.warning(f"Failed to wire knowledge manager: {e}")
            
            # Initialize modules
            self.utilities = TsundereUtilities(model)
            self.games = TsundereGames(api_manager=self.api_manager, search=None, ai_db=ai_db)
            self.search = TsundereSearch(model)
            self.social = TsundereSocial()
            
            # Wire dependencies
            try:
                self.games.set_api_manager(self.api_manager)
                self.games.set_ai_db(ai_db)
                self.games.set_knowledge_manager(knowledge_manager)
            except Exception as e:
                logger.warning(f"Failed to wire game dependencies: {e}")
            
            try:
                self.search.set_knowledge_manager(knowledge_manager)
            except Exception as e:
                logger.warning(f"Failed to wire search dependencies: {e}")
            
            # Initialize command parser and handlers
            self.parser = CommandParser()
            self.handlers = CommandHandlers(self)
            
            # Register command handlers
            self._register_command_handlers()
            
            # Create TUI app
            self.app = create_tui_app(bot_name=bot_name, user_name="You")
            self.app.set_command_callback(self.process_command)
            
            logger.info("TUI bot initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    def _register_command_handlers(self):
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
        self.parser.register_handler('personality', self.handlers.handle_personality)
        # Persona management
        self.parser.register_handler('persona', self.handlers.handle_persona)
        
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
    
    async def process_command(self, user_input: str):
        """Process user command"""
        try:
            # Parse input
            command, args, kwargs = self.parser.parse(user_input)
            
            # Get handler
            handler = self.parser.get_command_handler(command)
            
            if handler:
                # Check if it's an AI command for streaming
                if command in ['ai', 'chat', 'ask']:
                    # Handle streaming for AI commands
                    await self._handle_streaming_ai(args)
                else:
                    # Execute command normally
                    response = await handler(args)
                    
                    # Handle special responses
                    if response == "SHOW_HELP":
                        self.app.action_help()
                    elif response.startswith("SHOW_HELP:"):
                        # Detailed help for specific command
                        command = response.split(":", 1)[1]
                        self.app.action_help(command)
                    elif response == "STREAMING_COMPLETE":
                        pass  # Already handled
                    else:
                        self.app.add_bot_message(response)
                
                # Track interaction
                self.social.update_interaction(self.user_id)
            else:
                # Unknown command
                suggestion = self.parser.suggest_command(command)
                if suggestion:
                    self.app.add_bot_message(
                        f"Unknown command '{command}'. Did you mean '!{suggestion}'?"
                    )
                else:
                    self.app.add_bot_message(
                        f"Unknown command '{command}'. Type !help for available commands."
                    )
        
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.app.add_bot_message(f"Error: {e}")
    
    async def _handle_streaming_ai(self, args):
        """Handle AI command with streaming"""
        try:
            if not args:
                self.app.add_bot_message("Please provide a question. Usage: !ai <your question>")
                return
            
            question = " ".join(args)
            
            # Get conversation history
            try:
                user_prefs = await ai_db.get_user_preferences(self.user_id)
                memory_limit = user_prefs.get('conversation_memory', 10)
                # 0 means unlimited, None means get all
                limit = None if memory_limit == 0 else memory_limit
                conversation_history = await ai_db.get_conversation_history(
                    self.user_id,
                    limit=limit
                )
            except Exception:
                conversation_history = []
            
            # Get stored memories about the user
            stored_memories = []
            try:
                stored_memories = await ai_db.recall(self.user_id)
            except Exception:
                pass
            
            # Create context
            context_text = ""
            
            # Add stored memories - separate by type
            if stored_memories:
                user_memories = [m for m in stored_memories if m['memory_type'] == 'user']
                conversation_memories = [m for m in stored_memories if m['memory_type'] == 'conversation']
                
                if user_memories:
                    context_text += "\n\nThings you know about this user:\n"
                    for mem in sorted(user_memories, key=lambda x: x['importance'], reverse=True)[:10]:
                        context_text += f"- {mem['memory_key']}: {mem['memory_value']}\n"
                
                if conversation_memories:
                    context_text += "\n\nPrevious topics and things you discussed:\n"
                    for mem in sorted(conversation_memories, key=lambda x: x['importance'], reverse=True)[:8]:
                        context_text += f"- {mem['memory_key']}: {mem['memory_value']}\n"
            
            # Add recent conversation history
            if conversation_history:
                context_text += "\n\nRecent conversation snippets:\n"
                for conv in conversation_history[-3:]:
                    context_text += f"User: {conv['message_content'][:100]}...\n"
                    context_text += f"You: {conv['ai_response'][:100]}...\n"
            
            # Get relationship level
            try:
                user_rel = self.social.get_user_relationship(self.user_id)
                relationship_level = user_rel.get('relationship_level', 'stranger')
            except Exception:
                relationship_level = 'stranger'
            
            # Create prompt
            user_question = f"""The user asked: "{question}"\n{context_text}\n\nPlease answer the user's question. Keep your response under 1800 characters."""
            prompt = self.persona_manager.get_ai_prompt(user_question, relationship_level)
            
            # Show typing indicator
            self.app.show_typing_indicator()
            
            # Start streaming
            self.app.start_streaming_message()
            response_text = ""
            
            stream = self.api_manager.generate_content_stream(prompt)
            async for chunk in stream:
                if chunk is None:
                    self.app.end_streaming_message()
                    self.app.add_bot_message("Sorry, I couldn't generate a response.")
                    return
                response_text += chunk
                self.app.append_to_stream(chunk)
            
            self.app.end_streaming_message()
            
            # Save conversation
            try:
                await ai_db.save_conversation(
                    user_id=self.user_id,
                    message=question,
                    ai_response=response_text,
                    model_used="gemini-pro",
                    context_data={
                        'command_used': 'ai',
                        'relationship_level': relationship_level
                    }
                )
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")
            
            # Collect training data
            try:
                from modules.training_data_collector import training_collector
                training_collector.save_conversation(
                    user_input=question,
                    bot_response=response_text,
                    user_id=self.user_id,
                    context={'relationship_level': relationship_level}
                )
            except Exception as e:
                logger.error(f"Failed to save training data: {e}")
            
            # Auto-extract and store memories
            try:
                from modules.auto_memory import create_auto_memory
                auto_memory = create_auto_memory(self.api_manager)
                await auto_memory.analyze_and_remember(self.user_id, question, response_text)
            except Exception as e:
                logger.error(f"Failed to auto-extract memories: {e}")
        
        except Exception as e:
            logger.error(f"Error in streaming AI: {e}")
            self.app.end_streaming_message()
            self.app.add_bot_message(f"Error: {e}")
    
    async def run(self):
        """Run the TUI bot"""
        try:
            # Initialize
            if not await self.initialize():
                print("❌ Failed to initialize TUI bot")
                return
            
            self.running = True
            
            # Run the app
            await self.app.run_async()
            
            # Shutdown
            await self.shutdown()
        
        except Exception as e:
            logger.error(f"Fatal error in TUI bot: {e}")
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        try:
            logger.info("Shutting down TUI bot")
            
            # Save social data
            if self.social:
                self.social.save_user_data()
            
            # Close database
            try:
                await ai_db.close()
            except Exception as e:
                logger.warning(f"Error closing database: {e}")
            
            # Close search session
            if self.search:
                try:
                    await self.search.close_session()
                except Exception as e:
                    logger.warning(f"Error closing search session: {e}")
            
            logger.info("TUI bot shutdown complete")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def run_tui_bot(user_id=None):
    """Run the TUI bot"""
    if not is_textual_available():
        print("❌ Textual is not installed!")
        print("\nInstall with:")
        print("pip install textual")
        return
    
    bot = TUIBot(user_id)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal, shutting down...")
        bot.running = False
        if bot.app:
            bot.app.exit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Fatal error in TUI bot: {e}")
