#!/usr/bin/env python3
"""
Automated tool version checker and README updater for AI Agent Development Workstation
Uses APIs to check for updates to tracked tools and updates documentation
"""

import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from utils import ConfigManager, DependencyManager, HTTPClient, Logger, ReportGenerator, get_current_timestamp


class ToolVersionChecker:
    """Checks for updates to tracked tools and frameworks"""
    
    def __init__(self, config_path: str = "config/tools-tracking.json"):
        self.config_manager = ConfigManager(config_path)
        self.http_client = HTTPClient()
        self.updates_found = []
        self.trending_tools = []
        
    def check_pypi_version(self, package_name: str) -> Optional[str]:
        """Check PyPI for latest version of a package"""
        url = f"https://pypi.org/pypi/{package_name}/json"
        data = self.http_client.get(url)
        
        if data and 'info' in data:
            return data['info']['version']
        return None
    
    def check_npm_version(self, package_name: str) -> Optional[str]:
        """Check npm registry for latest version of a package"""
        url = f"https://registry.npmjs.org/{package_name}"
        data = self.http_client.get(url)
        
        if data and 'dist-tags' in data:
            return data['dist-tags']['latest']
        return None
    
    def check_github_releases(self, repo_url: str) -> Optional[str]:
        """Check GitHub releases for latest version"""
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return None
        
        owner, repo = match.groups()
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        data = self.http_client.get(url)
        
        if data and 'tag_name' in data:
            return data['tag_name'].lstrip('v')
        return None
    
    def check_tool_updates(self):
        """Check for updates to all tracked tools"""
        logging.info("Checking for tool updates...")
        
        for category, tools in self.config_manager.config['tracked_tools'].items():
            logging.info(f"Checking {category}...")
            
            for tool_name, tool_info in tools.items():
                latest_version = self._get_latest_version(tool_info)
                
                if latest_version and self._is_newer_version(latest_version, tool_info['current_version']):
                    self._record_update(tool_name, category, tool_info, latest_version)
                    logging.info(f"Update found for {tool_name}: {tool_info['current_version']} → {latest_version}")
                else:
                    logging.debug(f"{tool_name} is up to date: {tool_info['current_version']}")
    
    def _get_latest_version(self, tool_info: Dict) -> Optional[str]:
        """Get latest version from available sources"""
        # Check PyPI first
        if tool_info.get('pypi_package'):
            version = self.check_pypi_version(tool_info['pypi_package'])
            if version:
                return version
        
        # Check npm
        if tool_info.get('npm_package'):
            version = self.check_npm_version(tool_info['npm_package'])
            if version:
                return version
        
        # Check GitHub releases
        if tool_info.get('source'):
            return self.check_github_releases(tool_info['source'])
        
        return None
    
    def _is_newer_version(self, new_version: str, current_version: str) -> bool:
        """Compare versions to determine if new version is newer"""
        try:
            from packaging import version
            return version.parse(new_version) > version.parse(current_version)
        except Exception as e:
            logging.warning(f"Error comparing versions {current_version} vs {new_version}: {e}")
            return new_version != current_version
    
    def _record_update(self, tool_name: str, category: str, tool_info: Dict, latest_version: str):
        """Record an update in the tracking system"""
        self.updates_found.append({
            'tool': tool_name,
            'category': category,
            'old_version': tool_info['current_version'],
            'new_version': latest_version,
            'description': tool_info['description']
        })
        
        # Update config
        tool_info['current_version'] = latest_version
        tool_info['last_updated'] = get_current_timestamp()
    
    def search_trending_tools(self):
        """Search for trending tools on GitHub"""
        logging.info("Searching for trending tools...")
        
        topics = self.config_manager.config['monitoring_sources']['github_topics']
        
        for topic in topics:
            try:
                # Search for recent repositories with stars
                created_since = datetime.now().strftime('%Y-%m-%d')
                query = f"topic:{topic} created:>={created_since}"
                url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=5"
                
                data = self.http_client.get(url)
                if data and 'items' in data:
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
                logging.warning(f"Error searching topic {topic}: {e}")
    
    def update_readme(self):
        """Update README.md with latest tool versions"""
        logging.info("Updating README.md...")
        
        readme_path = Path("README.md")
        if not readme_path.exists():
            logging.error("README.md not found!")
            return
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update version numbers in framework table
        for update in self.updates_found:
            if update['category'] == 'ai_frameworks':
                pattern = rf"(\*\*{re.escape(update['tool'])}\*\*\|)([^|]+)(\|)"
                replacement = rf"\g<1>{update['new_version']} (Updated {get_current_timestamp()})\g<3>"
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Add trending tools section if new tools found
        if self.trending_tools:
            content = self._add_trending_section(content)
        
        # Update timestamp
        today = datetime.now().strftime('%B %d, %Y')
        content = re.sub(r'Generated.*?–', f'Generated {today} –', content)
        
        with open(readme_path, 'w') as f:
            f.write(content)
        
        logging.info("README.md updated successfully")
    
    def _add_trending_section(self, content: str) -> str:
        """Add or update trending tools section in README"""
        trending_section = self._generate_trending_section()
        
        if "## Trending Tools to Investigate" not in content:
            content += f"\n\n---\n\n{trending_section}"
        else:
            pattern = r"## Trending Tools to Investigate.*?(?=\n\n---|\n\n##|\Z)"
            content = re.sub(pattern, trending_section, content, flags=re.DOTALL)
        
        return content
    
    def _generate_trending_section(self) -> str:
        """Generate trending tools section"""
        section = "## Trending Tools to Investigate\n\n"
        section += "| Tool | Stars | Language | Use Case | Repository |\n"
        section += "|------|-------|----------|----------|------------|\n"
        
        for tool in self.trending_tools[:10]:  # Top 10 only
            desc = tool['description'][:100] + ('...' if len(tool['description']) > 100 else '')
            section += f"|**{tool['name']}**|{tool['stars']}|{tool['language'] or 'N/A'}|{desc}|[GitHub]({tool['url']})|\n"
        
        return section
    
    def generate_summary(self) -> str:
        """Generate summary of updates found"""
        if not self.updates_found and not self.trending_tools:
            return "No updates found."
        
        sections = []
        
        if self.updates_found:
            sections.append({
                'title': f"Tool Updates Found ({len(self.updates_found)})",
                'items': [f"**{u['tool']}**: {u['old_version']} → {u['new_version']}" 
                         for u in self.updates_found]
            })
        
        if self.trending_tools:
            sections.append({
                'title': f"Trending Tools Found ({len(self.trending_tools)})",
                'items': [f"**{t['name']}** ({t['stars']} stars): {t['description'][:100]}{'...' if len(t['description']) > 100 else ''}"
                         for t in self.trending_tools[:5]]
            })
        
        return ReportGenerator.generate_markdown_report("Update Summary", sections)
    
    def run(self):
        """Run the complete update process"""
        logging.info("Starting tool update check...")
        
        # Check for updates
        self.check_tool_updates()
        
        # Search for trending tools
        self.search_trending_tools()
        
        # Update configuration
        self.config_manager.config['last_update_check'] = get_current_timestamp()
        self.config_manager.config['trending_tools'] = self.trending_tools
        self.config_manager.save_config()
        
        # Update README
        self.update_readme()
        
        # Generate and display summary
        summary = self.generate_summary()
        print(summary)
        
        return len(self.updates_found) > 0 or len(self.trending_tools) > 0


def main():
    """Main entry point"""
    Logger.setup_logging("INFO")
    
    # Check and install dependencies
    DependencyManager.check_and_install(['requests', 'packaging'])
    
    try:
        checker = ToolVersionChecker()
        has_updates = checker.run()
        
        if has_updates:
            logging.info("Update check completed with changes!")
        else:
            logging.info("Update check completed - everything is up to date!")
            
    except Exception as e:
        logging.error(f"Error during update check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()