"""
Bot Name Service - Centralized bot name management with persona card integration
"""
import json
import os
from .logger import BotLogger

# Constants
DEFAULT_PERSONA_FILE = "persona_card.json"
FALLBACK_BOT_NAME = "Discord AI"

class BotNameService:
    """
    Centralized service for managing the bot's display name.
    
    This service reads the bot name from the persona card configuration
    and provides a fallback to "Discord AI" when the persona card is
    unavailable or doesn't contain a name field.
    """
    
    def __init__(self, persona_card_path: str = DEFAULT_PERSONA_FILE):
        """
        Initialize the BotNameService.
        
        Args:
            persona_card_path: Path to the persona card JSON file
        """
        self.persona_card_path = persona_card_path
        self.logger = BotLogger.get_logger(__name__)
        self._cached_name = None
        
        # Load the initial name
        self._load_bot_name()
    
    def get_bot_name(self) -> str:
        """
        Get the current bot name.
        
        Returns the name from the persona card if available,
        otherwise returns the fallback name "Discord AI".
        
        Returns:
            str: The bot's display name
        """
        if self._cached_name is None:
            self._load_bot_name()
        
        return self._cached_name or self._get_fallback_name()
    
    def reload_bot_name(self) -> bool:
        """
        Reload the bot name from the persona card.
        
        This method refreshes the cached name by re-reading the persona card.
        Useful when the persona card has been updated and you want to apply
        the changes without restarting the application.
        
        Returns:
            bool: True if reload was successful, False if there were errors
        """
        try:
            old_name = self._cached_name
            self._load_bot_name()
            new_name = self._cached_name
            
            if old_name != new_name:
                self.logger.info(f"Bot name updated: '{old_name}' -> '{new_name}'")
            else:
                self.logger.info(f"Bot name reloaded (unchanged): '{new_name}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload bot name: {e}")
            return False
    
    def _load_bot_name(self) -> None:
        """
        Load the bot name from the persona card.
        
        This method attempts to read the persona card file and extract
        the name field. If any step fails, it falls back to the default name.
        """
        try:
            name = self._load_name_from_persona()
            if name:
                self._cached_name = name
                self.logger.info(f"Bot name loaded from persona card: '{name}'")
            else:
                self._cached_name = self._get_fallback_name()
                self.logger.info(f"Using fallback bot name: '{self._cached_name}'")
                
        except Exception as e:
            self._cached_name = self._get_fallback_name()
            self.logger.error(f"Error loading bot name, using fallback: {e}")
    
    def _load_name_from_persona(self) -> str:
        """
        Load the name field from the persona card file.
        
        Returns:
            str: The name from the persona card, or empty string if not found
            
        Raises:
            FileNotFoundError: If the persona card file doesn't exist
            json.JSONDecodeError: If the persona card contains invalid JSON
            KeyError: If the name field is missing (handled gracefully)
        """
        # Check if file exists
        if not os.path.exists(self.persona_card_path):
            self.logger.warning(f"Persona card not found at '{self.persona_card_path}'")
            return ""
        
        try:
            # Read and parse the persona card
            with open(self.persona_card_path, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
            
            # Extract the name field
            name = persona_data.get('name', '').strip()
            
            if not name:
                self.logger.info("Persona card exists but contains no name field or empty name")
                return ""
            
            return name
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in persona card '{self.persona_card_path}': {e}")
            raise
            
        except (IOError, OSError) as e:
            self.logger.error(f"Failed to read persona card '{self.persona_card_path}': {e}")
            raise
    
    def _get_fallback_name(self) -> str:
        """
        Get the fallback bot name.
        
        Returns:
            str: The fallback name "Discord AI"
        """
        return FALLBACK_BOT_NAME
    
    def get_persona_card_path(self) -> str:
        """
        Get the current persona card file path.
        
        Returns:
            str: Path to the persona card file
        """
        return self.persona_card_path
    
    def set_persona_card_path(self, new_path: str) -> bool:
        """
        Update the persona card file path and reload the name.
        
        Args:
            new_path: New path to the persona card file
            
        Returns:
            bool: True if the path was updated successfully
        """
        try:
            self.persona_card_path = new_path
            self.logger.info(f"Persona card path updated to: '{new_path}'")
            return self.reload_bot_name()
            
        except Exception as e:
            self.logger.error(f"Failed to update persona card path: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of the service."""
        return f"BotNameService(name='{self.get_bot_name()}', path='{self.persona_card_path}')"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"BotNameService(persona_card_path='{self.persona_card_path}', "
                f"cached_name='{self._cached_name}', fallback='{self._get_fallback_name()}')")