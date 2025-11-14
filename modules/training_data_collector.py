"""
Training Data Collector - Collects and exports conversation data for AI training

This module preserves COMPLETE conversation logs for training future AI models.
It works alongside the auto-memory system which extracts structured facts.

Data Flow:
- Full conversations -> training_data/conversations.jsonl (for model training)
- Extracted facts -> ai_database.db (for real-time context)
- Both systems work together to provide comprehensive learning
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from modules.logger import BotLogger

logger = BotLogger.get_logger(__name__)


class TrainingDataCollector:
    """
    Collects conversation data for training custom AI models
    
    Preserves complete conversation history including:
    - Full user messages and AI responses
    - Context (relationship level, mood, etc.)
    - Timestamps and user IDs
    - All nuance and conversational flow
    
    This data can be exported in various formats (OpenAI, Llama, Alpaca)
    for fine-tuning custom models.
    """
    
    def __init__(self, data_dir: str = "training_data"):
        """
        Initialize the training data collector
        
        Args:
            data_dir: Directory to store training data
        """
        self.data_dir = data_dir
        self.conversations_file = os.path.join(data_dir, "conversations.jsonl")
        self.metadata_file = os.path.join(data_dir, "metadata.json")
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize metadata
        self.metadata = self._load_metadata()
        
        logger.info(f"Training data collector initialized: {data_dir}")
    
    def _load_metadata(self) -> Dict:
        """Load or create metadata file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
        
        # Default metadata
        return {
            "created_at": datetime.now().isoformat(),
            "total_conversations": 0,
            "last_updated": None,
            "format_version": "1.0"
        }
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            self.metadata["last_updated"] = datetime.now().isoformat()
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def save_conversation(
        self,
        user_input: str,
        bot_response: str,
        user_id: str,
        context: Optional[Dict] = None
    ):
        """
        Save a conversation turn for training
        
        Args:
            user_input: User's message
            bot_response: Bot's response
            user_id: User identifier
            context: Optional context information (mood, relationship level, etc.)
        """
        try:
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "user_input": user_input,
                "bot_response": bot_response,
                "context": context or {}
            }
            
            # Append to JSONL file (one JSON object per line)
            with open(self.conversations_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(conversation_data, ensure_ascii=False) + '\n')
            
            # Update metadata
            self.metadata["total_conversations"] += 1
            self._save_metadata()
            
            logger.info(f"Conversation saved: {self.metadata['total_conversations']} total")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
    
    def export_for_fine_tuning(
        self,
        output_file: str = None,
        format_type: str = "openai"
    ) -> str:
        """
        Export conversations in a format suitable for fine-tuning
        
        Args:
            output_file: Output file path (default: training_data/export_<format>.jsonl)
            format_type: Export format - "openai", "llama", or "alpaca"
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            output_file = os.path.join(
                self.data_dir,
                f"export_{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            )
        
        try:
            conversations = self._load_all_conversations()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for conv in conversations:
                    if format_type == "openai":
                        # OpenAI fine-tuning format
                        formatted = {
                            "messages": [
                                {"role": "user", "content": conv["user_input"]},
                                {"role": "assistant", "content": conv["bot_response"]}
                            ]
                        }
                    elif format_type == "llama":
                        # Llama format with special tokens
                        formatted = {
                            "text": f"<s>[INST] {conv['user_input']} [/INST] {conv['bot_response']} </s>"
                        }
                    elif format_type == "alpaca":
                        # Alpaca instruction format
                        formatted = {
                            "instruction": conv["user_input"],
                            "input": "",
                            "output": conv["bot_response"]
                        }
                    else:
                        formatted = conv
                    
                    f.write(json.dumps(formatted, ensure_ascii=False) + '\n')
            
            logger.info(f"Exported {len(conversations)} conversations to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error exporting conversations: {e}")
            return None
    
    def _load_all_conversations(self) -> List[Dict]:
        """Load all conversations from file"""
        conversations = []
        
        if not os.path.exists(self.conversations_file):
            return conversations
        
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        conversations.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
        
        return conversations
    
    def get_statistics(self) -> Dict:
        """Get statistics about collected data"""
        conversations = self._load_all_conversations()
        
        if not conversations:
            return {
                "total_conversations": 0,
                "unique_users": 0,
                "date_range": None,
                "avg_user_input_length": 0,
                "avg_bot_response_length": 0
            }
        
        users = set(conv.get("user_id") for conv in conversations)
        user_lengths = [len(conv.get("user_input", "")) for conv in conversations]
        bot_lengths = [len(conv.get("bot_response", "")) for conv in conversations]
        
        dates = [conv.get("timestamp") for conv in conversations if conv.get("timestamp")]
        date_range = None
        if dates:
            date_range = {
                "first": min(dates),
                "last": max(dates)
            }
        
        return {
            "total_conversations": len(conversations),
            "unique_users": len(users),
            "date_range": date_range,
            "avg_user_input_length": sum(user_lengths) / len(user_lengths) if user_lengths else 0,
            "avg_bot_response_length": sum(bot_lengths) / len(bot_lengths) if bot_lengths else 0
        }
    
    def clear_data(self, confirm: bool = False):
        """
        Clear all collected training data
        
        Args:
            confirm: Must be True to actually clear data (safety check)
        """
        if not confirm:
            logger.warning("Clear data called without confirmation")
            return False
        
        try:
            if os.path.exists(self.conversations_file):
                os.remove(self.conversations_file)
            
            self.metadata = {
                "created_at": datetime.now().isoformat(),
                "total_conversations": 0,
                "last_updated": None,
                "format_version": "1.0"
            }
            self._save_metadata()
            
            logger.info("Training data cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return False


# Global instance
training_collector = TrainingDataCollector()
