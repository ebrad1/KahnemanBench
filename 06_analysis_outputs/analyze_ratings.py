# python generate_dashboard.py --rating_dir=.

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from fire import Fire

def calculate_question_gaps(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Calculate score gaps per question for each rater model."""
    gaps_by_rater = {}
    
    for result in results:
        if result['summary_metrics']['num_real_responses'] == 0:
            continue
            
        rater = result['rating_metadata']['rater_model']
        gaps_by_rater[rater] = {}
        
        for question in result['ratings']:
            question_id = question['question_id']
            
            # Calculate averages for this question
            real_scores = [r['authenticity_score'] for r in question['response_ratings'] 
                          if r['hidden_source'] == 'real_kahneman']
            ai_scores = [r['authenticity_score'] for r in question['response_ratings'] 
                        if r['hidden_source'] != 'real_kahneman']
            
            if real_scores and ai_scores:
                real_avg = sum(real_scores) / len(real_scores)
                ai_avg = sum(ai_scores) / len(ai_scores)
                gap = real_avg - ai_avg
                gaps_by_rater[rater][question_id] = gap
    
    return gaps_by_rater

def get_color_for_gap(gap: float) -> str:
    """Return color based on gap value."""
    if gap > 20:
        return '#1a5490'  # Dark blue - real much better
    elif gap > 10:
        return '#3498db'  # Blue
    elif gap > 0:
        return '#85C1E9'  # Light blue
    elif gap > -10:
        return '#F9B5AC'  # Light red
    elif gap > -20:
        return '#e74c3c'  # Red
    else:
        return '#922B21'  # Dark red - AI much better

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
    
    # Calculate per-question gaps
    question_gaps = calculate_question_gaps(results)
    
    # Get all unique questions (sorted)
    all_questions = set()
    for rater_gaps in question_gaps.values():
        all_questions.update(rater_gaps.keys())
    all_questions = sorted(list(all_questions))
    
    # Extract question numbers for sorting
    def extract_question_num(q_id):
        parts = q_id.split('_')
        try:
            return int(parts[-1])
        except:
            return 999
    
    all_questions.sort(key=extract_question_num)
    
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
            max-width: 1400px;
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
        
        /* Gap matrix styles */
        .gap-matrix {{
            overflow-x: auto;
            margin: 20px 0;
        }}
        .gap-matrix table {{
            font-size: 14px;
        }}
        .gap-matrix td {{
            text-align: center;
            font-weight: bold;
            color: white;
            min-width: 80px;
        }}
        .gap-matrix th {{
            font-size: 12px;
            white-space: nowrap;
        }}
        .gap-matrix th.rotate {{
            height: 140px;
            white-space: nowrap;
        }}
        .gap-matrix th.rotate > div {{
            transform: translate(25px, 51px) rotate(315deg);
            width: 30px;
        }}
        .gap-matrix th.rotate > div > span {{
            padding: 5px 10px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 10px 0;
            font-size: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-box {{
            width: 20px;
            height: 20px;
            border: 1px solid #ccc;
        }}
        .tooltip {{
            position: relative;
            display: inline-block;
        }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            font-weight: normal;
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
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
        
        <h2>Score Gap by Question and Rater</h2>
        <p style="text-align: center; color: #666;">Score Gap = Real Kahneman Score - AI Response Score</p>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-box" style="background-color: #1a5490;"></div>
                <span>Real > AI by 20+</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: #3498db;"></div>
                <span>Real > AI by 10-20</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: #85C1E9;"></div>
                <span>Real > AI by 0-10</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: #F9B5AC;"></div>
                <span>AI > Real by 0-10</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: #e74c3c;"></div>
                <span>AI > Real by 10-20</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background-color: #922B21;"></div>
                <span>AI > Real by 20+</span>
            </div>
        </div>
        
        <div class="gap-matrix">
            <table>
                <tr>
                    <th>Rater Model</th>
"""
    
    # Add question headers
    for question in all_questions:
        short_q = question.replace('_', ' ').replace('motley fool', 'MF').replace('conversations with tyler', 'CWT')
        html_content += f'<th class="rotate"><div><span>{short_q}</span></div></th>'
    
    html_content += '<th>Overall Avg</th></tr>'
    
    # Add data rows
    for rater in sorted(question_gaps.keys()):
        html_content += f'<tr><td><strong>{rater}</strong></td>'
        
        rater_gaps = question_gaps[rater]
        gap_values = []
        
        for question in all_questions:
            if question in rater_gaps:
                gap = rater_gaps[question]
                gap_values.append(gap)
                color = get_color_for_gap(gap)
                html_content += f'''<td style="background-color: {color};" class="tooltip">
                    {gap:.1f}
                    <span class="tooltiptext">{question}<br>Gap: {gap:.1f}</span>
                </td>'''
            else:
                html_content += '<td style="background-color: #ccc;">-</td>'
        
        # Add overall average
        overall_avg = sum(gap_values) / len(gap_values) if gap_values else 0
        overall_color = get_color_for_gap(overall_avg)
        html_content += f'<td style="background-color: {overall_color};">{overall_avg:.1f}</td>'
        
        html_content += '</tr>'
    
    # Add question averages row
    html_content += '<tr><td><strong>Question Avg</strong></td>'
    for question in all_questions:
        q_gaps = [question_gaps[r][question] for r in question_gaps if question in question_gaps[r]]
        if q_gaps:
            q_avg = sum(q_gaps) / len(q_gaps)
            color = get_color_for_gap(q_avg)
            html_content += f'<td style="background-color: {color};">{q_avg:.1f}</td>'
        else:
            html_content += '<td style="background-color: #ccc;">-</td>'
    
    # Overall average
    all_gaps = [gap for rater_gaps in question_gaps.values() for gap in rater_gaps.values()]
    total_avg = sum(all_gaps) / len(all_gaps) if all_gaps else 0
    html_content += f'<td style="background-color: {get_color_for_gap(total_avg)};">{total_avg:.1f}</td></tr>'
    
    html_content += """
            </table>
        </div>
        
        <h2>Score Comparison by Rater Model</h2>
        <div id="barChart" class="chart"></div>
        
        <h2>Score Gap Analysis</h2>
        <div id="gapChart" class="chart"></div>
        
        <h2>Heatmap: Score Gaps by Question</h2>
        <div id="heatmap" class="chart"></div>
        
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
            yaxis: { title: 'Average Score' },
            height: 400
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
            height: 400,
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
        
        // Heatmap data
        var questionGaps = """ + json.dumps(question_gaps) + """;
        var questions = """ + json.dumps(all_questions) + """;
        var raterList = """ + json.dumps(sorted(question_gaps.keys())) + """;
        
        // Create matrix for heatmap
        var zValues = [];
        for (var i = 0; i < raterList.length; i++) {
            var row = [];
            for (var j = 0; j < questions.length; j++) {
                var gap = questionGaps[raterList[i]][questions[j]];
                row.push(gap !== undefined ? gap : null);
            }
            zValues.push(row);
        }
        
        var heatmapTrace = {
            z: zValues,
            x: questions.map(q => q.replace(/_/g, ' ')),
            y: raterList,
            type: 'heatmap',
            colorscale: [
                [0, '#922B21'],
                [0.25, '#e74c3c'],
                [0.4, '#F9B5AC'],
                [0.5, '#ffffff'],
                [0.6, '#85C1E9'],
                [0.75, '#3498db'],
                [1, '#1a5490']
            ],
            zmid: 0,
            colorbar: {
                title: 'Score Gap',
                titleside: 'right'
            },
            hoverongaps: false
        };
        
        var heatmapLayout = {
            title: 'Score Gaps by Question and Rater Model',
            xaxis: { 
                title: 'Question',
                tickangle: -45
            },
            yaxis: { title: 'Rater Model' },
            height: 500
        };
        
        Plotly.newPlot('heatmap', [heatmapTrace], heatmapLayout);
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Dashboard generated: {output_path}")

def main(
    rating_dir: str = ".", 
    output_path: str = "rating_dashboard.html",
    rating_results: str = None,
    update_dashboard: bool = False
):
    """
    Generate an HTML dashboard from rating results.
    
    Args:
        rating_dir: Directory containing rating results files
        output_path: Path for generated HTML dashboard
        rating_results: Specific rating results file to include
        update_dashboard: If True, update the default dashboard location
    """
    
    # Determine output path
    if update_dashboard:
        output_path = "06_analysis_outputs/rating_dashboard.html"
    
    # Load rating results
    results = []
    
    if rating_results:
        # Load specific rating results file
        try:
            with open(rating_results, 'r') as f:
                results.append(json.load(f))
            print(f"Loaded specific rating results: {rating_results}")
        except Exception as e:
            print(f"Error loading {rating_results}: {e}")
            return
    else:
        # Load all rating results from directory
        search_dir = rating_dir if rating_dir != "." else "05_rating_results"
        
        if not os.path.exists(search_dir):
            print(f"Rating results directory not found: {search_dir}")
            return
            
        for filename in os.listdir(search_dir):
            if filename.startswith("rating_results_") and filename.endswith(".json"):
                filepath = os.path.join(search_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        results.append(json.load(f))
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    if results:
        generate_html_dashboard(results, output_path)
        print(f"Dashboard generated: {output_path}")
        print(f"Open {output_path} in your browser to view the results")
    else:
        print("No rating results found!")

if __name__ == "__main__":
    Fire(main)