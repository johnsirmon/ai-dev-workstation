#!/usr/bin/env python3
"""
Forum and Community Monitor for AI Agent Development Workstation
Monitors key forums and communities for new discussions and trending topics
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from utils import (
    ConfigManager, DependencyManager, HTTPClient, Logger,
    ReportGenerator, extract_keywords, get_current_timestamp, rate_limit_delay
)


class ForumMonitor:
    """Monitors forums and communities for AI agent discussions"""

    def __init__(self, config_path: str = "config/tools-tracking.json"):
        self.config_manager = ConfigManager(config_path)
        self.http_client = HTTPClient()
        self.discussions: List[Dict[str, str]] = []
        self.ai_keywords = [
            'agent', 'ai', 'llm', 'gpt', 'claude', 'automation', 'assistant',
            'langchain', 'autogen', 'crewai', 'semantic', 'kernel', 'function',
            'tool', 'api', 'integration', 'workflow', 'orchestration', 'mcp'
        ]
        
    def monitor_openai_forum(self) -> List[Dict[str, str]]:
        """Monitor OpenAI Developer Community for new discussions"""
        logging.info("Monitoring OpenAI Developer Community...")
        discussions: List[Dict[str, str]] = []

        try:
            # Note: This is a simplified approach as OpenAI forum
            # requires specific parsing
            # In a real implementation, you'd need to handle their
            # specific HTML structure

            # For now, we'll use a mock approach since web scraping
            # requires careful handling
            # In production, you'd implement proper HTML parsing here
            logging.info(
                "OpenAI forum monitoring requires specific HTML parsing "
                "implementation")

        except Exception as e:
            logging.warning(f"Error monitoring OpenAI forum: {e}")

        return discussions
    
    def monitor_github_discussions(self) -> List[Dict[str, str]]:
        """Monitor GitHub discussions for AI agent repositories"""
        logging.info("Monitoring GitHub discussions...")
        discussions: List[Dict[str, str]] = []

        repos_to_monitor = [
            "microsoft/autogen",
            "langchain-ai/langchain",
            "crewAIInc/crewAI",
            "microsoft/semantic-kernel"
        ]
        
        for repo in repos_to_monitor:
            try:
                url = f"https://api.github.com/repos/{repo}/discussions"
                data = self.http_client.get(url)
                
                if data:
                    for discussion in data[:5]:  # Top 5 recent discussions
                        created_at = datetime.fromisoformat(
                            discussion['created_at'].replace('Z', '+00:00'))

                        # Check if created in last 7 days
                        now = datetime.now().replace(tzinfo=created_at.tzinfo)
                        if created_at > now - timedelta(days=7):
                            discussions.append({
                                'title': discussion['title'],
                                'url': discussion['html_url'],
                                'source': f'GitHub - {repo}',
                                'relevance': self._calculate_relevance(
                                    discussion['title']),
                                'keywords': extract_keywords(
                                    discussion['title'], self.ai_keywords),
                                'created_at': discussion['created_at']
                            })
                
                rate_limit_delay(1)  # GitHub API rate limiting
                
            except Exception as e:
                logging.warning(f"Error monitoring {repo}: {e}")
        
        return discussions
    
    def monitor_reddit_communities(self) -> List[Dict[str, str]]:
        """Monitor Reddit AI communities for trending discussions"""
        logging.info("Monitoring Reddit AI communities...")
        discussions: List[Dict[str, str]] = []

        subreddits = [
            'MachineLearning',
            'artificial',
            'OpenAI',
            'ChatGPT',
            'LocalLLaMA'
        ]
        
        for subreddit in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                data = self.http_client.get(url)
                
                if data and 'data' in data:
                    for post in data['data']['children']:
                        post_data = post['data']
                        title = post_data['title']
                        
                        # Check if related to AI agents
                        if any(keyword in title.lower() for keyword in
                               self.ai_keywords):
                            discussions.append({
                                'title': title,
                                'url': (
                                    "https://www.reddit.com"
                                    f"{post_data['permalink']}"),
                                'source': f'Reddit - r/{subreddit}',
                                'relevance': self._calculate_relevance(title),
                                'keywords': extract_keywords(
                                    title, self.ai_keywords),
                                'score': str(post_data.get('score', 0))
                            })
                
                rate_limit_delay(2)  # Reddit API rate limiting
                
            except Exception as e:
                logging.warning(f"Error monitoring r/{subreddit}: {e}")
        
        return discussions
    
    def _calculate_relevance(self, title: str) -> str:
        """Calculate relevance score based on keyword matches"""
        title_lower = title.lower()
        high_value_keywords = [
            'agent', 'assistant', 'automation', 'llm', 'mcp']

        if any(keyword in title_lower for keyword in high_value_keywords):
            return 'high'
        elif any(keyword in title_lower for keyword in self.ai_keywords):
            return 'medium'
        else:
            return 'low'
    
    def analyze_discussions(self, discussions: List[Dict[str, str]]) -> Dict[str, List]:
        """Analyze discussions for trends and insights"""
        logging.info("Analyzing discussions for trends...")

        keyword_counts: Dict[str, int] = {}
        tool_mentions: Dict[str, int] = {}
        
        for discussion in discussions:
            # Count keywords
            for keyword in discussion['keywords']:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Count tool mentions
            title_lower = discussion['title'].lower()
            frameworks = self.config_manager.config['tracked_tools'][
                'ai_frameworks']
            for tool_name in frameworks.keys():
                if tool_name.lower() in title_lower:
                    tool_mentions[tool_name] = (
                        tool_mentions.get(tool_name, 0) + 1)
        
        trending_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        trending_tools = sorted(
            tool_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'trending_keywords': trending_keywords,
            'trending_tools': trending_tools,
            'total_discussions': len(discussions),
            'high_relevance_count': len(
                [d for d in discussions if d['relevance'] == 'high']),
            'sources_monitored': len(set(d['source'] for d in discussions))
        }
    
    def generate_insights_report(
            self,
            discussions: List[Dict[str, str]],
            analysis: Dict[str, List]) -> str:
        """Generate insights report from forum monitoring"""
        sections = []
        
        # Summary section
        sections.append({
            'title': 'Summary',
            'items': [
                (f"**Total Discussions Found**: "
                 f"{analysis['total_discussions']}"),
                (f"**High Relevance Discussions**: "
                 f"{analysis['high_relevance_count']}"),
                f"**Sources Monitored**: {analysis['sources_monitored']}"
            ]
        })
        
        # Trending keywords
        if analysis['trending_keywords']:
            sections.append({
                'title': 'Trending Keywords',
                'items': [f"**{keyword}**: {count} mentions"
                          for keyword, count in analysis['trending_keywords']]
            })
        
        # Tool mentions
        if analysis['trending_tools']:
            sections.append({
                'title': 'Tool Mentions',
                'items': [f"**{tool}**: {count} mentions"
                          for tool, count in analysis['trending_tools']]
            })
        
        # High relevance discussions
        high_relevance = [d for d in discussions if d['relevance'] == 'high'][:10]
        if high_relevance:
            discussion_items = []
            for discussion in high_relevance:
                discussion_items.append(
                    f"**{discussion['title']}**\n"
                    f"  - Source: {discussion['source']}\n"
                    f"  - URL: {discussion['url']}\n"
                    f"  - Keywords: {', '.join(discussion['keywords'])}"
                )
            sections.append({
                'title': 'Recent High-Relevance Discussions',
                'items': discussion_items
            })
        
        return ReportGenerator.generate_markdown_report(
            "AI Agent Development Community Insights",
            sections
        )
    
    def run(self) -> Tuple[List[Dict[str, str]], Dict[str, List]]:
        """Run the complete forum monitoring process"""
        logging.info("Starting community monitoring...")

        all_discussions = []
        
        # Monitor different sources
        all_discussions.extend(self.monitor_github_discussions())
        all_discussions.extend(self.monitor_reddit_communities())
        # Note: OpenAI forum monitoring disabled pending proper implementation
        
        # Analyze discussions
        analysis = self.analyze_discussions(all_discussions)
        
        # Generate insights report
        report = self.generate_insights_report(all_discussions, analysis)
        
        # Save report
        timestamp = get_current_timestamp()
        report_path = f"reports/community-insights-{timestamp}.md"
        ReportGenerator.save_report(report, report_path)

        logging.info(
            f"Community monitoring completed: "
            f"{len(all_discussions)} discussions found")
        
        return all_discussions, analysis


def main():
    """Main entry point"""
    Logger.setup_logging("INFO")
    
    # Check and install dependencies
    DependencyManager.check_and_install(['requests', 'beautifulsoup4'])
    
    try:
        monitor = ForumMonitor()
        discussions, analysis = monitor.run()
        
        print("Forum monitoring completed!")
        print(f"- Found {len(discussions)} relevant discussions")
        print(
            f"- {analysis['high_relevance_count']} high-relevance "
            "discussions")
        
        if analysis['trending_keywords']:
            top_keyword = analysis['trending_keywords'][0]
            print(
                f"- Top trending keyword: {top_keyword[0]} "
                f"({top_keyword[1]} mentions)")
            
    except Exception as e:
        logging.error(f"Error during forum monitoring: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
