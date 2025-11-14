"""
Games module - simplified for terminal use (single-player games)
Adapted from Discord bot games module
"""
import random
import asyncio
import json
from datetime import datetime

from .persona_manager import PersonaManager
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Game constants
DEFAULT_GUESSING_MAX = 100
MAGIC_8BALL_DELAY = 1
TRIVIA_TIMEOUT = 30

class TsundereGames:
    def __init__(self, persona_file="persona_card.json", api_manager=None, search=None, ai_db=None):
        self.active_games = {}  # {user_id: {game_data}}
        self.persona_manager = PersonaManager(persona_file)
        
        # Optional external services
        self.api_manager = api_manager
        self.search = search
        self.ai_db = ai_db
        self.knowledge_manager = None

    def set_api_manager(self, api_manager):
        self.api_manager = api_manager

    def set_search(self, search):
        self.search = search

    def set_ai_db(self, ai_db):
        self.ai_db = ai_db
    
    def set_knowledge_manager(self, km):
        self.knowledge_manager = km

    def _get_persona_response(self, category, subcategory, **format_kwargs):
        """Helper to get persona responses"""
        try:
            responses = self.persona_manager.persona.get("activity_responses", {}).get(category, {}).get(subcategory, [])
            if responses:
                selected = random.choice(responses) if isinstance(responses, list) else responses
                return selected.format(**format_kwargs) if format_kwargs else selected
        except (KeyError, TypeError, ValueError):
            pass
        return None

    async def start_number_guessing(self, user_id, max_number=DEFAULT_GUESSING_MAX):
        """Start a number guessing game"""
        try:
            if not isinstance(max_number, int) or max_number < 2 or max_number > 10000:
                return "Please choose a number between 2 and 10000."
            
            number = random.randint(1, max_number)
            self.active_games[user_id] = {
                'type': 'number_guess',
                'number': number,
                'max': max_number,
                'attempts': 0,
                'start_time': datetime.now()
            }
            
            logger.info(f"Number guessing game started for user {user_id}, max: {max_number}")
            persona_msg = self._get_persona_response("games", "start")
            start_text = persona_msg or "Let's play!"
            
            return f"{start_text} I picked a number between 1 and {max_number}. Try to guess it!"
            
        except Exception as e:
            logger.error(f"Error starting number guessing: {e}")
            return "Error starting game. Please try again."

    async def guess_number(self, user_id, guess):
        """Make a guess in the number guessing game"""
        try:
            if user_id not in self.active_games or self.active_games[user_id].get('type') != 'number_guess':
                return "You don't have an active number guessing game. Start one with !game guess"
            
            game = self.active_games[user_id]
            game['attempts'] += 1
            
            if guess == game['number']:
                attempts = game['attempts']
                del self.active_games[user_id]
                
                persona_msg = self._get_persona_response("games", "win")
                return f"{persona_msg or 'You won!'} You guessed {guess} in {attempts} attempts!"
            elif guess < game['number']:
                persona_msg = self._get_persona_response("games", "hint_low")
                return persona_msg or "Too low! Try a higher number."
            else:
                persona_msg = self._get_persona_response("games", "hint_high")
                return persona_msg or "Too high! Try a lower number."
                
        except Exception as e:
            logger.error(f"Error in guess_number: {e}")
            return "Error processing guess. Please try again."

    async def rock_paper_scissors(self, user_choice, user_id=None):
        """Play rock paper scissors"""
        try:
            choices = ['rock', 'paper', 'scissors']
            user_choice = user_choice.lower() if isinstance(user_choice, str) else None
            
            if user_choice not in choices:
                return "Please choose rock, paper, or scissors!"
            
            bot_choice = random.choice(choices)
            logger.info(f"RPS: user={user_choice}, bot={bot_choice}")
            
            if user_choice == bot_choice:
                persona_msg = self._get_persona_response("games", "tie", choice=bot_choice)
                return persona_msg or f"It's a tie! We both chose {bot_choice}."
            elif (user_choice == 'rock' and bot_choice == 'scissors') or \
                 (user_choice == 'paper' and bot_choice == 'rock') or \
                 (user_choice == 'scissors' and bot_choice == 'paper'):
                persona_msg = self._get_persona_response("games", "win")
                return f"{persona_msg or 'You won!'} You picked {user_choice}, I picked {bot_choice}."
            else:
                persona_msg = self._get_persona_response("games", "lose")
                return f"{persona_msg or 'I won!'} I picked {bot_choice}, you picked {user_choice}."
                
        except Exception as e:
            logger.error(f"Error in rock_paper_scissors: {e}")
            return "Error playing game. Please try again."

    async def magic_8ball(self, question):
        """Magic 8-ball with persona responses"""
        try:
            if not question or len(question.strip()) < 3:
                return "Please ask a proper question!"
            
            # Dramatic pause
            await asyncio.sleep(MAGIC_8BALL_DELAY)
            
            answers = self.persona_manager.persona.get("activity_responses", {}).get("magic_8ball", {}).get("answers", [
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
            ])
            
            answer = random.choice(answers)
            action = self.persona_manager.persona.get("activity_responses", {}).get("magic_8ball", {}).get("action", "*shakes magic 8-ball*")
            
            logger.info(f"Magic 8-ball answered: {answer}")
            return f"{action}\n🎱 {answer}"
            
        except Exception as e:
            logger.error(f"Error in magic_8ball: {e}")
            return "The magic 8-ball is unclear right now."

    async def trivia_game(self, user_id, source: str = None):
        """Start a trivia game"""
        try:
            # Try to get trivia from knowledge base first
            question_data = None
            
            if self.knowledge_manager:
                try:
                    results = await self.knowledge_manager.search_knowledge("", category="trivia", limit=10)
                    if results:
                        question_data = random.choice(results)
                except Exception as e:
                    logger.warning(f"Error getting trivia from knowledge base: {e}")
            
            # Fallback to AI-generated trivia
            if not question_data and self.api_manager:
                try:
                    prompt = "Generate a single trivia question with answer. Format: Question: [question]\nAnswer: [answer]"
                    response = await self.api_manager.generate_content(prompt)
                    
                    if response and "Question:" in response and "Answer:" in response:
                        parts = response.split("Answer:")
                        question = parts[0].replace("Question:", "").strip()
                        answer = parts[1].strip()
                        question_data = {'content': question, 'key_term': answer}
                except Exception as e:
                    logger.error(f"Error generating AI trivia: {e}")
            
            if not question_data:
                return "Sorry, I couldn't generate a trivia question right now."
            
            # Store the active trivia
            question = question_data.get('content', question_data.get('key_term', 'Unknown'))
            answer = question_data.get('key_term', question_data.get('content', 'Unknown'))
            
            self.active_games[user_id] = {
                'type': 'trivia',
                'question': question,
                'answer': answer,
                'start_time': datetime.now()
            }
            
            logger.info(f"Trivia started for user {user_id}")
            persona_msg = self._get_persona_response("games", "trivia_start", question=question)
            return persona_msg or f"Here's your trivia question:\n\n**{question}**\n\nUse !answer <your answer> to respond!"
            
        except Exception as e:
            logger.error(f"Error in trivia_game: {e}")
            return "Error starting trivia. Please try again."

    async def answer_trivia(self, user_id, answer):
        """Answer a trivia question"""
        try:
            if user_id not in self.active_games or self.active_games[user_id].get('type') != 'trivia':
                return "You don't have an active trivia game. Start one with !trivia"
            
            game = self.active_games[user_id]
            correct_answer = game['answer'].lower().strip()
            user_answer = answer.lower().strip()
            
            # Calculate time taken
            elapsed = (datetime.now() - game['start_time']).total_seconds()
            
            # Check if answer is correct (fuzzy matching)
            is_correct = user_answer == correct_answer or user_answer in correct_answer or correct_answer in user_answer
            
            del self.active_games[user_id]
            
            if is_correct:
                if elapsed < 5:
                    persona_msg = self._get_persona_response("games", "trivia_fast_correct", time=elapsed)
                    return persona_msg or f"Correct! You got it in {elapsed:.1f} seconds! That's fast!"
                else:
                    persona_msg = self._get_persona_response("games", "trivia_correct", time=elapsed)
                    return persona_msg or f"Correct! You got it in {elapsed:.1f} seconds!"
            else:
                persona_msg = self._get_persona_response("games", "trivia_wrong", answer=game['answer'])
                return persona_msg or f"Sorry, that's not correct. The answer was '{game['answer']}'."
                
        except Exception as e:
            logger.error(f"Error in answer_trivia: {e}")
            return "Error processing answer. Please try again."

    async def answer(self, user_id, answer):
        """Generic answer handler - routes to appropriate game"""
        try:
            if user_id not in self.active_games:
                return "You don't have an active game. Try !game guess, !trivia, or !rps"
            
            game_type = self.active_games[user_id].get('type')
            
            if game_type == 'trivia':
                return await self.answer_trivia(user_id, answer)
            elif game_type == 'number_guess':
                try:
                    guess_num = int(answer)
                    return await self.guess_number(user_id, guess_num)
                except ValueError:
                    return "Please provide a number for your guess."
            else:
                return "Unknown game type. Please start a new game."
                
        except Exception as e:
            logger.error(f"Error in answer: {e}")
            return "Error processing answer. Please try again."
