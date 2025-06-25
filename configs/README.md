# Pipeline Configuration Files

This directory contains pre-configured YAML files for common evaluation scenarios.

## Available Configurations

### `quick_test.yaml`
**Purpose**: Fast testing and development  
**Models**: gpt-4o, claude-3-5-sonnet  
**Use case**: Quick validation of changes, debugging pipeline issues

```bash
python scripts/run_full_pipeline.py --config=configs/quick_test.yaml
```

### `comprehensive.yaml`
**Purpose**: Full evaluation across all major models  
**Models**: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, claude-3-haiku, claude-3-opus-20240229  
**Use case**: Research, publication, comprehensive model comparison

```bash
python scripts/run_full_pipeline.py --config=configs/comprehensive.yaml
```

### `gpt_vs_claude.yaml`
**Purpose**: Direct comparison between model families  
**Models**: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, claude-3-opus-20240229  
**Use case**: Comparative studies between OpenAI and Anthropic models

```bash
python scripts/run_full_pipeline.py --config=configs/gpt_vs_claude.yaml
```

### `rating_only.yaml`
**Purpose**: Skip impersonation, only run rating evaluation  
**Models**: None (uses existing dataset)  
**Use case**: Re-evaluate existing responses with different rater models

```bash
# First, update the rating_dataset_path in the config file
python scripts/run_full_pipeline.py --config=configs/rating_only.yaml
```

## Configuration Format

```yaml
# Configuration name and description
name: "Configuration Name"
description: "What this configuration is for"

# Models for impersonation generation
models:
  - "gpt-4o"
  - "claude-3-5-sonnet"

# Model for rating evaluation
rater_model: "gpt-4o"

# Dataset path (usually the same)
dataset_path: "02_curated_datasets/kahneman_dataset_v1.json"

# Pipeline options
skip_impersonation: false  # Set to true to skip to rating step
rating_dataset_path: null  # Required if skip_impersonation=true

# Weave project suffix
project_suffix: "_config_name"
```

## Creating Custom Configurations

1. Copy an existing config file
2. Modify the `models` list and `rater_model`
3. Update `name`, `description`, and `project_suffix`
4. Save with a descriptive filename

## Command Line Override

You can override config values from the command line:

```bash
# Use config but override rater model
python scripts/run_full_pipeline.py --config=configs/quick_test.yaml --rater_model=claude-3-5-sonnet

# Use config but add more models
python scripts/run_full_pipeline.py --config=configs/quick_test.yaml --models=gpt-4o,claude-3-5-sonnet,claude-3-opus-20240229
```