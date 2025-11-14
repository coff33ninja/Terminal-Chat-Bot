"""
Command Parser - Parses user input and routes to command handlers
"""
import shlex
from typing import Tuple, List, Dict, Any, Optional, Callable
from difflib import get_close_matches


class CommandParser:
    """Parses commands and routes to appropriate handlers"""
    
    def __init__(self, command_handlers: Dict[str, Callable] = None):
        """Initialize command parser
        
        Args:
            command_handlers: Dictionary mapping command names to handler functions
        """
        self.command_handlers = command_handlers or {}
        self.command_aliases = self._build_aliases()
        self.command_prefix = '!'
    
    def _build_aliases(self) -> Dict[str, str]:
        """Build command alias mapping
        
        Returns:
            Dictionary mapping aliases to canonical command names
        """
        aliases = {
            # AI commands
            'ask': 'ai',
            'chat': 'ai',
            
            # Search commands
            'find': 'search',
            'google': 'search',
            'web': 'search',
            
            # Game commands
            'rock': 'rps',
            'paper': 'rps',
            'scissors': 'rps',
            'g': 'answer',
            
            # Help commands
            'commands': 'help',
            '?': 'help',
            
            # Stats commands
            'mystats': 'stats',
            'usage': 'stats',
        }
        return aliases
    
    def register_handler(self, command: str, handler: Callable):
        """Register a command handler
        
        Args:
            command: Command name
            handler: Handler function
        """
        self.command_handlers[command] = handler
    
    def parse(self, input_text: str) -> Tuple[str, List[str], Dict[str, Any]]:
        """Parse input into command, args, and kwargs
        
        Args:
            input_text: User input text
            
        Returns:
            Tuple of (command, args, kwargs)
        """
        if not input_text:
            return ('', [], {})
        
        input_text = input_text.strip()
        
        # Check if it's a command
        if not self.is_command(input_text):
            # Not a command, treat as plain text (AI chat)
            return ('chat', [input_text], {})
        
        # Remove command prefix
        input_text = input_text[len(self.command_prefix):]
        
        # Parse using shlex to handle quoted strings
        try:
            parts = shlex.split(input_text)
        except ValueError:
            # If shlex fails, fall back to simple split
            parts = input_text.split()
        
        if not parts:
            return ('', [], {})
        
        # First part is the command
        command = parts[0].lower()
        
        # Resolve aliases
        command = self.command_aliases.get(command, command)
        
        # Rest are arguments
        args = parts[1:] if len(parts) > 1 else []
        
        # For now, we don't parse kwargs (could be added later)
        kwargs = {}
        
        return (command, args, kwargs)
    
    def is_command(self, input_text: str) -> bool:
        """Check if input is a command
        
        Args:
            input_text: User input text
            
        Returns:
            True if input starts with command prefix
        """
        return input_text.startswith(self.command_prefix)
    
    def get_command_handler(self, command: str) -> Optional[Callable]:
        """Get handler for command
        
        Args:
            command: Command name
            
        Returns:
            Handler function or None if not found
        """
        # Check direct command
        if command in self.command_handlers:
            return self.command_handlers[command]
        
        # Check aliases
        canonical = self.command_aliases.get(command)
        if canonical and canonical in self.command_handlers:
            return self.command_handlers[canonical]
        
        return None
    
    def suggest_command(self, invalid_command: str) -> Optional[str]:
        """Suggest similar valid command for typo
        
        Args:
            invalid_command: Invalid command entered by user
            
        Returns:
            Suggested command or None
        """
        # Get all valid commands (including aliases)
        all_commands = list(self.command_handlers.keys()) + list(self.command_aliases.keys())
        
        # Find close matches
        matches = get_close_matches(invalid_command, all_commands, n=1, cutoff=0.6)
        
        if matches:
            suggested = matches[0]
            # If it's an alias, resolve to canonical name
            return self.command_aliases.get(suggested, suggested)
        
        return None
    
    def validate_args(self, command: str, args: List[str], min_args: int = 0, max_args: int = None) -> Tuple[bool, str]:
        """Validate argument count for command
        
        Args:
            command: Command name
            args: List of arguments
            min_args: Minimum required arguments
            max_args: Maximum allowed arguments (None for unlimited)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        arg_count = len(args)
        
        if arg_count < min_args:
            if min_args == 1:
                return (False, f"Command '{command}' requires at least 1 argument.")
            else:
                return (False, f"Command '{command}' requires at least {min_args} arguments.")
        
        if max_args is not None and arg_count > max_args:
            if max_args == 0:
                return (False, f"Command '{command}' doesn't take any arguments.")
            elif max_args == 1:
                return (False, f"Command '{command}' takes at most 1 argument.")
            else:
                return (False, f"Command '{command}' takes at most {max_args} arguments.")
        
        return (True, "")
    
    def get_all_commands(self) -> List[str]:
        """Get list of all available commands
        
        Returns:
            List of command names
        """
        return sorted(self.command_handlers.keys())
    
    def get_command_aliases(self, command: str) -> List[str]:
        """Get aliases for a command
        
        Args:
            command: Command name
            
        Returns:
            List of aliases
        """
        aliases = []
        for alias, canonical in self.command_aliases.items():
            if canonical == command:
                aliases.append(alias)
        return aliases
    
    def format_command_usage(self, command: str, usage: str, description: str) -> str:
        """Format command usage information
        
        Args:
            command: Command name
            usage: Usage pattern
            description: Command description
            
        Returns:
            Formatted usage string
        """
        aliases = self.get_command_aliases(command)
        alias_text = f" (aliases: {', '.join(aliases)})" if aliases else ""
        
        return f"""
Command: !{command}{alias_text}
Usage: {usage}
Description: {description}
"""
