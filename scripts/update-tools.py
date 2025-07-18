#!/usr/bin/env python3
"""
Automated tool version checker and README updater for AI Agent Development Workstation
Uses MCP servers and web scraping to check for updates to tracked tools
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from packaging import version


class ToolVersionChecker:
    def __init__(self, config_path: str = "config/tools-tracking.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.updates_found = []
        self.trending_tools = []
        
    def load_config(self) -> Dict:
        """Load the tools tracking configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            sys.exit(1)
    
    def save_config(self):
        """Save updated configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_pypi_version(self, package_name: str) -> Optional[str]:
        """Check PyPI for latest version of a package"""
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['info']['version']
        except Exception as e:
            print(f"Error checking PyPI for {package_name}: {e}")
        return None
    
    def check_npm_version(self, package_name: str) -> Optional[str]:
        """Check npm registry for latest version of a package"""
        try:
            response = requests.get(f"https://registry.npmjs.org/{package_name}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['dist-tags']['latest']
        except Exception as e:
            print(f"Error checking npm for {package_name}: {e}")
        return None
    
    def check_github_releases(self, repo_url: str) -> Optional[str]:
        """Check GitHub releases for latest version"""
        try:
            # Extract owner/repo from URL
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                return None
            
            owner, repo = match.groups()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['tag_name'].lstrip('v')
        except Exception as e:
            print(f"Error checking GitHub releases for {repo_url}: {e}")
        return None
    
    def check_tool_updates(self):
        """Check for updates to all tracked tools"""
        print("Checking for tool updates...")
        
        for category, tools in self.config['tracked_tools'].items():
            print(f"\nChecking {category}...")
            
            for tool_name, tool_info in tools.items():
                print(f"  Checking {tool_name}...")
                latest_version = None
                
                # Check PyPI if package is available
                if tool_info.get('pypi_package'):
                    latest_version = self.check_pypi_version(tool_info['pypi_package'])
                
                # Check npm if package is available
                if not latest_version and tool_info.get('npm_package'):
                    latest_version = self.check_npm_version(tool_info['npm_package'])
                
                # Check GitHub releases
                if not latest_version and tool_info.get('source'):
                    latest_version = self.check_github_releases(tool_info['source'])
                
                # Compare versions
                if latest_version and latest_version != tool_info['current_version']:
                    try:
                        if version.parse(latest_version) > version.parse(tool_info['current_version']):
                            self.updates_found.append({
                                'tool': tool_name,
                                'category': category,
                                'old_version': tool_info['current_version'],
                                'new_version': latest_version,
                                'description': tool_info['description']
                            })
                            
                            # Update config
                            tool_info['current_version'] = latest_version
                            tool_info['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                            
                            print(f"    → Update found: {tool_info['current_version']} → {latest_version}")
                    except Exception as e:
                        print(f"    → Error comparing versions: {e}")
                else:
                    print(f"    → Up to date: {tool_info['current_version']}")
    
    def search_trending_tools(self):
        """Search for trending tools on GitHub and forums"""
        print("\nSearching for trending tools...")
        
        # Search GitHub topics
        for topic in self.config['monitoring_sources']['github_topics']:
            try:
                # Search for repositories created in the last 30 days
                query = f"topic:{topic} created:>={datetime.now().strftime('%Y-%m-%d')}"
                url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for repo in data['items']:
                        if repo['stargazers_count'] > 50:  # Minimum stars threshold
                            self.trending_tools.append({
                                'name': repo['name'],
                                'url': repo['html_url'],
                                'description': repo['description'] or 'No description available',
                                'stars': repo['stargazers_count'],
                                'language': repo['language'],
                                'topic': topic,
                                'created_at': repo['created_at']
                            })
            except Exception as e:
                print(f"Error searching topic {topic}: {e}")
    
    def update_readme(self):
        """Update README.md with latest tool versions and trending tools"""
        print("\nUpdating README.md...")
        
        readme_path = Path("README.md")
        if not readme_path.exists():
            print("README.md not found!")
            return
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update version numbers in the frameworks table
        for update in self.updates_found:
            if update['category'] == 'ai_frameworks':
                # Look for version pattern in the table
                old_pattern = rf"(\*\*{re.escape(update['tool'])}\*\*\|)([^|]+)(\|)"
                new_replacement = rf"\g<1>{update['new_version']} (Updated {datetime.now().strftime('%b %d %Y')})\g<3>"
                content = re.sub(old_pattern, new_replacement, content, flags=re.IGNORECASE)
        
        # Add trending tools section if new tools found
        if self.trending_tools:
            trending_section = self.generate_trending_section()
            
            # Find the end of the existing content and add trending section
            if "## Trending Tools to Investigate" not in content:
                content += f"\n\n---\n\n{trending_section}"
            else:
                # Replace existing trending section
                pattern = r"## Trending Tools to Investigate.*?(?=\n\n---|\n\n##|\Z)"
                content = re.sub(pattern, trending_section, content, flags=re.DOTALL)
        
        # Update the last updated timestamp
        today = datetime.now().strftime('%B %d, %Y')
        content = re.sub(
            r'Generated.*?–',
            f'Generated {today} –',
            content
        )
        
        with open(readme_path, 'w') as f:
            f.write(content)
        
        print("README.md updated successfully!")
    
    def generate_trending_section(self) -> str:
        """Generate the trending tools section"""
        section = "## Trending Tools to Investigate\n\n"
        section += "| Tool | Stars | Language | Use Case | Repository |\n"
        section += "|------|-------|----------|----------|------------|\n"
        
        for tool in self.trending_tools[:10]:  # Limit to top 10
            section += f"|**{tool['name']}**|{tool['stars']}|{tool['language'] or 'N/A'}|{tool['description'][:100]}{'...' if len(tool['description']) > 100 else ''}|[GitHub]({tool['url']})|\n"
        
        return section
    
    def generate_update_summary(self) -> str:
        """Generate summary of updates found"""
        if not self.updates_found and not self.trending_tools:
            return "No updates found."
        
        summary = []
        
        if self.updates_found:
            summary.append(f"## Tool Updates Found ({len(self.updates_found)})")
            for update in self.updates_found:
                summary.append(f"- **{update['tool']}**: {update['old_version']} → {update['new_version']}")
        
        if self.trending_tools:
            summary.append(f"\n## Trending Tools Found ({len(self.trending_tools)})")
            for tool in self.trending_tools[:5]:  # Show top 5 in summary
                summary.append(f"- **{tool['name']}** ({tool['stars']} stars): {tool['description'][:100]}{'...' if len(tool['description']) > 100 else ''}")
        
        return "\n".join(summary)
    
    def run(self):
        """Run the complete update process"""
        print("Starting AI Agent Development Workstation Update Check...")
        print(f"Config: {self.config_path}")
        print(f"Last update check: {self.config.get('last_update_check', 'Never')}")
        
        # Check for tool updates
        self.check_tool_updates()
        
        # Search for trending tools
        self.search_trending_tools()
        
        # Update configuration
        self.config['last_update_check'] = datetime.now().strftime('%Y-%m-%d')
        self.config['trending_tools'] = self.trending_tools
        self.save_config()
        
        # Update README
        self.update_readme()
        
        # Print summary
        print(f"\n{self.generate_update_summary()}")
        
        return len(self.updates_found) > 0 or len(self.trending_tools) > 0


if __name__ == "__main__":
    try:
        import requests
        from packaging import version
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "packaging"])
        import requests
        from packaging import version
    
    checker = ToolVersionChecker()
    has_updates = checker.run()
    
    if has_updates:
        print(f"\n✅ Update check completed with changes!")
        print("Consider reviewing the updates and committing the changes.")
    else:
        print(f"\n✅ Update check completed - everything is up to date!")