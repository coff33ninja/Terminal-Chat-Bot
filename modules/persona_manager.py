"""
Persona Manager - Centralized personality system using persona cards
"""
import json
import random
import os
import glob
from .bot_name_service import BotNameService

# Constants for persona management
DEFAULT_PERSONA_FILE = "persona_card.json"
DEFAULT_PERSONA_NAME = "AI Assistant"
DEFAULT_PERSONA_PERSONALITY = "helpful"
DEFAULT_AI_PROMPT = "You are a helpful AI assistant."
AI_GENERATION_TIMEOUT = 15.0  # seconds

class PersonaManager:
    STATE_FILENAME = "bot_state.json"

    def __init__(self, persona_file="persona_card.json", ai_db=None, knowledge_manager=None):
        # If caller used default, try to load persisted selection
        if persona_file == DEFAULT_PERSONA_FILE:
            saved = self._load_selected_persona()
            if saved:
                persona_file = saved

        self.persona_file = persona_file
        self.persona = self.load_persona()
        # Initialize bot name service with the same persona file
        self.bot_name_service = BotNameService(self.persona_file)
        # Backwards-compatible storage of raw ai_db
        self.ai_db = ai_db
        # Preferred knowledge manager wrapper
        self.knowledge_manager = knowledge_manager

    def _state_file_path(self):
        """Return absolute path to state file at project root."""
        root = self._project_root()
        return os.path.join(root, self.STATE_FILENAME)

    def _save_selected_persona(self, persona_path):
        try:
            data = {"selected_persona": os.path.abspath(persona_path)}
            with open(self._state_file_path(), 'w', encoding='utf-8') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    def _load_selected_persona(self):
        try:
            path = self._state_file_path()
            if not os.path.exists(path):
                return None
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('selected_persona')
        except Exception:
            return None

    def set_ai_db(self, ai_db):
        """Inject an AI DB instance (AIDatabase) for saving generated persona outputs (backwards-compatible)."""
        self.ai_db = ai_db
        try:
            # If a knowledge manager module exists at import-time, set its ai_db too
            from .knowledge_manager import knowledge_manager
            knowledge_manager.set_ai_db(ai_db)
            self.knowledge_manager = knowledge_manager
        except Exception:
            pass

    def set_knowledge_manager(self, km):
        """Inject a KnowledgeManager instance for saving generated persona outputs."""
        self.knowledge_manager = km
    
    def load_persona(self):
        """Load persona card from JSON file"""
        try:
            with open(self.persona_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.persona_file} not found. Using default persona.")
            return self.get_default_persona()
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.persona_file}. Using default persona.")
            return self.get_default_persona()
    
    def get_default_persona(self):
        """Fallback default persona with all necessary response templates"""
        return {
            "name": DEFAULT_PERSONA_NAME,
            "personality": DEFAULT_PERSONA_PERSONALITY,
            "description": "A helpful AI assistant that provides assistance with various tasks",
            "core_traits": [
                "Helpful and informative",
                "Polite and professional",
                "Clear and concise communication",
                "Eager to assist users"
            ],
            "speech_patterns": {
                "greeting": ["Hello!", "Hi there!", "Good day!"],
                "acknowledgment": ["I understand", "Got it", "Certainly"],
                "thinking": ["Let me think about that", "One moment", "Processing..."],
                "completion": ["Done!", "Complete", "Finished"]
            },
            "response_templates": {
                "error": [
                    "I apologize, but something went wrong. Let me try to help you anyway.",
                    "There seems to be an issue, but I'm here to assist you.",
                    "Oops! Something didn't work as expected. How can I help you resolve this?"
                ],
                "mention": [
                    "Hello! You mentioned me. How can I assist you today?",
                    "Hi there! I'm here to help. What do you need?",
                    "You called? I'm ready to assist you with whatever you need."
                ],
                "compliment_received": [
                    "Thank you for the kind words! I'm happy to help.",
                    "I appreciate that! It's my pleasure to assist you.",
                    "That's very nice of you to say. How else can I help?"
                ],
                "missing_args": [
                    "I need a bit more information to help you with that.",
                    "Could you provide more details so I can assist you better?",
                    "I'm missing some information. Could you be more specific?"
                ]
            },
            "relationship_responses": {
                "stranger": {
                    "greeting": "Hello! I'm here to help you with whatever you need.",
                    "compliment": "Thank you! I'm glad I could be of assistance.",
                    "mood": "I'm doing well and ready to help you today!"
                },
                "acquaintance": {
                    "greeting": "Nice to see you again! How can I help you today?",
                    "compliment": "I appreciate your kind words! Happy to help as always.",
                    "mood": "I'm doing great! Thanks for asking. What can I do for you?"
                },
                "friend": {
                    "greeting": "Hey there! Good to see you again. What's on your mind?",
                    "compliment": "You're too kind! I really enjoy helping you out.",
                    "mood": "I'm feeling great today! Ready to tackle whatever you need help with."
                },
                "close_friend": {
                    "greeting": "Hello, my friend! Always a pleasure. What can I help you with?",
                    "compliment": "You always know how to make me feel appreciated! Thank you.",
                    "mood": "I'm wonderful, especially when I get to help good friends like you!"
                }
            },
            "activity_responses": {
                "weather": {
                    "success": "Here's the weather information for {location}: {weather_info}",
                    "error": "I'm sorry, I couldn't retrieve weather information for '{location}' right now."
                },
                "calculation": {
                    "success": "The result of {expression} is {result}.",
                    "error": "I couldn't calculate that expression. Please check the format and try again."
                },
                "games": {
                    "start": "Great! Let's play a game. I'm ready when you are!",
                    "win": "Congratulations! You won! Well played!",
                    "lose": "Better luck next time! Want to play again?",
                    "tie": "It's a tie! We both chose {choice}. Great minds think alike!",
                    "hint_low": "Too low! Try a higher number.",
                    "hint_high": "Too high! Try a lower number.",
                    "trivia_start": "Here's your trivia question:\n\n**{question}**\n\nTake your time!",
                    "trivia_timeout": "Time's up! The correct answer was '{answer}'. Better luck next time!",
                    "trivia_fast_correct": "Wow! Correct answer in {time:.1f} seconds! Impressive!",
                    "trivia_correct": "Correct! You got it right in {time:.1f} seconds. Well done!",
                    "trivia_wrong": "Sorry, that's not correct. The answer was '{answer}'. Try again next time!",
                    "no_active_game": "No active game found. Start a new game first!"
                },
                "magic_8ball": {
                    "answers": [
                        "Yes, definitely!",
                        "No, I don't think so.",
                        "Maybe, it's possible.",
                        "Absolutely!",
                        "Probably not.",
                        "Ask again later.",
                        "I think so.",
                        "Unlikely.",
                        "Most likely.",
                        "Yes, go for it!"
                    ],
                    "action": "*shakes magic 8-ball*"
                },
                "utilities": {
                    "dice": "You rolled: {result}",
                    "time": "The current time is {time}",
                    "coin": "The coin landed on: {result}",
                    "weather": "Here's the weather information for {location}: {weather_info}",
                    "calculate": "The result of {expression} is {result}",
                    "fact": "Here's an interesting fact: {fact}",
                    "joke": "Here's a joke for you:\n\n{setup}\n{punchline}",
                    "cat_fact": "Here's a cat fact: {fact}"
                },
                "facts": {
                    "success": [
                        "Here's an interesting fact: {fact}",
                        "Did you know? {fact}",
                        "Fun fact: {fact}"
                    ],
                    "error": [
                        "I couldn't retrieve a fact right now. Please try again later.",
                        "The fact service is currently unavailable.",
                        "Sorry, I can't get facts at the moment."
                    ]
                },
                "jokes": {
                    "success": [
                        "Here's a joke for you:\n\n{setup}\n{punchline}",
                        "Hope this makes you smile:\n\n{setup}\n{punchline}",
                        "Time for a joke:\n\n{setup}\n{punchline}"
                    ],
                    "error": [
                        "I couldn't get a joke right now. Maybe I can tell you one later!",
                        "The joke service is currently down. Sorry about that!",
                        "No jokes available at the moment, but I'm still here to help!"
                    ]
                },
                "cat_facts": {
                    "success": [
                        "Here's a cat fact: {fact}",
                        "Cat fact: {fact}",
                        "Did you know this about cats? {fact}"
                    ],
                    "error": [
                        "I couldn't get cat facts right now. Try again later!",
                        "The cat fact service is unavailable at the moment.",
                        "No cat facts available right now, but cats are still amazing!"
                    ]
                },
                "help_command": {
                    "title": "Available Commands",
                    "description": "Here are the commands I can help you with:",
                    "footer": "Use these commands to interact with me!"
                },
                "admin": {
                    "reload_success": "Configuration reloaded successfully: {result}",
                    "no_permission": "You don't have permission to use that command.",
                    "shutdown": [
                        "Shutting down now. Goodbye!",
                        "System shutdown initiated. See you later!",
                        "Goodbye! Shutting down the system.",
                        "Farewell! The system is shutting down."
                    ],
                    "restart": [
                        "Restarting the system now. I'll be back shortly!",
                        "System restart initiated. Please wait a moment.",
                        "Restarting now. See you in a moment!",
                        "System reboot in progress. Back soon!"
                    ]
                },
                "permissions": {
                    "no_send_permission": "I don't have permission to send messages in that channel.",
                    "general_permission_error": "I don't have the necessary permissions for that action."
                },
                "bot_status": "Ready to help! | Use !help_ai for commands",
                "server_actions": {
                    "no_permission": "You don't have permission to use that command.",
                    "user_not_found": "I couldn't find that user. Are they in this server?",
                    "role_not_found": "I couldn't find a role with that name.",
                    "channel_not_found": "I couldn't find that channel.",
                    "already_has_role": "{user} already has that role.",
                    "doesnt_have_role": "{user} doesn't have that role.",
                    "cant_kick_self": "I can't kick myself from the server.",
                    "hierarchy_error": "I can't perform that action on someone with a higher role.",
                    "success_mention": "Hey {user}! Someone wanted to get your attention.",
                    "success_role_give": "Successfully gave {user} the {role} role.",
                    "success_role_remove": "Successfully removed the {role} role from {user}.",
                    "success_kick": "{user} has been kicked from the server.",
                    "success_role_create": "Successfully created the '{role_name}' role.",
                    "success_channel": "Successfully created the {type} channel {channel}.",
                    "success_message": "Message delivered to {channel}."
                },
                "search": {
                    "instant_answer": [
                        "Here's your answer: **{answer}**",
                        "I found this: **{answer}**",
                        "The answer is: **{answer}**"
                    ],
                    "abstract": [
                        "I found this information about **{query}**:\n\n{abstract}\n\n*Source: {source}*",
                        "Here's what I found on **{query}**:\n\n{abstract}\n\n*From: {source}*",
                        "Information about **{query}**:\n\n{abstract}\n\n*Source: {source}*"
                    ],
                    "related_topics": [
                        "Here are the search results for **{query}**:\n\n{results}",
                        "I found these results for **{query}**:\n\n{results}",
                        "Search results for **{query}**:\n\n{results}"
                    ],
                    "definition": [
                        "Here's the definition of **{query}**:\n\n{definition}\n\n*Source: {source}*",
                        "**{query}** means:\n\n{definition}\n\n*From: {source}*"
                    ],
                    "web_results": [
                        "Here are the web search results for **{query}**:\n\n{results}",
                        "Web search results for **{query}**:\n\n{results}",
                        "I found these web results for **{query}**:\n\n{results}"
                    ],
                    "no_results": [
                        "I couldn't find any results for **{query}**. Try a different search term.",
                        "No results found for **{query}**. Please try rephrasing your search.",
                        "Sorry, no results for **{query}**. Try searching for something else."
                    ],
                    "error": [
                        "Search is currently unavailable. Please try again later.",
                        "I'm having trouble with the search function right now.",
                        "Search service is temporarily down. Try again in a moment."
                    ],
                    "timeout": [
                        "The search is taking too long. Please try a simpler query.",
                        "Search timed out. Try searching for something more specific.",
                        "The search took too long to complete. Please try again."
                    ]
                },
                "reminders": {
                    "reminder_ping": [
                        "Hey {user_mention}! Here's your reminder:",
                        "{user_mention}, you asked me to remind you about this:",
                        "Reminder for {user_mention}:"
                    ]
                }
            },
            "ai_system_prompt": "You are a helpful AI assistant. You are polite, informative, and eager to help users with their questions and tasks. Provide clear, accurate, and helpful responses while maintaining a friendly and professional tone."
        }
    
    def get_name(self):
        """Get persona name using the bot name service"""
        return self.bot_name_service.get_bot_name()
    
    def get_ai_prompt(self, user_question, relationship_level="stranger"):
        """Generate AI system prompt with full persona card context"""
        # Pass the entire persona card to the AI
        persona_json = json.dumps(self.persona, indent=2)
        
        prompt = f"""You are an AI that must understand and embody the personality described in this persona card:

PERSONA CARD:
{persona_json}

INSTRUCTIONS:
1. Read and understand your complete personality from the persona card above
2. You ARE the character described - embody them completely in your responses
3. Your relationship with this user is: {relationship_level}
4. Respond naturally as this character would, using their speech patterns and personality traits

USER QUESTION: {user_question}

Generate an authentic response as the character described in the persona card."""
        
        return prompt
    
    def get_ai_response_prompt(self, user_action, user_name, relationship_level="stranger"):
        """Generate AI prompt based on persona card and user action"""
        # Pass the persona card to AI so it can embody the personality
        persona_json = json.dumps(self.persona, indent=2)
        
        prompt = f"""PERSONA CARD:
{persona_json}

You ARE the character described above. Embody this personality completely.

USER ACTION: {user_name} just used: {user_action}
RELATIONSHIP LEVEL: {relationship_level}

Based on your personality and what the user did, generate ONE authentic response. Stay in character."""
        
        return prompt
    
    def create_ai_prompt(self, user_action, user_name=None, relationship_level="stranger"):
        """Create AI prompt for use with API manager"""
        if user_name:
            return self.get_ai_response_prompt(user_action, user_name, relationship_level)
        else:
            # For general AI questions without specific user context
            persona_json = json.dumps(self.persona, indent=2)
            
            prompt = f"""PERSONA CARD:
{persona_json}

You ARE the character described above. Embody this personality completely.

USER QUESTION: {user_action}

Generate an authentic response as the character described in the persona card."""
            
            return prompt
    
    def get_response(self, response_type, **kwargs):
        """Get a random response of the specified type with comprehensive fallbacks"""
        responses = self.persona.get("response_templates", {}).get(response_type, [])
        
        # If no responses found, provide generic fallbacks
        if not responses:
            fallback_responses = {
                "error": ["I apologize, but something went wrong. How can I help you?"],
                "mention": ["Hello! How can I assist you today?"],
                "compliment_received": ["Thank you! I'm happy to help."],
                "missing_args": ["I need more information to help you with that."],
                "greeting": ["Hello! How can I help you today?"],
                "goodbye": ["Goodbye! Have a great day!"],
                "thanks": ["You're welcome! Happy to help."],
                "unknown": ["I'm not sure about that, but I'm here to help however I can."]
            }
            responses = fallback_responses.get(response_type, [f"I'm here to help with {response_type}."])
        
        response = random.choice(responses)
        
        # Format response with any provided kwargs
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the unformatted response
            return response
    
    async def get_ai_generated_response(self, model, user_action, user_name, relationship_level="stranger"):
        """Generate a response using AI based on persona and user action"""
        import asyncio
        import concurrent.futures
        
        try:
            prompt = self.get_ai_response_prompt(user_action, user_name, relationship_level)
            
            # Generate response using Gemini with timeout protection
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                try:
                    response = await asyncio.wait_for(
                        loop.run_in_executor(executor, model.generate_content, prompt),
                        timeout=AI_GENERATION_TIMEOUT
                    )
                    result = response.text.strip()
                    # Persist persona-generated response to DB for potential reuse
                    try:
                        if getattr(self, 'knowledge_manager', None) and result:
                            await self.knowledge_manager.add_knowledge('persona', user_action, result)
                        elif getattr(self, 'ai_db', None) and result:
                            await self.ai_db.add_knowledge('persona', user_action, result)
                    except Exception:
                        # Don't let DB persistence fail the response
                        pass
                    return result
                except asyncio.TimeoutError:
                    # Fallback to template response if AI times out
                    return self.get_response("error")
        except Exception:
            # Fallback to template response if AI fails
            return self.get_response("error")
    
    def get_relationship_response(self, relationship_level, response_type, **kwargs):
        """Get relationship-specific response with comprehensive fallbacks"""
        rel_responses = self.persona.get("relationship_responses", {})
        
        # Try the specific relationship level first
        if relationship_level in rel_responses:
            response = rel_responses[relationship_level].get(response_type)
            if response:
                try:
                    return response.format(**kwargs)
                except (KeyError, ValueError):
                    return response
        
        # Fall back to stranger level
        if "stranger" in rel_responses:
            response = rel_responses["stranger"].get(response_type)
            if response:
                try:
                    return response.format(**kwargs)
                except (KeyError, ValueError):
                    return response
        
        # Ultimate fallbacks if nothing is configured
        fallback_responses = {
            "greeting": "Hello! How can I help you today?",
            "compliment": "Thank you! I appreciate that.",
            "mood": "I'm doing well, thank you for asking!",
            "goodbye": "Goodbye! Have a great day!",
            "thanks": "You're welcome!",
            "help": "I'm here to help you with whatever you need."
        }
        
        response = fallback_responses.get(response_type, "Hi there!")
        
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError):
            return response
    
    def get_activity_response(self, activity, result_type, **kwargs):
        """Get activity-specific response with comprehensive fallbacks"""
        activity_responses = self.persona.get("activity_responses", {})
        
        # If activity not found, provide generic fallbacks
        if activity not in activity_responses:
            generic_fallbacks = {
                "success": "Operation completed successfully!",
                "error": "I'm sorry, something went wrong with that request.",
                "timeout": "That operation took too long to complete.",
                "no_permission": "You don't have permission for that action.",
                "not_found": "I couldn't find what you're looking for.",
                "invalid_input": "Please check your input and try again."
            }
            response = generic_fallbacks.get(result_type, "Something happened!")
        else:
            response = activity_responses[activity].get(result_type)
            
            # If specific response not found, try generic fallbacks
            if response is None:
                generic_fallbacks = {
                    "success": "Operation completed successfully!",
                    "error": "I'm sorry, something went wrong.",
                    "timeout": "That took too long to complete.",
                    "no_permission": "You don't have permission for that.",
                    "not_found": "I couldn't find that.",
                    "invalid_input": "Please check your input."
                }
                response = generic_fallbacks.get(result_type, "Something happened!")
        
        # Handle list responses (like shutdown/restart messages)
        if isinstance(response, list):
            response = random.choice(response)
        
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError, AttributeError):
            # If formatting fails, return the unformatted response or a generic message
            if isinstance(response, str):
                return response
            else:
                return f"Completed {activity} operation."
    
    def get_speech_pattern(self, pattern_type):
        """Get random speech pattern element"""
        patterns = self.persona.get("speech_patterns", {}).get(pattern_type, [])
        if not patterns:
            return ""
        return random.choice(patterns)
    
    def format_error_response(self, error):
        """Format error with persona flair and robust fallbacks"""
        try:
            base_response = self.get_response("error")
            # Don't include the actual error details in user-facing messages for security
            return base_response
        except Exception:
            # Ultimate fallback if everything fails
            return "I apologize, but something went wrong. Please try again or contact support if the issue persists."
    
    def reload_persona(self):
        """Reload persona from file (useful for live updates)"""
        self.persona = self.load_persona()
        # Also reload the bot name service
        name_reload_success = self.bot_name_service.reload_bot_name()
        bot_name = self.get_name()
        
        if name_reload_success:
            return f"Persona reloaded: {bot_name}"
        else:
            return f"Persona reloaded: {bot_name} (name reload had issues, check logs)"    
   
 # Enhanced response methods for comprehensive personality management
    
    def get_error_response(self, error_type="general", **kwargs):
        """Get error response with fallback hierarchy"""
        try:
            # Try specific error type first
            error_responses = self.persona.get("error_responses", {})
            if error_type in error_responses:
                response = error_responses[error_type]
                return self._format_response(response, **kwargs)
            
            # Fall back to general error template
            response = self.get_response("error", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return "Something went wrong. Please try again."
    
    def get_confirmation_response(self, action="general", **kwargs):
        """Get confirmation response for actions"""
        try:
            # Try activity-specific confirmation
            confirmations = self.persona.get("activity_responses", {}).get("confirmations", {})
            if action in confirmations:
                response = confirmations[action]
                return self._format_response(response, **kwargs)
            
            # Fall back to general confirmation template
            response = self.get_response("confirmation", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return f"Are you sure you want to {action}?"
    
    def get_success_response(self, action="general", **kwargs):
        """Get success response for completed actions"""
        try:
            # Try activity-specific success message
            success_responses = self.persona.get("activity_responses", {}).get("success", {})
            if action in success_responses:
                response = success_responses[action]
                return self._format_response(response, **kwargs)
            
            # Fall back to general success template
            response = self.get_response("success", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return "Operation completed successfully!"
    
    def get_utility_response(self, utility_type, result_type="success", **kwargs):
        """Get utility-specific response (weather, time, dice, etc.)"""
        try:
            # Try specific utility response
            utility_responses = self.persona.get("activity_responses", {}).get("utilities", {})
            if utility_type in utility_responses:
                if isinstance(utility_responses[utility_type], dict):
                    response = utility_responses[utility_type].get(result_type)
                else:
                    response = utility_responses[utility_type]
                
                if response:
                    return self._format_response(response, **kwargs)
            
            # Fall back to general activity response
            return self.get_activity_response("utilities", result_type, **kwargs)
            
        except Exception:
            # Ultimate fallback based on result type
            fallbacks = {
                "success": f"Here's your {utility_type} result.",
                "error": f"Couldn't get {utility_type} right now.",
                "timeout": f"{utility_type.title()} request timed out."
            }
            return fallbacks.get(result_type, f"{utility_type.title()} operation completed.")
    
    def get_game_response(self, game_type, result_type, **kwargs):
        """Get game-specific response"""
        try:
            # Try specific game response
            game_responses = self.persona.get("activity_responses", {}).get("games", {})
            if game_type in game_responses:
                if isinstance(game_responses[game_type], dict):
                    response = game_responses[game_type].get(result_type)
                else:
                    response = game_responses[game_type]
                
                if response:
                    return self._format_response(response, **kwargs)
            
            # Fall back to general game response
            general_games = self.persona.get("activity_responses", {}).get("games", {})
            if result_type in general_games:
                response = general_games[result_type]
                return self._format_response(response, **kwargs)
            
            # Fall back to general activity response
            return self.get_activity_response("games", result_type, **kwargs)
            
        except Exception:
            # Ultimate fallback
            fallbacks = {
                "start": "Let's play!",
                "win": "You won!",
                "lose": "You lost!",
                "tie": "It's a tie!",
                "hint_low": "Too low!",
                "hint_high": "Too high!",
                "no_active_game": "No active game."
            }
            return fallbacks.get(result_type, "Game action completed.")
    
    def get_command_response(self, command_type, result_type="success", **kwargs):
        """Get command-specific response"""
        try:
            # Try specific command response
            command_responses = self.persona.get("activity_responses", {}).get("commands", {})
            if command_type in command_responses:
                if isinstance(command_responses[command_type], dict):
                    response = command_responses[command_type].get(result_type)
                else:
                    response = command_responses[command_type]
                
                if response:
                    return self._format_response(response, **kwargs)
            
            # Fall back to general activity response
            return self.get_activity_response("commands", result_type, **kwargs)
            
        except Exception:
            # Ultimate fallback
            return f"Command {command_type} completed."
    
    def get_validation_response(self, validation_type, **kwargs):
        """Get validation error response"""
        try:
            # Try specific validation response
            validation_responses = self.persona.get("response_templates", {}).get("validation", {})
            if validation_type in validation_responses:
                response = validation_responses[validation_type]
                return self._format_response(response, **kwargs)
            
            # Fall back to general invalid input response
            response = self.get_response("invalid_input", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return "Please check your input and try again."
    
    def get_permission_response(self, action="general", **kwargs):
        """Get permission denied response"""
        try:
            # Try specific permission response
            permission_responses = self.persona.get("response_templates", {}).get("permissions", {})
            if action in permission_responses:
                response = permission_responses[action]
                return self._format_response(response, **kwargs)
            
            # Fall back to general permission response
            response = self.get_response("no_permission", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return "You don't have permission for that action."
    
    def get_timeout_response(self, operation="operation", **kwargs):
        """Get timeout response"""
        try:
            # Try specific timeout response
            timeout_responses = self.persona.get("response_templates", {}).get("timeouts", {})
            if operation in timeout_responses:
                response = timeout_responses[operation]
                return self._format_response(response, **kwargs)
            
            # Fall back to general timeout response
            response = self.get_response("timeout", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return f"{operation.title()} timed out. Please try again."
    
    def get_api_error_response(self, service="service", **kwargs):
        """Get API error response"""
        try:
            # Try specific API error response
            api_responses = self.persona.get("error_responses", {}).get("api_errors", {})
            if service in api_responses:
                response = api_responses[service]
                return self._format_response(response, **kwargs)
            
            # Fall back to general API error
            response = self.get_error_response("api_error", **kwargs)
            return response
            
        except Exception:
            # Ultimate fallback
            return f"{service.title()} is currently unavailable."
    
    def _format_response(self, response, **kwargs):
        """Internal method to format responses with error handling"""
        try:
            # Handle list responses
            if isinstance(response, list):
                response = random.choice(response)
            
            # Format with provided kwargs
            if isinstance(response, str):
                return response.format(**kwargs)
            else:
                return str(response)
                
        except (KeyError, ValueError, AttributeError):
            # If formatting fails, return unformatted response
            if isinstance(response, str):
                return response
            else:
                return str(response)
    
    def validate_persona_completeness(self):
        """Validate persona card completeness and return report"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "completeness": 0.0,
            "missing_elements": [],
            "fallback_usage": {}
        }
        
        # Check required elements
        required_fields = ["name", "personality"]
        for field in required_fields:
            if field not in self.persona:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["valid"] = False
        
        # Check recommended elements
        recommended_fields = [
            "response_templates",
            "activity_responses", 
            "relationship_responses",
            "speech_patterns"
        ]
        
        present_recommended = 0
        for field in recommended_fields:
            if field in self.persona and self.persona[field]:
                present_recommended += 1
            else:
                validation_result["missing_elements"].append(field)
        
        validation_result["completeness"] = present_recommended / len(recommended_fields)
        
        # Check specific response categories
        response_categories = [
            "error", "success", "timeout", "invalid_input", 
            "no_permission", "not_found", "confirmation"
        ]
        
        missing_responses = []
        response_templates = self.persona.get("response_templates", {})
        for category in response_categories:
            if category not in response_templates:
                missing_responses.append(category)
        
        if missing_responses:
            validation_result["warnings"].append(f"Missing response templates: {', '.join(missing_responses)}")
        
        return validation_result
    
    def get_fallback_usage_report(self):
        """Generate report on fallback usage (would need tracking implementation)"""
        # This would require implementing usage tracking
        # For now, return a placeholder structure
        return {
            "total_responses": 0,
            "fallback_responses": 0,
            "fallback_percentage": 0.0,
            "most_used_fallbacks": [],
            "missing_response_types": []
        }

    # -----------------
    # Persona switching
    # -----------------
    def _project_root(self):
        """Return the project root (one level up from modules directory)."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def list_personas(self, personalities_dir="personality"):
        """List available persona files in the `personality/` directory.

        Returns list of persona basenames (without extension).
        """
        root = self._project_root()
        dir_path = os.path.join(root, personalities_dir)
        if not os.path.isdir(dir_path):
            return []

        files = glob.glob(os.path.join(dir_path, "*.json"))
        personas = [os.path.splitext(os.path.basename(f))[0] for f in sorted(files)]
        return personas

    def set_persona_by_name(self, name, personalities_dir="personality"):
        """Set the current persona by name (filename without .json) from `personality/`.

        Returns (success: bool, message: str).
        """
        root = self._project_root()
        candidate = os.path.join(root, personalities_dir, f"{name}.json")
        if not os.path.exists(candidate):
            return False, f"Persona file not found: {candidate}"

        # Update persona_file and reload
        self.persona_file = candidate
        self.persona = self.load_persona()

        # Inform bot name service
        try:
            self.bot_name_service.set_persona_card_path(self.persona_file)
            self.bot_name_service.reload_bot_name()
        except Exception:
            pass

        # Persist selection
        try:
            self._save_selected_persona(self.persona_file)
        except Exception:
            pass

        return True, f"Persona switched to '{name}'"

    def set_persona_file(self, file_path):
        """Set the persona by an explicit file path. Returns (success, message)."""
        if not os.path.exists(file_path):
            return False, f"Persona file not found: {file_path}"

        self.persona_file = file_path
        self.persona = self.load_persona()
        try:
            self.bot_name_service.set_persona_card_path(self.persona_file)
            self.bot_name_service.reload_bot_name()
        except Exception:
            pass

        try:
            self._save_selected_persona(self.persona_file)
        except Exception:
            pass

        return True, f"Persona file set to '{file_path}'"

    def get_current_persona_summary(self):
        """Return a short summary of the loaded persona."""
        try:
            return {
                "name": self.persona.get("name"),
                "personality": self.persona.get("personality"),
                "description": self.persona.get("description", "")
            }
        except Exception:
            return {"name": None, "personality": None, "description": ""}