#!/usr/bin/env python3
"""
Simple test script for the Educational Tutor FastAPI application
Run this after starting the FastAPI server to test basic functionality
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_STUDENT_ID = "test_student_001"

def test_api_health():
    """Test API health check"""
    print("🔹 Testing API health check...")
    response = requests.get(f"{API_BASE_URL}/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API is healthy: {data['message']}")
        return True
    else:
        print(f"❌ API health check failed: {response.status_code}")
        return False

def test_session_creation():
    """Test session creation"""
    print("\n🔹 Testing session creation...")
    
    payload = {"student_id": TEST_STUDENT_ID}
    response = requests.post(f"{API_BASE_URL}/api/sessions", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        print(f"✅ Session created successfully: {session_id}")
        return session_id
    else:
        print(f"❌ Session creation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def test_concept_explanation(session_id: str):
    """Test concept explanation"""
    print("\n🔹 Testing concept explanation...")
    
    payload = {
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "difficulty_level": "medium",
        "learning_style": "visual"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/sessions/{session_id}/concepts/explain",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Concept explanation received")
        print(f"Subject: {data['subject']}")
        print(f"Topic: {data['topic']}")
        print(f"Explanation (preview): {data['explanation'][:100]}...")
        return True
    else:
        print(f"❌ Concept explanation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_problem_generation(session_id: str):
    """Test practice problem generation"""
    print("\n🔹 Testing practice problem generation...")
    
    payload = {
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "count": 1,
        "difficulty": "medium"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/sessions/{session_id}/problems/generate",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Practice problems generated")
        print(f"Number of problems: {len(data['problems'])}")
        if data['problems']:
            problem = data['problems'][0]
            print(f"Sample problem: {problem['question']}")
            return problem['problem_id']
        return True
    else:
        print(f"❌ Problem generation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None

def test_solution_evaluation(session_id: str, problem_id: str):
    """Test solution evaluation"""
    print("\n🔹 Testing solution evaluation...")
    
    payload = {
        "problem_id": problem_id,
        "solution": "x = 2, x = 5"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/sessions/{session_id}/problems/evaluate",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Solution evaluation completed")
        print(f"Is correct: {data['is_correct']}")
        print(f"Performance score: {data['performance_score']}")
        print(f"Feedback (preview): {data['feedback'][:100]}...")
        return True
    else:
        print(f"❌ Solution evaluation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_progress_report(session_id: str):
    """Test progress report generation"""
    print("\n🔹 Testing progress report...")
    
    response = requests.get(f"{API_BASE_URL}/api/sessions/{session_id}/progress")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Progress report generated")
        print(f"Summary: {data['summary']}")
        print(f"Strengths: {data['strengths']}")
        print(f"Areas for improvement: {data['areas_for_improvement'][:3]}...")
        return True
    else:
        print(f"❌ Progress report failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_student_analytics():
    """Test student analytics"""
    print("\n🔹 Testing student analytics...")
    
    response = requests.get(f"{API_BASE_URL}/api/students/{TEST_STUDENT_ID}/analytics")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Student analytics retrieved")
        print(f"Total sessions: {data['total_sessions']}")
        print(f"Total problems solved: {data['total_problems_solved']}")
        print(f"Average score: {data['average_score']:.2f}")
        print(f"Subjects studied: {data['subjects_studied']}")
        return True
    else:
        print(f"❌ Student analytics failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_dashboard_data():
    """Test dashboard data"""
    print("\n🔹 Testing dashboard data...")
    
    response = requests.get(f"{API_BASE_URL}/api/students/{TEST_STUDENT_ID}/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Dashboard data retrieved")
        print(f"Recent activity: {len(data['summary']['recent_activity'])} items")
        print(f"Active sessions: {data['summary']['active_sessions']}")
        return True
    else:
        print(f"❌ Dashboard data failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

def test_utility_endpoints():
    """Test utility endpoints"""
    print("\n🔹 Testing utility endpoints...")
    
    # Test subjects endpoint
    response = requests.get(f"{API_BASE_URL}/api/subjects")
    if response.status_code == 200:
        subjects = response.json()
        print(f"✅ Available subjects: {subjects}")
    else:
        print(f"❌ Subjects endpoint failed: {response.status_code}")
        return False
    
    # Test topics endpoint
    response = requests.get(f"{API_BASE_URL}/api/subjects/Mathematics/topics")
    if response.status_code == 200:
        topics = response.json()
        print(f"✅ Mathematics topics: {topics[:3]}...")
        return True
    else:
        print(f"❌ Topics endpoint failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Educational Tutor API Tests")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API is not running. Please start the FastAPI server first:")
        print("   python app.py")
        return
    
    # Test session creation
    session_id = test_session_creation()
    if not session_id:
        print("\n❌ Cannot proceed without a valid session")
        return
    
    # Add small delay for agent initialization
    print("\n⏳ Waiting for agents to initialize...")
    time.sleep(3)
    
    # Test concept explanation
    test_concept_explanation(session_id)
    
    # Test problem generation
    problem_id = test_problem_generation(session_id)
    
    # Test solution evaluation (if we have a problem)
    if problem_id:
        test_solution_evaluation(session_id, problem_id)
    
    # Test progress report
    test_progress_report(session_id)
    
    # Test student analytics
    test_student_analytics()
    
    # Test dashboard data
    test_dashboard_data()
    
    # Test utility endpoints
    test_utility_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\nTo explore the API interactively, visit:")
    print(f"   {API_BASE_URL}/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc() 