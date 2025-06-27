#!/usr/bin/env python3
"""
Debug Response Matching Utility for KahnemanBench Dataset

PURPOSE:
This utility script helps debug why specific Q&A responses in the dataset 
may not be matching correctly against their source interview transcripts.
It's useful during dataset curation to verify response authenticity and 
troubleshoot extraction issues.

FUNCTIONALITY:
- Loads a specific Q&A entry from kahneman_dataset_v2.json
- Reads the corresponding interview transcript
- Extracts all Kahneman responses from the transcript
- Calculates similarity scores to find the best match
- Reports matching statistics and potential issues

USAGE:
python scripts/utilities/debug_matching.py
(Edit the kahneman_id at bottom of file to debug specific entries)

CREATED: 2025-06-27 during dataset expansion session
AUTHOR: Generated during KahnemanBench development
"""

import json
import os

def debug_specific_entry(kahneman_id):
    """Debug a specific entry to see why it's not matching."""
    dataset_path = '/Users/edbradon/dev/KahnemanBench/02_curated_datasets/kahneman_dataset_v2.json'
    transcript_dir = '/Users/edbradon/dev/KahnemanBench/01_source_data/interview_transcripts'
    
    # Read the dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find the specific entry
    target_entry = None
    for entry in data:
        if entry['kahneman_id'] == kahneman_id:
            target_entry = entry
            break
    
    if not target_entry:
        print(f"Entry {kahneman_id} not found")
        return
    
    source_doc_id = target_entry['source_doc_id']
    response_text = target_entry['true_kahneman_response']
    
    print(f"Debugging: {kahneman_id}")
    print(f"Source: {source_doc_id}")
    print(f"Response length: {len(response_text)} chars")
    print(f"Response: {response_text[:200]}...")
    print()
    
    # Read transcript
    transcript_path = os.path.join(transcript_dir, f"{source_doc_id}.txt")
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_content = f.read()
    
    # Clean the response text
    clean_response = ' '.join(response_text.split())
    
    # Define possible Kahneman speaker patterns
    kahneman_patterns = [
        'KAHNEMAN:',
        'DANIEL KAHNEMAN:',
        'Daniel Kahneman:',
        'Kahneman:',
        'DK:',
    ]
    
    # Find all Kahneman responses in transcript
    lines = transcript_content.split('\n')
    kahneman_responses = []
    current_response = []
    in_kahneman_response = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_kahneman_response and current_response:
                current_response.append('')
            continue
            
        # Check if this is a Kahneman speaker line
        is_kahneman_line = any(line.startswith(pattern) for pattern in kahneman_patterns)
        
        if is_kahneman_line:
            if current_response:
                kahneman_responses.append('\n'.join(current_response))
            # Extract speech part
            for pattern in kahneman_patterns:
                if line.startswith(pattern):
                    speech_part = line[len(pattern):].strip()
                    current_response = [speech_part] if speech_part else []
                    break
            in_kahneman_response = True
        elif line.startswith(('Morgan:', 'Tyler:', 'Shane:', 'Krista:', 'Fareed:', 'ZAKARIA:', 'HOUSEL:', 'PARRISH:', 'TIPPETT:', 'COWEN:')):
            if current_response:
                kahneman_responses.append('\n'.join(current_response))
                current_response = []
            in_kahneman_response = False
        elif in_kahneman_response:
            current_response.append(line)
    
    # Don't forget the last response
    if current_response:
        kahneman_responses.append('\n'.join(current_response))
    
    print(f"Found {len(kahneman_responses)} Kahneman responses in transcript")
    
    # Try to match
    best_match = None
    best_similarity = 0
    
    for i, response in enumerate(kahneman_responses):
        clean_transcript_response = ' '.join(response.replace('\n', ' ').split())
        
        # Calculate similarity
        response_words = set(clean_response.split())
        transcript_words = set(clean_transcript_response.split())
        
        if not response_words or not transcript_words:
            continue
            
        intersection = len(response_words & transcript_words)
        union = len(response_words | transcript_words)
        similarity = intersection / union if union > 0 else 0
        
        print(f"\nResponse {i+1}:")
        print(f"  Length: {len(clean_transcript_response)} chars")
        print(f"  Similarity: {similarity:.3f}")
        print(f"  Text: {clean_transcript_response[:150]}...")
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = response
    
    print(f"\nBest match similarity: {best_similarity:.3f}")
    if best_match and best_similarity > 0.7:
        print("Best match (with paragraphs):")
        paragraphs = [p.strip() for p in best_match.split('\n') if p.strip()]
        final_response = '\n\n'.join(paragraphs)
        print(final_response)

if __name__ == "__main__":
    # Change this ID to debug specific entries
    debug_specific_entry("motley_fool_2013_3")