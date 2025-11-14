"""
Response Formatter - Terminal-specific response formatting
"""
import textwrap
from typing import List

# Try to import colorama for cross-platform color support
try:
    from colorama import Fore, Back, Style
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""


class ResponseFormatter:
    """Formats responses for terminal display"""
    
    @staticmethod
    def format_success(message: str) -> str:
        """Format success message with green color
        
        Args:
            message: Success message text
            
        Returns:
            Formatted success message
        """
        if COLORS_AVAILABLE:
            return f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}"
        return f"✓ {message}"
    
    @staticmethod
    def format_error(message: str) -> str:
        """Format error message with red color
        
        Args:
            message: Error message text
            
        Returns:
            Formatted error message
        """
        if COLORS_AVAILABLE:
            return f"{Fore.RED}✗ Error: {message}{Style.RESET_ALL}"
        return f"✗ Error: {message}"
    
    @staticmethod
    def format_info(message: str) -> str:
        """Format info message with blue color
        
        Args:
            message: Info message text
            
        Returns:
            Formatted info message
        """
        if COLORS_AVAILABLE:
            return f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}"
        return f"ℹ {message}"
    
    @staticmethod
    def format_warning(message: str) -> str:
        """Format warning message with yellow color
        
        Args:
            message: Warning message text
            
        Returns:
            Formatted warning message
        """
        if COLORS_AVAILABLE:
            return f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}"
        return f"⚠ {message}"
    
    @staticmethod
    def format_box(title: str, content: str, width: int = 60) -> str:
        """Create bordered box for content
        
        Args:
            title: Box title
            content: Box content
            width: Box width
            
        Returns:
            Formatted box with border
        """
        # Ensure width is reasonable
        width = max(20, min(width, 100))
        
        # Create border
        top_border = "╔" + "═" * (width - 2) + "╗"
        bottom_border = "╚" + "═" * (width - 2) + "╝"
        
        # Format title
        title_text = f" {title} "
        title_padding = (width - len(title_text) - 2) // 2
        title_line = "║" + " " * title_padding + title_text + " " * (width - len(title_text) - title_padding - 2) + "║"
        
        # Format content lines
        content_lines = []
        for line in content.split('\n'):
            wrapped = textwrap.wrap(line, width - 4) if line else ['']
            for wrapped_line in wrapped:
                padding = width - len(wrapped_line) - 4
                content_lines.append(f"║ {wrapped_line}{' ' * padding} ║")
        
        # Combine all parts
        box_lines = [top_border, title_line] + content_lines + [bottom_border]
        
        if COLORS_AVAILABLE:
            return f"{Fore.CYAN}{chr(10).join(box_lines)}{Style.RESET_ALL}"
        return "\n".join(box_lines)
    
    @staticmethod
    def format_list(items: List[str], bullet: str = "•") -> str:
        """Format bulleted list
        
        Args:
            items: List of items
            bullet: Bullet character
            
        Returns:
            Formatted list
        """
        if not items:
            return ""
        
        formatted_items = [f"{bullet} {item}" for item in items]
        return "\n".join(formatted_items)
    
    @staticmethod
    def format_numbered_list(items: List[str]) -> str:
        """Format numbered list
        
        Args:
            items: List of items
            
        Returns:
            Formatted numbered list
        """
        if not items:
            return ""
        
        formatted_items = [f"{i+1}. {item}" for i, item in enumerate(items)]
        return "\n".join(formatted_items)
    
    @staticmethod
    def format_table(headers: List[str], rows: List[List[str]]) -> str:
        """Format simple table
        
        Args:
            headers: Table headers
            rows: Table rows
            
        Returns:
            Formatted table
        """
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Create separator
        separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
        
        # Format header
        header_row = "|" + "|".join([f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)]) + "|"
        
        # Format rows
        data_rows = []
        for row in rows:
            row_str = "|" + "|".join([f" {str(cell):<{col_widths[i]}} " for i, cell in enumerate(row)]) + "|"
            data_rows.append(row_str)
        
        # Combine all parts
        table_lines = [separator, header_row, separator] + data_rows + [separator]
        
        return "\n".join(table_lines)
    
    @staticmethod
    def wrap_text(text: str, width: int = 80) -> str:
        """Wrap text to specified width
        
        Args:
            text: Text to wrap
            width: Maximum width
            
        Returns:
            Wrapped text
        """
        if not text:
            return ""
        
        # Handle multiple paragraphs
        paragraphs = text.split('\n\n')
        wrapped_paragraphs = []
        
        for paragraph in paragraphs:
            # Preserve single line breaks within paragraphs
            lines = paragraph.split('\n')
            wrapped_lines = []
            for line in lines:
                if line.strip():
                    wrapped = textwrap.fill(line, width=width)
                    wrapped_lines.append(wrapped)
                else:
                    wrapped_lines.append('')
            wrapped_paragraphs.append('\n'.join(wrapped_lines))
        
        return '\n\n'.join(wrapped_paragraphs)
    
    @staticmethod
    def format_code_block(code: str, language: str = "") -> str:
        """Format code in a code block
        
        Args:
            code: Code to format
            language: Programming language (optional)
            
        Returns:
            Formatted code block
        """
        lang_label = f" ({language})" if language else ""
        header = f"┌─ Code{lang_label} " + "─" * (60 - len(lang_label) - 8)
        footer = "└" + "─" * 60
        
        code_lines = code.split('\n')
        formatted_lines = [f"│ {line}" for line in code_lines]
        
        result = "\n".join([header] + formatted_lines + [footer])
        
        if COLORS_AVAILABLE:
            return f"{Fore.YELLOW}{result}{Style.RESET_ALL}"
        return result
    
    @staticmethod
    def format_key_value_pairs(pairs: dict, separator: str = ": ") -> str:
        """Format key-value pairs
        
        Args:
            pairs: Dictionary of key-value pairs
            separator: Separator between key and value
            
        Returns:
            Formatted pairs
        """
        if not pairs:
            return ""
        
        # Find max key length for alignment
        max_key_len = max(len(str(k)) for k in pairs.keys())
        
        formatted_pairs = []
        for key, value in pairs.items():
            formatted_pairs.append(f"{str(key):<{max_key_len}}{separator}{value}")
        
        return "\n".join(formatted_pairs)
    
    @staticmethod
    def format_progress_bar(current: int, total: int, width: int = 30) -> str:
        """Format a progress bar
        
        Args:
            current: Current progress value
            total: Total value
            width: Width of progress bar
            
        Returns:
            Formatted progress bar
        """
        if total == 0:
            percentage = 0
        else:
            percentage = min(100, int((current / total) * 100))
        
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        result = f"[{bar}] {percentage}%"
        
        if COLORS_AVAILABLE:
            if percentage < 33:
                color = Fore.RED
            elif percentage < 66:
                color = Fore.YELLOW
            else:
                color = Fore.GREEN
            return f"{color}{result}{Style.RESET_ALL}"
        return result
    
    @staticmethod
    def format_header(text: str, level: int = 1) -> str:
        """Format a header
        
        Args:
            text: Header text
            level: Header level (1-3)
            
        Returns:
            Formatted header
        """
        if level == 1:
            underline = "=" * len(text)
            result = f"\n{text}\n{underline}\n"
            if COLORS_AVAILABLE:
                return f"{Fore.CYAN}{Style.BRIGHT}{result}{Style.RESET_ALL}"
        elif level == 2:
            underline = "-" * len(text)
            result = f"\n{text}\n{underline}\n"
            if COLORS_AVAILABLE:
                return f"{Fore.CYAN}{result}{Style.RESET_ALL}"
        else:
            result = f"\n{text}\n"
            if COLORS_AVAILABLE:
                return f"{Fore.BLUE}{result}{Style.RESET_ALL}"
        
        return result
