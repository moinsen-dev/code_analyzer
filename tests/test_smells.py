"""
Test script for code smell detector
"""

from pathlib import Path

from codeinsight.analysis.smells import CodeSmellDetector
from codeinsight.models.metrics import Language


def test_code_smells():
    """Test the code smell detector functionality"""
    detector = CodeSmellDetector()

    # Test with our smelly file
    smells = detector.detect_smells(
        Path("examples/sample_project/smelly.py"), Language.PYTHON
    )

    print("Code smell detection test passed!")
    print(f"Detected {len(smells)} code smells:")
    for smell in smells:
        print(f"  - {smell}")


if __name__ == "__main__":
    test_code_smells()
