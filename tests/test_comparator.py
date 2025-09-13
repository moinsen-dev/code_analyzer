"""
Test script for report comparator
"""
import json

from codeinsight.models.metrics import AnalysisReport
from codeinsight.analysis.comparator import ReportComparator

def test_comparator():
    """Test the report comparator functionality"""
    # Load our test reports
    with open("reports/report1.json", 'r') as f:
        report1_data = json.load(f)
    report1 = AnalysisReport.from_dict(report1_data)
    
    with open("reports/report2.json", 'r') as f:
        report2_data = json.load(f)
    report2 = AnalysisReport.from_dict(report2_data)
    
    # Compare the reports
    comparator = ReportComparator()
    comparison = comparator.compare(report1, report2)
    
    print("Comparison test passed!")
    print(f"Total lines changed: {comparison['summary']['total_lines']['difference']}")
    print(f"Files changed: {len(comparison['files']['changed_files'])}")
    print(f"Complexity changes: {len(comparison['complexity']['files_with_changes'])}")

if __name__ == "__main__":
    test_comparator()