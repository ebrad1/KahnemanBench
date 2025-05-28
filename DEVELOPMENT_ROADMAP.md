# KahnemanBench Development Plan

## Current Status
We have successfully completed Phase 1 (Dataset Curation) and made significant progress on Phase 2 (AI Impersonator Development). We now have a working 10-question Kahneman dataset with summarised contexts, and a fully functional AI impersonation system that can generate Kahneman-style responses using various LLMs. The impersonation pipeline has been tested and is working with `GPT-4o`.

## Goal for Next Session
Complete Phase 2 by testing the impersonation quality, then begin Phase 3: AI Rater Development to create a system for scoring the authenticity of generated responses.

## Phase 0: Project Initialization & Foundation (Adapting SimpleBench) ✅ COMPLETED

### GitHub Setup:
-   **Action:** Ensure your forked repository is named `KahnemanBench` (or your preferred name) on GitHub.
-   **Action:** Clone your forked `KahnemanBench` repository to your local machine if you haven't already.

### Initial README.md:
-   **Action:** Create/Update `README.md` in the root directory.
-   **Content:**
    -   Project Title: KahnemanBench
    -   Brief Description: "An AI benchmark to test AI's ability to impersonate Daniel Kahneman's interview responses and for other AIs to rate their 'behavioral science taste'. Inspired by `SimpleBench` and powered by `Weave`."
    -   High-level goals. (To be expanded)
    -   (Placeholder for setup/run instructions). (To be updated for `KahnemanBench` specifics)

### Virtual Environment & Dependencies:
-   **Action:** Follow the Python version and virtual environment setup from `SimpleBench`'s `README.md` (e.g., `python -m venv kb_env`, `.\kb_env\Scripts\activate`).
-   **Decision:** Using Python 3.10.x as available, `kb_env` created and activated.
-   **Action:** Review `uv.lock` from `SimpleBench`. Install the existing dependencies using `uv pip install -r pyproject.toml`.
-   **Action:** Create your `.env` file and add your API keys (OpenAI, Anthropic, etc.).
-   **Note:** OpenAI API key tested and working after resolving initial quota issue.

### .gitignore Review:
-   **Action:** Review the existing `.gitignore`.
-   **Action:** Add any new directories or file patterns specific to `KahnemanBench` that should be ignored (e.g., `kb_env/`, `.env`, `.weave/`).
-   **Note:** A comprehensive `.gitignore` has been created and committed.

### Weave/W&B Integration Test:
-   **Action:** Successfully ran `run_benchmark.py` with original `SimpleBench` data (`simple_bench_public.json`) and `gpt-4o-mini`.
-   **Action:** Observed run logging to W&B under the default `simplebench/simple_bench_public` project.

## Phase 1: Dataset Curation & Initial Weave Integration ✅ COMPLETED

### Gather Kahneman Interview Data:
-   **Action:** Collect 5-10 high-quality examples of Daniel Kahneman being asked a question and his actual response.
-   **Deliverable:** Created `kahneman_dataset_v1.json` with 10 Q&A pairs from CNN Fareed Zakaria (2012), Motley Fool (2013), and Conversations with Tyler (2018) interviews.

### Define KahnemanBench Data Format:
-   **Action:** Create a JSON structure for dataset with `kahneman_id`, `question_text`, `true_kahneman_response`, `source_info`, and `context` fields.
-   **Action:** Create `kahneman_dataset_v1.json` file with 10 examples including `summarised_context` for each question.

### Adapt Dataset Loading:
-   **Action:** Modify dataset loading to read the new `kahneman_dataset_v1.json` format.

### Define Weave Types for Dataset:
-   **Action:** Use standard Python dictionaries (compatible with current `Weave` version) for dataset objects.

### Initial Weave Test:
-   **Action:** Successfully tested dataset loading and `Weave` logging integration.

## Phase 2: AI Impersonator Development - **IN PROGRESS**

-   Adapt `LiteLLMModel` (reusable from `SimpleBench`).

### Develop Impersonator Prompts:
-   Created comprehensive system prompt capturing Kahneman's intellectual style, speaking patterns, key concepts, and personality traits.
-   Prompt includes specific guidance on his humility, precision, collaboration references, and nuanced thinking.

### Modify Script for Impersonation:
-   Created `run_impersonation.py` script for generating Kahneman-style responses.
-   Integrated with existing `Weave` logging and `LiteLLM` infrastructure.

### Define Output Data Structure:
-   Created structured JSON output format with run metadata and response details.

### Weave Logging for Impersonations:
-   Successfully integrated `Weave` ops for tracking generation process.

### End-to-End Testing:
-   Successfully tested complete pipeline with `GPT-4o` model.

### Quality Assessment:
-   **Action:** Generate responses with multiple models (`GPT-4o`, `Claude`, etc.) for comparison.
-   **Action:** Manual review of generated responses for authenticity.
-   **Action:** Iterate on prompts based on quality assessment.

## Phase 3: AI Rater Development & Scoring Logic

-   Define Rating Criteria.
-   Develop Rater Prompts.
-   Adapt `scorers.py` to `kahneman_bench_core/rating_logic.py` (or similar, e.g., `weave_utils/rating_logic.py`).
-   Define `Weave` Type for Ratings (`KahnemanRating`).
-   Weave Logging for Ratings.

## Phase 4: Orchestration & Full Benchmark Flow

-   Update `run_benchmark.py` for two-stage (Generation, Rating) process.
-   Update Command-Line Interface.
-   Initial Summary Metrics.

## Phase 5: Testing, Refinement, & Documentation

-   End-to-End Testing.
-   Prompt & Criteria Refinement.
-   Expand Dataset.
-   Documentation (README, code comments).
-   Project Structure Finalization.

## Phase 6: Advanced Features & Community (Future)

-   Advanced Metrics.
-   Human Evaluation Integration.
-   Broader Model Support.
-   Community Contributions.

## Context for Resuming Our Work:

### Our Goal
Transform `SimpleBench` into `KahnemanBench`.

### Current State of Codebase:
-   ✅ Project is a fork of `SimpleBench` with `pyproject.toml` renamed to `kahnemanbench`
-   ✅ `README.md` has initial `KahnemanBench` title and description
-   ✅ Virtual environment `kb_env` is set up with dependencies and API keys configured
-   ✅ Created comprehensive dataset (`kahneman_dataset_v1.json`) with 10 Q&A pairs and summarised contexts
-   ✅ Built complete AI impersonation system (`run_impersonation.py`) with `Weave` integration
-   ✅ Developed sophisticated Kahneman impersonation prompt capturing his intellectual style
-   ✅ Successfully tested end-to-end pipeline with `GPT-4o` generating authentic-sounding responses

### Key Files Now Available:
-   `run_impersonation.py`: Main script for AI impersonation generation
-   `kahneman_impersonation_prompt.txt`: Comprehensive system prompt for Kahneman impersonation
-   `data/kahneman_dataset_v1.json`: Curated dataset with 10 Q&A pairs and contexts
-   `weave_utils/models.py`: `LiteLLMModel` (adapted for impersonation)
-   `weave_utils/scorers.py`: Original scorers (to be adapted for rating authenticity)
-   `run_benchmark.py`: Original `SimpleBench` script (working baseline)

### Current Focus:
Phase 2 completion (quality assessment) → Phase 3 (AI rater development for authenticity scoring)



Prompts used
Creating summarised context
Hi Claude, today I'd like to finish preparing our test dataset. First look at kahneman_dataset_v1.json. I want you to read through the interviews (they should be all available to you via github) and provide me a suitable summarised_context for each one. This should be several sentences that describe the flow of the conversation so far, and particularly the previous answer and anything that the question references or builds upon from previous questions. The purpose is to help a model give a good answer to the question by understanding the full context in which it was asked. The output should be 10 summarised contexts, one for each of question in our dataset so far