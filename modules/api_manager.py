"""
API Key Manager for rotating Gemini API keys and managing rate limits
"""
import os
import random
import time
import asyncio
import google.generativeai as genai
from typing import List, Optional
import json
from datetime import datetime, timedelta
import concurrent.futures
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Constants for API management
DEFAULT_RATE_LIMIT_PER_KEY = 60  # Requests per minute
DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash'
API_REQUEST_TIMEOUT = 30.0  # seconds
API_GENERATION_TIMEOUT = 15.0  # seconds for faster responses
KEY_COOLDOWN_DURATION = 10  # minutes
ERROR_COOLDOWN_DURATION = 5  # minutes
ERROR_THRESHOLD = 3  # errors before cooldown
MAX_RETRIES = 3

class GeminiAPIManager:
    def __init__(self, api_keys: List[str] = None, rate_limit_per_key: int = DEFAULT_RATE_LIMIT_PER_KEY):
        """
        Initialize the API manager with rotating keys
        
        Args:
            api_keys: List of Gemini API keys to rotate through
            rate_limit_per_key: Requests per minute per key (default: 60)
        """
        self.api_keys = api_keys or []
        self.rate_limit_per_key = rate_limit_per_key
        self.current_key_index = 0
        self.key_usage = {}  # Track usage per key
        self.key_cooldowns = {}  # Track cooldown periods
        self.models = {}  # Cache models for each key
        
        # Load API keys from environment if not provided
        if not self.api_keys:
            self._load_keys_from_env()
        
        # Initialize usage tracking
        self._init_usage_tracking()
        
        # Set up the first key
        if self.api_keys:
            self._configure_current_key()
    
    def _load_keys_from_env(self):
        """Load API keys from environment variables"""
        # Primary key
        primary_key = os.getenv('GEMINI_API_KEY')
        if primary_key:
            self.api_keys.append(primary_key)
        
        # Additional keys (GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
        i = 2
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                self.api_keys.append(key)
                i += 1
            else:
                break
        
        logger.info(f"Loaded {len(self.api_keys)} Gemini API key(s)")
    
    def _init_usage_tracking(self):
        """Initialize usage tracking for all keys"""
        for i, key in enumerate(self.api_keys):
            self.key_usage[i] = {
                'requests': 0,
                'last_reset': datetime.now(),
                'errors': 0,
                'last_error': None
            }
            self.key_cooldowns[i] = None
    
    def _configure_current_key(self):
        """Configure the current API key"""
        if not self.api_keys:
            logger.warning("No API keys available yet")
            return None
        
        current_key = self.api_keys[self.current_key_index]
        genai.configure(api_key=current_key)
        
        # Create or get cached model
        if self.current_key_index not in self.models:
            self.models[self.current_key_index] = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
        
        return self.models[self.current_key_index]
    
    def get_current_model(self):
        """Get the current Gemini model"""
        model = self._configure_current_key()
        if model is None:
            logger.warning("No API keys loaded, model will be None until configuration is validated")
        return model
        """Get the current Gemini model"""
        return self._configure_current_key()
    
    def _is_key_available(self, key_index: int) -> bool:
        """Check if a key is available for use"""
        now = datetime.now()
        
        # Check if key is in cooldown
        if self.key_cooldowns[key_index]:
            if now < self.key_cooldowns[key_index]:
                return False
            else:
                # Cooldown expired, clear it
                self.key_cooldowns[key_index] = None
        
        # Check rate limit
        usage = self.key_usage[key_index]
        time_since_reset = now - usage['last_reset']
        
        # Reset counter if more than a minute has passed
        if time_since_reset >= timedelta(minutes=1):
            usage['requests'] = 0
            usage['last_reset'] = now
        
        # Check if under rate limit
        return usage['requests'] < self.rate_limit_per_key
    
    def _rotate_to_next_key(self) -> bool:
        """Rotate to the next available key"""
        if len(self.api_keys) <= 1:
            return False
        
        original_index = self.current_key_index
        start_time = time.time()
        
        # Try each key once
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            if self._is_key_available(self.current_key_index):
                rotation_time = time.time() - start_time
                logger.info(f"API key rotated to #{self.current_key_index + 1} (took {rotation_time:.2f}s)")
                print(f"🔄 Rotated to API key #{self.current_key_index + 1} (took {rotation_time:.2f}s)")
                self._configure_current_key()
                return True
        
        # No keys available, revert to original
        self.current_key_index = original_index
        logger.warning("No available API keys for rotation")
        return False
    
    def _record_request(self, success: bool = True, error: str = None):
        """Record a request for the current key"""
        usage = self.key_usage[self.current_key_index]
        usage['requests'] += 1
        
        if success:
            logger.info(f"API request successful on key #{self.current_key_index + 1}")
        else:
            usage['errors'] += 1
            usage['last_error'] = error
            logger.error(f"API error on key #{self.current_key_index + 1}: {error}")
            
            # If too many errors, put key in cooldown
            if usage['errors'] >= ERROR_THRESHOLD:
                cooldown_time = datetime.now() + timedelta(minutes=ERROR_COOLDOWN_DURATION)
                self.key_cooldowns[self.current_key_index] = cooldown_time
                logger.warning(f"API key #{self.current_key_index + 1} in cooldown due to {usage['errors']} errors")
                print(f"⚠️ API key #{self.current_key_index + 1} in cooldown due to errors")
    
    async def generate_content_stream(self, prompt: str, callback=None, max_retries: int = MAX_RETRIES):
        """
        Generate content with streaming and automatic key rotation
        
        Args:
            prompt: The prompt to send to Gemini
            callback: Optional callback function to receive text chunks as they arrive
            max_retries: Maximum number of retries across all keys
            
        Yields:
            Text chunks as they are generated
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Check if current key is available
                if not self._is_key_available(self.current_key_index):
                    if not self._rotate_to_next_key():
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        else:
                            error_msg = "All API keys are rate limited or in cooldown"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                
                # Get current model
                model = self.get_current_model()
                
                # Run streaming in thread pool
                loop = asyncio.get_event_loop()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    try:
                        # Generate streaming response
                        future = loop.run_in_executor(
                            executor,
                            lambda: model.generate_content(prompt, stream=True)
                        )
                        
                        response = await asyncio.wait_for(future, timeout=API_REQUEST_TIMEOUT)
                        
                        # Stream the chunks
                        full_text = ""
                        for chunk in response:
                            if chunk.text:
                                full_text += chunk.text
                                if callback:
                                    callback(chunk.text)
                                yield chunk.text
                        
                        # Record successful request
                        self._record_request(success=True)
                        logger.info("Streaming content generation successful")
                        return
                        
                    except asyncio.TimeoutError:
                        error_msg = "Request timed out"
                        self._record_request(success=False, error=error_msg)
                        logger.warning(f"API request timeout on key #{self.current_key_index + 1}")
                        last_error = error_msg
                        
                        if not self._rotate_to_next_key() and attempt < max_retries - 1:
                            await asyncio.sleep(1)
                        continue
            
            except Exception as e:
                error_msg = str(e)
                self._record_request(success=False, error=error_msg)
                last_error = error_msg
                
                if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                    cooldown_time = datetime.now() + timedelta(minutes=KEY_COOLDOWN_DURATION)
                    self.key_cooldowns[self.current_key_index] = cooldown_time
                    logger.warning(f"API key #{self.current_key_index + 1} hit rate limit")
                    
                    if not self._rotate_to_next_key() and attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    continue
                
                if attempt < max_retries - 1:
                    if len(self.api_keys) > 1:
                        self._rotate_to_next_key()
                    await asyncio.sleep(1)
                    continue
                else:
                    break
        
        logger.error(f"All streaming attempts failed. Last error: {last_error}")
        yield None
    
    async def generate_content(self, prompt: str, max_retries: int = MAX_RETRIES, stream: bool = False) -> Optional[str]:
        """
        Generate content with automatic key rotation and retry logic
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retries across all keys
            stream: If True, returns an async generator for streaming
            
        Returns:
            Generated content or None if all attempts failed
        """
        if stream:
            # Return async generator for streaming
            return self.generate_content_stream(prompt, max_retries=max_retries)
        
        # Non-streaming mode (original behavior)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Check if current key is available
                if not self._is_key_available(self.current_key_index):
                    if not self._rotate_to_next_key():
                        # No keys available, wait a bit and try again
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        else:
                            error_msg = "All API keys are rate limited or in cooldown"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                
                # Get current model and generate content
                model = self.get_current_model()
                
                # Run the blocking API call in a thread pool with timeout
                loop = asyncio.get_event_loop()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    try:
                        response = await asyncio.wait_for(
                            loop.run_in_executor(executor, model.generate_content, prompt),
                            timeout=API_REQUEST_TIMEOUT
                        )
                        
                        # Record successful request
                        self._record_request(success=True)
                        logger.info("Content generation successful")
                        
                        return response.text
                        
                    except asyncio.TimeoutError:
                        error_msg = "Request timed out"
                        self._record_request(success=False, error=error_msg)
                        logger.warning(f"API request timeout on key #{self.current_key_index + 1}")
                        last_error = error_msg
                        
                        # Try next key on timeout
                        if not self._rotate_to_next_key() and attempt < max_retries - 1:
                            await asyncio.sleep(1)
                        continue
            
            except Exception as e:
                error_msg = str(e)
                self._record_request(success=False, error=error_msg)
                last_error = error_msg
                
                # Check if it's a rate limit error
                if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                    # Put current key in cooldown and try next
                    cooldown_time = datetime.now() + timedelta(minutes=KEY_COOLDOWN_DURATION)
                    self.key_cooldowns[self.current_key_index] = cooldown_time
                    logger.warning(f"API key #{self.current_key_index + 1} hit rate limit, cooling down")
                    print(f"⚠️ API key #{self.current_key_index + 1} hit rate limit, cooling down")
                    
                    if not self._rotate_to_next_key() and attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    continue
                
                # For other errors, try next key or retry
                if attempt < max_retries - 1:
                    if len(self.api_keys) > 1:
                        self._rotate_to_next_key()
                    await asyncio.sleep(1)
                    continue
                else:
                    break
        
        # All attempts failed
        logger.error(f"All API attempts failed. Last error: {last_error}")
        print(f"❌ All API attempts failed. Last error: {last_error}")
        return None
    
    def get_status(self) -> dict:
        """Get status of all API keys"""
        status = {
            'total_keys': len(self.api_keys),
            'current_key': self.current_key_index + 1,
            'keys': [],
            'status_json': json.dumps({'timestamp': datetime.now().isoformat()})
        }
        
        logger.info(f"API status: {len(self.api_keys)} keys, current: #{self.current_key_index + 1}")
        
        now = datetime.now()
        
        for i, key in enumerate(self.api_keys):
            usage = self.key_usage[i]
            cooldown = self.key_cooldowns[i]
            
            key_status = {
                'key_number': i + 1,
                'is_current': i == self.current_key_index,
                'requests_this_minute': usage['requests'],
                'rate_limit': self.rate_limit_per_key,
                'errors': usage['errors'],
                'available': self._is_key_available(i),
                'in_cooldown': cooldown is not None and now < cooldown,
                'cooldown_expires': cooldown.isoformat() if cooldown and now < cooldown else None,
                'key_id': usage.get('key_id', random.randint(1000, 9999))
            }
            
            status['keys'].append(key_status)
        
        return status
    
    def add_api_key(self, api_key: str):
        """Add a new API key to the rotation"""
        if api_key not in self.api_keys:
            # Generate a random ID for tracking
            key_id = random.randint(1000, 9999)
            self.api_keys.append(api_key)
            key_index = len(self.api_keys) - 1
            
            # Initialize tracking for new key
            self.key_usage[key_index] = {
                'requests': 0,
                'last_reset': datetime.now(),
                'errors': 0,
                'last_error': None,
                'key_id': key_id
            }
            self.key_cooldowns[key_index] = None
            
            logger.info(f"Added new API key #{key_index + 1} (ID: {key_id})")
            print(f"➕ Added new API key #{key_index + 1} (ID: {key_id})")
            return True
        return False
    
    def remove_api_key(self, key_index: int):
        """Remove an API key from rotation"""
        if 0 <= key_index < len(self.api_keys):
            if len(self.api_keys) <= 1:
                logger.error("Cannot remove the last API key")
                raise ValueError("Cannot remove the last API key")
            
            # Remove key and associated data
            removed_key = self.api_keys.pop(key_index)
            removed_usage = self.key_usage.get(key_index, {})
            removal_msg = f"Removed API key #{key_index + 1} (ending in ...{removed_key[-8:]}) with {removed_usage.get('requests', 0)} requests and {removed_usage.get('errors', 0)} errors"
            logger.info(removal_msg)
            print(f"🗑️ {removal_msg}")
            
            del self.key_usage[key_index]
            del self.key_cooldowns[key_index]
            if key_index in self.models:
                del self.models[key_index]
            
            # Adjust current key index if necessary
            if self.current_key_index >= key_index:
                self.current_key_index = max(0, self.current_key_index - 1)
            
            # Reindex remaining keys
            self._reindex_keys()
            
            return True
        return False
    
    def _reindex_keys(self):
        """Reindex key tracking after removal"""
        new_usage = {}
        new_cooldowns = {}
        new_models = {}
        
        for new_index, old_index in enumerate(sorted(self.key_usage.keys())):
            if old_index < len(self.api_keys):
                new_usage[new_index] = self.key_usage[old_index]
                new_cooldowns[new_index] = self.key_cooldowns[old_index]
                if old_index in self.models:
                    new_models[new_index] = self.models[old_index]
        
        self.key_usage = new_usage
        self.key_cooldowns = new_cooldowns
        self.models = new_models