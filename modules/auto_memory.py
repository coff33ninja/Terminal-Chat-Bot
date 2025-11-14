"""
Auto Memory System - AI automatically extracts and stores important information

This system serves two purposes:
1. Real-time memory: Extracts key facts for immediate context in future conversations
2. Training data: Full conversations are saved separately for training future AI models

The memory system provides quick, structured access to important facts, while
the full conversation logs preserve all nuance and context for model training.
"""
import logging
from modules.ai_database import ai_db

logger = logging.getLogger(__name__)


class AutoMemorySystem:
    """
    Automatically extract and store important information from conversations
    
    Note: This extracts structured memories for quick retrieval. Full conversation
    logs are preserved separately in training_data/ for future AI model training.
    """
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
    
    async def analyze_and_remember(self, user_id: str, user_message: str, ai_response: str):
        """
        Analyze a conversation and automatically extract important information to remember
        
        Args:
            user_id: User identifier
            user_message: What the user said
            ai_response: What the AI responded
        """
        try:
            # Create a prompt for the AI to extract memorable information
            extraction_prompt = f"""Analyze this conversation and extract important information that should be remembered for future conversations. Extract information about BOTH the user AND what the AI (you) said.

User said: "{user_message}"
AI responded: "{ai_response}"

Extract information in this JSON format (return ONLY the JSON, nothing else):
{{
  "memories": [
    {{"key": "user_name", "value": "John", "importance": 10, "about": "user"}},
    {{"key": "user_favorite_color", "value": "blue", "importance": 5, "about": "user"}},
    {{"key": "ai_told_user_about_python", "value": "explained Python basics on 2024-01-15", "importance": 6, "about": "conversation"}},
    {{"key": "ai_recommended_book", "value": "recommended 'Clean Code' for learning", "importance": 5, "about": "conversation"}}
  ]
}}

Rules for extraction:
1. USER INFORMATION (about: "user"):
   - Name, age, location, job, hobbies, preferences, family, pets, important dates
   - Use prefix "user_" for user facts (e.g., "user_name", "user_job")
   
2. CONVERSATION CONTEXT (about: "conversation"):
   - What the AI explained, taught, or told the user
   - Recommendations, advice, or suggestions the AI made
   - Topics discussed, problems solved, questions answered
   - Use prefix "ai_" for AI's contributions (e.g., "ai_explained_topic", "ai_recommended_X")
   - Include brief context of WHEN/WHY (e.g., "explained X when user asked about Y")

3. GENERAL RULES:
   - Use simple, clear keys (lowercase, underscores)
   - Importance: 1-10 (10 = critical like name, 5-7 = useful context, 1-3 = minor)
   - If nothing important, return: {{"memories": []}}
   - Skip: temporary states, simple greetings, generic responses

Examples of what TO remember:

USER INFO:
- "My name is Sarah" -> {{"key": "user_name", "value": "Sarah", "importance": 10, "about": "user"}}
- "I work as a teacher" -> {{"key": "user_job", "value": "teacher", "importance": 8, "about": "user"}}
- "I'm learning Python" -> {{"key": "user_learning", "value": "Python programming", "importance": 7, "about": "user"}}

CONVERSATION CONTEXT:
- AI explained how loops work -> {{"key": "ai_explained_loops", "value": "taught Python loops when user was learning", "importance": 6, "about": "conversation"}}
- AI recommended a book -> {{"key": "ai_recommended_clean_code", "value": "suggested Clean Code book for better coding", "importance": 5, "about": "conversation"}}
- AI helped debug code -> {{"key": "ai_helped_debug_api", "value": "fixed API connection issue together", "importance": 6, "about": "conversation"}}

Examples of what NOT to remember:
- "What's the weather?" -> nothing important
- "Thanks!" -> just politeness
- "I'm tired today" -> temporary state

Return the JSON now:"""

            # Get AI to extract information
            model = self.api_manager.get_current_model()
            if not model:
                return
            
            response = model.generate_content(extraction_prompt)
            
            if not response or not response.text:
                return
            
            # Parse the response
            import json
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                data = json.loads(response_text)
                memories = data.get("memories", [])
                
                # Store each memory
                for memory in memories:
                    key = memory.get("key", "").strip()
                    value = memory.get("value", "").strip()
                    importance = memory.get("importance", 5)
                    about = memory.get("about", "user")  # "user" or "conversation"
                    
                    if key and value:
                        await ai_db.remember(
                            user_id=user_id,
                            key=key,
                            value=value,
                            memory_type=about,  # Store as "user" or "conversation"
                            importance=importance
                        )
                        logger.info(f"Auto-remembered ({about}): {key} = {value} (importance: {importance})")
                
                if memories:
                    logger.info(f"Auto-memory: Stored {len(memories)} new memories for {user_id}")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse memory extraction JSON: {e}")
                logger.debug(f"Response was: {response_text}")
                
        except Exception as e:
            logger.error(f"Auto-memory error: {e}")
    
    async def get_memory_summary(self, user_id: str) -> str:
        """Get a summary of what the AI knows about the user"""
        try:
            memories = await ai_db.recall(user_id)
            
            if not memories:
                return "I don't know much about you yet. Chat with me more so I can learn!"
            
            # Group by importance
            important = [m for m in memories if m['importance'] >= 8]
            moderate = [m for m in memories if 5 <= m['importance'] < 8]
            minor = [m for m in memories if m['importance'] < 5]
            
            summary = "Here's what I know about you:\n\n"
            
            if important:
                summary += "**Important:**\n"
                for m in important:
                    summary += f"  • {m['memory_key']}: {m['memory_value']}\n"
                summary += "\n"
            
            if moderate:
                summary += "**Preferences & Details:**\n"
                for m in moderate:
                    summary += f"  • {m['memory_key']}: {m['memory_value']}\n"
                summary += "\n"
            
            if minor:
                summary += "**Other Details:**\n"
                for m in minor:
                    summary += f"  • {m['memory_key']}: {m['memory_value']}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Memory summary error: {e}")
            return "Error retrieving memory summary"


def create_auto_memory(api_manager):
    """Factory function to create auto memory system"""
    return AutoMemorySystem(api_manager)
