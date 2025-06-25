#!/usr/bin/env python3
"""
Integration tests for KahnemanBench pipeline with mock data.
Tests the full pipeline flow without making API calls.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime
from unittest.mock import AsyncMock, patch

# Add scripts directory to path
sys.path.insert(0, 'scripts')

class MockLiteLLMModel:
    """Mock model that returns predefined responses without API calls."""
    
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.temp = kwargs.get('temp', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 1000)
        self.system_prompt = kwargs.get('system_prompt', '')
    
    async def predict(self, prompt):
        """Return a mock response based on the model name."""
        responses = {
            'gpt-4o': "Well, you know, this is a fascinating question that touches on the dual-system theory...",
            'claude-3-opus-20240229': "From a behavioral economics perspective, I would say that...",
            'default': "This is a thoughtful question about human psychology and decision-making..."
        }
        return responses.get(self.model_name, responses['default'])

def create_mock_dataset():
    """Create a small mock dataset for testing."""
    return [
        {
            "kahneman_id": "mock_1",
            "source_doc_id": "test_interview_1",
            "sequence_in_source": 1,
            "question_text": "What do you think about the role of intuition in decision-making?",
            "summarised_context": "Discussion about System 1 vs System 2 thinking",
            "true_kahneman_response": "Intuition is essentially the operation of System 1 - it's fast, automatic, and often quite accurate in familiar domains. However, it can also lead us astray when we're dealing with statistical thinking or unfamiliar situations."
        },
        {
            "kahneman_id": "mock_2", 
            "source_doc_id": "test_interview_1",
            "sequence_in_source": 2,
            "question_text": "How do you view the relationship between happiness and decision-making?",
            "summarised_context": "Discussion about hedonic psychology and well-being",
            "true_kahneman_response": "The relationship is complex. We often make decisions based on predicted happiness, but our predictions are systematically biased. We overestimate both the intensity and duration of future emotional states."
        }
    ]

def test_impersonation_pipeline():
    """Test the impersonation generation pipeline with mock data."""
    print("Testing impersonation pipeline...")
    
    try:
        import run_impersonation
        
        # Create temporary dataset
        mock_data = create_mock_dataset()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_data, f)
            dataset_path = f.name
        
        # Create temporary output directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Mock the LiteLLMModel and weave
            with patch('run_impersonation.LiteLLMModel', MockLiteLLMModel), \
                 patch('run_impersonation.weave') as mock_weave:
                
                # Mock weave.op decorator
                mock_weave.op.return_value = lambda f: f
                mock_weave.init.return_value = None
                
                # Load and process dataset
                questions = run_impersonation.load_kahneman_dataset(dataset_path)
                
                if len(questions) != 2:
                    print(f"✗ Expected 2 questions, got {len(questions)}")
                    return False
                
                # Check that true responses are excluded
                if 'true_kahneman_response' in questions[0]:
                    print("✗ True responses should be excluded from impersonation questions")
                    return False
                
                print("✓ Impersonation pipeline test passed")
                return True
                
        finally:
            # Cleanup
            os.unlink(dataset_path)
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"✗ Impersonation pipeline test failed: {e}")
        return False

def test_rating_pipeline():
    """Test the rating pipeline with mock data."""
    print("Testing rating pipeline...")
    
    try:
        import run_rating
        
        # Create mock rating dataset
        mock_rating_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "models_used": ["gpt-4o", "claude-3-opus-20240229"],
                "dataset_version": "mock_v1.json",
                "total_questions": 1,
                "responses_per_question": 3
            },
            "questions": [
                {
                    "question_id": "mock_1",
                    "source_doc_id": "test_interview_1",
                    "sequence_in_source": 1,
                    "question_text": "What do you think about the role of intuition in decision-making?",
                    "summarised_context": "Discussion about System 1 vs System 2 thinking",
                    "responses": [
                        {
                            "response_id": "mock_1_resp_1",
                            "response_text": "Intuition is essentially the operation of System 1...",
                            "hidden_source": "real_kahneman"
                        },
                        {
                            "response_id": "mock_1_resp_2", 
                            "response_text": "Well, you know, this is a fascinating question...",
                            "hidden_source": "gpt-4o"
                        },
                        {
                            "response_id": "mock_1_resp_3",
                            "response_text": "From a behavioral economics perspective...",
                            "hidden_source": "claude-3-opus-20240229"
                        }
                    ]
                }
            ]
        }
        
        # Create temporary rating dataset file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_rating_data, f)
            rating_dataset_path = f.name
        
        try:
            # Test loading rating dataset
            loaded_data = run_rating.load_rating_dataset(rating_dataset_path)
            
            if len(loaded_data['questions']) != 1:
                print(f"✗ Expected 1 question, got {len(loaded_data['questions'])}")
                return False
            
            question = loaded_data['questions'][0]
            if len(question['responses']) != 3:
                print(f"✗ Expected 3 responses, got {len(question['responses'])}")
                return False
            
            # Test rating output parsing
            mock_rating_output = "Score: 85\nReasoning: This response demonstrates deep understanding of the dual-system theory..."
            score, reasoning = run_rating.parse_rating_output(mock_rating_output)
            
            if score != 85.0:
                print(f"✗ Expected score 85.0, got {score}")
                return False
            
            if not reasoning.startswith("This response demonstrates"):
                print(f"✗ Unexpected reasoning: {reasoning}")
                return False
            
            print("✓ Rating pipeline test passed")
            return True
            
        finally:
            os.unlink(rating_dataset_path)
            
    except Exception as e:
        print(f"✗ Rating pipeline test failed: {e}")
        return False

def test_end_to_end_flow():
    """Test the complete pipeline flow conceptually."""
    print("Testing end-to-end flow...")
    
    try:
        # 1. Source data exists
        if not os.path.exists("01_source_data/interview_transcripts"):
            print("✗ Source transcripts directory missing")
            return False
        
        # 2. Curated dataset exists
        if not os.path.exists("02_curated_datasets/kahneman_dataset_v1.json"):
            print("✗ Curated dataset missing")
            return False
        
        # 3. Output directories exist
        required_dirs = [
            "03_impersonation_runs",
            "04_rating_datasets", 
            "05_rating_results",
            "06_analysis_outputs"
        ]
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                print(f"✗ Output directory {dir_name} missing")
                return False
        
        # 4. Scripts exist in scripts directory
        required_scripts = [
            "scripts/run_impersonation.py",
            "scripts/run_multi_impersonation.py",
            "scripts/run_rating.py"
        ]
        
        for script_path in required_scripts:
            if not os.path.exists(script_path):
                print(f"✗ Script {script_path} missing")
                return False
        
        # 5. Analysis tools exist
        if not os.path.exists("06_analysis_outputs/analyze_ratings.py"):
            print("✗ Analysis script missing")
            return False
            
        if not os.path.exists("06_analysis_outputs/rating_dashboard.html"):
            print("✗ Rating dashboard missing")
            return False
        
        print("✓ End-to-end flow structure test passed")
        return True
        
    except Exception as e:
        print(f"✗ End-to-end flow test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("KahnemanBench Integration Tests")
    print("=" * 40)
    
    tests = [
        test_impersonation_pipeline,
        test_rating_pipeline,
        test_end_to_end_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Integration tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)