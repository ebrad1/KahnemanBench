# python generate_dashboard.py --rating_dir=.

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from fire import Fire

def generate_html_dashboard(results: List[Dict[str, Any]], output_path: str = "rating_dashboard.html"):
    """Generate an interactive HTML dashboard for rating results."""
    
    # Extract key metrics
    rater_data = []
    for result in results:
        if result['summary_metrics']['num_real_responses'] > 0:
            rater_data.append({
                'rater': result['rating_metadata']['rater_model'],
                'real_avg': result['summary_metrics']['real_kahneman_avg_score'],
                'ai_avg': result['summary_metrics']['ai_responses_avg_score'],
                'gap': result['summary_metrics']['score_gap'],
                'timestamp': result['rating_metadata']['timestamp']
            })
    
    # Sort by rater name
    rater_data.sort(key=lambda x: x['rater'])
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>KahnemanBench Rating Results Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .chart {{
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .positive {{
            color: #28a745;
        }}
        .negative {{
            color: #dc3545;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>KahnemanBench Rating Results Dashboard</h1>
        <p style="text-align: center; color: #666;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Rater Models Analyzed</div>
                <div class="metric-value">{len(rater_data)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Real Kahneman Score</div>
                <div class="metric-value">{sum(r['real_avg'] for r in rater_data) / len(rater_data):.1f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg AI Response Score</div>
                <div class="metric-value">{sum(r['ai_avg'] for r in rater_data) / len(rater_data):.1f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Score Gap</div>
                <div class="metric-value">{sum(r['gap'] for r in rater_data) / len(rater_data):.1f}</div>
            </div>
        </div>
        
        <h2>Score Comparison by Rater Model</h2>
        <div id="barChart" class="chart"></div>
        
        <h2>Score Gap Analysis</h2>
        <div id="gapChart" class="chart"></div>
        
        <h2>Detailed Results by Rater</h2>
        <table>
            <tr>
                <th>Rater Model</th>
                <th>Real Kahneman Avg</th>
                <th>AI Response Avg</th>
                <th>Score Gap</th>
                <th>Timestamp</th>
            </tr>
"""
    
    for r in rater_data:
        gap_class = 'positive' if r['gap'] > 0 else 'negative'
        html_content += f"""
            <tr>
                <td><strong>{r['rater']}</strong></td>
                <td>{r['real_avg']:.1f}</td>
                <td>{r['ai_avg']:.1f}</td>
                <td class="{gap_class}">{r['gap']:.1f}</td>
                <td>{r['timestamp'][:19]}</td>
            </tr>
"""
    
    html_content += """
        </table>
    </div>
    
    <script>
        // Bar chart data
        var raters = """ + json.dumps([r['rater'] for r in rater_data]) + """;
        var realScores = """ + json.dumps([r['real_avg'] for r in rater_data]) + """;
        var aiScores = """ + json.dumps([r['ai_avg'] for r in rater_data]) + """;
        
        var trace1 = {
            x: raters,
            y: realScores,
            name: 'Real Kahneman',
            type: 'bar',
            marker: { color: '#3498db' }
        };
        
        var trace2 = {
            x: raters,
            y: aiScores,
            name: 'AI Responses',
            type: 'bar',
            marker: { color: '#e74c3c' }
        };
        
        var barLayout = {
            barmode: 'group',
            title: 'Average Authenticity Scores by Rater Model',
            xaxis: { title: 'Rater Model' },
            yaxis: { title: 'Average Score' }
        };
        
        Plotly.newPlot('barChart', [trace1, trace2], barLayout);
        
        // Gap chart
        var gaps = """ + json.dumps([r['gap'] for r in rater_data]) + """;
        var gapColors = gaps.map(g => g > 0 ? '#2ecc71' : '#e74c3c');
        
        var gapTrace = {
            x: raters,
            y: gaps,
            type: 'bar',
            marker: { color: gapColors },
            text: gaps.map(g => g.toFixed(1)),
            textposition: 'auto'
        };
        
        var gapLayout = {
            title: 'Score Gap: Real Kahneman - AI Responses',
            xaxis: { title: 'Rater Model' },
            yaxis: { title: 'Score Gap', zeroline: true },
            shapes: [{
                type: 'line',
                x0: 0,
                y0: 0,
                x1: 1,
                y1: 0,
                xref: 'paper',
                line: { color: 'black', width: 1 }
            }]
        };
        
        Plotly.newPlot('gapChart', [gapTrace], gapLayout);
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Dashboard generated: {output_path}")

def main(rating_dir: str = ".", output_path: str = "rating_dashboard.html"):
    """Generate an HTML dashboard from rating results."""
    
    # Load all rating results
    results = []
    for filename in os.listdir(rating_dir):
        if filename.startswith("rating_results_") and filename.endswith(".json"):
            filepath = os.path.join(rating_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    results.append(json.load(f))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    if results:
        generate_html_dashboard(results, output_path)
        print(f"\nOpen {output_path} in your browser to view the dashboard")
    else:
        print("No rating results found!")

if __name__ == "__main__":
    Fire(main)