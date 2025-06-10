# python run_rating.py --rater_model=gpt-4o --dataset_path=rating_datasets/rating_dataset_20250528_200201.json

import json
import weave
import asyncio
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from fire import Fire
from dotenv import load_dotenv

load_dotenv()

from weave_utils.models import LiteLLMModel

def load_rating_dataset(file_path: str) -> Dict[str, Any]:
    """Load rating dataset with questions and responses."""
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_rating_output(output: str) -> Tuple[float, str]:
    """Parse the rating output to extract score and reasoning."""
    # Look for score pattern
    score_match = re.search(r'Score:\s*(\d+(?:\.\d+)?)', output, re.IGNORECASE)
    if not score_match:
        raise ValueError(f"Could not find score in output: {output}")
    
    score = float(score_match.group(1))
    
    # Extract reasoning if present
    reasoning_match = re.search(r'Reasoning:\s*(.*)', output, re.IGNORECASE | re.DOTALL)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
    
    return score, reasoning

@weave.op()
async def rate_response(
    model: LiteLLMModel,
    question: Dict[str, Any],
    response: Dict[str, Any]
) -> Dict[str, Any]:
    """Rate a single response for authenticity."""
    
    # Construct the prompt
    prompt = f"""Question asked to Daniel Kahneman: {question['question_text']}

Response to evaluate:
{response['response_text']}

Please rate this response."""

    start_time = datetime.now()
    rating_output = await model.predict(prompt)
    end_time = datetime.now()
    
    generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
    
    # Parse the output
    try:
        score, reasoning = parse_rating_output(rating_output)
    except ValueError as e:
        print(f"Error parsing rating: {e}")
        score, reasoning = 50.0, "Failed to parse rating"
    
    return {
        'response_id': response['response_id'],
        'authenticity_score': score,
        'reasoning': reasoning,
        'hidden_source': response['hidden_source'],
        'rating_time_ms': generation_time_ms
    }

def calculate_metrics(all_ratings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary metrics from ratings."""
    real_scores = [r['authenticity_score'] for r in all_ratings if r['hidden_source'] == 'real_kahneman']
    ai_scores = [r['authenticity_score'] for r in all_ratings if r['hidden_source'] != 'real_kahneman']
    
    # Group by model
    model_scores = {}
    for rating in all_ratings:
        if rating['hidden_source'] != 'real_kahneman':
            model = rating['hidden_source']
            if model not in model_scores:
                model_scores[model] = []
            model_scores[model].append(rating['authenticity_score'])
    
    return {
        'num_real_responses': len(real_scores),
        'num_ai_responses': len(ai_scores),
        'real_kahneman_avg_score': sum(real_scores) / len(real_scores) if real_scores else 0,
        'ai_responses_avg_score': sum(ai_scores) / len(ai_scores) if ai_scores else 0,
        'score_gap': (sum(real_scores) / len(real_scores) if real_scores else 0) - 
                     (sum(ai_scores) / len(ai_scores) if ai_scores else 0),
        'model_avg_scores': {model: sum(scores) / len(scores) 
                            for model, scores in model_scores.items()}
    }

def save_rating_results(
    ratings: Dict[str, Any],
    rater_model: str,
    dataset_path: str,
    output_path: str = None,
    output_dir: str = "rating_results"
) -> str:
    """Save rating results to JSON file in specified directory."""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rating_results_{rater_model.replace('/', '-')}_{timestamp}.json"
        output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w') as f:
        json.dump(ratings, f, indent=2)
    
    print(f"Results saved to: {output_path}")
    return output_path

async def run_rating(
    rater_model: str = "gpt-4o",
    dataset_path: str = "rating_datasets/rating_dataset_20250528_200201.json",
    entity: str = None,
    project: str = "kahneman_rating",
    temp: float = 0.7,
    max_tokens: int = 512,
    top_p: float = 0.95,
    max_retries: int = 3,
    system_prompt_path: str = "prompt_library/kahneman_rater_prompt.txt",
    output_path: str = None,
    output_dir: str = "rating_results"
):
    """
    Run rating task on a dataset of Kahneman responses.
    
    Args:
        rater_model (str): Model to use for rating.
        dataset_path (str): Path to the rating dataset JSON file.
        entity (str): Optional Weave entity (org/user name).
        project (str): The project name under the specified entity.
        temp (float): Temperature for the model.
        max_tokens (int): Maximum number of tokens to generate.
        top_p (float): Top-p for the model.
        max_retries (int): Maximum number of retries for the model.
        system_prompt_path (str): Path to system prompt file.
        output_path (str): Path to save results (auto-generated if None).
        output_dir (str): Directory to save results in. Default is "rating_results".
    """
    
    # Initialize Weave
    if entity is not None:
        weave.init(f"{entity}/{project}")
    else:
        weave.init(f"{project}")
    
    # Load dataset
    dataset = load_rating_dataset(dataset_path)
    questions = dataset['questions']
    print(f"Loaded {len(questions)} questions from {dataset_path}")
    print(f"Each question has {dataset['metadata']['responses_per_question']} responses")
    
    # Load system prompt
    with open(system_prompt_path, "r") as f:
        system_prompt = f.read().strip()
    
    # Initialize model
    model = LiteLLMModel(
        model_name=rater_model,
        temp=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        max_retries=max_retries,
        system_prompt=system_prompt
    )
    
    # Rate all responses
    print(f"Rating responses with {rater_model}...")
    all_ratings = []
    question_ratings = []
    
    for i, question in enumerate(questions, 1):
        print(f"Rating question {i}/{len(questions)}: {question['question_id']}")
        
        response_ratings = []
        for j, response in enumerate(question['responses'], 1):
            print(f"  Rating response {j}/{len(question['responses'])}")
            try:
                rating = await rate_response(model, question, response)
                response_ratings.append(rating)
                all_ratings.append(rating)
            except Exception as e:
                print(f"  Error rating response: {e}")
                continue
        
        question_ratings.append({
            'question_id': question['question_id'],
            'response_ratings': response_ratings
        })
    
    # Calculate metrics
    metrics = calculate_metrics(all_ratings)
    
    # Prepare output
    output_data = {
        "rating_metadata": {
            "rater_model": rater_model,
            "rating_dataset": dataset_path,
            "timestamp": datetime.now().isoformat(),
            "total_responses_rated": len(all_ratings)
        },
        "ratings": question_ratings,
        "summary_metrics": metrics
    }
    
    # Save results
    output_file = save_rating_results(output_data, rater_model, dataset_path, output_path, output_dir)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Rating Summary for {rater_model}")
    print(f"{'='*50}")
    print(f"Real Kahneman avg score: {metrics['real_kahneman_avg_score']:.1f}")
    print(f"AI responses avg score: {metrics['ai_responses_avg_score']:.1f}")
    print(f"Score gap (Real - AI): {metrics['score_gap']:.1f}")
    print(f"\nModel breakdown:")
    for model, avg_score in metrics['model_avg_scores'].items():
        print(f"  {model}: {avg_score:.1f}")
    
    return output_data

def main(
    rater_model: str = "gpt-4o",
    dataset_path: str = "rating_datasets/rating_dataset_20250528_200201.json",
    entity: str = None,
    project: str = "kahneman_rating",
    temp: float = 0.7,
    max_tokens: int = 512,
    top_p: float = 0.95,
    max_retries: int = 3,
    system_prompt_path: str = "prompt_library/kahneman_rater_prompt.txt",
    output_path: str = None,
    output_dir: str = "rating_results"
):
    """Main entry point for CLI usage."""
    return asyncio.run(run_rating(
        rater_model=rater_model,
        dataset_path=dataset_path,
        entity=entity,
        project=project,
        temp=temp,
        max_tokens=max_tokens,
        top_p=top_p,
        max_retries=max_retries,
        system_prompt_path=system_prompt_path,
        output_path=output_path,
        output_dir=output_dir
    ))

if __name__ == "__main__":
    Fire(main)