#!/usr/bin/env python3
"""
Shared utilities for AI Agent Development Workstation automation scripts
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self, config_path: str = "config/tools-tracking.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            raise


class DependencyManager:
    """Manages Python package dependencies"""
    
    @staticmethod
    def install_packages(packages: List[str]):
        """Install Python packages using pip"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--quiet"
            ] + packages)
            logging.info(f"Installed packages: {', '.join(packages)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install packages: {e}")
            raise
    
    @staticmethod
    def install_requirements():
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
    def check_and_install(packages: List[str]):
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
    
    def get(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Make GET request and return JSON response"""
        try:
            import requests
            
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
    def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
        """Setup logging configuration"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        handlers = [logging.StreamHandler(sys.stdout)]
        
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
    def save_report(content: str, file_path: str):
        """Save report to file"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
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


def rate_limit_delay(seconds: int = 1):
    """Add delay for rate limiting"""
    import time
    time.sleep(seconds)