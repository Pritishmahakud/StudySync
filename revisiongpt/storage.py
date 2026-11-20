"""
Persistent storage engine for RevisionGPT decks and flashcards.
Saves and loads cards from data/decks.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import Deck, Flashcard


DEFAULT_STORAGE_FILE = Path(__file__).parent.parent / "data" / "decks.json"


class StorageManager:
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or DEFAULT_STORAGE_FILE
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._init_empty_storage()

    def _init_empty_storage(self):
        initial = {
            "default": {
                "id": "default",
                "name": "General Revision Deck",
                "description": "Default repository for StudySync revision flashcards",
                "cards": []
            }
        }
        self.file_path.write_text(json.dumps(initial, indent=2), encoding="utf-8")

    def load_decks(self) -> Dict[str, Deck]:
        if not self.file_path.exists():
            self._init_empty_storage()

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            decks = {}
            for d_id, d_data in data.items():
                cards = [Flashcard(**c) for c in d_data.get("cards", [])]
                decks[d_id] = Deck(
                    id=d_id,
                    name=d_data.get("name", d_id),
                    description=d_data.get("description", ""),
                    cards=cards,
                    created_at=d_data.get("created_at", "")
                )
            return decks
        except Exception:
            return {}

    def save_decks(self, decks: Dict[str, Deck]):
        serializable = {}
        for d_id, deck in decks.items():
            serializable[d_id] = {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "created_at": deck.created_at,
                "cards": [c.model_dump(mode="json") for c in deck.cards]
            }
        self.file_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def get_all_cards(self) -> List[Flashcard]:
        decks = self.load_decks()
        all_cards = []
        for d in decks.values():
            all_cards.extend(d.cards)
        return all_cards
