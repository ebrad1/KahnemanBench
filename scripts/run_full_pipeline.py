#!/usr/bin/env python3
"""
KahnemanBench Full Pipeline Automation

Orchestrates the complete evaluation pipeline:
1. Multi-model impersonation generation
2. Rating dataset creation 
3. Rating evaluation
4. Dashboard generation
5. Summary reporting

Usage:
    python scripts/run_full_pipeline.py --models=gpt-4o,claude-3-opus-20240229 --rater=gpt-4o
    python scripts/run_full_pipeline.py --config=configs/quick_test.yaml
"""

import os
import sys
import json
import yaml
import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from fire import Fire

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PipelineRunner:
    """Orchestrates the full KahnemanBench evaluation pipeline."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.run_id = self.start_time.strftime("pipeline_%Y%m%d_%H%M%S")
        self.results = {
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "steps_completed": [],
            "outputs": {},
            "errors": []
        }
        
    def log_step(self, step_name: str, status: str, details: Dict[str, Any] = None):
        """Log pipeline step completion."""
        step_info = {
            "step": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results["steps_completed"].append(step_info)
        
        if status == "completed":
            logger.info(f"✓ {step_name} completed successfully")
        elif status == "failed":
            logger.error(f"✗ {step_name} failed: {details}")
        else:
            logger.info(f"⏳ {step_name}: {status}")
    
    def run_subprocess(self, command: List[str], step_name: str) -> Dict[str, Any]:
        """Run a subprocess and handle errors."""
        try:
            logger.info(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            error_details = {
                "command": command,
                "returncode": e.returncode,
                "stdout": e.stdout,
                "stderr": e.stderr
            }
            self.log_step(step_name, "failed", error_details)
            return {
                "success": False,
                "error": str(e),
                "details": error_details
            }
    
    def step1_multi_impersonation(self, models: List[str], dataset_path: str) -> Optional[str]:
        """Step 1: Generate impersonations from multiple models."""
        self.log_step("multi_impersonation", "starting")
        
        models_str = ",".join(models)
        command = [
            "python", "scripts/run_multi_impersonation.py",
            f"--models={models_str}",
            f"--dataset_path={dataset_path}",
            f"--project=kahneman_pipeline_{self.run_id}"
        ]
        
        result = self.run_subprocess(command, "multi_impersonation")
        
        if result["success"]:
            # Extract rating dataset path from output
            output_lines = result["stdout"].split('\n')
            rating_dataset_path = None
            
            for line in output_lines:
                if "Rating dataset saved to:" in line:
                    rating_dataset_path = line.split("Rating dataset saved to:")[-1].strip()
                    break
            
            if rating_dataset_path:
                self.log_step("multi_impersonation", "completed", {
                    "models": models,
                    "rating_dataset": rating_dataset_path
                })
                self.results["outputs"]["rating_dataset"] = rating_dataset_path
                return rating_dataset_path
            else:
                self.log_step("multi_impersonation", "failed", {
                    "error": "Could not find rating dataset path in output"
                })
                return None
        
        return None
    
    def step2_rating_evaluation(self, rater_model: str, rating_dataset_path: str) -> Optional[str]:
        """Step 2: Evaluate ratings using rater model."""
        self.log_step("rating_evaluation", "starting")
        
        command = [
            "python", "scripts/run_rating.py",
            f"--rater_model={rater_model}",
            f"--dataset_path={rating_dataset_path}",
            f"--project=kahneman_pipeline_{self.run_id}"
        ]
        
        result = self.run_subprocess(command, "rating_evaluation")
        
        if result["success"]:
            # Extract rating results path from output
            output_lines = result["stdout"].split('\n')
            rating_results_path = None
            
            for line in output_lines:
                if "Results saved to:" in line:
                    rating_results_path = line.split("Results saved to:")[-1].strip()
                    break
            
            if rating_results_path:
                self.log_step("rating_evaluation", "completed", {
                    "rater_model": rater_model,
                    "rating_results": rating_results_path
                })
                self.results["outputs"]["rating_results"] = rating_results_path
                return rating_results_path
            else:
                self.log_step("rating_evaluation", "failed", {
                    "error": "Could not find rating results path in output"
                })
                return None
        
        return None
    
    def step3_generate_dashboard(self, rating_results_path: str) -> bool:
        """Step 3: Generate updated analysis dashboard."""
        self.log_step("dashboard_generation", "starting")
        
        command = [
            "python", "06_analysis_outputs/analyze_ratings.py",
            f"--rating_results={rating_results_path}",
            "--update_dashboard"
        ]
        
        result = self.run_subprocess(command, "dashboard_generation")
        
        if result["success"]:
            dashboard_path = "06_analysis_outputs/rating_dashboard.html"
            self.log_step("dashboard_generation", "completed", {
                "dashboard_path": dashboard_path
            })
            self.results["outputs"]["dashboard"] = dashboard_path
            return True
        
        return False
    
    def step4_generate_summary(self) -> str:
        """Step 4: Generate pipeline summary report."""
        self.log_step("summary_generation", "starting")
        
        summary = {
            "pipeline_run": self.results,
            "duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
            "outputs_generated": list(self.results["outputs"].keys()),
            "success": len(self.results["errors"]) == 0
        }
        
        summary_path = f"06_analysis_outputs/pipeline_summary_{self.run_id}.json"
        
        try:
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.log_step("summary_generation", "completed", {
                "summary_path": summary_path
            })
            self.results["outputs"]["summary"] = summary_path
            return summary_path
            
        except Exception as e:
            self.log_step("summary_generation", "failed", {"error": str(e)})
            return None
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load pipeline configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config {config_path}: {e}")
            return {}
    
    def run_pipeline(
        self,
        models: List[str] = None,
        rater_model: str = "gpt-4o",
        dataset_path: str = "02_curated_datasets/kahneman_dataset_v1.json",
        config_path: str = None,
        skip_impersonation: bool = False,
        rating_dataset_path: str = None
    ) -> Dict[str, Any]:
        """
        Run the complete KahnemanBench evaluation pipeline.
        
        Args:
            models: List of models for impersonation (e.g., ["gpt-4o", "claude-3-opus-20240229"])
            rater_model: Model to use for rating evaluation
            dataset_path: Path to Kahneman dataset
            config_path: Path to YAML/JSON config file (overrides other args)
            skip_impersonation: Skip to rating if you have existing rating dataset
            rating_dataset_path: Use existing rating dataset (requires skip_impersonation=True)
        """
        
        logger.info(f"🚀 Starting KahnemanBench pipeline run: {self.run_id}")
        
        # Load config if provided
        if config_path:
            config = self.load_config(config_path)
            models = config.get("models", models)
            rater_model = config.get("rater_model", rater_model)
            dataset_path = config.get("dataset_path", dataset_path)
            skip_impersonation = config.get("skip_impersonation", skip_impersonation)
            rating_dataset_path = config.get("rating_dataset_path", rating_dataset_path)
        
        # Validate inputs
        if not skip_impersonation and not models:
            raise ValueError("Must provide models list or set skip_impersonation=True")
        
        if skip_impersonation and not rating_dataset_path:
            raise ValueError("Must provide rating_dataset_path when skip_impersonation=True")
        
        # Step 1: Multi-model impersonation (unless skipped)
        if not skip_impersonation:
            rating_dataset_path = self.step1_multi_impersonation(models, dataset_path)
            if not rating_dataset_path:
                logger.error("❌ Pipeline failed at impersonation step")
                return self.results
        else:
            logger.info(f"⏭️  Skipping impersonation, using: {rating_dataset_path}")
            self.results["outputs"]["rating_dataset"] = rating_dataset_path
        
        # Step 2: Rating evaluation
        rating_results_path = self.step2_rating_evaluation(rater_model, rating_dataset_path)
        if not rating_results_path:
            logger.error("❌ Pipeline failed at rating step")
            return self.results
        
        # Step 3: Dashboard generation (optional - don't fail pipeline if this fails)
        try:
            self.step3_generate_dashboard(rating_results_path)
        except Exception as e:
            logger.warning(f"⚠️  Dashboard generation failed: {e}")
            self.results["errors"].append(f"Dashboard generation failed: {e}")
        
        # Step 4: Summary generation
        summary_path = self.step4_generate_summary()
        
        # Final results
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        logger.info(f"🎉 Pipeline completed in {duration:.1f} minutes")
        logger.info(f"📊 Outputs: {list(self.results['outputs'].keys())}")
        
        if self.results["errors"]:
            logger.warning(f"⚠️  Pipeline completed with {len(self.results['errors'])} warnings")
        
        return self.results

# CLI interface
def main(
    models: str = None,
    rater_model: str = "gpt-4o", 
    dataset_path: str = "02_curated_datasets/kahneman_dataset_v1.json",
    config: str = None,
    skip_impersonation: bool = False,
    rating_dataset_path: str = None
):
    """
    Run the complete KahnemanBench evaluation pipeline.
    
    Examples:
        # Full pipeline with multiple models
        python scripts/run_full_pipeline.py --models=gpt-4o,claude-3-opus-20240229 --rater_model=gpt-4o
        
        # Using a config file
        python scripts/run_full_pipeline.py --config=configs/quick_test.yaml
        
        # Skip impersonation and use existing rating dataset
        python scripts/run_full_pipeline.py --skip_impersonation --rating_dataset_path=04_rating_datasets/rating_dataset_20250101_120000.json --rater_model=gpt-4o
    """
    
    # Parse models string to list
    models_list = None
    if models:
        models_list = [m.strip() for m in models.split(',')]
    
    # Create and run pipeline
    pipeline = PipelineRunner()
    
    try:
        results = pipeline.run_pipeline(
            models=models_list,
            rater_model=rater_model,
            dataset_path=dataset_path,
            config_path=config,
            skip_impersonation=skip_impersonation,
            rating_dataset_path=rating_dataset_path
        )
        
        # Print summary
        print("\n" + "="*60)
        print("PIPELINE SUMMARY")
        print("="*60)
        print(f"Run ID: {results['run_id']}")
        print(f"Duration: {(datetime.now() - pipeline.start_time).total_seconds() / 60:.1f} minutes")
        print(f"Steps completed: {len(results['steps_completed'])}")
        print(f"Outputs generated: {len(results['outputs'])}")
        
        if results['outputs']:
            print("\nGenerated files:")
            for output_type, path in results['outputs'].items():
                print(f"  {output_type}: {path}")
        
        if results['errors']:
            print(f"\nWarnings/Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed with exception: {e}")
        raise

if __name__ == "__main__":
    Fire(main)