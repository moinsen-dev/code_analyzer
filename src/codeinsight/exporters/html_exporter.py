"""
HTML export functionality
"""

from pathlib import Path

from codeinsight.models.metrics import AnalysisReport


class HTMLExporter:
    """Exports analysis reports to HTML format"""

    def export(self, report: AnalysisReport, output_path: Path) -> None:
        """
        Export report to HTML file

        Args:
            report: AnalysisReport to export
            output_path: Path to output file
        """
        html_content = self._generate_html(report)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_html(self, report: AnalysisReport) -> str:
        """
        Generate HTML content for the report

        Args:
            report: AnalysisReport to convert to HTML

        Returns:
            HTML content as string
        """
        # Generate file table rows
        file_rows = ""
        for i, file_insight in enumerate(report.top_files[:20]):  # Limit to top 20
            file_metrics = file_insight.file_metrics
            complexity_metrics = file_insight.complexity_metrics

            # Determine risk level based on complexity
            risk_level = "🟢 Good"
            risk_class = "risk-good"
            if complexity_metrics:
                cyclomatic = complexity_metrics.cyclomatic_complexity
                if cyclomatic > 20:
                    risk_level = "🔴 High"
                    risk_class = "risk-high"
                elif cyclomatic > 10:
                    risk_level = "🟠 Medium"
                    risk_class = "risk-medium"
                elif cyclomatic > 5:
                    risk_level = "🟡 Low"
                    risk_class = "risk-low"

            file_rows += f"""
                <tr>
                    <td>{file_metrics.relative_path}</td>
                    <td>{file_metrics.language.value if hasattr(file_metrics.language, 'value') else str(file_metrics.language)}</td>
                    <td>{file_metrics.lines_of_code:,}</td>
                    <td>{file_metrics.size_bytes:,}</td>
                    <td>{complexity_metrics.cyclomatic_complexity if complexity_metrics else '-'}</td>
                    <td class="{risk_class}">{risk_level}</td>
                </tr>
            """

        # Generate language distribution
        lang_dist = ""
        for lang, count in report.language_distribution.items():
            percentage = (count / report.total_files) * 100
            lang_dist += f"<li>{lang.value if hasattr(lang, 'value') else str(lang)}: {count} ({percentage:.0f}%)</li>"

        # Generate code smells
        smell_rows = ""
        total_smells = 0
        for file_insight in report.top_files:
            if file_insight.code_smells:
                total_smells += len(file_insight.code_smells)
                for smell in file_insight.code_smells[:3]:  # Limit to 3 smells per file
                    smell_rows += f"""
                        <tr>
                            <td>{file_insight.file_metrics.relative_path}</td>
                            <td>{smell}</td>
                        </tr>
                    """

        # Generate complexity hotspots
        complex_rows = ""
        for file_insight in report.top_files:
            if file_insight.complexity_metrics:
                complexity = file_insight.complexity_metrics
                cyclomatic = complexity.cyclomatic_complexity

                # Determine risk level
                if cyclomatic > 20:
                    risk_level = "🔴 High"
                    risk_class = "risk-high"
                elif cyclomatic > 10:
                    risk_level = "🟠 Medium"
                    risk_class = "risk-medium"
                elif cyclomatic > 5:
                    risk_level = "🟡 Low"
                    risk_class = "risk-low"
                else:
                    risk_level = "🟢 Good"
                    risk_class = "risk-good"

                complex_rows += f"""
                    <tr>
                        <td>{file_insight.file_metrics.relative_path}</td>
                        <td>{file_insight.file_metrics.lines_of_code:,}</td>
                        <td>{cyclomatic:.1f}</td>
                        <td>{complexity.cognitive_complexity:.1f}</td>
                        <td>{complexity.halstead_metrics.vocabulary_size if complexity.halstead_metrics else '-'}</td>
                        <td class="{risk_class}">{risk_level}</td>
                    </tr>
                """

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Insight Analysis Report</title>
    <style>
        :root {{
            --primary: #667eea;
            --primary-dark: #764ba2;
            --secondary: #f093fb;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --info: #0ea5e9;
            --light: #f8fafc;
            --dark: #0f172a;
            --gray: #94a3b8;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background-color: #f1f5f9;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.05);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--primary);
        }}
        
        .card-header h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--dark);
        }}
        
        .card-header i {{
            margin-right: 12px;
            font-size: 1.3rem;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .metric-card {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 8px;
            transition: transform 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-value {{
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 8px;
        }}
        
        .metric-label {{
            color: var(--gray);
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        th {{
            background-color: #f1f5f9;
            font-weight: 600;
            color: var(--dark);
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background-color: #f8fafc;
        }}
        
        .risk-high {{
            color: var(--danger);
            font-weight: 600;
        }}
        
        .risk-medium {{
            color: var(--warning);
            font-weight: 600;
        }}
        
        .risk-low {{
            color: var(--info);
            font-weight: 600;
        }}
        
        .risk-good {{
            color: var(--success);
            font-weight: 600;
        }}
        
        .lang-list {{
            columns: 2;
            column-gap: 30px;
            margin-top: 15px;
        }}
        
        .lang-list li {{
            margin-bottom: 8px;
            padding: 8px 12px;
            background: #f8fafc;
            border-radius: 6px;
            list-style: none;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary);
        }}
        
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: var(--gray);
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            
            .lang-list {{
                columns: 1;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
        
        .emoji-icon {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Refactoroscope Report</h1>
            <p>Project: {report.project_path}</p>
            <p>Analysis Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>📊 Analysis Summary</h2>
            </div>
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value">{report.total_files:,}</div>
                    <div class="metric-label">Total Files</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report.total_lines:,}</div>
                    <div class="metric-label">Lines of Code</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report.total_size:,}</div>
                    <div class="metric-label">Total Size (bytes)</div>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len([f for f in report.top_files if f.complexity_metrics])}</div>
                <div class="stat-label">Files with Complexity Analysis</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_smells}</div>
                <div class="stat-label">Code Smells Detected</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>🔤 Language Distribution</h2>
            </div>
            <ul class="lang-list">
                {lang_dist}
            </ul>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>🔥 Complexity Hotspots</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Lines</th>
                        <th>Cyclomatic</th>
                        <th>Cognitive</th>
                        <th>Vocabulary</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {complex_rows[:1000]} <!-- Limit output size -->
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2>📁 Top Files by Line Count</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Language</th>
                        <th>Lines</th>
                        <th>Size (bytes)</th>
                        <th>Complexity</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {file_rows}
                </tbody>
            </table>
        </div>
        
        {f'''
        <div class="card">
            <div class="card-header">
                <h2>💡 Code Smells Detected</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Smell</th>
                    </tr>
                </thead>
                <tbody>
                    {smell_rows}
                </tbody>
            </table>
        </div>
        ''' if smell_rows else ''}
        
    </div>
</body>
</html>
        """

        return html_template
