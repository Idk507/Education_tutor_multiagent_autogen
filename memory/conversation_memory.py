import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

class LangChainConversationMemory:
    def __init__(self, session_id: str, storage_path: str = "data/conversation_history"):
        self.session_id = session_id
        self.storage_path = storage_path
        self.memory = ConversationBufferMemory(return_messages=True)
        self.metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "subjects": [],
            "topics": []
        }
        os.makedirs(self.storage_path, exist_ok=True)
        self._load()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, str]] = None):
        if role == "student":
            self.memory.chat_memory.add_message(HumanMessage(content=content))
        else:
            self.memory.chat_memory.add_message(AIMessage(content=content))
        if metadata:
            if "subject" in metadata and metadata["subject"] not in self.metadata["subjects"]:
                self.metadata["subjects"].append(metadata["subject"])
            if "topic" in metadata and metadata["topic"] not in self.metadata["topics"]:
                self.metadata["topics"].append(metadata["topic"])
        self._save()

    def get_messages(self) -> List[Dict[str, Any]]:
        return [
            {"role": "human" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
            for msg in self.memory.chat_memory.messages
        ]

    def get_context(self) -> str:
        return self.memory.buffer

    def _save(self):
        filepath = os.path.join(self.storage_path, f"{self.session_id}.json")
        try:
            data = {
                "metadata": self.metadata,
                "messages": [
                    {"role": "human" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                    for msg in self.memory.chat_memory.messages
                ]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

    def _load(self):
        filepath = os.path.join(self.storage_path, f"{self.session_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.metadata = data.get("metadata", self.metadata)
                for msg in data.get("messages", []):
                    if msg["role"] == "human":
                        self.memory.chat_memory.add_message(HumanMessage(content=msg["content"]))
                    else:
                        self.memory.chat_memory.add_message(AIMessage(content=msg["content"]))
            except Exception as e:
                logger.error(f"Failed to load conversation: {e}")