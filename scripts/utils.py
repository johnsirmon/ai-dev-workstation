#!/usr/bin/env python3
"""
Shared utilities for AI Agent Development Workstation automation scripts
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except ImportError:
    requests = None


class ConfigManager:
    """Manages configuration loading and saving"""

    def __init__(self, config_path: str = "config/tools-tracking.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            if not self.config_path.exists():
                logging.error(f"Config file not found: {self.config_path}")
                logging.info("Please ensure the config file exists or run setup.sh first")
                sys.exit(1)

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Validate basic structure
            if not isinstance(config, dict):
                raise ValueError("Config must be a JSON object")

            return config

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file: {e}")
            logging.info("Please check the JSON syntax in your config file")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error loading config: {e}")
            sys.exit(1)

    def save_config(self) -> None:
        """Save configuration to JSON file"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            logging.debug(f"Config saved successfully to {self.config_path}")

        except PermissionError as e:
            logging.error(f"Permission denied saving config: {e}")
            raise
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            raise


class DependencyManager:
    """Manages Python package dependencies"""

    @staticmethod
    def install_packages(packages: List[str]) -> None:
        """Install Python packages using pip"""
        try:
            # Check if we're in a virtual environment
            in_venv = (hasattr(sys, 'real_prefix') or
                       (hasattr(sys, 'base_prefix') and
                        sys.base_prefix != sys.prefix))

            cmd = [sys.executable, "-m", "pip", "install", "--quiet"]

            # If not in virtual environment, suggest creating one
            if not in_venv:
                logging.warning(
                    "Not in a virtual environment. Consider activating "
                    "the .venv environment:")
                logging.warning("source .venv/bin/activate")
                logging.warning("Attempting to install packages anyway...")

            cmd.extend(packages)
            subprocess.check_call(cmd)
            logging.info(f"Installed packages: {', '.join(packages)}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install packages: {e}")
            logging.error("Try running: source .venv/bin/activate")
            raise

    @staticmethod
    def install_requirements() -> None:
        """Install packages from requirements.txt"""
        requirements_path = Path("requirements.txt")
        if requirements_path.exists():
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--quiet", "-r", str(requirements_path)
                ])
                logging.info("Installed packages from requirements.txt")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install requirements: {e}")
                raise
        else:
            logging.warning("requirements.txt not found")

    @staticmethod
    def check_and_install(packages: List[str]) -> None:
        """Check if packages are available and install if needed"""
        missing_packages = []

        for package in packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            logging.info(f"Installing missing packages: {', '.join(missing_packages)}")
            DependencyManager.install_packages(missing_packages)


class HTTPClient:
    """Simplified HTTP client with error handling"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = None

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Make GET request and return JSON response"""
        if requests is None:
            logging.error(
                "requests library not available. "
                "Install with: pip install requests")
            return None

        try:
            if not self.session:
                self.session = requests.Session()
                self.session.headers.update({
                    'User-Agent': 'AI-Dev-Workstation/1.0'
                })

            if headers:
                self.session.headers.update(headers)

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logging.warning(f"HTTP request failed for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON response from {url}: {e}")
            return None


class Logger:
    """Centralized logging configuration"""

    @staticmethod
    def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
        """Setup logging configuration"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]

        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=handlers
        )


class ReportGenerator:
    """Generates reports in various formats"""

    @staticmethod
    def to_json(payload: Dict[str, Any]) -> str:
        """Serialize report payload as pretty JSON text."""
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_markdown_report(title: str, sections: List[Dict]) -> str:
        """Generate markdown report from sections"""
        report = [f"# {title}"]
        report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        for section in sections:
            report.append(f"## {section['title']}")

            if 'content' in section:
                report.append(section['content'])

            if 'items' in section:
                for item in section['items']:
                    report.append(f"- {item}")

            report.append("")

        return "\n".join(report)

    @staticmethod
    def save_report(content: str, file_path: str) -> None:
        """Save report to file"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            logging.info(f"Report saved to: {file_path}")

        except Exception as e:
            logging.error(f"Error saving report: {e}")
            raise


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """Extract relevant keywords from text"""
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().strftime('%Y-%m-%d')


def rate_limit_delay(seconds: int = 1) -> None:
    """Add delay for rate limiting"""
    time.sleep(seconds)
