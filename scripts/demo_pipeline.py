#!/usr/bin/env python3
"""
Demo script to show pipeline functionality without making API calls.
This creates mock data to demonstrate the complete pipeline flow.
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_mock_rating_dataset():
    """Create a mock rating dataset for demo purposes."""
    mock_dataset = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "models_used": ["gpt-4o", "claude-3-5-sonnet"],
            "dataset_version": "demo_v1.json",
            "total_questions": 2,
            "responses_per_question": 3
        },
        "questions": [
            {
                "question_id": "demo_1",
                "source_doc_id": "demo_interview",
                "sequence_in_source": 1,
                "question_text": "What role does intuition play in decision-making?",
                "summarised_context": "Discussion about System 1 vs System 2 thinking",
                "responses": [
                    {
                        "response_id": "demo_1_resp_1",
                        "response_text": "Intuition is essentially the operation of System 1 - it's fast, automatic, and often quite accurate in familiar domains. However, it can also lead us astray when we're dealing with statistical thinking or unfamiliar situations.",
                        "hidden_source": "real_kahneman"
                    },
                    {
                        "response_id": "demo_1_resp_2",
                        "response_text": "Well, you know, this is a fascinating question that touches on the dual-system theory. Intuition represents our fast, automatic thinking processes that guide many of our daily decisions.",
                        "hidden_source": "gpt-4o"
                    },
                    {
                        "response_id": "demo_1_resp_3",
                        "response_text": "From a behavioral economics perspective, I would say that intuition plays a crucial role in how we navigate uncertainty and make rapid judgments in complex situations.",
                        "hidden_source": "claude-3-5-sonnet"
                    }
                ]
            },
            {
                "question_id": "demo_2",
                "source_doc_id": "demo_interview",
                "sequence_in_source": 2,
                "question_text": "How do you view the relationship between happiness and well-being?",
                "summarised_context": "Discussion about hedonic psychology",
                "responses": [
                    {
                        "response_id": "demo_2_resp_1",
                        "response_text": "The relationship is complex. We often make decisions based on predicted happiness, but our predictions are systematically biased. We overestimate both the intensity and duration of future emotional states.",
                        "hidden_source": "real_kahneman"
                    },
                    {
                        "response_id": "demo_2_resp_2",
                        "response_text": "Happiness and well-being are related but distinct concepts. Our research shows that people's moment-to-moment experiences differ significantly from their retrospective evaluations.",
                        "hidden_source": "gpt-4o"
                    },
                    {
                        "response_id": "demo_2_resp_3",
                        "response_text": "This is a fundamental question in psychology. The distinction between experienced utility and remembered utility is crucial for understanding how people actually make choices.",
                        "hidden_source": "claude-3-5-sonnet"
                    }
                ]
            }
        ]
    }
    
    return mock_dataset

def create_mock_rating_results(rating_dataset_path: str):
    """Create mock rating results for demo purposes."""
    mock_results = {
        "rating_metadata": {
            "rater_model": "gpt-4o",
            "dataset_path": rating_dataset_path,
            "timestamp": datetime.now().isoformat(),
            "total_responses_rated": 6
        },
        "ratings": [
            {
                "question_id": "demo_1",
                "question_text": "What role does intuition play in decision-making?",
                "response_ratings": [
                    {
                        "response_id": "demo_1_resp_1",
                        "response_text": "Intuition is essentially the operation of System 1...",
                        "hidden_source": "real_kahneman",
                        "authenticity_score": 92,
                        "reasoning": "This response demonstrates deep understanding of dual-system theory and matches Kahneman's typical explanatory style."
                    },
                    {
                        "response_id": "demo_1_resp_2", 
                        "response_text": "Well, you know, this is a fascinating question...",
                        "hidden_source": "gpt-4o",
                        "authenticity_score": 78,
                        "reasoning": "Good conceptual understanding but lacks the precise terminology and nuanced perspective typical of Kahneman."
                    },
                    {
                        "response_id": "demo_1_resp_3",
                        "response_text": "From a behavioral economics perspective...",
                        "hidden_source": "claude-3-5-sonnet", 
                        "authenticity_score": 71,
                        "reasoning": "Academically sound but uses more formal language than Kahneman typically employs in interviews."
                    }
                ]
            },
            {
                "question_id": "demo_2",
                "question_text": "How do you view the relationship between happiness and well-being?",
                "response_ratings": [
                    {
                        "response_id": "demo_2_resp_1",
                        "response_text": "The relationship is complex...",
                        "hidden_source": "real_kahneman",
                        "authenticity_score": 95,
                        "reasoning": "Perfectly captures Kahneman's research insights and communication style on this topic."
                    },
                    {
                        "response_id": "demo_2_resp_2",
                        "response_text": "Happiness and well-being are related but distinct...",
                        "hidden_source": "gpt-4o",
                        "authenticity_score": 82,
                        "reasoning": "Accurate content but slightly more structured than Kahneman's typical interview responses."
                    },
                    {
                        "response_id": "demo_2_resp_3",
                        "response_text": "This is a fundamental question in psychology...",
                        "hidden_source": "claude-3-5-sonnet",
                        "authenticity_score": 75,
                        "reasoning": "Shows understanding of key concepts but lacks personal insight and specific research references."
                    }
                ]
            }
        ],
        "summary_metrics": {
            "real_kahneman_avg_score": 93.5,
            "ai_responses_avg_score": 76.5,
            "score_gap": 17.0,
            "num_real_responses": 2,
            "num_ai_responses": 4,
            "model_avg_scores": {
                "gpt-4o": 80.0,
                "claude-3-5-sonnet": 73.0
            }
        }
    }
    
    return mock_results

def run_demo():
    """Run a complete demo of the pipeline with mock data."""
    print("🎭 KahnemanBench Pipeline Demo")
    print("=" * 50)
    print("This demo shows the complete pipeline flow using mock data")
    print("(no API calls will be made)\n")
    
    # Step 1: Create mock rating dataset
    print("📊 Step 1: Creating mock rating dataset...")
    rating_dataset = create_mock_rating_dataset()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir='04_rating_datasets') as f:
        json.dump(rating_dataset, f, indent=2)
        rating_dataset_path = f.name
    
    print(f"✓ Mock rating dataset created: {rating_dataset_path}")
    print(f"  - Models: {rating_dataset['metadata']['models_used']}")
    print(f"  - Questions: {rating_dataset['metadata']['total_questions']}")
    print(f"  - Responses per question: {rating_dataset['metadata']['responses_per_question']}")
    
    # Step 2: Create mock rating results
    print("\n🤖 Step 2: Creating mock rating results...")
    rating_results = create_mock_rating_results(rating_dataset_path)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rating_results_path = f"05_rating_results/demo_rating_results_{timestamp}.json"
    
    with open(rating_results_path, 'w') as f:
        json.dump(rating_results, f, indent=2)
    
    print(f"✓ Mock rating results created: {rating_results_path}")
    print(f"  - Real Kahneman avg: {rating_results['summary_metrics']['real_kahneman_avg_score']}")
    print(f"  - AI responses avg: {rating_results['summary_metrics']['ai_responses_avg_score']}")
    print(f"  - Score gap: {rating_results['summary_metrics']['score_gap']}")
    
    # Step 3: Generate dashboard
    print("\n📈 Step 3: Generating analysis dashboard...")
    try:
        import subprocess
        result = subprocess.run([
            "python", "06_analysis_outputs/analyze_ratings.py",
            f"--rating_results={rating_results_path}",
            "--update_dashboard"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if result.returncode == 0:
            print("✓ Dashboard generated successfully")
            print("  - Location: 06_analysis_outputs/rating_dashboard.html")
        else:
            print(f"⚠️  Dashboard generation had issues: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Dashboard generation failed: {e}")
    
    # Step 4: Summary
    print(f"\n🎉 Demo completed successfully!")
    print("\nGenerated files:")
    print(f"  - Rating dataset: {rating_dataset_path}")
    print(f"  - Rating results: {rating_results_path}")
    print(f"  - Dashboard: 06_analysis_outputs/rating_dashboard.html")
    
    print(f"\nTo view the dashboard:")
    print(f"  open 06_analysis_outputs/rating_dashboard.html")
    
    print(f"\nTo run a real pipeline:")
    print(f"  python scripts/run_full_pipeline.py --config=configs/quick_test.yaml")
    
    # Cleanup
    try:
        os.unlink(rating_dataset_path)
        print(f"\n🧹 Cleaned up temporary files")
    except:
        pass

if __name__ == "__main__":
    run_demo()