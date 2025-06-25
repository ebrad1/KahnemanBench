#!/usr/bin/env python3
"""
Test that the updated impersonation prompt properly eliminates stage directions.
This test verifies the prompt content without making API calls.
"""

import os
import sys

def test_prompt_content():
    """Test that the impersonation prompt includes stage direction prohibitions."""
    print("Testing impersonation prompt content...")
    
    prompt_path = "prompt_library/kahneman_impersonation_prompt.txt"
    
    if not os.path.exists(prompt_path):
        print(f"✗ Prompt file not found: {prompt_path}")
        return False
    
    try:
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
        
        # Check for key prohibition phrases (case insensitive)
        required_prohibitions = [
            "stage directions",
            "asterisks", 
            "*pauses*",
            "*chuckles*",
            "*thinks for a moment*",
            "only your spoken words",
            "interview transcript"
        ]
        
        missing_prohibitions = []
        for prohibition in required_prohibitions:
            if prohibition.lower() not in prompt_content.lower():
                missing_prohibitions.append(prohibition)
        
        if missing_prohibitions:
            print(f"✗ Missing prohibitions in prompt: {missing_prohibitions}")
            return False
        
        # Check that the prohibitions are in the IMPORTANT section
        important_section = prompt_content.split("IMPORTANT:")[1].split("\n\n")[0]
        
        key_checks = ["stage directions", "asterisks", "spoken words"]
        for check in key_checks:
            if check.lower() not in important_section.lower():
                print(f"✗ '{check}' not found in IMPORTANT section")
                return False
        
        print("✓ Prompt contains comprehensive stage direction prohibitions")
        return True
        
    except Exception as e:
        print(f"✗ Failed to read prompt file: {e}")
        return False

def test_prompt_structure():
    """Test that the prompt maintains its expected structure."""
    print("Testing prompt structure...")
    
    prompt_path = "prompt_library/kahneman_impersonation_prompt.txt"
    
    try:
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
        
        # Check for expected sections
        expected_sections = [
            "You are Daniel Kahneman",
            "IMPORTANT:",
            "Key aspects of your personality",
            "Key concepts you frequently discuss",
            "Your background and collaborations",
            "Speaking patterns"
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in prompt_content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"✗ Missing sections in prompt: {missing_sections}")
            return False
        
        print("✓ Prompt maintains expected structure")
        return True
        
    except Exception as e:
        print(f"✗ Failed to analyze prompt structure: {e}")
        return False

def simulate_stage_direction_detection():
    """Simulate checking for stage directions in responses."""
    print("Testing stage direction detection patterns...")
    
    # Examples of responses that should be flagged
    bad_examples = [
        "*pauses to think* Well, you know, this is interesting...",
        "This is a good question. *chuckles* I think that...",
        "Well, *thinks for a moment*, the answer is complex...",
        "(pauses) You know, in my experience...",
        "*smiles* That's exactly what Amos and I discovered..."
    ]
    
    # Examples of responses that should be acceptable
    good_examples = [
        "Well, you know, this is interesting...",
        "This is a good question. I think that...",
        "Well, the answer is complex...",
        "You know, in my experience...",
        "That's exactly what Amos and I discovered..."
    ]
    
    import re
    
    # Pattern to detect stage directions
    stage_direction_pattern = r'(\*[^*]+\*|\([^)]*pause[^)]*\)|\([^)]*think[^)]*\)|\([^)]*chuckle[^)]*\))'
    
    # Test bad examples (should be detected)
    bad_detected = 0
    for example in bad_examples:
        if re.search(stage_direction_pattern, example, re.IGNORECASE):
            bad_detected += 1
    
    # Test good examples (should not be detected)
    good_clean = 0
    for example in good_examples:
        if not re.search(stage_direction_pattern, example, re.IGNORECASE):
            good_clean += 1
    
    if bad_detected == len(bad_examples) and good_clean == len(good_examples):
        print(f"✓ Stage direction detection works correctly")
        print(f"  - Detected {bad_detected}/{len(bad_examples)} problematic examples")
        print(f"  - Clean on {good_clean}/{len(good_examples)} good examples")
        return True
    else:
        print(f"✗ Stage direction detection issues:")
        print(f"  - Detected {bad_detected}/{len(bad_examples)} problematic examples") 
        print(f"  - Clean on {good_clean}/{len(good_examples)} good examples")
        return False

def main():
    """Run all prompt-related tests."""
    print("KahnemanBench Prompt Update Tests")
    print("=" * 40)
    
    tests = [
        test_prompt_content,
        test_prompt_structure,
        simulate_stage_direction_detection
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
    print(f"Prompt tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All prompt tests passed!")
        print("\nThe updated prompt should eliminate stage directions in AI responses.")
        print("Next impersonation runs should produce cleaner, more authentic responses.")
        return True
    else:
        print("❌ Some prompt tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)