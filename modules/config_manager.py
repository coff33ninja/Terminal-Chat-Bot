"""
Configuration Manager - Centralized bot configuration and constants
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration Constants
BOT_COMMAND_PREFIX = '!'

# API Configuration
DEFAULT_RATE_LIMIT = 60  # requests per minute
DEFAULT_API_TIMEOUT = 30  # seconds
DEFAULT_GENERATION_TIMEOUT = 15  # seconds

# Terminal Bot Settings (no Discord-specific config needed)

# API Keys
GEMINI_API_KEYS = []

# Search Configuration Constants
SEARCH_INDICATORS = [
    # Current events and news
    'latest', 'recent', 'current', 'news', 'today', 'this year', '2024', '2025',
    # Specific information requests
    'what is', 'who is', 'where is', 'when did', 'how to', 'tutorial',
    # Product/company/technology queries
    'price', 'cost', 'buy', 'download', 'install', 'specs', 'review',
    # Location-based queries
    'near me', 'location', 'address', 'directions',
    # Factual lookups
    'definition', 'meaning', 'explain', 'about',
    # Technology and tools
    'github', 'documentation', 'docs', 'api', 'library', 'framework',
    # Specific brands/products
    'esp32', 'arduino', 'raspberry pi', 'python', 'javascript', 'react', 'vue',
    'nvidia', 'amd', 'intel', 'microsoft', 'google', 'apple', 'amazon',
]

QUESTION_STARTERS = ['what', 'who', 'where', 'when', 'how', 'why']
SEARCH_RELEVANT_KEYWORDS = ['company', 'website', 'service', 'app', 'software', 'tool']

# Message Configuration
DEFAULT_EMBED_COLOR = 0x9C27B0  # Purple
MAX_EMBED_DESCRIPTION_LENGTH = 4096
MAX_FIELD_VALUE_LENGTH = 1024

# File Paths
PERSONA_FILE = "persona_card.json"
USER_DATA_FILE = "user_relationships.json"

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

class ConfigManager:
    """Centralized configuration management for the bot"""
    
    def __init__(self, validate=False):
        """
        Initialize configuration from environment
        
        Args:
            validate: If True, validate configuration immediately. If False, defer validation.
        """
        self._load_gemini_keys()
        if validate:
            self.validate_config()
    
    def _load_gemini_keys(self):
        """Load Gemini API keys from environment"""
        global GEMINI_API_KEYS
        
        # Only load if not already loaded
        if GEMINI_API_KEYS:
            return
        
        # Primary key
        primary_key = os.getenv('GEMINI_API_KEY')
        if primary_key:
            GEMINI_API_KEYS.append(primary_key)
        
        # Additional keys (GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
        i = 2
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                GEMINI_API_KEYS.append(key)
                i += 1
            else:
                break
    
    def validate_config(self):
        """Validate required configuration"""
        # Reload the environment variables in case they were set after initialization
        load_dotenv()
        
        # Terminal bot only needs API keys, no Discord token required
        if not GEMINI_API_KEYS:
            raise ValueError("At least one GEMINI_API_KEY environment variable is required")
    
    @staticmethod
    def should_search_web(question):
        """
        Determine if a question would benefit from web search
        
        Args:
            question: The user's question/input
            
        Returns:
            bool: True if web search is recommended
        """
        question_lower = question.lower()
        
        # Check for search indicators
        for indicator in SEARCH_INDICATORS:
            if indicator in question_lower:
                return True
        
        # Check for question words that often need current info
        first_word = question_lower.split()[0] if question_lower.split() else ''
        
        if first_word in QUESTION_STARTERS:
            # Additional checks for questions that likely need web search
            if any(word in question_lower for word in SEARCH_RELEVANT_KEYWORDS):
                return True
        
        return False
    
    @staticmethod
    def get_gemini_keys():
        """Get list of configured Gemini API keys"""
        return GEMINI_API_KEYS.copy()
    

