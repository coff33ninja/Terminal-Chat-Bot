"""
Social interaction module - relationship building with persona-driven responses
"""
import random
import json
import os
from .persona_manager import PersonaManager
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Constants for relationship tracking
USER_DATA_FILE = "user_relationships.json"
RELATIONSHIP_THRESHOLDS = {
    'close_friend': 50,
    'friend': 20,
    'acquaintance': 5,
    'stranger': 0
}

class TsundereSocial:
    def __init__(self, persona_file="persona_card.json"):
        self.user_data_file = USER_DATA_FILE
        self.user_data = self.load_user_data()
        self.persona_manager = PersonaManager(persona_file)
    
    def load_user_data(self):
        """Load user relationship data"""
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"User data loaded: {len(data)} users")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading user data: {e}")
                print(f"⚠️ Error loading user data: {e}")
                return {}
        logger.info("User data file not found, starting fresh")
        return {}
    
    def save_user_data(self):
        """Save user relationship data"""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2)
                logger.info(f"User data saved: {len(self.user_data)} users")
        except (IOError, OSError) as e:
            logger.error(f"Error saving user data: {e}")
            print(f"⚠️ Error saving user data: {e}")
    
    def get_user_relationship(self, user_id):
        """Get relationship level with user"""
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'interactions': 0,
                'compliments_given': 0,
                'relationship_level': 'stranger'
            }
        return self.user_data[user_id]
    
    def update_interaction(self, user_id):
        """Update interaction count and relationship level"""
        user_id = str(user_id)
        data = self.get_user_relationship(user_id)
        data['interactions'] += 1
        interactions = data['interactions']
        
        # Update relationship level based on interaction thresholds
        if interactions >= RELATIONSHIP_THRESHOLDS['close_friend']:
            data['relationship_level'] = 'close_friend'
        elif interactions >= RELATIONSHIP_THRESHOLDS['friend']:
            data['relationship_level'] = 'friend'
        elif interactions >= RELATIONSHIP_THRESHOLDS['acquaintance']:
            data['relationship_level'] = 'acquaintance'
        else:
            data['relationship_level'] = 'stranger'
        
        logger.info(f"User {user_id} interaction updated: {interactions} interactions, level: {data['relationship_level']}")
        self.save_user_data()
        return data
    
    async def get_relationship_status(self, user_id):
        """Get current relationship status"""
        data = self.get_user_relationship(user_id)
        level = data['relationship_level']
        interactions = data['interactions']
        
        base_response = self.persona_manager.get_relationship_response(level, "greeting")
        return f"{base_response} We've talked {interactions} times now..."
    
    async def give_compliment(self, user_id):
        """Give a compliment based on relationship level"""
        data = self.update_interaction(user_id)
        level = data['relationship_level']
        
        return self.persona_manager.get_relationship_response(level, "compliment")
    
    async def get_mood(self):
        """Get current mood using persona"""
        # Use a random relationship level for mood variety
        mood_levels = ['stranger', 'acquaintance', 'friend', 'close_friend']
        random_level = random.choice(mood_levels)
        return self.persona_manager.get_relationship_response(random_level, "mood")