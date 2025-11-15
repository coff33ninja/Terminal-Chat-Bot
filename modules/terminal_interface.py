"""
Terminal Interface - Handles terminal I/O, formatting, and user interaction
"""
import sys
import os
import shutil
from typing import Optional

# Try to import colorama for cross-platform color support
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback: no colors
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""


class TerminalInterface:
    """Manages terminal I/O and formatting"""
    
    def __init__(self, user_id: Optional[str] = None, bot_name: str = "AI Assistant"):
        """Initialize terminal interface
        
        Args:
            user_id: User identifier for the session
            bot_name: Name of the bot for display
        """
        self.user_id = user_id or "user"
        self.bot_name = bot_name
        self.terminal_width = self._get_terminal_width()
        self.colors_enabled = COLORS_AVAILABLE
        self.output_stream = sys.stdout
        
    def _get_terminal_width(self) -> int:
        """Get terminal width, default to 80 if unable to detect"""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80
    
    def display_welcome(self):
        """Display welcome message with bot name and quick help"""
        width = self.terminal_width
        border = "=" * width
        
        welcome_text = f"""
{border}
{self._center_text(f"Welcome to {self.bot_name} Terminal Chat!", width)}
{self._center_text("Type your message or use commands starting with !", width)}
{self._center_text("Type 'help' or '!help' for available commands", width)}
{self._center_text("Type 'exit' or 'quit' to leave", width)}
{border}
"""
        
        if self.colors_enabled:
            print(f"{Fore.CYAN}{Style.BRIGHT}{welcome_text}{Style.RESET_ALL}")
        else:
            print(welcome_text)
    
    def _center_text(self, text: str, width: int) -> str:
        """Center text within given width"""
        padding = (width - len(text)) // 2
        return " " * padding + text
    
    def display_prompt(self):
        """Display input prompt"""
        if self.colors_enabled:
            prompt = f"{Fore.GREEN}You: {Style.RESET_ALL}"
        else:
            prompt = "You: "
        print(prompt, end="", flush=True)
    
    def get_input(self) -> str:
        """Get user input from terminal
        
        Returns:
            User input string
        """
        try:
            return input().strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"
    
    def display_message(self, message: str, message_type: str = "normal"):
        """Display formatted message
        
        Args:
            message: Message text to display
            message_type: Type of message (normal, success, error, info, bot)
        """
        if message_type == "success":
            self._display_success(message)
        elif message_type == "error":
            self._display_error(message)
        elif message_type == "info":
            self._display_info(message)
        elif message_type == "bot":
            self._display_bot_message(message)
        else:
            print(message)
    
    def _display_success(self, message: str):
        """Display success message in green"""
        if self.colors_enabled:
            print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            print(f"✓ {message}")
    
    def _display_error(self, message: str):
        """Display error message in red"""
        if self.colors_enabled:
            print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        else:
            print(f"✗ {message}")
    
    def _display_info(self, message: str):
        """Display info message in blue"""
        if self.colors_enabled:
            print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ {message}")
    
    def _display_bot_message(self, message: str):
        """Display bot message with bot name prefix"""
        if self.colors_enabled:
            print(f"{Fore.CYAN}{self.bot_name}: {Style.RESET_ALL}{message}")
        else:
            print(f"{self.bot_name}: {message}")
    
    def display_typing(self):
        """Show typing indicator"""
        if self.colors_enabled:
            print(f"{Fore.YELLOW}⋯ {self.bot_name} is thinking...{Style.RESET_ALL}", end="", flush=True)
        else:
            print(f"⋯ {self.bot_name} is thinking...", end="", flush=True)
    
    def clear_typing(self):
        """Clear typing indicator"""
        # Move cursor to beginning of line and clear it
        print("\r" + " " * (len(self.bot_name) + 20) + "\r", end="", flush=True)
    
    def format_response(self, text: str, max_width: Optional[int] = None) -> str:
        """Format text with wrapping
        
        Args:
            text: Text to format
            max_width: Maximum width (defaults to terminal width - 10)
            
        Returns:
            Formatted text
        """
        if max_width is None:
            max_width = self.terminal_width - 10
        
        # Simple word wrapping
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_width:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    # Word is longer than max_width, just add it
                    lines.append(word)
                    current_length = 0
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return "\n".join(lines)
    
    def display_help(self, command: Optional[str] = None):
        """Display help information
        
        Args:
            command: Specific command to show help for (None for all commands)
        """
        if command:
            # Show help for specific command
            self._display_command_help(command)
        else:
            # Show all commands
            self._display_all_commands()
    
    def _display_all_commands(self):
        """Display all available commands"""
        help_text = f"""
{Fore.CYAN if self.colors_enabled else ''}╔══════════════════════════════════════════════════════════════╗
║                    Available Commands                        ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL if self.colors_enabled else ''}

{Fore.YELLOW if self.colors_enabled else ''}AI & Chat:{Style.RESET_ALL if self.colors_enabled else ''}
  !ai <question>        Ask the AI a question
  !ask <question>       Alias for !ai
  !chat <question>      Alias for !ai

{Fore.YELLOW if self.colors_enabled else ''}Utilities:{Style.RESET_ALL if self.colors_enabled else ''}
  !time                 Get current time
  !calc <expression>    Calculate math expression
  !dice [sides]         Roll dice (default 6 sides)
  !flip                 Flip a coin
  !weather <city>       Get weather information
  !fact                 Get a random fact
  !joke                 Get a random joke
  !catfact              Get a cat fact

{Fore.YELLOW if self.colors_enabled else ''}Games:{Style.RESET_ALL if self.colors_enabled else ''}
  !game guess [max]     Start number guessing game
  !guess <number>       Make a guess
  !rps <choice>         Play rock-paper-scissors
  !8ball <question>     Ask the magic 8-ball
  !trivia               Start a trivia question
  !answer <answer>      Answer trivia or game

{Fore.YELLOW if self.colors_enabled else ''}Search:{Style.RESET_ALL if self.colors_enabled else ''}
  !search <query>       Search the web
  !find <query>         Alias for !search

{Fore.YELLOW if self.colors_enabled else ''}Training:{Style.RESET_ALL if self.colors_enabled else ''}
  !training_stats       View training data statistics
  !training_export <fmt> Export data (openai/llama/alpaca)
  !train_model <size>   Train a custom model (tiny/small/medium/large)
  !list_models          List your trained models
  !training_requirements Show hardware requirements

{Fore.YELLOW if self.colors_enabled else ''}Memory (AI auto-learns about you):{Style.RESET_ALL if self.colors_enabled else ''}
  !memories             View what AI remembers about you
  !recall <key>         Retrieve specific memory
  !remember <key> <val> Manually add a memory
  !forget <key>         Delete a memory

{Fore.YELLOW if self.colors_enabled else ''}System:{Style.RESET_ALL if self.colors_enabled else ''}
  !help [command]       Show this help or help for specific command
  !memory [number]      View/set conversation memory (0=unlimited)
  !stats                View your usage statistics
  !mood                 Check bot's mood
  !relationship         Check your relationship level
  !compliment           Give the bot a compliment
  exit, quit            Exit the chat

{Fore.GREEN if self.colors_enabled else ''}💡 Tip: You can chat without commands - just type your message!{Style.RESET_ALL if self.colors_enabled else ''}
"""
        print(help_text)
    
    def _display_command_help(self, command: str):
        """Display help for a specific command"""
        command = command.lower().lstrip('!')
        
        command_help = {
            'ai': 'Ask the AI a question. Usage: !ai <your question>',
            'ask': 'Alias for !ai. Ask the AI a question.',
            'chat': 'Alias for !ai. Chat with the AI.',
            'time': 'Get the current time. Usage: !time',
            'calc': 'Calculate a math expression. Usage: !calc 2+2*5',
            'dice': 'Roll dice. Usage: !dice [sides] (default 6)',
            'flip': 'Flip a coin. Usage: !flip',
            'weather': 'Get weather for a city. Usage: !weather <city name>',
            'fact': 'Get a random fact. Usage: !fact',
            'joke': 'Get a random joke. Usage: !joke',
            'catfact': 'Get a cat fact. Usage: !catfact',
            'game': 'Start a game. Usage: !game guess [max_number]',
            'guess': 'Make a guess in number game. Usage: !guess <number>',
            'rps': 'Play rock-paper-scissors. Usage: !rps <rock|paper|scissors>',
            '8ball': 'Ask the magic 8-ball. Usage: !8ball <question>',
            'trivia': 'Start a trivia question. Usage: !trivia',
            'answer': 'Answer trivia or game. Usage: !answer <your answer>',
            'search': 'Search the web. Usage: !search <query>',
            'find': 'Alias for !search. Search the web.',
            'training_stats': 'View training data statistics. Usage: !training_stats',
            'training_export': 'Export training data. Usage: !training_export <openai|llama|alpaca>',
            'train_model': 'Train a custom AI model. Usage: !train_model <tiny|small|medium|large> [epochs]',
            'list_models': 'List your trained models. Usage: !list_models',
            'training_requirements': 'Show training hardware requirements. Usage: !training_requirements [size]',
            'memories': 'View what the AI remembers about you. Usage: !memories',
            'recall': 'Retrieve a specific memory. Usage: !recall <key>',
            'remember': 'Manually add a memory. Usage: !remember <key> <value>',
            'forget': 'Delete a memory. Usage: !forget <key>',
            'help': 'Show help. Usage: !help [command]',
            'memory': 'View/set conversation memory (0=unlimited). Usage: !memory [number]',
            'stats': 'View your usage statistics. Usage: !stats',
            'mood': 'Check the bot\'s current mood. Usage: !mood',
            'relationship': 'Check your relationship level. Usage: !relationship',
            'compliment': 'Give the bot a compliment. Usage: !compliment',
        }
        
        help_msg = command_help.get(command, f"No help available for '{command}'. Type !help to see all commands.")
        
        if self.colors_enabled:
            print(f"{Fore.CYAN}Help for '{command}':{Style.RESET_ALL}\n{help_msg}")
        else:
            print(f"Help for '{command}':\n{help_msg}")
    
    def display_separator(self):
        """Display a separator line"""
        print("-" * self.terminal_width)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def update_bot_name(self, new_name: str, refresh_welcome: bool = True):
        """Update the bot name used in prompts and optionally refresh the welcome banner."""
        try:
            self.bot_name = new_name
            if refresh_welcome:
                try:
                    self.clear_screen()
                except Exception:
                    pass
                try:
                    self.display_welcome()
                except Exception:
                    pass
        except Exception:
            pass
