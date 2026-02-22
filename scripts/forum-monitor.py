#!/usr/bin/env python3
"""
Forum and Community Monitor for AI Agent Development Workstation
Monitors key forums and communities for new discussions and trending topics
"""

import logging
import re
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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
        self.source_weights = {
            'github': 1.0,
            'reddit': 0.8,
            'hackernews': 0.9,
        }
        self.lookback_days = 7
        
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
        """Monitor GitHub repository conversations using issue search API"""
        logging.info("Monitoring GitHub repository conversations...")
        discussions: List[Dict[str, str]] = []

        repos_to_monitor = [
            "microsoft/autogen",
            "langchain-ai/langchain",
            "crewAIInc/crewAI",
            "microsoft/semantic-kernel"
        ]

        since = (datetime.utcnow() - timedelta(days=self.lookback_days)
                 ).strftime('%Y-%m-%d')
        
        for repo in repos_to_monitor:
            try:
                query = (
                    f"repo:{repo} is:issue is:open "
                    f"updated:>={since} sort:updated-desc"
                )
                url = (
                    "https://api.github.com/search/issues?"
                    f"q={query}&per_page=10"
                )
                data = self.http_client.get(url)
                
                if data and 'items' in data:
                    for issue in data['items'][:5]:
                        created_at = datetime.fromisoformat(
                            issue['created_at'].replace('Z', '+00:00'))

                        # Check if created in last 7 days
                        now = datetime.now().replace(tzinfo=created_at.tzinfo)
                        if created_at > now - timedelta(days=7):
                            title = issue['title']
                            discussions.append({
                                'title': title,
                                'url': issue['html_url'],
                                'source': f'GitHub - {repo}',
                                'source_type': 'github',
                                'relevance': self._calculate_relevance(title),
                                'keywords': extract_keywords(
                                    title, self.ai_keywords),
                                'created_at': issue['created_at'],
                                'engagement': int(issue.get('comments', 0)),
                            })
                
                rate_limit_delay(1)  # GitHub API rate limiting
                
            except Exception as e:
                logging.warning(f"Error monitoring {repo}: {e}")
        
        return discussions

    def monitor_hackernews(self) -> List[Dict[str, str]]:
        """Monitor Hacker News for AI agent related stories"""
        logging.info("Monitoring Hacker News...")
        discussions: List[Dict[str, str]] = []

        try:
            url = (
                "https://hn.algolia.com/api/v1/search_by_date?"
                "tags=story&query=ai%20agent&hitsPerPage=30"
            )
            data = self.http_client.get(url)

            if data and 'hits' in data:
                cutoff = datetime.utcnow() - timedelta(days=self.lookback_days)
                for hit in data['hits']:
                    title = hit.get('title') or hit.get('story_title')
                    created_at = hit.get('created_at')
                    if not title or not created_at:
                        continue

                    try:
                        created = datetime.fromisoformat(
                            created_at.replace('Z', '+00:00')).replace(
                            tzinfo=None)
                    except ValueError:
                        continue

                    if created < cutoff:
                        continue

                    discussions.append({
                        'title': title,
                        'url': hit.get('url') or (
                            "https://news.ycombinator.com/item?id="
                            f"{hit.get('objectID', '')}"
                        ),
                        'source': 'Hacker News',
                        'source_type': 'hackernews',
                        'relevance': self._calculate_relevance(title),
                        'keywords': extract_keywords(title, self.ai_keywords),
                        'created_at': created_at,
                        'engagement': int(hit.get('points', 0)),
                    })
        except Exception as e:
            logging.warning(f"Error monitoring Hacker News: {e}")

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
                                'source_type': 'reddit',
                                'relevance': self._calculate_relevance(title),
                                'keywords': extract_keywords(
                                    title, self.ai_keywords),
                                'created_at': datetime.utcfromtimestamp(
                                    post_data.get('created_utc', 0)
                                ).isoformat() + 'Z',
                                'engagement': int(post_data.get('score', 0)),
                            })
                
                rate_limit_delay(2)  # Reddit API rate limiting
                
            except Exception as e:
                logging.warning(f"Error monitoring r/{subreddit}: {e}")
        
        return discussions

    def _normalize_title(self, title: str) -> str:
        """Normalize title for fuzzy deduplication."""
        normalized = re.sub(r'[^a-z0-9\s]', ' ', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def deduplicate_discussions(
        self,
        discussions: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Deduplicate discussions by normalized title and keep best signal."""
        deduped: Dict[str, Dict[str, str]] = {}

        for item in discussions:
            key = self._normalize_title(item.get('title', ''))
            if not key:
                continue
            previous = deduped.get(key)
            if not previous:
                deduped[key] = item
                continue

            prev_engagement = int(previous.get('engagement', 0))
            curr_engagement = int(item.get('engagement', 0))
            if curr_engagement > prev_engagement:
                deduped[key] = item

        return list(deduped.values())

    def _freshness_score(self, created_at: Optional[str]) -> int:
        """Convert recency into a bounded freshness score."""
        if not created_at:
            return 0

        try:
            created = datetime.fromisoformat(
                created_at.replace('Z', '+00:00')).replace(tzinfo=None)
        except ValueError:
            return 0

        age_days = max(0, (datetime.utcnow() - created).days)
        return max(0, 30 - min(30, age_days * 4))

    def _relevance_score(self, relevance: str) -> int:
        if relevance == 'high':
            return 40
        if relevance == 'medium':
            return 20
        return 5

    def score_discussions(self, discussions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Attach weighted score to each discussion for ranking."""
        scored: List[Dict[str, str]] = []

        for item in discussions:
            source_type = item.get('source_type', '').lower()
            source_weight = self.source_weights.get(source_type, 0.7)
            relevance_score = self._relevance_score(item.get('relevance', 'low'))
            freshness = self._freshness_score(item.get('created_at'))
            engagement = min(30, int(item.get('engagement', 0)) // 5)
            total = int((relevance_score + freshness + engagement) * source_weight)

            updated = dict(item)
            updated['score'] = total
            scored.append(updated)

        scored.sort(key=lambda x: int(x.get('score', 0)), reverse=True)
        return scored
    
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
            'sources_monitored': len(set(d['source'] for d in discussions)),
            'top_discussions': discussions[:10],
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
        
        # Top scored discussions
        top_discussions = discussions[:10]
        if top_discussions:
            discussion_items = []
            for discussion in top_discussions:
                discussion_items.append(
                    f"**{discussion['title']}**\n"
                    f"  - Source: {discussion['source']}\n"
                    f"  - Score: {discussion.get('score', 0)}\n"
                    f"  - URL: {discussion['url']}\n"
                    f"  - Keywords: {', '.join(discussion['keywords'])}"
                )
            sections.append({
                'title': 'Top Ranked Discussions',
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
        all_discussions.extend(self.monitor_hackernews())
        # Note: OpenAI forum monitoring disabled pending proper implementation

        # Clean and score results
        deduped_discussions = self.deduplicate_discussions(all_discussions)
        scored_discussions = self.score_discussions(deduped_discussions)
        
        # Analyze discussions
        analysis = self.analyze_discussions(scored_discussions)
        
        # Generate insights report
        report = self.generate_insights_report(scored_discussions, analysis)
        
        # Save report
        timestamp = get_current_timestamp()
        report_path = f"reports/community-insights-{timestamp}.md"
        json_report_path = f"reports/community-insights-{timestamp}.json"
        ReportGenerator.save_report(report, report_path)
        ReportGenerator.save_report(
            ReportGenerator.to_json({
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'analysis': analysis,
                'discussions': scored_discussions,
            }),
            json_report_path,
        )

        logging.info(
            f"Community monitoring completed: "
            f"{len(scored_discussions)} discussions found")
        
        return scored_discussions, analysis


def main():
    """Main entry point"""
    Logger.setup_logging("INFO")

    parser = argparse.ArgumentParser(
        description="Monitor AI communities for high-signal discussions")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="How many days of history to include (default: 7)")
    args = parser.parse_args()
    
    # Check and install dependencies
    DependencyManager.check_and_install(['requests', 'beautifulsoup4'])
    
    try:
        monitor = ForumMonitor()
        monitor.lookback_days = max(1, args.days)
        discussions, analysis = monitor.run()
        
        print("Forum monitoring completed!")
        print(f"- Found {len(discussions)} relevant discussions")
        print(
            f"- {analysis['high_relevance_count']} high-relevance "
            "discussions")
        print(
            f"- Sources covered: {analysis['sources_monitored']}")
        
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
