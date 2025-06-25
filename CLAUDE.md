# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KahnemanBench is an AI benchmark that evaluates models' ability to impersonate Daniel Kahneman's interview responses and assess "behavioral science taste." It uses Weave (W&B's evaluation framework) for experiment tracking and supports multiple AI model providers via LiteLLM.

## Core Architecture

### Main Evaluation Scripts
- `run_impersonation.py`: Single-model Kahneman impersonation evaluation
- `run_multi_impersonation.py`: Multi-model comparison that generates rating datasets
- `run_rating.py`: Evaluates authenticity of responses using AI raters
- `run_benchmark.py`: Original SimpleBench multiple-choice evaluation

### Key Components
- `weave_utils/models.py`: Model wrappers including `LiteLLMModel` and `MajorityVoteModel`
- `weave_utils/scorers.py`: Evaluation functions for multiple-choice scoring
- `data/kahneman_dataset_v1.json`: Core dataset with interview questions and true responses
- `prompt_library/`: Contains impersonation and rating prompts

### Data Flow
1. Questions from `kahneman_dataset_v1.json` → AI model responses
2. Multi-model runs create mixed datasets (real + AI responses)
3. Rater models evaluate authenticity (0-100 scores)
4. Results saved to `rating_results_*` files

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install anthropic fire litellm openai python-dotenv weave

# Set API keys in .env file or environment
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
# etc.
```

### Running Evaluations

#### Full Pipeline (Recommended)
```bash
# Activate environment first
source venv/bin/activate

# Quick test with 2 models
python scripts/run_full_pipeline.py --config=configs/quick_test.yaml

# Comprehensive evaluation with all models
python scripts/run_full_pipeline.py --config=configs/comprehensive.yaml

# Custom model selection
python scripts/run_full_pipeline.py --models=gpt-4o,claude-3-5-sonnet --rater_model=gpt-4o

# Rating only (skip impersonation)
python scripts/run_full_pipeline.py --skip_impersonation --rating_dataset_path=04_rating_datasets/[dataset_file] --rater_model=gpt-4o
```

#### Individual Scripts
```bash
# Single model impersonation
python scripts/run_impersonation.py --model_name=gpt-4o

# Multi-model comparison  
python scripts/run_multi_impersonation.py --models=gpt-4o,claude-3-opus-20240229

# Rating evaluation
python scripts/run_rating.py --rater_model=gpt-4o --dataset_path=04_rating_datasets/[dataset_file]

# Original SimpleBench
python scripts/run_benchmark.py --model_name=gpt-4o --dataset_path=simple_bench_public.json

# Generate analysis dashboard
python 06_analysis_outputs/analyze_ratings.py --rating_dir=05_rating_results
```

### Testing
```bash
# Quick structure test (no dependencies needed)
python3 tests/test_structure_only.py

# Full functionality tests (requires venv activation)
source venv/bin/activate
python3 tests/test_basic_functionality.py
python3 tests/test_integration.py

# Pipeline automation tests
python3 tests/test_pipeline.py
```

## Key Data Structures

### Dataset Format
Each question contains:
- `kahneman_id`: Unique identifier
- `source_doc_id`: Interview source reference
- `question_text`: The interview question
- `summarised_context`: Interview context
- `true_kahneman_response`: Kahneman's actual response

### Model Configuration
Models are configured in `weave_utils/models.py` with comprehensive mapping for current models (GPT-4o, Claude-4, O3, etc.). All API calls use async/await for efficiency.

## Output Locations
- `03_impersonation_runs/`: Individual model response files
- `04_rating_datasets/`: Mixed datasets for rating evaluation  
- `05_rating_results/`: Final evaluation metrics and scores
- `06_analysis_outputs/`: Dashboards and analysis tools

## Complete Pipeline Flow

The KahnemanBench evaluation follows this end-to-end pipeline:

### Stage 1: Source Data Preparation
- **Raw materials**: 28 interview transcript files in `data/interview_transcripts/`
- **Manual curation**: Extract Q&A pairs into `data/kahneman_dataset_v1.json` (10 questions)
- **Context**: Each question includes interview context and source attribution

### Stage 2: AI Impersonation Generation
- **Single model**: `run_impersonation.py` generates responses for one model
- **Multi-model**: `run_multi_impersonation.py` generates responses across multiple models
- **Output**: Individual model files in `impersonation_runs/` with metadata and responses

### Stage 3: Rating Dataset Creation
- **Process**: Multi-model runs automatically create mixed datasets
- **Content**: Shuffle real Kahneman responses with AI-generated ones
- **Output**: Anonymous datasets in `rating_datasets/` for blind evaluation

### Stage 4: Authenticity Rating
- **Script**: `run_rating.py` with AI rater models
- **Process**: Score each response 0-100 for authenticity without knowing source
- **Output**: Detailed results in `rating_results/` with model comparisons

### Stage 5: Analysis & Interpretation
- **Tools**: `analyze_ratings.py` and `rating_dashboard.html`
- **Metrics**: Score gaps between real/AI responses, model rankings
- **Future**: Academic paper and website publication with potential human ratings

## Suggested Organizational Improvements

### File Naming Standardization
- **Impersonation runs**: `impersonation_{model}_{timestamp}.json`
- **Rating datasets**: `rating_dataset_{timestamp}.json` 
- **Rating results**: `rating_results_{rater_model}_{timestamp}.json`

### Folder Structure Enhancements
```
KahnemanBench/
├── 01_source_data/           # Raw transcripts and metadata
├── 02_curated_datasets/      # Structured Q&A datasets
├── 03_impersonation_runs/    # AI-generated responses
├── 04_rating_datasets/       # Mixed datasets for evaluation
├── 05_rating_results/        # Final evaluation scores
├── 06_analysis_outputs/      # Dashboards, reports, visualizations
├── archive/                  # Completed experiment runs
└── scripts/                  # All run_*.py and analysis scripts
```

### Integration Opportunities
1. **Automated pipeline**: Script to process transcripts → structured dataset
2. **Integrated dashboard**: Auto-generate `rating_dashboard.html` after rating runs
3. **Experiment tracking**: Metadata files linking related runs across stages
4. **Archive management**: Organize completed experiments by date/purpose