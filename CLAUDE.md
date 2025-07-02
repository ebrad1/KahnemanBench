# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KahnemanBench is an AI benchmark that evaluates models' ability to impersonate Daniel Kahneman's interview responses and assess human preference patterns for authentic versus AI-generated content. The research focus is on whether humans can distinguish authentic Kahneman responses from AI-generated ones, and how expert preference patterns reveal insights about AI authenticity. It uses Weave (W&B's evaluation framework) for experiment tracking and supports multiple AI model providers via LiteLLM. The project includes both automated AI evaluation and a web interface for human expert evaluation.

## Core Architecture

### Main Evaluation Scripts
- `run_impersonation.py`: Single-model Kahneman impersonation evaluation
- `run_multi_impersonation.py`: Multi-model comparison that generates rating datasets
- `run_rating.py`: Evaluates authenticity of responses using AI raters
- `run_benchmark.py`: Original SimpleBench multiple-choice evaluation
- `run_full_pipeline.py`: Orchestrates complete evaluation workflow

### Key Components
- `weave_utils/models.py`: Model wrappers including `LiteLLMModel` and `MajorityVoteModel`
- `weave_utils/scorers.py`: Evaluation functions for multiple-choice scoring
- `02_curated_datasets/kahneman_dataset_v2.json`: Expanded dataset with 103 Q&A pairs from multiple interviews
- `prompt_library/`: Contains impersonation and rating prompts

### Website & Expert Interface
- `07_website/`: Next.js web application for human expert evaluation
- `07_website/app/`: Next.js App Router pages (home, public demo, expert mode)
- `07_website/components/`: React components for question display and rating interface
- `07_website/lib/`: TypeScript definitions and data handling utilities

### Data Flow
1. Questions from `kahneman_dataset_v2.json` → AI model responses
2. Multi-model runs create mixed datasets (real + AI responses)
3. **AI Raters**: Rater models evaluate authenticity (0-100 scores)
4. **Human Experts**: Web interface allows expert preference evaluation of same datasets
5. Results saved to `rating_results_*` files with preference tracking (not scored as right/wrong)

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install anthropic fire litellm openai python-dotenv weave pandas pyyaml

# Set API keys in .env file or environment
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Login to Weights & Biases for Weave experiment tracking
wandb login [your-api-key]
```

### Website Development
```bash
# Navigate to website directory
cd 07_website

# Install Node.js dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
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

# Prompt quality tests
python3 tests/test_prompt_changes.py

# Run management (view/archive old runs)
python scripts/manage_runs.py
```

## Key Data Structures

### Dataset Format
Each question contains:
- `kahneman_id`: Unique identifier (e.g., "strategy_business_2003_11")
- `source_doc_id`: Interview source reference
- `sequence_in_source`: Order within that interview
- `full_context`: Extended context (currently empty, reserved for future use)
- `summarised_context`: Interviewer style and conversational flow description
- `question_text`: The interview question
- `true_kahneman_response`: Kahneman's actual response with preserved paragraph breaks

### Rating Dataset Format (for Expert Interface)
```json
{
  "metadata": {
    "created_at": "2025-07-02T...",
    "models_used": ["gpt-4o", "claude-3-5-sonnet"],
    "total_questions": 103,
    "responses_per_question": 3
  },
  "questions": [{
    "question_id": "strategy_business_2003_1",
    "question_text": "How did you become interested in psychology?",
    "summarised_context": "Opening question in Strategy+Business interview...",
    "responses": [{
      "response_id": "resp_1",
      "response_text": "Well, it was somewhat accidental...",
      "hidden_source": "real_kahneman"
    }, {
      "response_id": "resp_2", 
      "response_text": "My journey into psychology began...",
      "hidden_source": "gpt-4o"
    }]
  }]
}
```

### Model Configuration
Models are configured in `weave_utils/models.py` with comprehensive mapping for current models (GPT-4o, Claude-4, O3, etc.). All API calls use async/await for efficiency.

## Output Locations
- `03_impersonation_runs/`: Individual model response files
- `04_rating_datasets/`: Mixed datasets for rating evaluation  
- `05_rating_results/`: Final evaluation metrics and scores
- `06_analysis_outputs/`: Dashboards and analysis tools
- `07_website/`: Web interface for expert evaluation

## Complete Pipeline Flow

The KahnemanBench evaluation follows this end-to-end pipeline:

### Stage 1: Source Data Preparation
- **Raw materials**: 28 interview transcript files in `01_source_data/interview_transcripts/`
- **Manual curation**: Extract Q&A pairs into `02_curated_datasets/kahneman_dataset_v2.json` (103 questions)
- **Coverage**: 9 different interview sources with diverse conversational styles
- **Context**: Each question includes interviewer style description and conversational flow

### Stage 2: AI Impersonation Generation
- **Single model**: `run_impersonation.py` generates responses for one model
- **Multi-model**: `run_multi_impersonation.py` generates responses across multiple models
- **Output**: Individual model files in `impersonation_runs/` with metadata and responses

### Stage 3: Rating Dataset Creation
- **Process**: Multi-model runs automatically create mixed datasets
- **Content**: Shuffle real Kahneman responses with AI-generated ones
- **Output**: Anonymous datasets in `rating_datasets/` for blind evaluation

### Stage 4: Authenticity Rating
- **AI Raters**: `run_rating.py` with AI rater models
- **Human Experts**: Web interface at `/expert` for human evaluation
- **Process**: Score each response 0-100 for authenticity without knowing source
- **Output**: Detailed results in `rating_results/` with model comparisons

### Stage 5: Analysis & Interpretation
- **Tools**: `analyze_ratings.py` and `rating_dashboard.html`
- **Metrics**: Score gaps between real/AI responses, model rankings
- **Human vs AI**: Compare human expert performance with AI rater accuracy

## Expert Evaluation Workflow

### Expert Participant Process
1. **Access**: Navigate to `website.com/expert`
2. **Authentication**: Enter unique expert code (e.g., `EXPERT_ALICE_2025`)
3. **Auto-Loading**: Pre-configured dataset automatically loads (no file upload needed)
4. **Evaluation**: Express preferences between responses without knowing sources
5. **Progress Saving**: Automatic save after each question, can resume anytime
6. **Completion**: Submit preferences for analysis (framed as research contribution, not scoring)

### Expert Management
- **Code Generation**: Create unique codes per expert for tracking
- **Progress Monitoring**: Track completion status across experts
- **Data Export**: Export expert ratings with individual attribution
- **Analysis**: Compare expert agreement and performance metrics

## Folder Structure
```
KahnemanBench/
├── 01_source_data/           # Raw transcripts and metadata
├── 02_curated_datasets/      # Structured Q&A datasets
├── 03_impersonation_runs/    # AI-generated responses
├── 04_rating_datasets/       # Mixed datasets for evaluation
├── 05_rating_results/        # Final evaluation metrics and scores
├── 06_analysis_outputs/      # Dashboards, reports, visualizations
├── 07_website/              # Next.js web interface for expert evaluation
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   ├── lib/                 # TypeScript utilities and types
│   └── public/             # Static assets
├── archive/                  # Completed experiment runs
├── scripts/                  # All run_*.py and analysis scripts
└── tests/                   # Test suites
```

## Recent Improvements (2025-07-02)

### ✅ Core Pipeline Complete (Previous Work)
- **Pipeline automation**: `run_full_pipeline.py` handles complete evaluation flow
- **Configuration system**: 5 pre-built configs for common scenarios
- **Prompt enhancement**: Eliminated stage directions for cleaner responses
- **Dataset expansion**: Expanded from 11 to 103 Q&A pairs (10x growth)
- **Testing & validation**: Comprehensive test suite operational

### ✅ Website Development (Completed)
- **Next.js foundation**: Basic website structure with TypeScript and Tailwind
- **Public demo**: Interactive sample at `/try` for general users
- **Expert interface**: Evaluation platform at `/expert` for research participants
- **Component library**: Reusable React components for question display and rating
- **Dataset management**: Server-side pre-loaded datasets with easy swapping
- **Progress saving**: Automatic save after each question with resume capability
- **Expert tracking**: Individual codes with session persistence and navigation
- **Preference-based evaluation**: Framed as preference/authenticity assessment, not right/wrong scoring
- **File-based persistence**: Local JSON storage with Vercel-ready architecture

### ⚡ Current Priorities
- **End-to-end testing**: Validate complete expert evaluation workflow
- **Production deployment**: Vercel setup for public access
- **Expert data collection**: Begin testing with 5-10 experts
- **UI polish**: Based on expert feedback and usability testing

## Current Development Focus

### Expert Evaluation Workflow (Phase 5 - Complete)

The expert evaluation system includes:

1. **Pre-loaded Datasets**: Researchers configure datasets server-side via `lib/datasetConfig.ts`
2. **Expert Authentication**: Unique codes (e.g., `EXPERT_ALICE_2025`) for tracking
3. **Progress Saving**: Automatic save after each question selection
4. **Resume Capability**: Experts can quit and return to continue from last position
5. **Navigation**: Forward/backward navigation with previous selections preserved
6. **Data Export**: Individual and bulk CSV/JSON export from dashboard

### Dataset Management System
- **Easy Dataset Swapping**: Change `DATASET_CONFIG.activeDataset` in `lib/datasetConfig.ts`
- **Dataset Tracking**: All responses linked to specific dataset names
- **Validation**: Automatic verification of dataset configuration
- **Progress Isolation**: Expert progress tied to specific datasets

### Data Storage Strategy
**Local Development:**
- File-based storage in `/data/expert-responses.json`
- Persistent across server restarts
- Automatic directory creation

**Production (Vercel):**
- Vercel filesystem is read-only, requires external storage
- Recommended options:
  - **Vercel KV**: Redis-like key-value store (easiest integration)
  - **Supabase**: PostgreSQL database with real-time features
  - **MongoDB Atlas**: NoSQL database with free tier
  - **Simple approach**: Commit responses to GitHub repo as JSON files

### Expert Management System  
- **Individual Tracking**: Unique codes per expert (e.g., `EXPERT_ALICE_2025`)
- **Data Export**: CSV/JSON export with expert attribution
- **Progress Dashboard**: Real-time completion tracking at `/dashboard`
- **Session Persistence**: Experts can quit and resume evaluation seamlessly

## Suggested Next Steps

### Immediate (This Week)
1. **Complete website basics**: Run Claude Code to fix TypeScript and missing components
2. **Test expert workflow**: Verify file upload and rating interface work end-to-end
3. **Create expert codes**: Generate system for unique expert tracking
4. **Deploy to Vercel**: Set up production hosting for expert access

### Short-term (Next Few Weeks)
1. **Expert data collection**: Test with 5-10 experts using real rating datasets
2. **UI improvements**: Based on expert feedback and usability testing
3. **Data analysis tools**: Compare human expert vs AI rater performance
4. **Documentation**: Instructions for expert participants

### Medium-term (Research Direction)
1. **Human baseline establishment**: Large-scale expert evaluation for AI validation
2. **Cross-validation studies**: Compare expert agreement and calibration
3. **Academic publication**: Paper on AI impersonation evaluation methodology
4. **Public benchmark**: Open system for community model evaluation

## Evaluation Methodology

### Dual-Score System for Model Assessment

KahnemanBench evaluates models across two dimensions:

1. **Generation Quality Score**: Average preference rate for responses generated by a given LLM
   - Measures how well the model impersonates Kahneman when generating responses
   - Scored by other models and human experts expressing preferences (not right/wrong scoring)

2. **Evaluation Discrimination Score**: Average Kahneman preference delta for ratings the model produces as a rater
   - Measures how well the model distinguishes authentic Kahneman from AI-generated responses
   - Calculated as difference between preference rates given to real Kahneman vs AI responses
   - Higher delta indicates better discrimination ability

### Human vs AI Rater Comparison
- **Expert Baseline**: Human experts provide ground truth for authenticity ratings
- **AI Validation**: Compare AI rater performance against human expert consensus
- **Calibration Studies**: Analyze where humans and AI raters agree/disagree
- **Methodology Validation**: Ensure AI evaluation correlates with human judgment

## References & Inspiration

### Evaluation Websites
- **VendingBench by Andon Labs**: https://andonlabs.com/evals/vending-bench
  - Excellent example of clean evaluation presentation and response comparison interface
  - Demonstrates effective side-by-side model comparison with clear navigation
  - Direct inspiration for KahnemanBench website design in `07_website/`

### Expert Evaluation Platforms
- **Academic survey platforms**: Inspiration for expert participant experience
- **Blind review systems**: Methodology for unbiased evaluation
- **Research data collection**: Best practices for expert study management

---

*Last Updated: July 2, 2025*  
*Current Phase: Website development and expert data collection (Phase 5)*  
*Previous Completion: Core AI evaluation pipeline (Phases 1-4)*