"""
TUI Interface - Modern terminal UI using Textual
"""
import asyncio
from typing import Optional

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
    from textual.widgets import Header, Footer, Input, Static, Button, Label
    from textual.binding import Binding
    from textual.reactive import reactive
    from textual import events
    from textual.message import Message
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:
    class MessageDeleted(Message):
        """Message sent when a chat message is deleted"""
        
        def __init__(self, message_id: str):
            self.message_id = message_id
            super().__init__()
    
    
    class ChatMessage(Static):
        """A single chat message widget"""
        
        def __init__(self, sender: str, message: str, is_bot: bool = False, message_id: str = None):
            self.sender = sender
            self.message_text = message
            self.is_bot = is_bot
            self.message_id = message_id or f"msg_{id(self)}"
            super().__init__()
        
        def compose(self) -> ComposeResult:
            """Compose the message widget"""
            with Vertical():
                if self.is_bot:
                    yield Label(f"[bold cyan]{self.sender}:[/bold cyan]")
                    yield Label(f"[white]{self.message_text}[/white]")
                else:
                    yield Label(f"[bold green]{self.sender}:[/bold green]")
                    yield Label(f"[dim]{self.message_text}[/dim]")
        
        def on_click(self, event: events.Click) -> None:
            """Handle click events on message"""
            # Could add context menu or actions here
            pass
    
    
    class StreamingMessage(Static):
        """A message that can be updated during streaming"""
        
        text_content = reactive("")
        
        def __init__(self, sender: str):
            self.sender = sender
            super().__init__()
        
        def render(self) -> str:
            """Render the streaming message"""
            return f"[bold cyan]{self.sender}:[/bold cyan]\n[white]{self.text_content}[/white]"
        
        def append_text(self, text: str):
            """Append text to the streaming message"""
            self.text_content += text
    
    
    class ChatApp(App):
        """A Textual TUI chat application"""
        
        CSS = """
        Screen {
            background: $surface;
        }
        
        #main-container {
            height: 100%;
        }
        
        #chat-container {
            height: 1fr;
            border: thick $primary;
            background: $panel;
            padding: 1 2;
            overflow-y: scroll;
        }
        
        #input-container {
            height: auto;
            dock: bottom;
            background: $surface-darken-1;
            padding: 1 2;
            border-top: solid $primary;
        }
        
        Input {
            width: 1fr;
            border: solid $accent;
            margin-right: 1;
        }
        
        Input:focus {
            border: solid $accent-lighten-2;
        }
        
        #send-button {
            min-width: 10;
            background: $accent;
        }
        
        #send-button:hover {
            background: $accent-lighten-1;
        }
        
        ChatMessage {
            margin: 1 0;
            padding: 1 2;
            background: $boost;
            border-left: thick $primary;
            height: auto;
        }
        
        ChatMessage Vertical {
            height: auto;
        }
        
        ChatMessage Label {
            margin: 0 0 1 0;
            height: auto;
        }
        
        StreamingMessage {
            margin: 1 0;
            padding: 1 2;
            background: $boost;
            border-left: thick $accent;
            text-style: italic;
        }
        
        #status-bar {
            height: 1;
            background: $primary;
            color: $text;
            padding: 0 2;
            text-style: bold;
        }
        
        Header {
            background: $primary-darken-2;
        }
        
        Footer {
            background: $surface-darken-1;
        }
        """
        
        BINDINGS = [
            Binding("ctrl+c", "quit", "Quit", show=True),
            Binding("ctrl+l", "clear", "Clear", show=True),
            Binding("f1", "help", "Help", show=True),
        ]
        
        def __init__(self, bot_name: str = "AI Assistant", user_name: str = "You"):
            super().__init__()
            self.bot_name = bot_name
            self.user_name = user_name
            self.message_queue = asyncio.Queue()
            self.streaming_message = None
            self.command_callback = None
        
        def compose(self) -> ComposeResult:
            """Compose the app layout"""
            yield Header(show_clock=True)
            
            with Container(id="main-container"):
                yield ScrollableContainer(id="chat-container")
                
                with Horizontal(id="input-container"):
                    yield Input(
                        placeholder="Type your message or !help for commands...",
                        id="message-input"
                    )
                    yield Button("Send", id="send-button", variant="primary")
            
            yield Static("Ready", id="status-bar")
            yield Footer()
        
        def on_mount(self) -> None:
            """Called when app is mounted"""
            self.title = f"Terminal Chat - {self.bot_name}"
            self.sub_title = "Press F1 for help, Ctrl+C to quit"
            
            # Focus the input
            self.query_one("#message-input", Input).focus()
            
            # Display welcome message
            self.add_bot_message(
                f"Welcome to {self.bot_name} Terminal Chat!\n"
                "Type your message or use commands starting with !\n"
                "Type !help for available commands"
            )
        
        async def on_input_submitted(self, event: Input.Submitted) -> None:
            """Handle input submission"""
            await self._process_message(event.value)
        
        async def on_button_pressed(self, event: Button.Pressed) -> None:
            """Handle button press"""
            if event.button.id == "send-button":
                message_input = self.query_one("#message-input", Input)
                await self._process_message(message_input.value)
        
        async def _process_message(self, message: str):
            """Process a message from input or button"""
            message = message.strip()
            
            if not message:
                return
            
            # Clear input
            message_input = self.query_one("#message-input", Input)
            message_input.value = ""
            
            # Add user message to chat
            self.add_user_message(message)
            
            # Check for exit commands
            if message.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                self.add_bot_message("Goodbye! Thanks for chatting!")
                await asyncio.sleep(1)
                self.exit()
                return
            
            # Show typing indicator
            self.update_status("🤔 Thinking...")
            
            # Send to command callback
            if self.command_callback:
                await self.command_callback(message)
        
        def add_user_message(self, message: str):
            """Add a user message to the chat"""
            chat_container = self.query_one("#chat-container", ScrollableContainer)
            chat_container.mount(ChatMessage(self.user_name, message, is_bot=False))
            chat_container.scroll_end(animate=False)
        
        def add_bot_message(self, message: str):
            """Add a bot message to the chat"""
            chat_container = self.query_one("#chat-container", ScrollableContainer)
            chat_container.mount(ChatMessage(self.bot_name, message, is_bot=True))
            chat_container.scroll_end(animate=False)
            self.update_status("Ready")

        def update_bot_name(self, new_name: str):
            """Update the bot name across the app (title and status) and announce the change."""
            try:
                self.bot_name = new_name
                try:
                    self.title = f"Terminal Chat - {self.bot_name}"
                except Exception:
                    pass
                try:
                    self.add_bot_message(f"Persona switched to {self.bot_name}")
                except Exception:
                    pass
            except Exception:
                pass
        
        def start_streaming_message(self):
            """Start a new streaming message"""
            chat_container = self.query_one("#chat-container", ScrollableContainer)
            self.streaming_message = StreamingMessage(self.bot_name)
            chat_container.mount(self.streaming_message)
            chat_container.scroll_end(animate=False)
        
        def append_to_stream(self, text: str):
            """Append text to the current streaming message"""
            if self.streaming_message:
                self.streaming_message.append_text(text)
                chat_container = self.query_one("#chat-container", ScrollableContainer)
                chat_container.scroll_end(animate=False)
        
        def end_streaming_message(self):
            """End the current streaming message"""
            self.streaming_message = None
            self.update_status("Ready")
        
        def update_status(self, status: str):
            """Update the status bar"""
            status_bar = self.query_one("#status-bar", Static)
            status_bar.update(status)
        
        def action_clear(self) -> None:
            """Clear the chat"""
            chat_container = self.query_one("#chat-container", ScrollableContainer)
            chat_container.remove_children()
            self.add_bot_message("Chat cleared!")
        
        def action_help(self) -> None:
            """Show help"""
            help_text = """[bold cyan]Available Commands:[/bold cyan]

[yellow]AI & Chat:[/yellow]
  !ai <question>        Ask the AI a question
  !ask <question>       Alias for !ai
  !chat <question>      Alias for !ai

[yellow]Utilities:[/yellow]
  !time                 Get current time
  !calc <expression>    Calculate math expression
  !dice [sides]         Roll dice (default 6 sides)
  !flip                 Flip a coin
  !weather <city>       Get weather information
  !fact                 Get a random fact
  !joke                 Get a random joke
  !catfact              Get a cat fact

[yellow]Games:[/yellow]
  !game guess [max]     Start number guessing game
  !guess <number>       Make a guess
  !rps <choice>         Play rock-paper-scissors
  !8ball <question>     Ask the magic 8-ball
  !trivia               Start a trivia question
  !answer <answer>      Answer trivia or game

[yellow]Search:[/yellow]
  !search <query>       Search the web
  !find <query>         Alias for !search

[yellow]Training:[/yellow]
  !training_stats       View training data statistics
  !training_export <fmt> Export data (openai/llama/alpaca)
  !train_model <size>   Train a custom model (tiny/small/medium/large)
  !list_models          List your trained models
  !training_requirements Show hardware requirements

[yellow]Memory (AI auto-learns about you):[/yellow]
  !memories             View what AI remembers about you
  !recall <key>         Retrieve specific memory
  !remember <key> <val> Manually add a memory
  !forget <key>         Delete a memory

[yellow]System:[/yellow]
  !help [command]       Show this help or help for specific command
  !memory [number]      View/set conversation memory (0=unlimited)
  !stats                View your usage statistics
  !mood                 Check bot's mood
  !relationship         Check your relationship level
  !compliment           Give the bot a compliment
  exit, quit            Exit the chat

[green]Shortcuts:[/green]
  Ctrl+C                Quit
  Ctrl+L                Clear chat
  F1                    This help

[green]💡 Tip: You can chat without commands - just type your message![/green]"""
            self.add_bot_message(help_text)
        
        def set_command_callback(self, callback):
            """Set the callback for processing commands"""
            self.command_callback = callback


def is_textual_available() -> bool:
    """Check if Textual is available"""
    return TEXTUAL_AVAILABLE


def create_tui_app(bot_name: str = "AI Assistant", user_name: str = "You") -> Optional['ChatApp']:
    """Create a TUI app instance"""
    if not TEXTUAL_AVAILABLE:
        return None
    return ChatApp(bot_name=bot_name, user_name=user_name)
