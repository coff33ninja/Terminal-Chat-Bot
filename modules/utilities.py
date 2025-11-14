"""Utility functions module - helpful tools with persona-driven responses and memory awareness"""
import random
import datetime
import requests
import json
from .persona_manager import PersonaManager
from .logger import BotLogger
from .ai_database import ai_db

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Constants for external APIs
OPENWEATHERMAP_API_URL = "http://api.openweathermap.org/data/2.5/weather"
RANDOM_FACTS_API_URL = "https://uselessfacts.jsph.pl/random.json"
JOKES_API_URL = "https://official-joke-api.appspot.com/random_joke"
CAT_FACTS_API_URL = "https://catfact.ninja/fact"

DEFAULT_TIMEOUT = 5
DEFAULT_API_KEY = "demo_key"  # Replace with real API key from .env
DEFAULT_DICE_SIDES = 6

class TsundereUtilities:
    def __init__(self, gemini_model, persona_file="persona_card.json"):
        self.model = gemini_model
        self.persona_manager = PersonaManager(persona_file)
    
    def _get_persona_response(self, category, subcategory, **format_kwargs):
        """Helper method to safely get persona responses from nested dictionaries"""
        try:
            responses = self.persona_manager.persona.get("activity_responses", {}).get(category, {}).get(subcategory, [])
            if responses:
                selected = random.choice(responses)
                return selected.format(**format_kwargs) if format_kwargs else selected
        except (KeyError, TypeError, ValueError) as e:
            print(f"⚠️ Error retrieving persona response: {e}")
        return None
    
    async def get_weather(self, location, user_id=None):
        """Get weather info using OpenWeatherMap API with memory awareness"""
        try:
            # Memory-aware location handling
            if not location and user_id:
                # Try to get user's previous weather locations
                try:
                    conversations = await ai_db.get_conversation_history(user_id, limit=20)
                    for conv in conversations:
                        if 'weather' in conv['message_content'].lower():
                            # Extract location from previous weather requests
                            words = conv['message_content'].split()
                            if 'weather' in words:
                                weather_idx = words.index('weather')
                                if weather_idx + 1 < len(words):
                                    location = ' '.join(words[weather_idx + 1:]).strip()
                                    if location:
                                        break
                except Exception as e:
                    logger.warning(f"Error retrieving weather history: {e}")
            
            if not isinstance(location, str) or not location.strip():
                logger.warning(f"Invalid weather location: {location}")
                return self.persona_manager.get_validation_response("location")
            
            logger.info(f"Fetching weather for location: {location}")
            params = {
                "q": location,
                "appid": DEFAULT_API_KEY,
                "units": "metric"
            }
            response = requests.get(OPENWEATHERMAP_API_URL, params=params, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                feels_like = data['main']['feels_like']
                
                weather_info = f"{temp}°C with {description}. Feels like {feels_like}°C"
                logger.info(f"Weather retrieved for {location}: {weather_info}")
                
                # Check if user has asked for this location before
                is_repeat_location = False
                if user_id:
                    try:
                        conversations = await ai_db.get_conversation_history(user_id, limit=10)
                        for conv in conversations:
                            if location.lower() in conv['message_content'].lower() and 'weather' in conv['message_content'].lower():
                                is_repeat_location = True
                                break
                    except Exception:
                        pass
                
                persona_msg = self._get_persona_response("utilities", "weather", 
                                                       location=location, 
                                                       weather_info=weather_info,
                                                       is_repeat=is_repeat_location)
                return persona_msg or f"Weather in {location}: {weather_info}"
            else:
                logger.warning(f"Weather API error for {location}: {response.status_code}")
                return self.persona_manager.get_utility_response("weather", "not_found", location=location)
                
        except requests.exceptions.Timeout:
            logger.error(f"Weather API timeout for location: {location}")
            return self.persona_manager.get_timeout_response("weather API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            print(f"⚠️ Weather API error: {e}")
            return self.persona_manager.get_api_error_response("weather")
    
    async def roll_dice(self, sides=DEFAULT_DICE_SIDES):
        """Roll dice with persona-driven attitude"""
        try:
            # Validate sides parameter (2-1000 range)
            if not isinstance(sides, int) or sides < 2 or sides > 1000:
                logger.warning(f"Invalid dice sides: {sides}")
                return self.persona_manager.get_validation_response("dice_sides")
            
            result = random.randint(1, sides)
            logger.info(f"Dice rolled: {result} out of {sides}")
            persona_msg = self._get_persona_response("utilities", "dice", result=result, sides=sides)
            return persona_msg or f"You rolled a {result}!"
        except (TypeError, ValueError) as e:
            logger.error(f"Dice roll error: {e}")
            return self.persona_manager.get_validation_response("dice_parameters")
    
    async def get_time(self):
        """Get current time with persona flair"""
        try:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            logger.debug(f"Current time retrieved: {time_str}")
            persona_msg = self._get_persona_response("utilities", "time", time=time_str)
            return persona_msg or f"The current time is {time_str}."
        except Exception as e:
            logger.error(f"Error getting time: {e}")
            print(f"⚠️ Error getting time: {e}")
            return self.persona_manager.get_utility_response("time", "error")
    
    async def flip_coin(self):
        """Flip a coin with persona attitude"""
        try:
            result = random.choice(["Heads", "Tails"])
            logger.info(f"Coin flipped: {result}")
            persona_msg = self._get_persona_response("utilities", "coin", result=result)
            return persona_msg or f"The coin landed on {result}!"
        except Exception as e:
            logger.error(f"Error flipping coin: {e}")
            print(f"⚠️ Error flipping coin: {e}")
            return self.persona_manager.get_utility_response("coin", "error")
    
    async def calculate(self, expression):
        """Safe calculator with persona-driven responses"""
        try:
            if not isinstance(expression, str):
                logger.warning("Non-string calculation expression received")
                return self.persona_manager.get_validation_response("math_expression")
            
            if len(expression) > 200:
                logger.warning(f"Expression too long: {len(expression)} characters")
                return self.persona_manager.get_validation_response("expression_length")
            
            # Simple safe evaluation for basic math
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                logger.warning(f"Invalid characters in expression: {expression}")
                return self.persona_manager.get_validation_response("invalid_characters")
            
            result = eval(expression)
            logger.info(f"Calculation successful: {expression} = {result}")
            persona_msg = self._get_persona_response("utilities", "calculate", expression=expression, result=result)
            return persona_msg or f"{expression} = {result}"
        except ZeroDivisionError:
            logger.warning("Division by zero attempted")
            return self.persona_manager.get_validation_response("division_by_zero")
        except (SyntaxError, ValueError) as e:
            logger.warning(f"Invalid expression: {e}")
            return self.persona_manager.get_validation_response("syntax_error", error=str(e))
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            print(f"⚠️ Calculation error: {e}")
            return self.persona_manager.get_utility_response("calculation", "error")
    
    async def get_random_fact(self, user_id=None):
        """Get a random fact using an API with memory awareness"""
        try:
            logger.info("Fetching random fact from API")
            
            # Memory-aware fact selection
            user_interests = []
            if user_id:
                try:
                    conversations = await ai_db.get_conversation_history(user_id, limit=30)
                    for conv in conversations:
                        message = conv['message_content'].lower()
                        # Simple interest detection
                        if any(word in message for word in ['space', 'astronomy', 'planet']):
                            user_interests.append('space')
                        if any(word in message for word in ['animal', 'cat', 'dog', 'wildlife']):
                            user_interests.append('animals')
                        if any(word in message for word in ['tech', 'computer', 'programming', 'code']):
                            user_interests.append('technology')
                except Exception as e:
                    logger.warning(f"Error analyzing user interests: {e}")
            
            response = requests.get(RANDOM_FACTS_API_URL, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                fact = data['text']
                logger.info(f"Random fact retrieved: {fact[:50]}...")
                
                # Add context if fact relates to user interests
                interest_context = ""
                if user_interests:
                    fact_lower = fact.lower()
                    for interest in set(user_interests):
                        if interest == 'space' and any(word in fact_lower for word in ['space', 'planet', 'star', 'universe']):
                            interest_context = "Since you seem interested in space, "
                            break
                        elif interest == 'animals' and any(word in fact_lower for word in ['animal', 'cat', 'dog', 'bird', 'fish']):
                            interest_context = "Since you like animals, "
                            break
                        elif interest == 'technology' and any(word in fact_lower for word in ['computer', 'tech', 'digital', 'internet']):
                            interest_context = "Since you're into tech, "
                            break
                
                persona_msg = self._get_persona_response("utilities", "fact", 
                                                       fact=fact, 
                                                       interest_context=interest_context)
                return persona_msg or f"{interest_context}Here's a fact: {fact}"
            else:
                logger.warning(f"Fact API error: {response.status_code}")
                return self.persona_manager.get_api_error_response("facts")
                
        except requests.exceptions.Timeout:
            logger.warning("Fact API request timed out")
            return self.persona_manager.get_timeout_response("facts API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Fact API error: {e}")
            print(f"⚠️ Fact API error: {e}")
            return self.persona_manager.get_api_error_response("facts")
    
    async def get_joke(self, user_id=None):
        """Get a random joke using an API with memory awareness"""
        try:
            logger.info("Fetching random joke from API")
            
            # Analyze user's joke preferences from history
            joke_feedback = {"positive": 0, "negative": 0}
            if user_id:
                try:
                    conversations = await ai_db.get_conversation_history(user_id, limit=20)
                    for i, conv in enumerate(conversations):
                        if 'joke' in conv['message_content'].lower():
                            # Look at the next message for reaction
                            if i > 0:
                                next_msg = conversations[i-1]['message_content'].lower()
                                if any(word in next_msg for word in ['haha', 'funny', 'good', 'lol', 'love']):
                                    joke_feedback["positive"] += 1
                                elif any(word in next_msg for word in ['bad', 'terrible', 'not funny', 'boring']):
                                    joke_feedback["negative"] += 1
                except Exception as e:
                    logger.warning(f"Error analyzing joke preferences: {e}")
            
            response = requests.get(JOKES_API_URL, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                setup = data['setup']
                punchline = data['punchline']
                logger.info("Joke retrieved")
                
                # Add context based on joke history
                joke_context = ""
                total_feedback = joke_feedback["positive"] + joke_feedback["negative"]
                if total_feedback > 2:
                    if joke_feedback["positive"] > joke_feedback["negative"]:
                        joke_context = "You seem to like my jokes, so here's another one! "
                    else:
                        joke_context = "Let me try a different style of humor... "
                
                persona_msg = self._get_persona_response("utilities", "joke", 
                                                       setup=setup, 
                                                       punchline=punchline,
                                                       joke_context=joke_context)
                return persona_msg or f"{joke_context}Here's a joke:\n{setup}\n{punchline}"
            else:
                logger.warning(f"Joke API error: {response.status_code}")
                return self.persona_manager.get_api_error_response("jokes")
                
        except requests.exceptions.Timeout:
            logger.warning("Joke API request timed out")
            return self.persona_manager.get_timeout_response("jokes API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Joke API error: {e}")
            print(f"⚠️ Joke API error: {e}")
            return self.persona_manager.get_api_error_response("jokes")
    
    async def get_cat_fact(self):
        """Get a random cat fact"""
        try:
            logger.info("Fetching random cat fact from API")
            response = requests.get(CAT_FACTS_API_URL, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                fact = data['fact']
                logger.info(f"Cat fact retrieved: {fact[:50]}...")
                persona_msg = self._get_persona_response("utilities", "cat_fact", fact=fact)
                return persona_msg or f"Here's a cat fact: {fact}"
            else:
                logger.warning(f"Cat fact API error: {response.status_code}")
                return self.persona_manager.get_api_error_response("cat_facts")
                
        except requests.exceptions.Timeout:
            logger.warning("Cat fact API request timed out")
            return self.persona_manager.get_timeout_response("cat facts API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Cat fact API error: {e}")
            print(f"⚠️ Cat fact API error: {e}")
            return self.persona_manager.get_api_error_response("cat_facts")
    
    async def get_usage_stats(self, user_id):
        """Get personalized usage statistics"""
        try:
            # Get all user conversations
            all_convs = await ai_db.get_conversation_history(user_id, limit=1000)
            
            if not all_convs:
                return self.persona_manager.get_utility_response("stats", "no_data")
            
            # Analyze usage patterns
            total_conversations = len(all_convs)
            
            # Most used commands
            commands = {}
            for conv in all_convs:
                if conv.get('context_data'):
                    try:
                        context = json.loads(conv['context_data']) if isinstance(conv['context_data'], str) else conv['context_data']
                        cmd = context.get('command_used', 'unknown')
                        commands[cmd] = commands.get(cmd, 0) + 1
                    except Exception:
                        pass
            
            # Time analysis
            if len(all_convs) > 1:
                first_conv = datetime.datetime.fromisoformat(all_convs[-1]['timestamp'].replace('Z', '+00:00'))
                last_conv = datetime.datetime.fromisoformat(all_convs[0]['timestamp'].replace('Z', '+00:00'))
                days_active = (last_conv - first_conv).days + 1
                avg_per_day = total_conversations / max(days_active, 1)
            else:
                days_active = 1
                avg_per_day = 1
            
            stats = f"""📊 Your Chat Statistics:
            
**Total Conversations:** {total_conversations}
**Days Active:** {days_active}
**Average per Day:** {avg_per_day:.1f}
            
**Most Used Commands:**"""
            
            if commands:
                sorted_commands = sorted(commands.items(), key=lambda x: x[1], reverse=True)[:3]
                for cmd, count in sorted_commands:
                    stats += f"\n• {cmd}: {count} times"
            else:
                stats += "\n• No command data available"
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in usage stats: {e}")
            return self.persona_manager.get_utility_response("stats", "error")