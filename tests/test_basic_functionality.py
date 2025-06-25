#!/usr/bin/env python3
"""
Basic functionality tests for KahnemanBench without making API calls.
Run with: python test_basic_functionality.py
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add both the root directory and scripts directory to path
sys.path.insert(0, '.')  # Root directory for weave_utils
sys.path.insert(0, 'scripts')  # Scripts directory

def test_imports():
    """Test that all main scripts can be imported without errors."""
    print("Testing script imports...")
    
    try:
        import importlib.util
        
        # Import run_impersonation
        spec = importlib.util.spec_from_file_location("run_impersonation", "scripts/run_impersonation.py")
        run_impersonation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_impersonation)
        print("✓ run_impersonation imported successfully")
        
        # Import run_multi_impersonation  
        spec = importlib.util.spec_from_file_location("run_multi_impersonation", "scripts/run_multi_impersonation.py")
        run_multi_impersonation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_multi_impersonation)
        print("✓ run_multi_impersonation imported successfully")
        
        # Import run_rating
        spec = importlib.util.spec_from_file_location("run_rating", "scripts/run_rating.py")
        run_rating = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_rating)
        print("✓ run_rating imported successfully")
        
    except Exception as e:
        print(f"✗ Script import failed: {e}")
        return False
    
    try:
        from weave_utils.models import LiteLLMModel
        print("✓ weave_utils.models imported successfully")
    except Exception as e:
        print(f"✗ weave_utils.models import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that the new file structure exists."""
    print("\nTesting file structure...")
    
    expected_dirs = [
        "01_source_data",
        "02_curated_datasets", 
        "03_impersonation_runs",
        "04_rating_datasets",
        "05_rating_results",
        "06_analysis_outputs",
        "scripts",
        "prompt_library",
        "weave_utils"
    ]
    
    all_exist = True
    for dir_name in expected_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name} exists")
        else:
            print(f"✗ {dir_name} missing")
            all_exist = False
    
    return all_exist

def test_dataset_loading():
    """Test that we can load the main dataset."""
    print("\nTesting dataset loading...")
    
    dataset_path = "02_curated_datasets/kahneman_dataset_v1.json"
    
    if not os.path.exists(dataset_path):
        print(f"✗ Dataset not found at {dataset_path}")
        return False
    
    try:
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("✗ Dataset is not a list")
            return False
        
        if len(data) == 0:
            print("✗ Dataset is empty")
            return False
        
        # Check first item has expected fields
        first_item = data[0]
        expected_fields = ['kahneman_id', 'question_text', 'true_kahneman_response']
        
        for field in expected_fields:
            if field not in first_item:
                print(f"✗ Missing field '{field}' in dataset")
                return False
        
        print(f"✓ Dataset loaded successfully ({len(data)} questions)")
        return True
        
    except Exception as e:
        print(f"✗ Failed to load dataset: {e}")
        return False

def test_model_initialization():
    """Test that we can initialize models without API calls."""
    print("\nTesting model initialization...")
    
    try:
        from weave_utils.models import LiteLLMModel
        
        # Create a simple model instance (shouldn't make API calls)
        model = LiteLLMModel(
            model_name="gpt-4o",
            temp=0.7,
            max_tokens=100,
            system_prompt="Test prompt"
        )
        
        print(f"✓ LiteLLMModel created successfully (model: {model.model_name})")
        return True
        
    except Exception as e:
        print(f"✗ Model initialization failed: {e}")
        return False

def test_data_processing_functions():
    """Test key data processing functions with mock data."""
    print("\nTesting data processing functions...")
    
    try:
        # Import the functions we want to test using importlib
        import importlib.util
        
        # Import run_impersonation
        spec = importlib.util.spec_from_file_location("run_impersonation", "scripts/run_impersonation.py")
        run_impersonation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_impersonation)
        
        # Import run_multi_impersonation
        spec = importlib.util.spec_from_file_location("run_multi_impersonation", "scripts/run_multi_impersonation.py")
        run_multi_impersonation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_multi_impersonation)
        
        # Test dataset loading function
        mock_data = [
            {
                "kahneman_id": "test_1",
                "source_doc_id": "test_doc",
                "sequence_in_source": 1,
                "question_text": "Test question?",
                "summarised_context": "Test context",
                "true_kahneman_response": "Test response"
            }
        ]
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_data, f)
            temp_path = f.name
        
        try:
            # Test loading functions
            questions = run_impersonation.load_kahneman_dataset(temp_path)
            if len(questions) == 1 and questions[0]['kahneman_id'] == 'test_1':
                print("✓ run_impersonation.load_kahneman_dataset works")
            else:
                print("✗ run_impersonation.load_kahneman_dataset failed")
                return False
            
            full_data = run_multi_impersonation.load_kahneman_dataset(temp_path)
            if len(full_data) == 1 and full_data[0]['true_kahneman_response'] == 'Test response':
                print("✓ run_multi_impersonation.load_kahneman_dataset works")
            else:
                print("✗ run_multi_impersonation.load_kahneman_dataset failed")
                return False
                
        finally:
            # Clean up temp file
            os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Data processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("KahnemanBench Basic Functionality Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_file_structure,
        test_dataset_loading,
        test_model_initialization,
        test_data_processing_functions
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
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The reorganization was successful.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)