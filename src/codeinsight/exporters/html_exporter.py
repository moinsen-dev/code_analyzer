"""
HTML export functionality
"""
from pathlib import Path
from codeinsight.models.metrics import AnalysisReport


class HTMLExporter:
    """Exports analysis reports to HTML format"""
    
    def export(self, report: AnalysisReport, output_path: Path):
        """
        Export report to HTML file
        
        Args:
            report: AnalysisReport to export
            output_path: Path to output file
        """
        html_content = self._generate_html(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
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
                if complexity_metrics.cyclomatic_complexity > 20:
                    risk_level = "🔴 High"
                    risk_class = "risk-high"
                elif complexity_metrics.cyclomatic_complexity > 10:
                    risk_level = "🟠 Medium"
                    risk_class = "risk-medium"
                elif complexity_metrics.cyclomatic_complexity > 5:
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
            lang_dist += f"<li>{lang.value if hasattr(lang, 'value') else str(lang)}: {count}</li>"
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Insight Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .summary-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metric {{
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .section {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-title {{
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .risk-high {{
            color: #dc2626;
            font-weight: bold;
        }}
        .risk-medium {{
            color: #ea580c;
            font-weight: bold;
        }}
        .risk-low {{
            color: #d97706;
            font-weight: bold;
        }}
        .risk-good {{
            color: #059669;
            font-weight: bold;
        }}
        .lang-list {{
            columns: 3;
            column-gap: 20px;
        }}
        .lang-list li {{
            margin-bottom: 5px;
        }}
        @media (max-width: 768px) {{
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            .lang-list {{
                columns: 1;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Code Insight Analysis Report</h1>
        <p>Project: {report.project_path}</p>
        <p>Analysis Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary-card">
        <h2>📊 Analysis Summary</h2>
        <div class="summary-grid">
            <div class="metric">
                <div class="metric-value">{report.total_files:,}</div>
                <div class="metric-label">Total Files</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.total_lines:,}</div>
                <div class="metric-label">Lines of Code</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.total_size:,}</div>
                <div class="metric-label">Total Size (bytes)</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2 class="section-title">🔤 Language Distribution</h2>
        <ul class="lang-list">
            {lang_dist}
        </ul>
    </div>
    
    <div class="section">
        <h2 class="section-title">🔥 Top Files by Line Count</h2>
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
</body>
</html>
        """
        
        return html_template