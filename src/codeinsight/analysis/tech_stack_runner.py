"""
Tech Stack Runner for Refactoroscope
Runs appropriate tools for detected technology stacks
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        self, root_path: Path, tech_stacks: Dict[str, List[str]], verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run appropriate tools for detected tech stacks

        Args:
            root_path: Root path of the project
            tech_stacks: Dict mapping folder paths to lists of detected tech stacks
            verbose: Whether to show verbose output

        Returns:
            Dict with results for each folder
        """
        results: Dict[str, Any] = {}

        for folder, stacks in tech_stacks.items():
            if verbose:
                print(f"  → Analyzing folder: {folder}")
                print(f"    Detected tech stacks: {', '.join(stacks)}")

            folder_path = root_path / folder
            folder_results: Dict[str, Any] = {
                "tech_stacks": stacks,
                "tool_results": {},
                "outdated_packages": {},
                "ai_summary": None,
            }

            # Run tools for each detected stack
            for stack in stacks:
                if stack in self.tools:
                    if verbose:
                        print(f"    Running tools for {stack}...")
                    tool_results = self._run_tools_for_stack(folder_path, stack)
                    folder_results["tool_results"].update(tool_results)

            # Check for outdated packages
            if verbose:
                print("    Checking for outdated packages...")
            folder_results["outdated_packages"] = self._check_outdated_packages(
                folder_path, stacks
            )

            # Generate AI summary for the project
            if verbose:
                print("    Generating AI summary...")
            folder_results["ai_summary"] = self._generate_ai_summary(
                folder_path, stacks
            )

            results[folder] = folder_results

        return results

    def _generate_ai_summary(
        self, folder_path: Path, tech_stacks: List[str]
    ) -> Optional[Dict[str, str]]:
        """
        Generate AI-powered summaries for the project based on project files

        Args:
            folder_path: Path to the project folder
            tech_stacks: List of detected tech stacks

        Returns:
            Dict with AI-generated summaries or None if not available
        """
        try:
            # Try to import AI analyzer
            from codeinsight.ai.analyzer import AIAnalyzer
            from codeinsight.config.manager import ConfigManager

            # Initialize AI analyzer
            config_manager = ConfigManager()
            ai_analyzer = AIAnalyzer(config_manager)

            if not ai_analyzer.is_available():
                return None

            summaries = {}

            # Generate README summary
            readme_summary = self._generate_readme_summary(folder_path, ai_analyzer)
            if readme_summary:
                summaries["project_overview"] = readme_summary

            # Generate tech stack specific summaries
            for stack in tech_stacks:
                stack_summary = self._generate_tech_stack_summary(
                    folder_path, stack, ai_analyzer
                )
                if stack_summary:
                    summaries[f"{stack}_summary"] = stack_summary

            return summaries if summaries else None

        except Exception:
            # If AI is not available or fails, return None
            return None

    def _generate_readme_summary(
        self, folder_path: Path, ai_analyzer: Any
    ) -> Optional[str]:
        """
        Generate AI summary from README file

        Args:
            folder_path: Path to the project folder
            ai_analyzer: AI analyzer instance

        Returns:
            AI-generated summary or None
        """
        try:
            # Look for README files
            readme_files = ["README.md", "README.txt", "README"]
            for readme_file in readme_files:
                readme_path = folder_path / readme_file
                if readme_path.exists():
                    # Read README content
                    with open(readme_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Limit content to reasonable size for AI processing
                    if len(content) > 5000:
                        content = content[:5000] + "... (content truncated)"

                    # Generate AI summary prompt
                    prompt = f"""Summarize the following project README in 100 words or less. 
Focus on the project's purpose, main features, and key benefits:

{content}"""

                    # Get AI response
                    ai_response = ai_analyzer.analyze(prompt)
                    return ai_response.strip() if ai_response else None

            return None
        except Exception:
            return None

    def _generate_tech_stack_summary(
        self, folder_path: Path, tech_stack: str, ai_analyzer: Any
    ) -> Optional[str]:
        """
        Generate AI summary for a specific tech stack based on project configuration files

        Args:
            folder_path: Path to the project folder
            tech_stack: Tech stack name
            ai_analyzer: AI analyzer instance

        Returns:
            AI-generated summary or None
        """
        try:
            config_content = None
            config_file = None

            # Determine which config file to use based on tech stack
            if tech_stack == "python":
                config_files = ["pyproject.toml", "requirements.txt", "setup.py"]
            elif tech_stack == "javascript" or tech_stack == "typescript":
                config_files = ["package.json"]
            elif tech_stack == "flutter":
                config_files = ["pubspec.yaml"]
            elif tech_stack == "go":
                config_files = ["go.mod"]
            elif tech_stack == "rust":
                config_files = ["Cargo.toml"]
            elif tech_stack == "java":
                config_files = ["pom.xml", "build.gradle"]
            else:
                return None

            # Find the first available config file
            for config_file_name in config_files:
                config_path = folder_path / config_file_name
                if config_path.exists():
                    config_file = config_file_name
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_content = f.read()
                    break

            if not config_content:
                return None

            # Limit content to reasonable size for AI processing
            if len(config_content) > 3000:
                config_content = config_content[:3000] + "... (content truncated)"

            # Generate AI summary prompt
            prompt = f"""Analyze the following {tech_stack} project configuration file ({config_file}) 
and provide a 50-word summary of the project's purpose, main dependencies, and key features:

{config_content}"""

            # Get AI response
            ai_response = ai_analyzer.analyze(prompt)
            return ai_response.strip() if ai_response else None

        except Exception:
            return None

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

        # Check for pyproject.toml in the folder or parent directories (for uv projects)
        pyproject_path = self._find_pyproject_toml(folder_path)
        if pyproject_path:
            try:
                # Try using uv to check for outdated packages
                # Run from the folder where pyproject.toml is located
                result = subprocess.run(
                    ["uv", "pip", "list", "--outdated"],
                    cwd=pyproject_path.parent,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0 and result.stdout:
                    # Parse uv pip list output
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

        return outdated

    def _find_pyproject_toml(self, folder_path: Path) -> Optional[Path]:
        """Find pyproject.toml in the folder or parent directories"""
        current_path = folder_path
        while current_path != current_path.parent:  # Stop at root
            pyproject_file = current_path / "pyproject.toml"
            if pyproject_file.exists():
                return pyproject_file
            current_path = current_path.parent
        return None

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
