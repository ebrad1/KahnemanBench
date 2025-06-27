# Utilities

This folder contains utility scripts for KahnemanBench dataset maintenance and debugging.

## Scripts

### `debug_matching.py`
**Purpose**: Debug response matching issues during dataset curation

Helps troubleshoot why specific Q&A responses may not be matching correctly against their source interview transcripts. Useful for verifying response authenticity and diagnosing extraction problems.

**Usage**:
```bash
python scripts/utilities/debug_matching.py
```
(Edit the `kahneman_id` at the bottom of the file to debug specific entries)

**Features**:
- Loads specific Q&A entries from the dataset
- Extracts all Kahneman responses from corresponding transcripts
- Calculates similarity scores using Jaccard similarity
- Reports matching statistics and potential issues

### `fix_paragraph_breaks.py`
**Purpose**: Restore natural paragraph breaks in dataset responses

Fixes paragraph breaks in `kahneman_dataset_v2.json` by matching responses against original interview transcripts. This preserves Kahneman's authentic speaking rhythm with natural pauses and thought breaks.

**Usage**:
```bash
python scripts/utilities/fix_paragraph_breaks.py
```

**⚠️ Warning**: This script modifies the dataset file! It creates a backup first, but always review changes carefully.

**Features**:
- Processes entire dataset automatically
- Uses robust text similarity matching (Jaccard + containment)
- Handles various transcript speaker naming conventions
- Creates backup before making changes
- Reports detailed statistics on fixes and errors

## Safety Notes

- Both scripts create backups before making modifications
- Always review changes before committing to git
- Test on individual entries with `debug_matching.py` before running batch operations
- These utilities were created during the 2025-06-27 dataset expansion session

## Development

These utilities can serve as templates for additional dataset maintenance tools. Common patterns include:
- Loading dataset and transcript files
- Text similarity matching algorithms
- Speaker pattern recognition across different transcript formats
- Safe file modification with backups