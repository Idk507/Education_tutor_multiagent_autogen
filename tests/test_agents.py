# tests/test_agents.py
import unittest
import os
from agents.tutor_agent import EducationalTutorAgent
from agents.student_agent import StudentAgent
from agents.progress_tracker import ProgressTrackerAgent
from config.llm_config import LLMProvider
from memory.progress_memory import ProgressMemory

class TestEducationalAgents(unittest.TestCase):
    def setUp(self):
        self.student_id = "test_student"
        self.tutor = EducationalTutorAgent(student_id=self.student_id)
        self.student = StudentAgent(student_id=self.student_id)
        self.tracker = ProgressTrackerAgent(student_id=self.student_id)
    
    def test_tutor_explanation(self):
        result = self.tutor._generate_explanation(
            subject="mathematics",
            topic="quadratic equations",
            difficulty_level="medium",
            learning_style="visual"
        )
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 50)  # Ensure non-empty response
    
    def test_student_question(self):
        result = self.student._ask_question(
            topic="quadratic equations",
            question="What is the quadratic formula?",
            context="Learning about solving equations"
        )
        self.assertIsInstance(result, dict)
        self.assertIn("topic", result)
        self.assertIn("original_question", result)
    
    def test_progress_tracker_report(self):
        result = self.tracker._generate_progress_report()
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)
    
    def tearDown(self):
        # Clean up test data
        progress_file = f"data/progress_data/{self.student_id}_progress.json"
        if os.path.exists(progress_file):
            os.remove(progress_file)

if __name__ == '__main__':
    unittest.main()