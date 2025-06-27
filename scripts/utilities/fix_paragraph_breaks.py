#!/usr/bin/env python3
"""
Paragraph Break Restoration Utility for KahnemanBench Dataset

PURPOSE:
This utility fixes paragraph breaks in kahneman_dataset_v2.json by matching
responses against their original interview transcripts. Natural paragraph
breaks are crucial for maintaining Kahneman's authentic speaking rhythm
and improving AI impersonation quality.

PROBLEM SOLVED:
During dataset curation, paragraph breaks were sometimes lost when extracting
Q&A pairs, resulting in wall-of-text responses that don't reflect Kahneman's
natural speech patterns with pauses and thought breaks.

FUNCTIONALITY:
- Reads the complete dataset from kahneman_dataset_v2.json
- For each entry, locates the corresponding interview transcript
- Uses text similarity matching to find the original response
- Restores proper paragraph breaks (double newlines) 
- Creates backup and saves updated dataset

SAFETY FEATURES:
- Creates backup before modifying original dataset
- Uses Jaccard similarity and containment matching for robustness
- Reports detailed statistics on fixes and errors
- Handles various transcript speaker naming conventions

USAGE:
python scripts/utilities/fix_paragraph_breaks.py

WARNING: This modifies the dataset file! Always review changes carefully.

CREATED: 2025-06-27 during dataset expansion session  
AUTHOR: Generated during KahnemanBench development
"""

import json
import os
import re
from pathlib import Path

def read_transcript(transcript_path):
    """Read a transcript file and return its content."""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {transcript_path}: {e}")
        return None

def find_response_with_paragraphs(transcript_content, response_text):
    """
    Find the original response in the transcript with paragraph breaks intact.
    
    Args:
        transcript_content: Full text of the interview transcript
        response_text: The response text we want to find (may lack paragraph breaks)
        
    Returns:
        String with proper paragraph breaks, or None if no match found
    """
    # Clean the response text for matching (remove extra whitespace, normalize)
    clean_response = ' '.join(response_text.split())
    
    # Split transcript into lines
    lines = transcript_content.split('\n')
    
    # Define possible Kahneman speaker patterns across different transcript formats
    kahneman_patterns = [
        'KAHNEMAN:',
        'DANIEL KAHNEMAN:',
        'Daniel Kahneman:',
        'Kahneman:',
        'DK:',  # Sometimes abbreviated
        'DANIEL KAHNEMAN, PHD',  # Sometimes with titles
    ]
    
    # Define interviewer patterns to detect speaker transitions
    interviewer_patterns = [
        'ZAKARIA:', 'HOUSEL:', 'PARRISH:', 'TIPPETT:', 'COWEN:',
        'Morgan:', 'Tyler:', 'Shane:', 'Krista:', 'Fareed:',
        'TYLER COWEN:', 'SHANE PARRISH:', 'KRISTA TIPPETT:',
        'MORGAN HOUSEL:', 'FAREED ZAKARIA:',
    ]
    
    # Find lines that start with Kahneman speaker indicators
    kahneman_responses = []
    current_response = []
    in_kahneman_response = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_kahneman_response and current_response:
                # Empty line indicates paragraph break within response
                current_response.append('')
            continue
            
        # Check if this is a Kahneman speaker line
        is_kahneman_line = any(line.startswith(pattern) for pattern in kahneman_patterns)
        is_interviewer_line = any(line.startswith(pattern) for pattern in interviewer_patterns)
        
        if is_kahneman_line:
            if current_response:
                # Save previous response
                kahneman_responses.append('\n'.join(current_response))
            # Extract the actual speech part (after the speaker indicator)
            for pattern in kahneman_patterns:
                if line.startswith(pattern):
                    speech_part = line[len(pattern):].strip()
                    current_response = [speech_part] if speech_part else []
                    break
            in_kahneman_response = True
        elif is_interviewer_line:
            # Different speaker, end current response
            if current_response:
                kahneman_responses.append('\n'.join(current_response))
                current_response = []
            in_kahneman_response = False
        elif in_kahneman_response:
            # Continue current response
            current_response.append(line)
    
    # Don't forget the last response
    if current_response:
        kahneman_responses.append('\n'.join(current_response))
    
    # Now try to match the clean response text to one of these responses
    for response in kahneman_responses:
        # Clean the transcript response for comparison
        clean_transcript_response = ' '.join(response.replace('\n', ' ').split())
        
        # Check if this matches our target response (allowing for minor differences)
        # Calculate word overlap similarity
        response_words = set(clean_response.split())
        transcript_words = set(clean_transcript_response.split())
        
        if not response_words or not transcript_words:
            continue
            
        # Jaccard similarity (intersection over union)
        intersection = len(response_words & transcript_words)
        union = len(response_words | transcript_words)
        jaccard_similarity = intersection / union if union > 0 else 0
        
        # Also check for direct containment (for shorter responses)
        containment_match = (clean_response in clean_transcript_response or 
                           clean_transcript_response in clean_response)
        
        # Use a lower threshold since we're doing word-level matching
        if jaccard_similarity > 0.7 or containment_match:
            
            # Return the response with paragraph breaks (double newlines)
            paragraphs = [p.strip() for p in response.split('\n') if p.strip()]
            return '\n\n'.join(paragraphs)
    
    return None

def fix_paragraph_breaks():
    """Main function to fix paragraph breaks in the dataset."""
    dataset_path = '/Users/edbradon/dev/KahnemanBench/02_curated_datasets/kahneman_dataset_v2.json'
    transcript_dir = '/Users/edbradon/dev/KahnemanBench/01_source_data/interview_transcripts'
    
    # Read the dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} entries...")
    
    fixed_count = 0
    errors = []
    
    for i, entry in enumerate(data):
        source_doc_id = entry['source_doc_id']
        kahneman_id = entry['kahneman_id']
        current_response = entry['true_kahneman_response']
        
        # Construct transcript file path
        transcript_path = os.path.join(transcript_dir, f"{source_doc_id}.txt")
        
        if not os.path.exists(transcript_path):
            errors.append(f"Transcript not found for {kahneman_id}: {transcript_path}")
            continue
        
        # Read transcript
        transcript_content = read_transcript(transcript_path)
        if not transcript_content:
            errors.append(f"Could not read transcript for {kahneman_id}")
            continue
        
        # Find the response with proper paragraph breaks
        fixed_response = find_response_with_paragraphs(transcript_content, current_response)
        
        if fixed_response and fixed_response != current_response:
            # Update the response
            data[i]['true_kahneman_response'] = fixed_response
            fixed_count += 1
            print(f"Fixed {kahneman_id}")
            print(f"  Original: {current_response[:100]}...")
            print(f"  Fixed:    {fixed_response[:100]}...")
            print()
        elif not fixed_response:
            errors.append(f"Could not find matching response for {kahneman_id}")
    
    # Save the updated dataset
    backup_path = dataset_path.replace('.json', '_backup.json')
    os.rename(dataset_path, backup_path)
    print(f"Backed up original to: {backup_path}")
    
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nCompleted!")
    print(f"Fixed: {fixed_count} entries")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

if __name__ == "__main__":
    fix_paragraph_breaks()