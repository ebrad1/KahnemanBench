# python scripts/run_multi_impersonation.py --models=gpt-4o,claude-3-opus-20240229 --dataset_path=02_curated_datasets/kahneman_dataset_v1.json

import json
import weave
import asyncio
import random
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from fire import Fire
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from weave_utils.models import LiteLLMModel

def load_kahneman_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Load Kahneman dataset including true responses."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

@weave.op()
async def generate_kahneman_response(
    model: LiteLLMModel, 
    question: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a Kahneman-style response to a question."""
    
    # Construct the prompt with context and question
    if question.get('summarised_context'):
        prompt = f"""Context: {question['summarised_context']}

Question: {question['question_text']}

Please respond as Daniel Kahneman would in this interview context."""
    else:
        prompt = f"""Question: {question['question_text']}

Please respond as Daniel Kahneman would in this interview context."""
    
    start_time = datetime.now()
    generated_response = await model.predict(prompt)
    end_time = datetime.now()
    
    generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
    
    return {
        'kahneman_id': question['kahneman_id'],
        'source_doc_id': question['source_doc_id'],
        'sequence_in_source': question['sequence_in_source'],
        'question_text': question['question_text'],
        'summarised_context': question.get('summarised_context', ''),
        'generated_response': generated_response,
        'generation_metadata': {
            "temperature": model.temp,
            "max_tokens": model.max_tokens,
            "generation_time_ms": generation_time_ms,
            "model_version": model.model_name
        }
    }

async def run_single_model_impersonation(
    model_name: str,
    questions: List[Dict[str, Any]],
    system_prompt: str,
    temp: float,
    max_tokens: int,
    top_p: float,
    max_retries: int
) -> Dict[str, Any]:
    """Run impersonation for a single model."""
    
    # Initialize model
    model = LiteLLMModel(
        model_name=model_name,
        temp=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        max_retries=max_retries,
        system_prompt=system_prompt
    )
    
    # Generate responses
    print(f"Generating responses with {model_name}...")
    responses = []
    
    for i, question in enumerate(questions, 1):
        print(f"  Processing question {i}/{len(questions)}: {question['kahneman_id']}")
        try:
            response = await generate_kahneman_response(model, question)
            responses.append(response)
        except Exception as e:
            print(f"  Error processing {question['kahneman_id']}: {e}")
            continue
    
    return {
        "run_metadata": {
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "system_prompt_version": "v1.0",
            "num_questions": len(responses)
        },
        "generated_responses": responses
    }

def save_model_results(results: Dict[str, Any], model_name: str, output_dir: str) -> str:
    """Save individual model results."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_name.replace('/', '-')}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved {model_name} results to: {filepath}")
    return filepath

def create_rating_dataset(
    questions: List[Dict[str, Any]], 
    model_results: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Create a dataset ready for rating with randomized responses."""
    
    rating_questions = []
    
    for question in questions:
        kahneman_id = question['kahneman_id']
        
        # Collect all responses for this question
        responses = []
        
        # Add real response
        response_id = f"{kahneman_id}_resp_real"
        responses.append({
            "response_id": response_id,
            "response_text": question['true_kahneman_response'],
            "hidden_source": "real_kahneman"
        })
        
        # Add AI responses
        resp_counter = 1
        for model_name, results in model_results.items():
            # Find the response for this question
            for resp in results['generated_responses']:
                if resp['kahneman_id'] == kahneman_id:
                    response_id = f"{kahneman_id}_resp_{resp_counter}"
                    responses.append({
                        "response_id": response_id,
                        "response_text": resp['generated_response'],
                        "hidden_source": model_name
                    })
                    resp_counter += 1
                    break
        
        # Randomize response order
        random.shuffle(responses)
        
        rating_questions.append({
            "question_id": kahneman_id,
            "source_doc_id": question['source_doc_id'],
            "sequence_in_source": question['sequence_in_source'],
            "question_text": question['question_text'],
            "summarised_context": question.get('summarised_context', ''),
            "responses": responses
        })
    
    return {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "models_used": list(model_results.keys()),
            "dataset_version": "kahneman_dataset_v1.json",
            "total_questions": len(rating_questions),
            "responses_per_question": len(rating_questions[0]['responses']) if rating_questions else 0
        },
        "questions": rating_questions
    }

def save_rating_dataset(rating_dataset: Dict[str, Any], output_dir: str = "04_rating_datasets") -> str:
    """Save the rating dataset."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rating_dataset_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(rating_dataset, f, indent=2)
    
    print(f"Saved rating dataset to: {filepath}")
    return filepath

async def run_multi_model_impersonation(
    models: str = "gpt-4o,claude-3-opus-20240229",
    dataset_path: str = "02_curated_datasets/kahneman_dataset_v1.json",
    entity: str = None,
    project: str = "kahneman_multi_impersonation",
    temp: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.95,
    max_retries: int = 3,
    system_prompt_path: str = "prompt_library/kahneman_impersonation_prompt.txt",
    output_dir: str = "03_impersonation_runs",
    rating_output_dir: str = "04_rating_datasets",
    random_seed: int = 42
):
    """
    Run Kahneman impersonation task on multiple models and create rating dataset.
    
    Args:
        models (str): Comma-separated list of model names.
        dataset_path (str): Path to the Kahneman dataset JSON file.
        entity (str): Optional Weave entity (org/user name).
        project (str): The project name under the specified entity.
        temp (float): Temperature for the models.
        max_tokens (int): Maximum number of tokens to generate.
        top_p (float): Top-p for the models.
        max_retries (int): Maximum number of retries for the models.
        system_prompt_path (str): Path to system prompt file.
        output_dir (str): Directory to save individual model results.
        rating_output_dir (str): Directory to save rating datasets.
        random_seed (int): Seed for randomization of responses.
    """
    
    # Set random seed for reproducibility
    random.seed(random_seed)
    
    # Initialize Weave
    if entity is not None:
        weave.init(f"{entity}/{project}")
    else:
        weave.init(f"{project}")
    
    # Parse model list
    model_list = [m.strip() for m in models.split(',')]
    print(f"Running impersonation with models: {model_list}")
    
    # Load dataset
    questions = load_kahneman_dataset(dataset_path)
    print(f"Loaded {len(questions)} questions from {dataset_path}")
    
    # Load system prompt
    with open(system_prompt_path, "r") as f:
        system_prompt = f.read().strip()
    
    # Run each model
    model_results = {}
    
    for model_name in model_list:
        print(f"\n{'='*50}")
        print(f"Running {model_name}")
        print(f"{'='*50}")
        
        try:
            results = await run_single_model_impersonation(
                model_name=model_name,
                questions=questions,
                system_prompt=system_prompt,
                temp=temp,
                max_tokens=max_tokens,
                top_p=top_p,
                max_retries=max_retries
            )
            
            # Save individual results
            save_model_results(results, model_name, output_dir)
            model_results[model_name] = results
            
        except Exception as e:
            print(f"Error running {model_name}: {e}")
            continue
    
    # Create and save rating dataset
    if model_results:
        print(f"\n{'='*50}")
        print("Creating rating dataset...")
        print(f"{'='*50}")
        
        rating_dataset = create_rating_dataset(questions, model_results)
        rating_filepath = save_rating_dataset(rating_dataset, rating_output_dir)
        
        print(f"\nCompleted! Generated responses from {len(model_results)} models.")
        print(f"Rating dataset contains {len(rating_dataset['questions'])} questions")
        print(f"with {rating_dataset['metadata']['responses_per_question']} responses each.")
        
        return rating_filepath
    else:
        print("\nNo successful model runs. Rating dataset not created.")
        return None

def main(
    models: str = "gpt-4o,claude-3-opus-20240229",
    dataset_path: str = "02_curated_datasets/kahneman_dataset_v1.json",
    entity: str = None,
    project: str = "kahneman_multi_impersonation",
    temp: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.95,
    max_retries: int = 3,
    system_prompt_path: str = "prompt_library/kahneman_impersonation_prompt.txt",
    output_dir: str = "03_impersonation_runs",
    rating_output_dir: str = "04_rating_datasets",
    random_seed: int = 42
):
    """Main entry point for CLI usage."""
    return asyncio.run(run_multi_model_impersonation(
        models=models,
        dataset_path=dataset_path,
        entity=entity,
        project=project,
        temp=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        max_retries=max_retries,
        system_prompt_path=system_prompt_path,
        output_dir=output_dir,
        rating_output_dir=rating_output_dir,
        random_seed=random_seed
    ))

if __name__ == "__main__":
    Fire(main)