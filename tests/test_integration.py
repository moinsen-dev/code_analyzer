"""
Integration test for the Code Insight Analyzer
"""
import tempfile
import shutil
from pathlib import Path

def test_integration():
    """Test the complete workflow of the code insight analyzer"""
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy our sample project to the temporary directory
        sample_project = Path("examples/sample_project")
        test_project = temp_path / "test_project"
        shutil.copytree(sample_project, test_project)
        
        # Run the analyzer with all features
        import subprocess
        import sys
        
        # Test basic analysis
        result = subprocess.run([
            sys.executable, "-m", "uv", "run", "codeinsight", "analyze", 
            str(test_project)
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0, f"Basic analysis failed: {result.stderr}"
        assert "Code Insight Analysis" in result.stdout, "Expected output not found"
        print("✓ Basic analysis test passed")
        
        # Test complexity analysis
        result = subprocess.run([
            sys.executable, "-m", "uv", "run", "codeinsight", "analyze", 
            str(test_project), "--complexity"
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0, f"Complexity analysis failed: {result.stderr}"
        assert "Complexity" in result.stdout, "Expected complexity output not found"
        print("✓ Complexity analysis test passed")
        
        # Test export functionality
        reports_dir = temp_path / "reports"
        result = subprocess.run([
            sys.executable, "-m", "uv", "run", "codeinsight", "analyze", 
            str(test_project), "--complexity", "--export", "json,csv,html",
            "--export-dir", str(reports_dir)
        ], capture_output=True, text=True, cwd=".")
        
        assert result.returncode == 0, f"Export failed: {result.stderr}"
        assert reports_dir.exists(), "Reports directory should be created"
        assert (reports_dir / "report.json").exists(), "JSON report should be created"
        assert (reports_dir / "report.csv").exists(), "CSV report should be created"
        assert (reports_dir / "report.html").exists(), "HTML report should be created"
        print("✓ Export functionality test passed")
        
        print("All integration tests passed!")

if __name__ == "__main__":
    test_integration()