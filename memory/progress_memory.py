import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class LearningProgress:
    subject: str
    topic: str
    skill_level: float
    attempts: int
    successful_attempts: int

@dataclass
class LearningSession:
    session_id: str
    start_time: str
    subjects_covered: List[str]
    questions_asked: int
    questions_answered_correctly: int

class ProgressMemory:
    def __init__(self, student_id: str, storage_path: str = "data/progress_data"):
        self.student_id = student_id
        self.storage_path = storage_path
        self.progress_data: Dict[str, Dict[str, LearningProgress]] = defaultdict(dict)
        self.learning_sessions: List[LearningSession] = []
        os.makedirs(self.storage_path, exist_ok=True)
        self._load()

    def start_session(self, session_id: str) -> LearningSession:
        session = LearningSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            subjects_covered=[],
            questions_asked=0,
            questions_answered_correctly=0
        )
        self.learning_sessions.append(session)
        self._save()
        return session

    def update_progress(self, subject: str, topic: str, performance_score: float, was_successful: bool):
        if subject not in self.progress_data:
            self.progress_data[subject] = {}
        if topic not in self.progress_data[subject]:
            self.progress_data[subject][topic] = LearningProgress(subject, topic, 0.0, 0, 0)
        progress = self.progress_data[subject][topic]
        progress.attempts += 1
        if was_successful:
            progress.successful_attempts += 1
        progress.skill_level = (progress.skill_level * 0.7) + (performance_score * 0.3)
        logger.info(f"Updated progress: {subject}/{topic}, skill={progress.skill_level:.2f}")
        self._save()

    def update_session(self, session_id: str, subject: str, topic: str, question_asked: bool = False, correct_answer: bool = False):
        for session in self.learning_sessions:
            if session.session_id == session_id:
                if subject not in session.subjects_covered:
                    session.subjects_covered.append(subject)
                if question_asked:
                    session.questions_asked += 1
                if correct_answer:
                    session.questions_answered_correctly += 1
                logger.info(f"Updated session {session_id}: subject={subject}, questions_asked={session.questions_asked}")
                self._save()
                break

    def get_progress_report(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "subjects": {s: {t: asdict(p) for t, p in topics.items()} for s, topics in self.progress_data.items()},
            "sessions": [asdict(s) for s in self.learning_sessions],
            "timestamp": datetime.now().isoformat()
        }

    def _save(self):
        filepath = os.path.join(self.storage_path, f"{self.student_id}_progress.json")
        try:
            data = {
                "student_id": self.student_id,
                "progress_data": {
                    s: {t: asdict(p) for t, p in topics.items()}
                    for s, topics in self.progress_data.items()
                },
                "learning_sessions": [asdict(s) for s in self.learning_sessions]
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def _load(self):
        filepath = os.path.join(self.storage_path, f"{self.student_id}_progress.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for subject, topics in data.get("progress_data", {}).items():
                    self.progress_data[subject] = {
                        topic: LearningProgress(**progress)
                        for topic, progress in topics.items()
                    }
                self.learning_sessions = [
                    LearningSession(**session)
                    for session in data.get("learning_sessions", [])
                ]
            except Exception as e:
                logger.error(f"Failed to load progress: {e}")