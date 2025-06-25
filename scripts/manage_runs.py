#!/usr/bin/env python3
"""
Run management utility for organizing and cleaning up KahnemanBench outputs.
Helps manage the accumulation of JSON files from multiple experiments.
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from fire import Fire

class RunManager:
    """Manages KahnemanBench experiment runs and outputs."""
    
    def __init__(self):
        self.base_dirs = {
            'impersonation': '03_impersonation_runs',
            'rating_datasets': '04_rating_datasets', 
            'rating_results': '05_rating_results',
            'analysis': '06_analysis_outputs'
        }
        self.archive_dir = 'archive'
    
    def list_runs(self, days: int = None, run_type: str = None):
        """
        List all runs, optionally filtered by recency and type.
        
        Args:
            days: Only show runs from last N days
            run_type: Filter by type (impersonation, rating_datasets, rating_results)
        """
        print("KahnemanBench Run Inventory")
        print("=" * 50)
        
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"Showing runs from last {days} days\n")
        
        total_files = 0
        total_size = 0
        
        for run_type_name, directory in self.base_dirs.items():
            if run_type and run_type != run_type_name:
                continue
                
            if not os.path.exists(directory):
                continue
                
            print(f"\n📁 {run_type_name.upper()} ({directory})")
            print("-" * 30)
            
            files = []
            for file_path in Path(directory).glob('*.json'):
                stat = file_path.stat()
                file_date = datetime.fromtimestamp(stat.st_mtime)
                
                if days and file_date < cutoff_date:
                    continue
                    
                files.append({
                    'name': file_path.name,
                    'date': file_date,
                    'size': stat.st_size,
                    'path': str(file_path)
                })
            
            # Sort by date (newest first)
            files.sort(key=lambda x: x['date'], reverse=True)
            
            for file_info in files:
                size_mb = file_info['size'] / (1024 * 1024)
                date_str = file_info['date'].strftime('%Y-%m-%d %H:%M')
                print(f"  {file_info['name']:<50} {date_str} ({size_mb:.1f}MB)")
                total_files += 1
                total_size += file_info['size']
        
        print(f"\n📊 SUMMARY")
        print(f"Total files: {total_files}")
        print(f"Total size: {total_size / (1024 * 1024):.1f}MB")
    
    def analyze_run_metadata(self):
        """Analyze metadata across all runs to show patterns."""
        print("Run Metadata Analysis")
        print("=" * 50)
        
        models_used = set()
        rater_models = set()
        run_dates = []
        
        # Analyze impersonation runs
        impersonation_dir = self.base_dirs['impersonation']
        if os.path.exists(impersonation_dir):
            for file_path in Path(impersonation_dir).glob('*.json'):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if 'run_metadata' in data:
                        model = data['run_metadata'].get('model_name', 'unknown')
                        models_used.add(model)
                        
                        timestamp = data['run_metadata'].get('timestamp')
                        if timestamp:
                            run_dates.append(timestamp)
                            
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
        
        # Analyze rating results
        rating_dir = self.base_dirs['rating_results']
        if os.path.exists(rating_dir):
            for file_path in Path(rating_dir).glob('*.json'):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if 'rating_metadata' in data:
                        rater = data['rating_metadata'].get('rater_model', 'unknown')
                        rater_models.add(rater)
                        
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
        
        print(f"Models tested: {len(models_used)}")
        for model in sorted(models_used):
            print(f"  - {model}")
        
        print(f"\nRater models used: {len(rater_models)}")
        for rater in sorted(rater_models):
            print(f"  - {rater}")
        
        if run_dates:
            run_dates.sort()
            print(f"\nRun timeline:")
            print(f"  First run: {run_dates[0]}")
            print(f"  Latest run: {run_dates[-1]}")
            print(f"  Total runs: {len(run_dates)}")
    
    def archive_old_runs(self, days: int = 30, dry_run: bool = True):
        """
        Archive runs older than specified days.
        
        Args:
            days: Archive runs older than this many days
            dry_run: If True, show what would be archived without doing it
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        print(f"Archiving runs older than {days} days (before {cutoff_date.strftime('%Y-%m-%d')})")
        print("=" * 60)
        
        if dry_run:
            print("DRY RUN - No files will be moved\n")
        
        # Create archive directory structure
        archive_base = Path(self.archive_dir)
        if not dry_run:
            for run_type in self.base_dirs.keys():
                (archive_base / run_type).mkdir(parents=True, exist_ok=True)
        
        total_archived = 0
        total_size = 0
        
        for run_type, directory in self.base_dirs.items():
            if not os.path.exists(directory):
                continue
            
            files_to_archive = []
            
            for file_path in Path(directory).glob('*.json'):
                stat = file_path.stat()
                file_date = datetime.fromtimestamp(stat.st_mtime)
                
                if file_date < cutoff_date:
                    files_to_archive.append((file_path, file_date, stat.st_size))
            
            if files_to_archive:
                print(f"\n📁 {run_type.upper()}")
                print("-" * 30)
                
                for file_path, file_date, size in files_to_archive:
                    size_mb = size / (1024 * 1024)
                    date_str = file_date.strftime('%Y-%m-%d %H:%M')
                    print(f"  {file_path.name:<50} {date_str} ({size_mb:.1f}MB)")
                    
                    if not dry_run:
                        # Move to archive
                        archive_path = archive_base / run_type / file_path.name
                        shutil.move(str(file_path), str(archive_path))
                    
                    total_archived += 1
                    total_size += size
        
        action = "Would archive" if dry_run else "Archived"
        print(f"\n📊 SUMMARY")
        print(f"{action} {total_archived} files ({total_size / (1024 * 1024):.1f}MB)")
        
        if dry_run and total_archived > 0:
            print(f"\nTo actually archive these files, run:")
            print(f"python scripts/manage_runs.py archive_old_runs --days={days} --dry_run=False")
    
    def cleanup_tmp_files(self):
        """Remove temporary files and incomplete runs."""
        print("Cleaning up temporary files")
        print("=" * 40)
        
        patterns_to_clean = [
            '04_rating_datasets/tmp*.json',
            '**/*tmp*',
            '**/*.log',
            '**/pipeline.log'
        ]
        
        cleaned_files = 0
        for pattern in patterns_to_clean:
            for file_path in Path('.').glob(pattern):
                if file_path.is_file():
                    print(f"Removing: {file_path}")
                    file_path.unlink()
                    cleaned_files += 1
        
        if cleaned_files == 0:
            print("No temporary files found to clean")
        else:
            print(f"Cleaned {cleaned_files} temporary files")
    
    def create_experiment_summary(self, output_file: str = "experiment_summary.json"):
        """Create a summary of all experiments for easier tracking."""
        print("Creating experiment summary...")
        
        experiments = []
        
        # Process rating results to build experiment info
        rating_dir = self.base_dirs['rating_results']
        if os.path.exists(rating_dir):
            for file_path in Path(rating_dir).glob('*.json'):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    if 'rating_metadata' in data and 'summary_metrics' in data:
                        experiment = {
                            'file': file_path.name,
                            'date': data['rating_metadata'].get('timestamp'),
                            'rater_model': data['rating_metadata'].get('rater_model'),
                            'dataset': data['rating_metadata'].get('dataset_path', '').split('/')[-1],
                            'real_avg_score': data['summary_metrics'].get('real_kahneman_avg_score'),
                            'ai_avg_score': data['summary_metrics'].get('ai_responses_avg_score'),
                            'score_gap': data['summary_metrics'].get('score_gap'),
                            'models_tested': list(data['summary_metrics'].get('model_avg_scores', {}).keys())
                        }
                        experiments.append(experiment)
                        
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
        
        # Sort by date
        experiments.sort(key=lambda x: x['date'] or '', reverse=True)
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_experiments': len(experiments),
            'experiments': experiments
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Experiment summary saved to: {output_file}")
        print(f"Total experiments: {len(experiments)}")

def main():
    """CLI interface for run management."""
    manager = RunManager()
    
    # If no command specified, show recent runs
    try:
        import sys
        if len(sys.argv) == 1:
            manager.list_runs(days=7)
            return
    except:
        pass
    
    Fire(manager)

if __name__ == "__main__":
    main()