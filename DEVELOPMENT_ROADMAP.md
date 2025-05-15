KahnemanBench Development Plan
This plan outlines the steps to adapt the forked/cloned SimpleBench project into KahnemanBench, focusing on creating a benchmark for AI's ability to impersonate Daniel Kahneman and for other AIs to rate the "behavioral science taste" of these impersonations.
Phase 0: Project Initialization & Foundation (Adapting SimpleBench)
GitHub Setup:
Action: Ensure your forked repository is named KahnemanBench (or your preferred name) on GitHub.
Action: Clone your forked KahnemanBench repository to your local machine if you haven't already.
Initial README.md:
Action: Create/Update README.md in the root directory.
Content:
Project Title: KahnemanBench
Brief Description: "An AI benchmark to test AI's ability to impersonate Daniel Kahneman's interview responses and for other AIs to rate their 'behavioral science taste'. Inspired by SimpleBench and powered by Weave."
High-level goals.
(Placeholder for setup/run instructions).
Virtual Environment & Dependencies:
Action: Follow the Python version and virtual environment setup from SimpleBench's README.md (e.g., pyenv local 3.10.11, python -m venv kb_env, source kb_env/bin/activate).
Action: Review uv.lock from SimpleBench. Install the existing dependencies using uv pip install -r pyproject.toml (or by directly referencing the lock file if pyproject.toml needs updating first). Many of these will be reusable.
Action: Create your .env file and add your API keys (OpenAI, Anthropic, etc.).
.gitignore Review:
Action: Review the existing .gitignore.
Action: Add any new directories or file patterns specific to KahnemanBench that should be ignored (e.g., a directory for raw interview text files if large, specific output folders for KahnemanBench).
Project Structure Cleanup (Optional Renaming):
Action: Consider renaming simple_bench_public.json and simple_bench_public_set.csv to something like sample_kahneman_data.json once you have your initial data. For now, you can work with copies or placeholders.
Action: The directory weave_utils in run_benchmark.py (from from weave_utils.models import LiteLLMModel...) implies the models.py and scorers.py are in a subdirectory. Ensure this structure is intended or adjust imports. For KahnemanBench, you might have a main package like kahneman_bench_core containing these modules.
Decision: Let's assume models.py and scorers.py are in a directory, say, kahneman_bench_core. Update imports in run_benchmark.py accordingly.
Phase 1: Dataset Curation & Initial Weave Integration
Gather Kahneman Interview Data:
Action: Collect 5-10 high-quality examples of Daniel Kahneman being asked a question and his actual response.
Deliverable: Text files or a document with these Q&A pairs and their sources.
Define KahnemanBench Data Format:
Action: Create a JSON structure for your dataset. Each entry should at least have:
kahneman_id: str (unique identifier for the Q&A pair)
question_text: str
true_kahneman_response: str
source_info: str (book, interview URL, etc.)
(Optional: context, date)
Action: Create an initial kahneman_dataset_v1.json file with your 5-10 examples.
Adapt Dataset Loading:
Action: Modify load_dataset in run_benchmark.py to read your new kahneman_dataset_v1.json format. The evaluation = weave.Evaluation(dataset=...) will use this.
Define Weave Types for Dataset:
Action: In a new file (e.g., kahneman_bench_core/types.py or within dataset.py), define a Weave Type for your Kahneman questions, e.g., KahnemanQuestionRecord.
import weave

@weave.type()
class KahnemanQuestionRecord:
    kahneman_id: str
    question_text: str
    true_kahneman_response: str
    source_info: str
Use code with caution.
Python
Action: Ensure your load_dataset function in run_benchmark.py (or a dedicated op) returns a list of these KahnemanQuestionRecord objects when passing data to weave.Evaluation.
Initial Weave Test:
Action: Temporarily modify run_benchmark.py to simply load the dataset and perhaps print it, to ensure Weave tracks these custom objects. You can inspect this in the Weave UI.
Phase 2: AI Impersonator Development
Adapt LiteLLMModel:
Action: The LiteLLMModel in models.py (e.g., kahneman_bench_core/models.py) is largely reusable.
Action: Ensure the MODEL_MAP includes the models you want to test as impersonators.
Develop Impersonator Prompts:
Action: Create a new file, e.g., kahneman_bench_core/prompts.py or prompts/impersonator_prompts.py.
Action: Define 1-2 initial system prompts for instructing an LLM to respond as Daniel Kahneman.
Example: KAHNEMAN_IMPERSONATOR_PROMPT_V1 = "You are an AI role-playing as Daniel Kahneman. Please provide a thoughtful and nuanced response to the following interview question, drawing upon your known works and characteristic style: {question_text}"
Modify run_benchmark.py for Impersonation:
Action: Update run_benchmark.py so that the model.predict() call uses the impersonator prompt, formatting it with question_text from your dataset.
Action: For now, remove the multiple-choice scorers. The goal is to generate text.
Define Weave Type for Generated Responses:
Action: In kahneman_bench_core/types.py, define:
@weave.type()
class ImpersonatedResponse:
    kahneman_id: str # from KahnemanQuestionRecord
    impersonator_model_name: str
    impersonator_prompt_template: str # The template used
    raw_question_text: str
    generated_response_text: str
    # Optional: generation_config (temp, tokens, etc.)
Use code with caution.
Python
Weave Logging for Impersonations:
Action: Modify run_benchmark.py (or create a new Weave op) to:
Iterate through the KahnemanQuestionRecord items.
For each, call the impersonator model.
Log the resulting ImpersonatedResponse object to Weave. weave.publish() or logging within an op.
Action: Test and verify these objects appear in the Weave UI, linked to your chosen models and dataset items.
Phase 3: AI Rater Development & Scoring Logic
Define Rating Criteria:
Action: Formulate 3-5 clear criteria for what makes a "good" Kahneman impersonation (e.g., Fidelity to Kahneman's Theories, Authenticity of Style, Depth of Behavioral Insight, Clarity).
Develop Rater Prompts:
Action: In kahneman_bench_core/prompts.py or prompts/rater_prompts.py, define prompts for AI Raters. These prompts will take a question, a response (either real or impersonated), and your criteria, and should ask the LLM to output scores and justifications, ideally in a parsable format (e.g., JSON).
Example: KAHNEMAN_RATER_PROMPT_V1 = "You are an expert in behavioral science... Evaluate the following response to the question '{question_text}'. Response: '{response_text}'. Provide scores (1-5) and a brief justification for: Fidelity, Style, Insight. Output as a JSON object: {'fidelity_score': X, 'fidelity_justification': '...', ...}"
Adapt scorers.py to kahneman_bench_core/rating_logic.py:
Action: Rename/refactor scorers.py.
Action: Create a new Weave op, e.g., rate_kahneman_response(question: KahnemanQuestionRecord, response_to_rate: Union[ImpersonatedResponse, str], rater_model: LiteLLMModel, rater_prompt_template: str).
This op will call the rater_model (another LiteLLMModel instance) with the formatted rater_prompt_template.
It will need a sub-function (like the old extract_answer) to parse the Rater AI's output (e.g., extracting JSON scores).
Define Weave Type for Ratings:
Action: In kahneman_bench_core/types.py:
@weave.type()
class KahnemanRating:
    kahneman_id: str
    rated_response_source: str # e.g., "real_kahneman" or impersonator model name
    rater_model_name: str
    rater_prompt_template: str
    fidelity_score: Optional[int]
    style_score: Optional[int]
    insight_score: Optional[int]
    # Add other scores as defined
    overall_justification: Optional[str]
    # Optional: raw_rater_output
Use code with caution.
Python
Weave Logging for Ratings:
Action: Ensure your rate_kahneman_response op returns a KahnemanRating object and logs it to Weave.
Phase 4: Orchestration & Full Benchmark Flow
Update run_benchmark.py (The Main Orchestrator):
Action: Refactor run_benchmark to handle the two-stage process:
Generation Loop: For each KahnemanQuestionRecord in the dataset and for each selected Impersonator AI model:
Call the impersonation op/model.
Store the ImpersonatedResponse.
Rating Loop: For each ImpersonatedResponse (and for the true_kahneman_response for each question):
For each selected Rater AI model:
Call the rate_kahneman_response op.
Store the KahnemanRating.
Action: Decide how to handle "scorers" in weave.Evaluation. You might pass your rate_kahneman_response op or a summary op as a scorer. Or, you might use weave.publish() directly in your loops and then create separate ops for analysis. The Evaluation object might be less central if your flow is highly custom.
Action: Ensure all relevant configurations (impersonator models used, rater models used, prompts, dataset version) are logged with Weave for each run.
Command-Line Interface:
Action: Update the fire CLI in run_benchmark.py to accept parameters like:
--dataset_path
--impersonator_models (comma-separated list of model names from MODEL_MAP)
--rater_models (comma-separated list)
--impersonator_prompt_key (to select a prompt from your prompt file)
--rater_prompt_key
--weave_project_name
Initial Summary Metrics:
Action: Create a simple Weave op that takes a list of KahnemanRating objects and calculates average scores for each criterion for each impersonator model. Log these summary tables to Weave.
Phase 5: Testing, Refinement, & Documentation
End-to-End Testing:
Action: Run the full benchmark with your small dataset, 1-2 impersonator models, and 1-2 rater models.
Action: Verify all data is logged correctly in Weave and that relationships (e.g., ratings linked to responses, responses linked to questions) are clear.
Prompt & Criteria Refinement:
Action: Analyze the generated responses and the AI ratings.
Action: Iterate on your impersonator and rater prompts to improve quality and consistency.
Action: Refine rating criteria if they prove ambiguous or hard for AIs to apply.
Expand Dataset:
Action: Gradually add more Q&A pairs to your kahneman_dataset.json.
Documentation:
Action: Write a comprehensive README.md for KahnemanBench:
Detailed explanation of the benchmark's purpose and methodology.
Clear setup instructions (Python, uv, API keys).
How to run the benchmark, with examples of CLI arguments.
Explanation of the output and how to interpret Weave results.
Structure of the dataset and how to add to it.
Action: Add code comments and docstrings to all Python files and functions.
Project Structure Finalization:
Action: Organize files logically (e.g., data/ for datasets, kahneman_bench_core/ for main logic, prompts/, scripts/ for executable scripts if run_benchmark.py becomes too complex).
Phase 6: Advanced Features & Community (Future)
Advanced Metrics:
Turing Test-like evaluation (can raters distinguish real vs. AI?).
Inter-rater reliability.
Analysis of linguistic features of impersonations.
Human Evaluation Integration:
Develop a small human evaluation component to calibrate or validate AI rater "taste."
Broader Model Support:
Test a wider range of impersonator and rater models.
Community Contributions:
Document how others could contribute new Kahneman Q&A pairs, suggest new rating criteria, or add new models to test.