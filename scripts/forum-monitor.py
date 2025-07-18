#!/usr/bin/env python3
"""
Forum and Community Monitor for AI Agent Development Workstation
Monitors key forums and communities for new discussions and trending topics
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class ForumMonitor:
    def __init__(self, config_path: str = "config/tools-tracking.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.new_discussions = []
        self.trending_topics = []
        
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
    
    def monitor_openai_forum(self) -> List[Dict]:
        """Monitor OpenAI Developer Community for new discussions"""
        print("Monitoring OpenAI Developer Community...")
        discussions = []
        
        try:
            # Use OpenAI API to search for recent discussions
            # Note: This would require proper API access
            # For now, we'll use web scraping approach
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = "https://community.openai.com/latest"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for recent topics (this is a simplified approach)
                topics = soup.find_all('div', class_='topic-list-item')[:10]
                
                for topic in topics:
                    try:
                        title_elem = topic.find('a', class_='title')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = urljoin(url, title_elem.get('href', ''))
                            
                            # Check if it's related to agents or API
                            if any(keyword in title.lower() for keyword in ['agent', 'api', 'assistant', 'function', 'tool']):
                                discussions.append({
                                    'title': title,
                                    'url': link,
                                    'source': 'OpenAI Community',
                                    'relevance': 'high',
                                    'keywords': self.extract_keywords(title)
                                })
                    except Exception as e:
                        print(f"Error parsing topic: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error monitoring OpenAI forum: {e}")
        
        return discussions
    
    def monitor_github_discussions(self) -> List[Dict]:
        """Monitor GitHub discussions for AI agent repositories"""
        print("Monitoring GitHub discussions...")
        discussions = []
        
        repos_to_monitor = [
            "microsoft/autogen",
            "langchain-ai/langchain",
            "crewAIInc/crewAI",
            "microsoft/semantic-kernel"
        ]
        
        for repo in repos_to_monitor:
            try:
                # GitHub API for discussions
                url = f"https://api.github.com/repos/{repo}/discussions"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for discussion in data[:5]:  # Top 5 recent discussions
                        # Check if created in last 7 days
                        created_at = datetime.fromisoformat(discussion['created_at'].replace('Z', '+00:00'))
                        if created_at > datetime.now().replace(tzinfo=created_at.tzinfo) - timedelta(days=7):
                            discussions.append({
                                'title': discussion['title'],
                                'url': discussion['html_url'],
                                'source': f'GitHub - {repo}',
                                'relevance': 'high',
                                'keywords': self.extract_keywords(discussion['title']),
                                'created_at': discussion['created_at']
                            })
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error monitoring {repo}: {e}")
        
        return discussions
    
    def monitor_reddit_ai_communities(self) -> List[Dict]:
        """Monitor Reddit AI communities for trending discussions"""
        print("Monitoring Reddit AI communities...")
        discussions = []
        
        subreddits = [
            'MachineLearning',
            'artificial',
            'OpenAI',
            'ChatGPT',
            'LocalLLaMA'
        ]
        
        for subreddit in subreddits:
            try:
                # Reddit API (requires authentication for full access)
                # Using web scraping approach for public posts
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for post in data['data']['children']:
                        post_data = post['data']
                        title = post_data['title']
                        
                        # Check if related to AI agents
                        if any(keyword in title.lower() for keyword in ['agent', 'assistant', 'automation', 'llm', 'ai']):
                            discussions.append({
                                'title': title,
                                'url': f"https://www.reddit.com{post_data['permalink']}",
                                'source': f'Reddit - r/{subreddit}',
                                'relevance': 'medium',
                                'keywords': self.extract_keywords(title),
                                'score': post_data.get('score', 0)
                            })
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"Error monitoring r/{subreddit}: {e}")
        
        return discussions
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Common AI agent keywords
        keywords = [
            'agent', 'ai', 'llm', 'gpt', 'claude', 'automation', 'assistant',
            'langchain', 'autogen', 'crewai', 'semantic', 'kernel', 'function',
            'tool', 'api', 'integration', 'workflow', 'orchestration', 'mcp'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw in text_lower]
        
        return found_keywords
    
    def analyze_discussions(self, discussions: List[Dict]) -> Dict:
        """Analyze discussions for trends and insights"""
        print("Analyzing discussions for trends...")
        
        # Count keyword frequency
        keyword_counts = {}
        tool_mentions = {}
        
        for discussion in discussions:
            for keyword in discussion['keywords']:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Check for tool mentions
            title_lower = discussion['title'].lower()
            for tool_name in self.config['tracked_tools']['ai_frameworks'].keys():
                if tool_name.lower() in title_lower:
                    tool_mentions[tool_name] = tool_mentions.get(tool_name, 0) + 1
        
        # Find trending topics
        trending_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        trending_tools = sorted(tool_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'trending_keywords': trending_keywords,
            'trending_tools': trending_tools,
            'total_discussions': len(discussions),
            'high_relevance_count': len([d for d in discussions if d['relevance'] == 'high'])
        }
    
    def generate_insights_report(self, discussions: List[Dict], analysis: Dict) -> str:
        """Generate insights report from forum monitoring"""
        report = []
        
        report.append("# AI Agent Development Community Insights")
        report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        report.append(f"## Summary")
        report.append(f"- **Total Discussions Found**: {analysis['total_discussions']}")
        report.append(f"- **High Relevance Discussions**: {analysis['high_relevance_count']}")
        report.append(f"- **Sources Monitored**: {len(set(d['source'] for d in discussions))}\n")
        
        if analysis['trending_keywords']:
            report.append("## Trending Keywords")
            for keyword, count in analysis['trending_keywords']:
                report.append(f"- **{keyword}**: {count} mentions")
            report.append("")
        
        if analysis['trending_tools']:
            report.append("## Tool Mentions")
            for tool, count in analysis['trending_tools']:
                report.append(f"- **{tool}**: {count} mentions")
            report.append("")
        
        report.append("## Recent High-Relevance Discussions")
        high_relevance = [d for d in discussions if d['relevance'] == 'high'][:10]
        
        for discussion in high_relevance:
            report.append(f"### {discussion['title']}")
            report.append(f"- **Source**: {discussion['source']}")
            report.append(f"- **URL**: {discussion['url']}")
            report.append(f"- **Keywords**: {', '.join(discussion['keywords'])}")
            report.append("")
        
        return "\n".join(report)
    
    def run(self):
        """Run the complete forum monitoring process"""
        print("Starting AI Agent Development Community Monitor...")
        
        all_discussions = []
        
        # Monitor different sources
        all_discussions.extend(self.monitor_openai_forum())
        all_discussions.extend(self.monitor_github_discussions())
        all_discussions.extend(self.monitor_reddit_ai_communities())
        
        # Analyze discussions
        analysis = self.analyze_discussions(all_discussions)
        
        # Generate insights report
        report = self.generate_insights_report(all_discussions, analysis)
        
        # Save report
        report_path = Path("reports") / f"community-insights-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"Community insights report saved to: {report_path}")
        print(f"Found {len(all_discussions)} relevant discussions")
        
        return all_discussions, analysis


if __name__ == "__main__":
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
        import requests
        from bs4 import BeautifulSoup
    
    monitor = ForumMonitor()
    discussions, analysis = monitor.run()
    
    print(f"\n✅ Forum monitoring completed!")
    print(f"- Found {len(discussions)} relevant discussions")
    print(f"- {analysis['high_relevance_count']} high-relevance discussions")
    
    if analysis['trending_keywords']:
        print(f"- Top trending keyword: {analysis['trending_keywords'][0][0]} ({analysis['trending_keywords'][0][1]} mentions)")