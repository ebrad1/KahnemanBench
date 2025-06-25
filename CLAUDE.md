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
# Python 3.10.11 required
uv pip install -r pyproject.toml
# Set API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
```

### Running Evaluations
```bash
# Single model impersonation
python run_impersonation.py --model_name=gpt-4o --dataset_path=data/kahneman_dataset_v1.json

# Multi-model comparison
python run_multi_impersonation.py --models=gpt-4o,claude-3-opus-20240229 --dataset_path=data/kahneman_dataset_v1.json

# Rating evaluation
python run_rating.py --rater_model=gpt-4o --dataset_path=rating_datasets/[dataset_file]

# Original SimpleBench
python run_benchmark.py --model_name=gpt-4o --dataset_path=simple_bench_public.json
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
- `impersonation_runs/`: Individual model response files
- `rating_datasets/`: Mixed datasets for rating evaluation
- `rating_results_*`: Final evaluation metrics and scores