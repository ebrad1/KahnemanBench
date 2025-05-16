# KahnemanBench Development Plan

**Current Status:** We have successfully set up the initial project environment, installed dependencies, configured API keys, and tested the original SimpleBench functionality. We've also made some initial project naming decisions and have a basic understanding of how Weave integrates with W&B for logging. The OpenAI API quota issue was resolved, allowing a full test run of the original SimpleBench.

**Goal for Next Session:** Begin Phase 1: Dataset Curation for KahnemanBench, starting with gathering Q&A pairs and defining the new JSON data format.

---

## Phase 0: Project Initialization & Foundation (Adapting SimpleBench)

*   **GitHub Setup:**
    *   [X] Action: Ensure your forked repository is named KahnemanBench (or your preferred name) on GitHub.
    *   [X] Action: Clone your forked KahnemanBench repository to your local machine if you haven't already.
*   **Initial README.md:**
    *   [X] Action: Create/Update README.md in the root directory.
    *   [X] Content:
        *   [X] Project Title: KahnemanBench
        *   [X] Brief Description: "An AI benchmark to test AI's ability to impersonate Daniel Kahneman's interview responses and for other AIs to rate their 'behavioral science taste'. Inspired by SimpleBench and powered by Weave."
        *   [ ] High-level goals. (To be expanded)
        *   [ ] (Placeholder for setup/run instructions). (To be updated for KahnemanBench specifics)
*   **Virtual Environment & Dependencies:**
    *   [X] Action: Follow the Python version and virtual environment setup from SimpleBench's README.md (e.g., `python -m venv kb_env`, `.\kb_env\Scripts\activate`).
        *   *Decision:* Using Python 3.10.x as available, `kb_env` created and activated.
    *   [X] Action: Review `uv.lock` from SimpleBench. Install the existing dependencies using `uv pip install -r pyproject.toml`.
    *   [X] Action: Create your `.env` file and add your API keys (OpenAI, Anthropic, etc.).
        *   *Note:* OpenAI API key tested and working after resolving initial quota issue.
*   **`.gitignore` Review:**
    *   [X] Action: Review the existing `.gitignore`.
    *   [X] Action: Add any new directories or file patterns specific to KahnemanBench that should be ignored (e.g., `kb_env/`, `.env`, `.weave/`).
        *   *Note:* A comprehensive `.gitignore` has been created and committed.
*   **Project Structure Cleanup (Optional Renaming):**
    *   [ ] Action: Consider renaming `simple_bench_public.json` and `simple_bench_public_set.csv` to something like `sample_kahneman_data.json` once you have your initial data. For now, you can work with copies or placeholders.
        *   *Decision:* We made copies: `kahneman_dataset_sample_v0.json` and `kahneman_questions_sample_v0.csv` as placeholders. Actual renaming/replacement will occur when new data format is defined.
    *   [ ] Action: The directory `weave_utils` in `run_benchmark.py` (from `from weave_utils.models import LiteLLMModel...`) implies the `models.py` and `scorers.py` are in a subdirectory. Ensure this structure is intended or adjust imports. For KahnemanBench, you might have a main package like `kahneman_bench_core` containing these modules.
    *   [ ] Decision: Let's assume `models.py` and `scorers.py` are in a directory, say, `kahneman_bench_core`. Update imports in `run_benchmark.py` accordingly.
        *   *Decision:* For now, we are keeping the directory named `weave_utils` and the imports as they are. This can be revisited later if desired.
*   **Weave/W&B Integration Test:**
    *   [X] Action: Successfully ran `run_benchmark.py` with original SimpleBench data (`simple_bench_public.json`) and `gpt-4o-mini`.
    *   [X] Action: Observed run logging to W&B under the default `simplebench/simple_bench_public` project.
    *   *Note:* Understood that `entity` and `project` parameters in `run_benchmark.py` (or CLI args) control the W&B destination. These will be updated for KahnemanBench-specific runs.

## Phase 1: Dataset Curation & Initial Weave Integration

*   **Gather Kahneman Interview Data:**
    *   [ ] Action: Collect 5-10 high-quality examples of Daniel Kahneman being asked a question and his actual response.
    *   [ ] Deliverable: Text files or a document with these Q&A pairs and their sources.
*   **Define KahnemanBench Data Format:**
    *   [ ] Action: Create a JSON structure for your dataset. Each entry should at least have:
        *   `kahneman_id: str` (unique identifier for the Q&A pair)
        *   `question_text: str`
        *   `true_kahneman_response: str`
        *   `source_info: str` (book, interview URL, etc.)
        *   (Optional: `context`, `date`)
    *   [ ] Action: Create an initial `kahneman_dataset_v1.json` file with your 5-10 examples.
*   **Adapt Dataset Loading:**
    *   [ ] Action: Modify `load_dataset` in `run_benchmark.py` to read your new `kahneman_dataset_v1.json` format. The `evaluation = weave.Evaluation(dataset=...)` will use this.
*   **Define Weave Types for Dataset:**
    *   [ ] Action: In a new file (e.g., `kahneman_bench_core/types.py` or `weave_utils/types.py`, or within `dataset.py`), define a Weave Type for your Kahneman questions, e.g., `KahnemanQuestionRecord`.
        ```python
        import weave

        @weave.type()
        class KahnemanQuestionRecord:
            kahneman_id: str
            question_text: str
            true_kahneman_response: str
            source_info: str
        ```
    *   [ ] Action: Ensure your `load_dataset` function in `run_benchmark.py` (or a dedicated op) returns a list of these `KahnemanQuestionRecord` objects when passing data to `weave.Evaluation`.
*   **Initial Weave Test:**
    *   [ ] Action: Temporarily modify `run_benchmark.py` to simply load the dataset and perhaps print it, to ensure Weave tracks these custom objects. You can inspect this in the Weave UI.

## Phase 2: AI Impersonator Development
*   [ ] Adapt `LiteLLMModel` (largely reusable).
*   [ ] Develop Impersonator Prompts.
*   [ ] Modify `run_benchmark.py` for Impersonation.
*   [ ] Define Weave Type for Generated Responses (`ImpersonatedResponse`).
*   [ ] Weave Logging for Impersonations.

## Phase 3: AI Rater Development & Scoring Logic
*   [ ] Define Rating Criteria.
*   [ ] Develop Rater Prompts.
*   [ ] Adapt `scorers.py` to `kahneman_bench_core/rating_logic.py` (or similar, e.g., `weave_utils/rating_logic.py`).
*   [ ] Define Weave Type for Ratings (`KahnemanRating`).
*   [ ] Weave Logging for Ratings.

## Phase 4: Orchestration & Full Benchmark Flow
*   [ ] Update `run_benchmark.py` for two-stage (Generation, Rating) process.
*   [ ] Update Command-Line Interface.
*   [ ] Initial Summary Metrics.

## Phase 5: Testing, Refinement, & Documentation
*   [ ] End-to-End Testing.
*   [ ] Prompt & Criteria Refinement.
*   [ ] Expand Dataset.
*   [ ] Documentation (README, code comments).
*   [ ] Project Structure Finalization.

## Phase 6: Advanced Features & Community (Future)
*   [ ] Advanced Metrics.
*   [ ] Human Evaluation Integration.
*   [ ] Broader Model Support.
*   [ ] Community Contributions.


Context for Resuming Our Work:
Our Goal: Transform SimpleBench into KahnemanBench.
Current State of Codebase:
The project is a fork of SimpleBench.
pyproject.toml name changed to kahnemanbench.
README.md has initial KahnemanBench title and description.
Virtual environment kb_env is set up with dependencies.
.env file contains API keys.
.gitignore is configured.
Directory weave_utils (containing models.py, scorers.py) is currently kept as is.
run_benchmark.py successfully executed with simple_bench_public.json and gpt-4o-mini, logging to simplebench/simple_bench_public on W&B. This provided a baseline understanding of the existing script's operation and Weave logging.
Key Files to Be Aware Of:
run_benchmark.py: The main script we'll be heavily modifying.
weave_utils/models.py: Contains LiteLLMModel (for calling LLMs) and MajorityVoteModel.
weave_utils/scorers.py: Contains eval_multi_choice and extract_answer (for the original multiple-choice task). This will be significantly refactored/replaced for KahnemanBench's rating logic.
simple_bench_public.json: The current dataset format (multiple choice).
system_prompt.txt: The system prompt for the multiple-choice task.
pyproject.toml: Project metadata and dependencies.
README.md: Project documentation.
Next Immediate Task (from Phase 1):
Gather Kahneman Q&A Data: Collect 5-10 examples of questions posed to Daniel Kahneman and his actual responses, along with their sources.
Define JSON Data Format: Based on the collected data, define the structure for kahneman_dataset_v1.json (fields like kahneman_id, question_text, true_kahneman_response, source_info).
Create the kahneman_dataset_v1.json file.