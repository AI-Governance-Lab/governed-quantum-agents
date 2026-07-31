import os
import json
import logging
from typing import Dict, Any, List, Optional

class VectorStore:
    """
    DiscoveryMemory (VectorStore) stores historical scientific results and their
    quantum parameters locally to provide multi-session cognitive retention.
    """
    def __init__(self, storage_path: str = "config/discovery_memory.json"):
        self.storage_path = storage_path
        self._initialize_store()

    def _initialize_store(self):
        # Create storage directories if not existing
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "w") as f:
                    json.dump([], f)
                logging.info(f"Initialized new discovery memory at {self.storage_path}")
            except Exception as e:
                logging.error(f"Failed to initialize discovery memory file: {e}")

    def save_discovery(self, goal: str, data: Dict[str, Any]) -> None:
        """
        Saves a discovery execution log into memory.
        """
        logging.info(f"Saving discovery run to memory: '{goal}'")
        try:
            memory_list = []
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    try:
                        memory_list = json.load(f)
                    except Exception:
                        memory_list = []

            record = {
                "goal": goal,
                "timestamp": "2026-07-31T18:45:00",
                "data": data
            }
            memory_list.append(record)
            
            with open(self.storage_path, "w") as f:
                json.dump(memory_list, f, indent=2)
            logging.info("Discovery saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save discovery to memory: {e}")

    def search_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Simulates semantic search by computing keyword overlaps with stored goals.
        """
        logging.info(f"Searching discovery memory for: '{query}'")
        try:
            if not os.path.exists(self.storage_path):
                return []

            with open(self.storage_path, "r") as f:
                try:
                    memory_list = json.load(f)
                except Exception:
                    return []
                
            query_words = set(query.lower().split())
            scored_results = []
            
            for item in memory_list:
                goal_words = set(item.get("goal", "").lower().split())
                overlap = len(query_words.intersection(goal_words))
                scored_results.append((overlap, item))
                
            # Sort by overlap score descending
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            # Return top matching items
            matches = [item for score, item in scored_results[:limit]]
            logging.info(f"Found {len(matches)} historical matches in memory.")
            return matches
        except Exception as e:
            logging.error(f"Failed to search discovery memory: {e}")
            return []
