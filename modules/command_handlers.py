"""
Command Handlers - Implements all command handlers for the terminal bot
"""
from typing import List

from modules.ai_database import ai_db
from modules.logger import BotLogger
from modules.training_data_collector import training_collector

# Initialize logger
logger = BotLogger.get_logger(__name__)


class CommandHandlers:
    """Handles all bot commands"""
    
    def __init__(self, bot_instance):
        """Initialize command handlers
        
        Args:
            bot_instance: Reference to the main TerminalChatBot instance
        """
        self.bot = bot_instance
        self.persona_manager = bot_instance.persona_manager
        self.api_manager = bot_instance.api_manager
        self.utilities = bot_instance.utilities
        self.games = bot_instance.games
        self.search = bot_instance.search
        self.social = bot_instance.social
        self.user_id = bot_instance.user_id
        
        logger.info("Command handlers initialized")
    
    # ==================== AI Commands ====================
    
    async def handle_ai(self, args: List[str]) -> str:
        """Handle AI chat command
        
        Args:
            args: List of arguments (the question)
            
        Returns:
            AI response
        """
        try:
            if not args:
                return "Please provide a question. Usage: !ai <your question>"
            
            question = " ".join(args)
            logger.info(f"AI command: {question[:100]}")
            
            # Update social interaction
            self.social.update_interaction(self.user_id)
            
            # Get conversation history for context
            try:
                user_prefs = await ai_db.get_user_preferences(self.user_id)
                memory_limit = user_prefs.get('conversation_memory', 10)
                # 0 means unlimited, None means get all
                limit = None if memory_limit == 0 else memory_limit
                conversation_history = await ai_db.get_conversation_history(
                    self.user_id,
                    limit=limit
                )
                logger.info(f"Retrieved {len(conversation_history)} previous conversations")
            except Exception as e:
                logger.warning(f"Failed to retrieve conversation history: {e}")
                conversation_history = []
            
            # Get stored memories about the user
            stored_memories = []
            try:
                stored_memories = await ai_db.recall(self.user_id)
                logger.info(f"Retrieved {len(stored_memories)} stored memories")
            except Exception as e:
                logger.warning(f"Failed to retrieve stored memories: {e}")
            
            # Create memory-enhanced prompt
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
            
            # Create AI prompt
            user_question = f"""The user asked: "{question}"\n{context_text}\n\nPlease answer the user's question. Keep your response under 1800 characters."""
            prompt = self.persona_manager.get_ai_prompt(user_question, relationship_level)
            
            # Generate response with streaming
            response_text = ""
            stream = self.api_manager.generate_content_stream(prompt)
            
            # Clear typing indicator and print bot name prefix
            print("\r" + " " * 50 + "\r", end="", flush=True)  # Clear typing indicator
            print(f"{self.bot.persona_manager.get_name()}: ", end="", flush=True)
            
            async for chunk in stream:
                if chunk is None:
                    print()  # New line
                    logger.error("AI response failed")
                    return self.persona_manager.get_error_response("ai_unavailable")
                response_text += chunk
                print(chunk, end="", flush=True)
            
            print()  # New line after streaming completes
            
            if not response_text:
                logger.error("AI response failed - empty response")
                return self.persona_manager.get_error_response("ai_unavailable")
            
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
                logger.info("Conversation saved to database")
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")
            
            # Collect training data
            try:
                training_collector.save_conversation(
                    user_input=question,
                    bot_response=response_text,
                    user_id=self.user_id,
                    context={
                        'relationship_level': relationship_level,
                        'timestamp': None  # Will be auto-generated
                    }
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
            
            # Return special marker to indicate streaming was already handled
            return "STREAMING_COMPLETE"
            
        except Exception as e:
            logger.error(f"AI command error: {e}")
            return self.persona_manager.get_error_response("ai_command_error", error=str(e))
    
    # ==================== Search Commands ====================
    
    async def handle_search(self, args: List[str]) -> str:
        """Handle web search command
        
        Args:
            args: Search query
            
        Returns:
            Search results
        """
        try:
            if not args:
                return "Please provide a search query. Usage: !search <query>"
            
            query = " ".join(args)
            logger.info(f"Search command: {query}")
            
            # Update social interaction
            self.social.update_interaction(self.user_id)
            
            # Perform search
            response = await self.search.search_duckduckgo(query, use_ai_analysis=True)
            
            return response
            
        except Exception as e:
            logger.error(f"Search command error: {e}")
            return self.persona_manager.get_error_response("search_error", error=str(e))
    
    # ==================== Utility Commands ====================
    
    async def handle_time(self, args: List[str]) -> str:
        """Handle time command"""
        try:
            return await self.utilities.get_time()
        except Exception as e:
            logger.error(f"Time command error: {e}")
            return "Error getting time."
    
    async def handle_calc(self, args: List[str]) -> str:
        """Handle calculator command"""
        try:
            if not args:
                return "Please provide an expression. Usage: !calc <expression>"
            
            expression = " ".join(args)
            return await self.utilities.calculate(expression)
        except Exception as e:
            logger.error(f"Calc command error: {e}")
            return "Error calculating expression."
    
    async def handle_dice(self, args: List[str]) -> str:
        """Handle dice roll command"""
        try:
            sides = 6
            if args:
                try:
                    sides = int(args[0])
                except ValueError:
                    return "Please provide a valid number for dice sides."
            
            return await self.utilities.roll_dice(sides)
        except Exception as e:
            logger.error(f"Dice command error: {e}")
            return "Error rolling dice."
    
    async def handle_flip(self, args: List[str]) -> str:
        """Handle coin flip command"""
        try:
            return await self.utilities.flip_coin()
        except Exception as e:
            logger.error(f"Flip command error: {e}")
            return "Error flipping coin."
    
    async def handle_weather(self, args: List[str]) -> str:
        """Handle weather command"""
        try:
            if not args:
                return "Please provide a location. Usage: !weather <city>"
            
            location = " ".join(args)
            return await self.utilities.get_weather(location, self.user_id)
        except Exception as e:
            logger.error(f"Weather command error: {e}")
            return "Error getting weather."
    
    async def handle_fact(self, args: List[str]) -> str:
        """Handle random fact command"""
        try:
            return await self.utilities.get_random_fact(self.user_id)
        except Exception as e:
            logger.error(f"Fact command error: {e}")
            return "Error getting fact."
    
    async def handle_joke(self, args: List[str]) -> str:
        """Handle joke command"""
        try:
            return await self.utilities.get_joke(self.user_id)
        except Exception as e:
            logger.error(f"Joke command error: {e}")
            return "Error getting joke."
    
    async def handle_catfact(self, args: List[str]) -> str:
        """Handle cat fact command"""
        try:
            return await self.utilities.get_cat_fact()
        except Exception as e:
            logger.error(f"Cat fact command error: {e}")
            return "Error getting cat fact."
    
    # ==================== Game Commands ====================
    
    async def handle_game(self, args: List[str]) -> str:
        """Handle game start command"""
        try:
            if not args:
                return "Please specify a game. Usage: !game guess [max_number]"
            
            game_type = args[0].lower()
            
            if game_type == 'guess':
                max_number = 100
                if len(args) > 1:
                    try:
                        max_number = int(args[1])
                    except ValueError:
                        return "Please provide a valid number for max."
                
                return await self.games.start_number_guessing(self.user_id, max_number)
            else:
                return f"Unknown game type '{game_type}'. Try: !game guess"
                
        except Exception as e:
            logger.error(f"Game command error: {e}")
            return "Error starting game."
    
    async def handle_guess(self, args: List[str]) -> str:
        """Handle guess command"""
        try:
            if not args:
                return "Please provide a number. Usage: !guess <number>"
            
            try:
                guess = int(args[0])
            except ValueError:
                return "Please provide a valid number."
            
            return await self.games.guess_number(self.user_id, guess)
        except Exception as e:
            logger.error(f"Guess command error: {e}")
            return "Error processing guess."
    
    async def handle_rps(self, args: List[str]) -> str:
        """Handle rock-paper-scissors command"""
        try:
            if not args:
                return "Please choose rock, paper, or scissors. Usage: !rps <choice>"
            
            choice = args[0].lower()
            return await self.games.rock_paper_scissors(choice, self.user_id)
        except Exception as e:
            logger.error(f"RPS command error: {e}")
            return "Error playing rock-paper-scissors."
    
    async def handle_8ball(self, args: List[str]) -> str:
        """Handle magic 8-ball command"""
        try:
            if not args:
                return "Please ask a question. Usage: !8ball <question>"
            
            question = " ".join(args)
            return await self.games.magic_8ball(question)
        except Exception as e:
            logger.error(f"8ball command error: {e}")
            return "Error consulting the magic 8-ball."
    
    async def handle_trivia(self, args: List[str]) -> str:
        """Handle trivia command"""
        try:
            source = args[0] if args else None
            return await self.games.trivia_game(self.user_id, source)
        except Exception as e:
            logger.error(f"Trivia command error: {e}")
            return "Error starting trivia."
    
    async def handle_answer(self, args: List[str]) -> str:
        """Handle answer command (for trivia and games)"""
        try:
            if not args:
                return "Please provide an answer. Usage: !answer <your answer>"
            
            answer = " ".join(args)
            return await self.games.answer(self.user_id, answer)
        except Exception as e:
            logger.error(f"Answer command error: {e}")
            return "Error processing answer."
    
    # ==================== System Commands ====================
    
    async def handle_help(self, args: List[str]) -> str:
        """Handle help command"""
        try:
            # Help is handled by interface (terminal or TUI)
            if args:
                # Specific command help requested
                return f"SHOW_HELP:{args[0]}"
            else:
                # Show all commands
                return "SHOW_HELP"
        except Exception as e:
            logger.error(f"Help command error: {e}")
            return "Error showing help."
    
    async def handle_memory(self, args: List[str]) -> str:
        """Handle memory settings command"""
        try:
            user_prefs = await ai_db.get_user_preferences(self.user_id)
            current_memory = user_prefs.get('conversation_memory', 10)
            
            if not args:
                # Show current settings
                memory_display = "unlimited" if current_memory == 0 else f"{current_memory} messages"
                return f"""🧠 Memory Settings

Your current conversation memory: **{memory_display}**

How it works:
I remember our previous conversations to provide better context.
Higher numbers = more memory but may slow responses.
Set to 0 for unlimited memory.

Change Settings:
Use !memory <number> to adjust
Example: !memory 20 or !memory 0 (unlimited)"""
            else:
                # Update memory settings
                try:
                    memory_length = int(args[0])
                except ValueError:
                    return "Please provide a valid number (0 for unlimited, or any positive number)."
                
                if memory_length >= 0:
                    await ai_db.update_user_preferences(self.user_id, {
                        'conversation_memory': memory_length
                    })
                    memory_display = "unlimited" if memory_length == 0 else f"{memory_length} messages"
                    return f"✅ Memory updated to {memory_display}!"
                else:
                    return "❌ Memory length must be 0 or a positive number!"
                    
        except Exception as e:
            logger.error(f"Memory command error: {e}")
            return f"❌ Error updating memory settings: {e}"
    
    async def handle_stats(self, args: List[str]) -> str:
        """Handle stats command"""
        try:
            return await self.utilities.get_usage_stats(self.user_id)
        except Exception as e:
            logger.error(f"Stats command error: {e}")
            return "Error getting statistics."
    
    async def handle_mood(self, args: List[str]) -> str:
        """Handle mood command"""
        try:
            user_data = self.social.get_user_relationship(self.user_id)
            relationship_level = user_data['relationship_level']
            
            # Generate AI response for mood
            prompt = self.persona_manager.create_ai_prompt(
                "!mood command", "user", relationship_level
            )
            response = await self.api_manager.generate_content(prompt)
            
            if response:
                return response
            else:
                return self.persona_manager.get_relationship_response(relationship_level, "mood")
        except Exception as e:
            logger.error(f"Mood command error: {e}")
            return "I'm doing well, thanks for asking!"
    
    async def handle_relationship(self, args: List[str]) -> str:
        """Handle relationship command"""
        try:
            user_data = self.social.get_user_relationship(self.user_id)
            relationship_level = user_data['relationship_level']
            interactions = user_data['interactions']
            
            return f"""📊 Your Relationship Status

**Level:** {relationship_level.title()}
**Interactions:** {interactions}

Keep chatting with me to improve our relationship!"""
        except Exception as e:
            logger.error(f"Relationship command error: {e}")
            return "Error getting relationship status."

    async def handle_persona(self, args: List[str]) -> str:
        """Handle persona commands: list, set <name>, show

        Usage:
          !persona list       - lists available personas
          !persona show       - shows the currently loaded persona summary
          !persona set <name> - switch to a persona from `personality/<name>.json`
        """
        try:
            if not args or args[0].lower() == 'show':
                summary = self.persona_manager.get_current_persona_summary()
                name = summary.get('name') or 'Unknown'
                personality = summary.get('personality') or 'Unknown'
                desc = summary.get('description') or ''
                return f"Current persona: **{name}** ({personality})\n{desc}"

            cmd = args[0].lower()
            if cmd == 'list':
                personas = self.persona_manager.list_personas()
                if not personas:
                    return "No personas found in the `personality/` directory."
                lines = "\n".join([f"- {p}" for p in personas])
                return f"Available personas:\n{lines}"

            if cmd == 'set' and len(args) > 1:
                name = args[1]
                success, msg = self.persona_manager.set_persona_by_name(name)
                # Update terminal interface if present
                try:
                    new_name = self.persona_manager.get_name()
                    if hasattr(self.bot, 'interface') and getattr(self.bot, 'interface'):
                        try:
                            self.bot.interface.bot_name = new_name
                            self.bot.interface.clear_screen()
                            self.bot.interface.display_welcome()
                        except Exception:
                            pass

                    # Update TUI if present
                    if hasattr(self.bot, 'app') and getattr(self.bot, 'app'):
                        try:
                            # ChatApp exposes bot_name; update and refresh title
                            if hasattr(self.bot.app, 'update_bot_name'):
                                self.bot.app.update_bot_name(new_name)
                            else:
                                self.bot.app.bot_name = new_name
                                try:
                                    self.bot.app.title = f"Terminal Chat - {new_name}"
                                except Exception:
                                    pass
                                try:
                                    self.bot.app.add_bot_message(f"Persona switched to {new_name}")
                                except Exception:
                                    pass
                        except Exception:
                            pass
                except Exception:
                    pass

                return msg if success else f"Failed to switch persona: {msg}"

            return "Invalid persona command. Usage: !persona (list|show|set <name>)"
        except Exception as e:
            logger.error(f"Persona command error: {e}")
            return "Error handling persona command."
    
    async def handle_compliment(self, args: List[str]) -> str:
        """Handle compliment command"""
        try:
            user_data = self.social.update_interaction(self.user_id)
            relationship_level = user_data['relationship_level']
            
            # Generate AI response for compliment
            prompt = self.persona_manager.create_ai_prompt(
                "!compliment command", "user", relationship_level
            )
            response = await self.api_manager.generate_content(prompt)
            
            if response:
                return response
            else:
                return self.persona_manager.get_response("compliment_received")
        except Exception as e:
            logger.error(f"Compliment command error: {e}")
            return "Thank you! That's very kind of you."
    
    async def handle_personality(self, args: List[str]) -> str:
        """Handle personality switching"""
        try:
            if not args:
                # Show current personality and available personas
                current = self.persona_manager.get_current_persona_summary()
                available = self.persona_manager.list_personas()
                
                personas_list = "\n".join([f"  • **{p}**" for p in available])
                
                return f"""🎭 Personality Switching

**Current Persona:** {current['name']}
**Type:** {current['personality']}
**Description:** {current.get('description', 'No description')}

**Available Personas:**
{personas_list}

**Usage:** !personality <name>
**Example:** !personality tsundere

**Note:** Personas are loaded from the personality/ folder"""
            
            # Switch personality
            persona_name = args[0].lower()
            
            success, message = self.persona_manager.set_persona_by_name(persona_name)
            
            if success:
                # Reload the bot name after switching
                new_name = self.persona_manager.get_name()
                
                # Update terminal interface if present
                try:
                    if hasattr(self.bot, 'interface') and getattr(self.bot, 'interface'):
                        if hasattr(self.bot.interface, 'update_bot_name'):
                            self.bot.interface.update_bot_name(new_name, refresh_welcome=False)
                        else:
                            self.bot.interface.bot_name = new_name
                except Exception:
                    pass
                
                # Update TUI if present
                try:
                    if hasattr(self.bot, 'app') and getattr(self.bot, 'app'):
                        if hasattr(self.bot.app, 'update_bot_name'):
                            self.bot.app.update_bot_name(new_name)
                        else:
                            self.bot.app.bot_name = new_name
                            try:
                                self.bot.app.title = f"Terminal Chat - {new_name}"
                            except Exception:
                                pass
                except Exception:
                    pass
                
                return f"✅ {message}\n\n**New persona:** {new_name}"
            else:
                available = self.persona_manager.list_personas()
                return f"❌ {message}\n\nAvailable personas: {', '.join(available)}"
            
        except Exception as e:
            logger.error(f"Personality command error: {e}")
            return f"❌ Error switching personality: {e}"
    
    # ==================== Training Data Commands ====================
    
    async def handle_training_stats(self, args: List[str]) -> str:
        """Handle training data statistics command"""
        try:
            # Get training data stats
            stats = training_collector.get_statistics()
            
            # Get memory stats
            memories = await ai_db.recall(self.user_id)
            user_memories = len([m for m in memories if m['memory_type'] == 'user'])
            conv_memories = len([m for m in memories if m['memory_type'] == 'conversation'])
            
            date_info = ""
            if stats['date_range']:
                date_info = f"\n**First:** {stats['date_range']['first'][:10]}\n**Last:** {stats['date_range']['last'][:10]}"
            
            return f"""📊 Training Data & Memory Statistics

**Full Conversation Logs (for AI training):**
- Total Conversations: {stats['total_conversations']}
- Unique Users: {stats['unique_users']}
- Avg User Input: {stats['avg_user_input_length']:.0f} chars
- Avg Bot Response: {stats['avg_bot_response_length']:.0f} chars{date_info}

**Extracted Memories (for quick context):**
- About You: {user_memories} facts
- Conversation Topics: {conv_memories} memories
- Total: {len(memories)} structured memories

💡 **Two-Layer Learning System:**
- Full logs preserve all conversation nuance for training
- Extracted memories provide instant context for responses

Use !training_export to export full logs for fine-tuning.
Use !memories to see extracted facts."""
        except Exception as e:
            logger.error(f"Training stats error: {e}")
            return f"Error getting training statistics: {e}"
    
    async def handle_training_export(self, args: List[str]) -> str:
        """Handle training data export command"""
        try:
            # Default format is OpenAI
            format_type = args[0] if args else "openai"
            
            if format_type not in ["openai", "llama", "alpaca"]:
                return f"""❌ Invalid format: {format_type}

Available formats:
- **openai**: OpenAI fine-tuning format
- **llama**: Llama/Mistral format with special tokens
- **alpaca**: Alpaca instruction format

Usage: !training_export <format>
Example: !training_export llama"""
            
            output_file = training_collector.export_for_fine_tuning(format_type=format_type)
            
            if output_file:
                return f"""✅ Training data exported!

**Format:** {format_type}
**File:** {output_file}

You can now use this file to fine-tune models like:
- OpenAI GPT models (openai format)
- Llama 2/3, Mistral (llama format)
- Alpaca models (alpaca format)"""
            else:
                return "❌ Failed to export training data. Check logs for details."
                
        except Exception as e:
            logger.error(f"Training export error: {e}")
            return f"Error exporting training data: {e}"
    
    async def handle_train_model(self, args: List[str]) -> str:
        """Handle model training command"""
        try:
            from modules.model_trainer import get_trainer
            
            trainer = get_trainer()
            if trainer is None:
                return """❌ Model trainer not available!

Install required packages:
pip install transformers datasets accelerate torch peft

For GPU support (recommended):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"""
            
            # Parse arguments
            model_size = args[0] if args else "tiny"
            
            if model_size not in trainer.COMPATIBLE_MODELS:
                models_list = "\n".join([f"- **{k}**: {v}" for k, v in trainer.COMPATIBLE_MODELS.items()])
                return f"""❌ Invalid model size: {model_size}

Available models:
{models_list}

Usage: !train_model <size> [epochs]
Example: !train_model tiny 3"""
            
            epochs = 3
            if len(args) > 1:
                try:
                    epochs = int(args[1])
                except ValueError:
                    return "❌ Epochs must be a number"
            
            # Check requirements
            reqs = trainer.estimate_requirements(model_size)
            
            return f"""🚀 Starting model training...

**Model:** {model_size} ({trainer.COMPATIBLE_MODELS[model_size]})
**Epochs:** {epochs}

**Requirements:**
- VRAM: {reqs.get('vram_gb', 'N/A')} GB
- RAM: {reqs.get('ram_gb', 'N/A')} GB
- Time: ~{reqs.get('time_per_epoch', 'N/A')} per epoch

Training will start in the background. This may take a while...
Check bot.log for progress updates.

Note: Training is CPU-intensive. Your terminal may be slow during training."""
            
        except Exception as e:
            logger.error(f"Train model error: {e}")
            return f"Error starting training: {e}"
    
    async def handle_list_models(self, args: List[str]) -> str:
        """Handle list trained models command"""
        try:
            from modules.model_trainer import get_trainer
            
            trainer = get_trainer()
            if trainer is None:
                return "❌ Model trainer not available. Install required packages first."
            
            models = trainer.list_trained_models()
            
            if not models:
                return """📁 No trained models found.

Train your first model with:
!train_model tiny

This will create a custom AI model based on your conversations!"""
            
            models_text = ""
            for i, model in enumerate(models, 1):
                models_text += f"""
**{i}. {model['name']}**
- Size: {model.get('model_size', 'unknown')}
- Conversations: {model.get('num_conversations', 0)}
- Trained: {model.get('trained_at', 'unknown')[:10]}
- Path: {model['path']}
"""
            
            return f"""📁 Trained Models ({len(models)} total)
{models_text}

Use these models by loading them in your code or switching the API manager."""
            
        except Exception as e:
            logger.error(f"List models error: {e}")
            return f"Error listing models: {e}"
    
    async def handle_training_requirements(self, args: List[str]) -> str:
        """Handle training requirements command"""
        try:
            from modules.model_trainer import get_trainer
            
            trainer = get_trainer()
            if trainer is None:
                return "❌ Model trainer not available."
            
            model_size = args[0] if args else None
            
            if model_size:
                if model_size not in trainer.COMPATIBLE_MODELS:
                    return f"❌ Invalid model size: {model_size}"
                
                reqs = trainer.estimate_requirements(model_size)
                return f"""💻 Requirements for {model_size} model:

**Hardware:**
- VRAM: {reqs.get('vram_gb', 'N/A')} GB (GPU)
- RAM: {reqs.get('ram_gb', 'N/A')} GB
- Storage: ~10-20 GB

**Time:**
- Per Epoch: {reqs.get('time_per_epoch', 'N/A')}
- Recommended: 3-5 epochs

**Best For:**
{reqs.get('recommended_for', 'General use')}

**Model:** {trainer.COMPATIBLE_MODELS[model_size]}"""
            else:
                # Show all models
                all_reqs = ""
                for size in trainer.COMPATIBLE_MODELS.keys():
                    reqs = trainer.estimate_requirements(size)
                    all_reqs += f"""
**{size.upper()}** - {reqs.get('vram_gb', 'N/A')} GB VRAM
{reqs.get('recommended_for', 'General use')}
"""
                
                return f"""💻 Training Requirements

{all_reqs}

For detailed info: !training_requirements <size>
Example: !training_requirements tiny"""
            
        except Exception as e:
            logger.error(f"Training requirements error: {e}")
            return f"Error getting requirements: {e}"

    async def handle_remember(self, args: List[str]) -> str:
        """Handle remember command - AI stores information about user"""
        try:
            if len(args) < 2:
                return """🧠 Remember Command

Usage: !remember <key> <value>

Examples:
  !remember favorite_color blue
  !remember birthday 1990-05-15
  !remember hobby programming

This allows me to remember important things about you!"""
            
            key = args[0]
            value = " ".join(args[1:])
            
            await ai_db.remember(self.user_id, key, value)
            return f"✅ I'll remember that your {key} is: {value}"
            
        except Exception as e:
            logger.error(f"Remember command error: {e}")
            return f"❌ Error storing memory: {e}"
    
    async def handle_recall(self, args: List[str]) -> str:
        """Handle recall command - retrieve specific memory"""
        try:
            if not args:
                return """🔍 Recall Command

Usage: !recall <key>

Examples:
  !recall favorite_color
  !recall birthday

Or use !memories to see all stored memories."""
            
            key = args[0]
            memory = await ai_db.recall(self.user_id, key)
            
            if memory:
                return f"💭 I remember: {memory['memory_key']} = {memory['memory_value']}"
            else:
                return f"❌ I don't have any memory stored for '{key}'"
                
        except Exception as e:
            logger.error(f"Recall command error: {e}")
            return f"❌ Error recalling memory: {e}"
    
    async def handle_forget(self, args: List[str]) -> str:
        """Handle forget command - delete a memory"""
        try:
            if not args:
                return """🗑️ Forget Command

Usage: !forget <key>

Examples:
  !forget favorite_color
  !forget old_hobby

This will permanently delete the memory."""
            
            key = args[0]
            success = await ai_db.forget(self.user_id, key)
            
            if success:
                return f"✅ I've forgotten about your {key}"
            else:
                return f"❌ I don't have any memory stored for '{key}'"
                
        except Exception as e:
            logger.error(f"Forget command error: {e}")
            return f"❌ Error forgetting memory: {e}"
    
    async def handle_memories(self, args: List[str]) -> str:
        """Handle memories command - list all stored memories"""
        try:
            memories = await ai_db.recall(self.user_id)
            
            if not memories:
                return """💭 No Memories Stored

I don't have any memories yet! As we chat, I'll automatically learn about you and remember our conversations.

You can also manually add memories:
  !remember name John
  !remember favorite_food pizza"""
            
            # Separate by type
            user_memories = [m for m in memories if m['memory_type'] == 'user']
            conversation_memories = [m for m in memories if m['memory_type'] == 'conversation']
            other_memories = [m for m in memories if m['memory_type'] not in ['user', 'conversation']]
            
            memories_text = "💭 **My Memory of Our Relationship:**\n\n"
            
            if user_memories:
                memories_text += "**About You:**\n"
                for mem in sorted(user_memories, key=lambda x: x['importance'], reverse=True):
                    memories_text += f"• **{mem['memory_key']}**: {mem['memory_value']}\n"
                    memories_text += f"  _(importance: {mem['importance']}/10, accessed {mem['access_count']} times)_\n"
                memories_text += "\n"
            
            if conversation_memories:
                memories_text += "**Our Conversations & Topics:**\n"
                for mem in sorted(conversation_memories, key=lambda x: x['importance'], reverse=True):
                    memories_text += f"• **{mem['memory_key']}**: {mem['memory_value']}\n"
                    memories_text += f"  _(importance: {mem['importance']}/10)_\n"
                memories_text += "\n"
            
            if other_memories:
                memories_text += "**Other Memories:**\n"
                for mem in other_memories:
                    memories_text += f"• **{mem['memory_key']}**: {mem['memory_value']}\n"
                memories_text += "\n"
            
            memories_text += f"**Total: {len(memories)} memories** (auto-learned from our chats)"
            return memories_text
            
        except Exception as e:
            logger.error(f"Memories command error: {e}")
            return f"❌ Error retrieving memories: {e}"
