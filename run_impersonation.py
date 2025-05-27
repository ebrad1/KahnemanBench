# python run_impersonation.py --model_name=gpt-4o --dataset_path=data/kahneman_dataset_v1.json

import json
import weave
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from fire import Fire
from dotenv import load_dotenv

load_dotenv()

from weave_utils.models import LiteLLMModel

def load_kahneman_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Load Kahneman dataset, excluding true responses."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    questions = []
    for item in data:
        question = {
            'kahneman_id': item['kahneman_id'],
            'source_doc_id': item['source_doc_id'],
            'sequence_in_source': item['sequence_in_source'],
            'question_text': item['question_text'],
            'summarised_context': item['summarised_context']
        }
        questions.append(question)
    
    return questions

@weave.op()
async def generate_kahneman_response(
    model: LiteLLMModel, 
    question: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a Kahneman-style response to a question."""
    
    # Construct the prompt with context and question
    if question['summarised_context']:
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
        'summarised_context': question['summarised_context'],
        'generated_response': generated_response,
        'generation_metadata': {
            "temperature": model.temp,
            "max_tokens": model.max_tokens,
            "generation_time_ms": generation_time_ms,
            "model_version": model.model_name
        }
    }

def save_impersonation_results(
    responses: List[Dict[str, Any]],
    model_name: str,
    dataset_path: str,
    output_path: str = None
) -> str:
    """Save impersonation results to JSON file."""
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"kahneman_impersonation_{model_name}_{timestamp}.json"
    
    output_data = {
        "run_metadata": {
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "system_prompt_version": "v1.0",
            "dataset_version": dataset_path,
            "run_id": f"kahneman_impersonation_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "num_questions": len(responses)
        },
        "generated_responses": responses
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Results saved to: {output_path}")
    return output_path

async def run_kahneman_impersonation(
    model_name: str = "gpt-4o",
    dataset_path: str = "data/kahneman_dataset_v1.json",
    entity: str = None,
    project: str = "kahneman_impersonation",
    temp: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.95,
    max_retries: int = 3,
    system_prompt_path: str = "kahneman_impersonation_prompt.txt",
    output_path: str = None
):
    """
    Run Kahneman impersonation task on a given model and dataset.
    
    Args:
        model_name (str): Name of the model to use for impersonation.
        dataset_path (str): Path to the Kahneman dataset JSON file.
        entity (str): Optional Weave entity (org/user name).
        project (str): The project name under the specified entity.
        temp (float): Temperature for the model.
        max_tokens (int): Maximum number of tokens to generate.
        top_p (float): Top-p for the model.
        max_retries (int): Maximum number of retries for the model.
        system_prompt_path (str): Path to system prompt file.
        output_path (str): Path to save results (auto-generated if None).
    """
    
    # Initialize Weave
    if entity is not None:
        weave.init(f"{entity}/{project}")
    else:
        weave.init(f"{project}")
    
    # Load dataset
    questions = load_kahneman_dataset(dataset_path)
    print(f"Loaded {len(questions)} questions from {dataset_path}")
    
    # Load system prompt
    with open(system_prompt_path, "r") as f:
        system_prompt = f.read().strip()
    
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
    print(f"Generating Kahneman impersonations with {model_name}...")
    responses = []
    
    for i, question in enumerate(questions, 1):
        print(f"Processing question {i}/{len(questions)}: {question['kahneman_id']}")
        try:
            response = await generate_kahneman_response(model, question)
            responses.append(response)
        except Exception as e:
            print(f"Error processing {question['kahneman_id']}: {e}")
            continue
    
    # Save results
    output_file = save_impersonation_results(responses, model_name, dataset_path, output_path)
    
    print(f"Completed! Generated {len(responses)} responses.")
    print(f"Results saved to: {output_file}")
    
    return responses

def main(
    model_name: str = "gpt-4o",
    dataset_path: str = "data/kahneman_dataset_v1.json",
    entity: str = None,
    project: str = "kahneman_impersonation", 
    temp: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.95,
    max_retries: int = 3,
    system_prompt_path: str = "prompt_library/kahneman_impersonation_prompt.txt",
    output_path: str = None
):
    """Main entry point for CLI usage."""
    return asyncio.run(run_kahneman_impersonation(
        model_name=model_name,
        dataset_path=dataset_path,
        entity=entity,
        project=project,
        temp=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        max_retries=max_retries,
        system_prompt_path=system_prompt_path,
        output_path=output_path
    ))

if __name__ == "__main__":
    Fire(main)