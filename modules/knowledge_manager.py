"""
Knowledge Manager - thin wrapper around the async AI database for reusable knowledge

Provides a small, stable interface used by other modules to add/search/get knowledge
without depending directly on the lower-level DB implementation.
"""
import logging
from typing import List, Optional, Dict

import json
from datetime import datetime


logger = logging.getLogger(__name__)


class KnowledgeManager:
    def __init__(self, ai_db=None):
        """Wrap an AIDatabase-like instance providing async methods.

        The wrapped object must implement: `add_knowledge`, `search_knowledge`, `get_random_knowledge`.
        """
        self.ai_db = ai_db

    def set_ai_db(self, ai_db):
        """Inject the underlying DB instance (AIDatabase)."""
        self.ai_db = ai_db

    async def add_knowledge(self, category: str, key_term: str, content: str, relevance_score: float = 1.0):
        """Add knowledge to the DB.

        Behavior: merge/append new facts into any existing record for (category, key_term).
        - If existing content is JSON array or object, attempt to merge entries (dedupe by 'text').
        - If existing content is plain text, convert to a single-item list and merge.
        - The final stored `content` is a JSON array string.
        """
        if not self.ai_db:
            logger.debug("No AI DB configured; skipping add_knowledge")
            return None
        try:
            # Normalize incoming content into a list of fact objects
            new_items = []
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    new_items = parsed
                elif isinstance(parsed, dict):
                    new_items = [parsed]
                else:
                    # Primitive types -> wrap as text
                    new_items = [{'text': str(parsed)}]
            except Exception:
                # Not JSON -> treat as plain text
                new_items = [{'text': str(content)}]

            # Try to find existing record for exact (category, key_term)
            existing_rows = []
            try:
                existing_rows = await self.ai_db.search_knowledge(key_term, category, limit=5)
            except Exception:
                existing_rows = []

            existing_content = None
            for r in existing_rows:
                if r.get('key_term') == key_term:
                    existing_content = r.get('content')
                    break

            merged = []
            seen_texts = set()

            # Load existing items if present and normalize into structured entries
            now_iso = datetime.utcnow().isoformat() + "Z"
            def _normalize_existing_item(it):
                # Normalize an existing item into comprehensive dict
                if isinstance(it, dict):
                    text = it.get('text') or it.get('content') or str(it)
                    meta = it.get('meta') if isinstance(it.get('meta'), dict) else it.get('metadata') if isinstance(it.get('metadata'), dict) else {}
                    created_at = it.get('created_at') or it.get('createdAt') or None
                    updated_at = it.get('updated_at') or it.get('updatedAt') or None
                    history = it.get('history') if isinstance(it.get('history'), list) else []
                else:
                    text = str(it)
                    meta = {}
                    created_at = None
                    updated_at = None
                    history = []

                if not created_at:
                    created_at = now_iso
                if not updated_at:
                    updated_at = created_at
                if not history:
                    history = [{'text': text, 'meta': meta, 'timestamp': created_at}]

                return {
                    'text': text,
                    'meta': meta,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'history': history
                }

            if existing_content:
                try:
                    parsed_existing = json.loads(existing_content)
                    if isinstance(parsed_existing, list):
                        for it in parsed_existing:
                            norm = _normalize_existing_item(it)
                            key = norm['text'].strip().lower()
                            if key not in seen_texts:
                                seen_texts.add(key)
                                merged.append(norm)
                    elif isinstance(parsed_existing, dict):
                        norm = _normalize_existing_item(parsed_existing)
                        key = norm['text'].strip().lower()
                        seen_texts.add(key)
                        merged.append(norm)
                    else:
                        txt = str(parsed_existing)
                        norm = _normalize_existing_item(txt)
                        seen_texts.add(norm['text'].strip().lower())
                        merged.append(norm)
                except Exception:
                    # Treat raw existing content as single text item
                    txt = str(existing_content)
                    norm = _normalize_existing_item(txt)
                    seen_texts.add(norm['text'].strip().lower())
                    merged.append(norm)

            # Merge in new items, with metadata merging and append-only history per entry
            for it in new_items:
                if isinstance(it, dict):
                    text = it.get('text') or it.get('content') or str(it)
                    new_meta = it.get('meta') if isinstance(it.get('meta'), dict) else it.get('metadata') if isinstance(it.get('metadata'), dict) else {}
                else:
                    text = str(it)
                    new_meta = {}

                key = text.strip().lower()

                # If exists, merge metadata and append version to history
                found = None
                for entry in merged:
                    if entry['text'].strip().lower() == key:
                        found = entry
                        break

                if found:
                    # Append a new version to history
                    version = {'text': text, 'meta': new_meta, 'timestamp': now_iso}
                    try:
                        found['history'].append(version)
                    except Exception:
                        found['history'] = [version]

                    # Merge metadata (new keys override existing)
                    try:
                        if not isinstance(found.get('meta'), dict):
                            found['meta'] = {}
                        found['meta'].update(new_meta or {})
                    except Exception:
                        found['meta'] = new_meta or {}

                    found['updated_at'] = now_iso
                else:
                    # New entry - create structured record with history
                    new_entry = {
                        'text': text,
                        'meta': new_meta or {},
                        'created_at': now_iso,
                        'updated_at': now_iso,
                        'history': [{'text': text, 'meta': new_meta or {}, 'timestamp': now_iso}]
                    }
                    merged.append(new_entry)

            # Final content as JSON array
            final_content = json.dumps(merged, ensure_ascii=False)

            return await self.ai_db.add_knowledge(category, key_term, final_content, relevance_score)

        except Exception as e:
            logger.exception(f"Failed to add knowledge: {e}")
            return None

    async def search_knowledge(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search the knowledge base; returns list of rows or empty list."""
        if not self.ai_db:
            logger.debug("No AI DB configured; search_knowledge returning empty list")
            return []
        try:
            return await self.ai_db.search_knowledge(query, category, limit)
        except Exception as e:
            logger.exception(f"Knowledge search failed: {e}")
            return []

    async def get_random_knowledge(self, category: str = None) -> Optional[Dict]:
        """Return a single random knowledge row or None."""
        if not self.ai_db:
            logger.debug("No AI DB configured; get_random_knowledge returning None")
            return None
        try:
            return await self.ai_db.get_random_knowledge(category)
        except Exception as e:
            logger.exception(f"get_random_knowledge failed: {e}")
            return None


# Module-level default manager for easy import
knowledge_manager = KnowledgeManager()
