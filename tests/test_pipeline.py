#!/usr/bin/env python3
"""
Tests for pipeline automation functionality.
These tests verify the pipeline components work correctly without making API calls.
"""

import sys
import os
import json
import tempfile
import yaml
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

def test_pipeline_config_loading():
    """Test that pipeline can load YAML configurations correctly."""
    print("Testing pipeline config loading...")
    
    try:
        import importlib.util
        
        # Import pipeline
        spec = importlib.util.spec_from_file_location("run_full_pipeline", "scripts/run_full_pipeline.py")
        pipeline_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pipeline_module)
        
        # Test config loading
        runner = pipeline_module.PipelineRunner()
        
        # Create test config
        test_config = {
            "models": ["gpt-4o", "claude-3-5-sonnet"],
            "rater_model": "gpt-4o",
            "dataset_path": "02_curated_datasets/kahneman_dataset_v1.json"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_path = f.name
        
        try:
            loaded_config = runner.load_config(config_path)
            
            if loaded_config == test_config:
                print("✓ Config loading works correctly")
                return True
            else:
                print(f"✗ Config mismatch: {loaded_config} != {test_config}")
                return False
                
        finally:
            os.unlink(config_path)
            
    except Exception as e:
        print(f"✗ Config loading test failed: {e}")
        return False

def test_existing_configs():
    """Test that all provided config files are valid."""
    print("Testing existing config files...")
    
    config_files = [
        "configs/quick_test.yaml",
        "configs/comprehensive.yaml",
        "configs/rating_only.yaml",
        "configs/gpt_vs_claude.yaml"
    ]
    
    all_valid = True
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"✗ Config file missing: {config_file}")
            all_valid = False
            continue
            
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check required fields
            if 'models' in config or 'skip_impersonation' in config:
                print(f"✓ {config_file} is valid")
            else:
                print(f"✗ {config_file} missing required fields")
                all_valid = False
                
        except Exception as e:
            print(f"✗ {config_file} failed to load: {e}")
            all_valid = False
    
    return all_valid

def test_pipeline_initialization():
    """Test that pipeline runner can be initialized correctly."""
    print("Testing pipeline initialization...")
    
    try:
        import importlib.util
        
        # Import pipeline
        spec = importlib.util.spec_from_file_location("run_full_pipeline", "scripts/run_full_pipeline.py")
        pipeline_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pipeline_module)
        
        # Create pipeline runner
        runner = pipeline_module.PipelineRunner()
        
        # Check initialization
        if hasattr(runner, 'run_id') and hasattr(runner, 'results'):
            print(f"✓ Pipeline runner initialized (ID: {runner.run_id})")
            return True
        else:
            print("✗ Pipeline runner missing required attributes")
            return False
            
    except Exception as e:
        print(f"✗ Pipeline initialization failed: {e}")
        return False

def test_logging_functionality():
    """Test that pipeline logging works correctly."""
    print("Testing pipeline logging...")
    
    try:
        import importlib.util
        
        # Import pipeline
        spec = importlib.util.spec_from_file_location("run_full_pipeline", "scripts/run_full_pipeline.py")
        pipeline_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pipeline_module)
        
        # Create pipeline runner
        runner = pipeline_module.PipelineRunner()
        
        # Test logging
        runner.log_step("test_step", "completed", {"test": "data"})
        
        # Check that step was logged
        if len(runner.results["steps_completed"]) == 1:
            step = runner.results["steps_completed"][0]
            if step["step"] == "test_step" and step["status"] == "completed":
                print("✓ Pipeline logging works correctly")
                return True
            else:
                print("✗ Logged step data incorrect")
                return False
        else:
            print("✗ Step not logged correctly")
            return False
            
    except Exception as e:
        print(f"✗ Pipeline logging test failed: {e}")
        return False

def test_analyze_ratings_integration():
    """Test that analyze_ratings.py can be called correctly."""
    print("Testing analyze_ratings integration...")
    
    try:
        import importlib.util
        
        # Import analyze_ratings
        spec = importlib.util.spec_from_file_location("analyze_ratings", "06_analysis_outputs/analyze_ratings.py")
        analyze_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analyze_module)
        
        # Check that main function exists and has expected parameters
        import inspect
        main_sig = inspect.signature(analyze_module.main)
        
        expected_params = ['rating_dir', 'output_path', 'rating_results', 'update_dashboard']
        actual_params = list(main_sig.parameters.keys())
        
        if all(param in actual_params for param in expected_params):
            print("✓ analyze_ratings has correct interface for pipeline integration")
            return True
        else:
            print(f"✗ analyze_ratings missing expected parameters. Has: {actual_params}")
            return False
            
    except Exception as e:
        print(f"✗ analyze_ratings integration test failed: {e}")
        return False

def main():
    """Run all pipeline tests."""
    print("KahnemanBench Pipeline Tests")
    print("=" * 40)
    
    tests = [
        test_pipeline_initialization,
        test_logging_functionality,
        test_pipeline_config_loading,
        test_existing_configs,
        test_analyze_ratings_integration
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
    print(f"Pipeline tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All pipeline tests passed!")
        print("\nYou can now run the pipeline with:")
        print("  python scripts/run_full_pipeline.py --config=configs/quick_test.yaml")
        return True
    else:
        print("❌ Some pipeline tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)