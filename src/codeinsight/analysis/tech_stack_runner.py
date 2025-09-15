"""
Tech Stack Runner for Refactoroscope
Runs appropriate tools for detected technology stacks
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


class TechStackRunner:
    """Runs appropriate tools for detected technology stacks"""

    def __init__(self) -> None:
        # Define tools for each tech stack
        self.tools = {
            "python": {
                "linters": ["ruff check .", "flake8 ."],
                "formatters": ["black --check .", "isort --check-only ."],
                "type_checkers": ["mypy ."],
            },
            "javascript": {
                "linters": ["eslint ."],
                "formatters": ["prettier --check ."],
            },
            "typescript": {
                "linters": ["eslint .", "tslint ."],
                "formatters": ["prettier --check ."],
                "type_checkers": ["tsc --noEmit"],
            },
            "flutter": {
                "linters": ["flutter analyze"],
                "formatters": ["dart format --output=none --set-exit-if-changed ."],
            },
            "go": {
                "linters": ["golint ./...", "go vet ./..."],
                "formatters": ["gofmt -l ."],
                "type_checkers": ["go build ./..."],
            },
            "rust": {
                "linters": ["cargo clippy"],
                "formatters": ["cargo fmt -- --check"],
                "type_checkers": ["cargo check"],
            },
        }

    def run_tools_for_stacks(
        self, root_path: Path, tech_stacks: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Run appropriate tools for detected tech stacks

        Args:
            root_path: Root path of the project
            tech_stacks: Dict mapping folder paths to lists of detected tech stacks

        Returns:
            Dict with results for each folder
        """
        results: Dict[str, Any] = {}

        for folder, stacks in tech_stacks.items():
            folder_path = root_path / folder
            folder_results: Dict[str, Any] = {
                "tech_stacks": stacks,
                "tool_results": {},
                "outdated_packages": {},
            }

            # Run tools for each detected stack
            for stack in stacks:
                if stack in self.tools:
                    tool_results = self._run_tools_for_stack(folder_path, stack)
                    folder_results["tool_results"].update(tool_results)

            # Check for outdated packages
            folder_results["outdated_packages"] = self._check_outdated_packages(
                folder_path, stacks
            )

            results[folder] = folder_results

        return results

    def _run_tools_for_stack(self, folder_path: Path, stack: str) -> Dict[str, Any]:
        """Run tools for a specific tech stack in a folder"""
        results: Dict[str, Any] = {}

        if stack not in self.tools:
            return results

        stack_tools = self.tools[stack]

        # Run linters
        if "linters" in stack_tools:
            for linter in stack_tools["linters"]:
                results[f"lint_{linter.split()[0]}"] = self._run_command(
                    folder_path, linter
                )

        # Run formatters
        if "formatters" in stack_tools:
            for formatter in stack_tools["formatters"]:
                results[f"format_{formatter.split()[0]}"] = self._run_command(
                    folder_path, formatter
                )

        # Run type checkers
        if "type_checkers" in stack_tools:
            for type_checker in stack_tools["type_checkers"]:
                results[f"type_{type_checker.split()[0]}"] = self._run_command(
                    folder_path, type_checker
                )

        return results

    def _run_command(self, folder_path: Path, command: str) -> Dict[str, Any]:
        """Run a command in a folder and return results"""
        try:
            # Using shell=True is safe here because commands are predefined tool commands
            # and not user input. The commands are from our own tech stack definitions.
            result = subprocess.run(  # nosec B602
                command,
                shell=True,
                cwd=folder_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip() or result.stderr.strip(),
                "return_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Command timed out", "return_code": -1}
        except Exception as e:
            return {"success": False, "output": str(e), "return_code": -1}

    def _check_outdated_packages(
        self, folder_path: Path, stacks: List[str]
    ) -> Dict[str, Any]:
        """Check for outdated packages in a folder"""
        outdated = {}

        for stack in stacks:
            if stack == "python":
                outdated.update(self._check_python_outdated(folder_path))
            elif stack == "javascript" or stack == "typescript":
                outdated.update(self._check_npm_outdated(folder_path))
            elif stack == "flutter":
                outdated.update(self._check_flutter_outdated(folder_path))
            elif stack == "rust":
                outdated.update(self._check_rust_outdated(folder_path))

        return outdated

    def _check_python_outdated(self, folder_path: Path) -> Dict[str, Any]:
        """Check for outdated Python packages"""
        outdated = {}

        # Check requirements.txt
        req_file = folder_path / "requirements.txt"
        if req_file.exists():
            try:
                result = subprocess.run(
                    ["pip", "list", "--outdated"],
                    cwd=folder_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    # Parse pip list output
                    lines = result.stdout.strip().split("\n")
                    for line in lines[2:]:  # Skip header lines
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3:
                                package, current, latest = parts[0], parts[1], parts[2]
                                outdated[package] = {
                                    "current": current,
                                    "latest": latest,
                                }
            except Exception:
                pass

        # Check pyproject.toml
        pyproject_file = folder_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                # For uv projects, we could check with 'uv lock --dry-run'
                # But for now, we'll just check with pip
                pass
            except Exception:
                pass

        return outdated

    def _check_npm_outdated(self, folder_path: Path) -> Dict[str, Any]:
        """Check for outdated npm packages"""
        outdated = {}

        package_json = folder_path / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    cwd=folder_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0 and result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        for package, info in data.items():
                            outdated[package] = {
                                "current": info.get("current", "unknown"),
                                "latest": info.get("latest", "unknown"),
                            }
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass

        return outdated

    def _check_flutter_outdated(self, folder_path: Path) -> Dict[str, Any]:
        """Check for outdated Flutter packages"""
        outdated = {}

        pubspec_file = folder_path / "pubspec.yaml"
        if pubspec_file.exists():
            try:
                result = subprocess.run(
                    ["flutter", "pub", "outdated", "--json"],
                    cwd=folder_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0 and result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        # Parse Flutter pub outdated output
                        if "packages" in data:
                            for package_info in data["packages"]:
                                if package_info.get("upgradeable"):
                                    outdated[package_info["package"]] = {
                                        "current": package_info.get(
                                            "current", "unknown"
                                        ),
                                        "latest": package_info.get("latest", "unknown"),
                                    }
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass

        return outdated

    def _check_rust_outdated(self, folder_path: Path) -> Dict[str, Any]:
        """Check for outdated Rust packages"""
        outdated = {}

        cargo_file = folder_path / "Cargo.toml"
        if cargo_file.exists():
            try:
                result = subprocess.run(
                    ["cargo", "update", "--dry-run"],
                    cwd=folder_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode == 0 and result.stdout:
                    # Parse cargo update output for outdated packages
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        if "Updating" in line and "->" in line:
                            # Extract package name and versions
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "->":
                                    if i > 1:
                                        package = parts[i - 1]
                                        current = parts[i - 2] if i > 2 else "unknown"
                                        latest = (
                                            parts[i + 1]
                                            if i + 1 < len(parts)
                                            else "unknown"
                                        )
                                        outdated[package] = {
                                            "current": current,
                                            "latest": latest,
                                        }
            except Exception:
                pass

        return outdated
