#!/usr/bin/env python3
"""
Structure-only tests for KahnemanBench that don't require external dependencies.
Run with: python3 test_structure_only.py
"""

import os
import json

def test_file_structure():
    """Test that the new file structure exists."""
    print("Testing file structure...")
    
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

def test_script_syntax():
    """Test that all Python scripts have valid syntax."""
    print("\nTesting script syntax...")
    
    script_files = [
        "scripts/run_impersonation.py",
        "scripts/run_multi_impersonation.py", 
        "scripts/run_rating.py",
        "scripts/run_benchmark.py"
    ]
    
    all_valid = True
    for script_path in script_files:
        if not os.path.exists(script_path):
            print(f"✗ {script_path} not found")
            all_valid = False
            continue
            
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Try to compile the script
            compile(content, script_path, 'exec')
            print(f"✓ {script_path} has valid syntax")
            
        except SyntaxError as e:
            print(f"✗ {script_path} has syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"✗ {script_path} failed to read: {e}")
            all_valid = False
    
    return all_valid

def test_data_files():
    """Test that key data files exist and are readable."""
    print("\nTesting data files...")
    
    key_files = [
        "02_curated_datasets/kahneman_dataset_v1.json",
        "01_source_data/sources_metadata.json",
        "prompt_library/kahneman_impersonation_prompt.txt",
        "prompt_library/kahneman_rater_prompt.txt"
    ]
    
    all_exist = True
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                if len(content) > 0:
                    print(f"✓ {file_path} exists and readable")
                else:
                    print(f"✗ {file_path} is empty")
                    all_exist = False
            except Exception as e:
                print(f"✗ {file_path} failed to read: {e}")
                all_exist = False
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_path_updates():
    """Test that scripts use the new paths."""
    print("\nTesting path updates in scripts...")
    
    # Check that scripts reference new paths
    path_tests = [
        ("scripts/run_impersonation.py", "02_curated_datasets/kahneman_dataset_v1.json"),
        ("scripts/run_multi_impersonation.py", "02_curated_datasets/kahneman_dataset_v1.json"),
        ("scripts/run_rating.py", "04_rating_datasets/"),
        ("scripts/run_impersonation.py", "03_impersonation_runs/"),
        ("scripts/run_multi_impersonation.py", "03_impersonation_runs/"),
        ("scripts/run_rating.py", "05_rating_results")
    ]
    
    all_updated = True
    for script_path, expected_path in path_tests:
        if not os.path.exists(script_path):
            print(f"✗ {script_path} not found")
            all_updated = False
            continue
            
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            if expected_path in content:
                print(f"✓ {script_path} uses {expected_path}")
            else:
                print(f"✗ {script_path} missing reference to {expected_path}")
                all_updated = False
                
        except Exception as e:
            print(f"✗ Failed to check {script_path}: {e}")
            all_updated = False
    
    return all_updated

def main():
    """Run all structure tests."""
    print("KahnemanBench Structure Tests")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_dataset_loading,
        test_script_syntax,
        test_data_files,
        test_path_updates
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
        print("🎉 All structure tests passed! The reorganization was successful.")
        print("\nYou can now run the scripts with the new paths:")
        print("  python scripts/run_impersonation.py --model_name=gpt-4o")
        print("  python scripts/run_multi_impersonation.py --models=gpt-4o,claude-3-opus-20240229")
        print("  python scripts/run_rating.py --rater_model=gpt-4o")
        return True
    else:
        print("❌ Some structure tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)