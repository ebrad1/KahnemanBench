# KahnemanBench Development Plan

## Current Status
✅ **Phase 1 (Dataset Curation)** - COMPLETED  
✅ **Phase 2 (AI Impersonator Development)** - COMPLETED  
We have successfully built a complete impersonation pipeline that can generate Kahneman-style responses from multiple models and prepare them for rating.

## Completed Work Summary

### Phase 0-1: Foundation & Dataset ✅
- Forked SimpleBench and adapted infrastructure
- Created 10-question Kahneman dataset with summarized contexts
- Set up Weave integration and API connections

### Phase 2: AI Impersonation ✅
- Built comprehensive Kahneman impersonation prompt
- Created single-model impersonation script (`run_impersonation.py`)
- Developed multi-model runner (`run_multi_impersonation.py`)
- Successfully tested with GPT-4o and Claude-3-Opus
- Generated rating-ready datasets with randomized responses

## Phase 3: AI Rater Development - **NEXT**

### 3.1 Define Rating Criteria
- **Authenticity Score (1-10)**: How much does this sound like Kahneman?
- **Key Indicators to Check**:
  - Use of uncertainty markers ("I don't know", "My guess is")
  - References to Amos Tversky and collaborative work
  - Specific examples and studies
  - Intellectual humility
  - Precision without jargon
  - System 1/System 2 framework usage

### 3.2 Develop Rater Prompts
- Create `prompt_library/kahneman_rater_prompt.txt`
- Include examples of authentic vs non-authentic responses
- Specify scoring rubric
- Handle edge cases (e.g., responses with stage directions like *pauses*)

### 3.3 Build Rating Infrastructure
- Create `run_rating.py` script that:
  - Loads rating datasets
  - Uses AI models to score each response
  - Tracks which responses are real vs AI-generated
  - Calculates accuracy metrics
- Adapt `weave_utils/scorers.py` for authenticity scoring

### 3.4 Rating Output Format
```json
{
  "rating_metadata": {
    "rater_model": "gpt-4o",
    "rating_dataset": "rating_dataset_20250528_200201.json",
    "timestamp": "..."
  },
  "ratings": [{
    "question_id": "cnn_fareed_zakaria_2012_1",
    "response_ratings": [
      {
        "response_id": "..._resp_1",
        "authenticity_score": 8.5,
        "rationale": "Strong use of uncertainty...",
        "predicted_source": "real_kahneman"
      }
    ]
  }],
  "summary_metrics": {
    "accuracy": 0.73,
    "real_kahneman_avg_score": 8.2,
    "ai_responses_avg_score": 6.5
  }
}
```

## Phase 4: Orchestration & Full Benchmark Flow

### 4.1 Unified Benchmark Runner
- Create `run_kahneman_benchmark.py` that:
  ```bash
  python run_kahneman_benchmark.py \
    --impersonator_models=gpt-4o,claude-3-opus \
    --rater_models=gpt-4o,claude-3-opus \
    --output_report=benchmark_results.json
  ```

### 4.2 Results Visualization
- Create `generate_report.py` for:
  - Model comparison charts
  - Per-question analysis
  - Authenticity score distributions
  - Confusion matrices (real vs AI predictions)

### 4.3 Prompt Iteration System
- Create `prompt_library/` structure:
  ```
  prompt_library/
  ├── impersonation/
  │   ├── v1_original.txt
  │   ├── v2_no_stage_directions.txt
  │   └── v3_refined.txt
  └── rating/
      ├── v1_basic.txt
      └── v2_detailed_rubric.txt
  ```
- Add `--impersonation_prompt_version` flag
- Track prompt version in results

## Phase 5: Testing & Quality Assurance

### 5.1 Unit Tests
- Test dataset loading
- Test response randomization
- Test scoring calculations
- Test file I/O operations

### 5.2 Integration Tests
- End-to-end pipeline tests
- Multi-model compatibility
- Error handling scenarios

### 5.3 Prompt Refinement Issues to Address
- ❗ Remove stage directions (e.g., "*pauses to think*")
- ❗ Ensure consistent response length
- ❗ Avoid anachronistic references
- ❗ Calibrate uncertainty levels

## Phase 6: Advanced Features & Release

### 6.1 Extended Capabilities
- Add more interview questions (expand to 25-50)
- Support for follow-up questions
- Chain-of-thought impersonation
- Multiple rater consensus mechanism

### 6.2 Benchmark Variations
- **KahnemanBench-Core**: Original 10 questions
- **KahnemanBench-Extended**: 50 questions
- **KahnemanBench-Hard**: Edge cases and tricky questions

### 6.3 Documentation & Release
- Comprehensive README with results
- Model leaderboard
- Submission guidelines for community
- Paper/blog post on findings

## Immediate Next Steps

1. **Create Improved Impersonation Prompt v2**:
   ```python
   # Add to prompt:
   "Important: Respond naturally as Kahneman would in conversation. 
   Do not include stage directions, actions in asterisks, or 
   parenthetical notes about pausing or thinking."
   ```

2. **Build Rating System** (Phase 3.1-3.3)

3. **Test Prompt Improvements**:
   ```bash
   python run_multi_impersonation.py \
     --models=gpt-4o \
     --system_prompt_path=prompt_library/impersonation/v2_no_stage_directions.txt
   ```

4. **Create Simple Test Suite**



## Timeline Estimate
- Phase 3 (Rating): 2-3 sessions
- Phase 4 (Orchestration): 1-2 sessions  
- Phase 5 (Testing): 1 session
- Phase 6 (Release): 2-3 sessions

---

*Last Updated: May 28, 2025*

Prompts used
Creating summarised context
Hi Claude, today I'd like to finish preparing our test dataset. First look at kahneman_dataset_v1.json. I want you to read through the interviews (they should be all available to you via github) and provide me a suitable summarised_context for each one. This should be several sentences that describe the flow of the conversation so far, and particularly the previous answer and anything that the question references or builds upon from previous questions. The purpose is to help a model give a good answer to the question by understanding the full context in which it was asked. The output should be 10 summarised contexts, one for each of question in our dataset so far