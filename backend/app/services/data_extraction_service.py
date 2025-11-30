"""
Crisis Social Media Monitoring System
Author: Your Name
Description: A comprehensive system for monitoring crisis-related content across social media platforms
"""

import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import feedparser
import urllib.parse
import random
import re
import ast
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer, util
import torch


class WebSearchBot:
    """
    Gemini WebSearch Bot using official google-genai client.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", ollama_url: str = "http://localhost:11434"):
        """
        Initialize WebSearchBot
        
        Args:
            api_key: Gemini API key
            model: Model name to use
            ollama_url: Ollama server URL
        """
        try:
            from google.genai import Client
            from google.genai.types import GoogleSearch, GenerateContentConfig
            self.Client = Client
            self.GoogleSearch = GoogleSearch
            self.GenerateContentConfig = GenerateContentConfig
        except ImportError:
            raise ImportError("Please install google-genai: pip install google-genai")
        
        self.client = self.Client(api_key=api_key)
        self.model = model
        self.ollama_url = ollama_url

    def ask(self, query: str) -> str:
        """
        Perform real-time grounded web search using Gemini + GoogleSearch.
        
        Args:
            query: Search query
            
        Returns:
            Response text from the model
        """
        resp = self.client.models.generate_content(
            model=self.model,
            contents=query,
            config=self.GenerateContentConfig(
                tools=[self.GoogleSearch],
                temperature=0.2
            )
        )
        return resp.text


class ClaimBot:
    """
    Claim extraction bot using Ollama
    """
    
    def __init__(self, model: str = "gpt-oss:20b-cloud"):
        """
        Initialize ClaimBot
        
        Args:
            model: Ollama model name
        """
        try:
            import ollama
            self.ollama = ollama
        except ImportError:
            raise ImportError("Please install ollama: pip install ollama")
        
        self.model = model

    def extract_claims(self, keyword: str, cluster_id: int, docs: List[Dict], num_claims: int = 5) -> str:
        """
        Extract claims from documents
        
        Args:
            keyword: Crisis keyword
            cluster_id: Cluster identifier
            docs: List of document dictionaries
            num_claims: Number of claims to extract
            
        Returns:
            Extracted claims as string
        """
        combined_text = "\n\n---\n\n".join(
            f"TITLE: {d.get('title', '')}\nTEXT:\n{d.get('selftext', '')}"
            for d in docs
        )

        prompt = f"""
        You are ClaimBot, an information extraction system trained to extract
        *public, impersonal, news-verifiable claims* ONLY.

        INSTRUCTIONS:
        - Extract EXACTLY {num_claims} factual claims.
        - Your claims must:
            • Be verifiable by public information, news, reports, or general knowledge.
            • NOT refer to private individuals, personal relationships, family disputes,
              medical issues, finances, or any information about specific people
              who are not public figures.
            • NOT describe interpersonal events (e.g., "Marc did X to the user…").
            • Focus on general themes, geopolitical issues, social phenomena,
              policy outcomes, economic trends, crisis conditions, conflict dynamics,
              or public facts.
        - If the source text contains personal or unverifiable details, ignore them.
        - Output a numbered list, 1 to {num_claims}, of generalized factual claims.

        KEYWORD: {keyword}
        CLUSTER ID: {cluster_id}

        SOURCE TEXT:
        {combined_text}
        """

        response = self.ollama.generate(
            model=self.model,
            prompt=prompt
        )
        return response.get("response", "").strip()





class GeminiVerifier:
    def __init__(self, api_key, model="gemini-2.5-flash"):
        from google.genai import Client
        from google.genai.types import GoogleSearch, GenerateContentConfig
        self.client = Client(api_key=api_key)
        self.model = model
        self.GoogleSearch = GoogleSearch
        self.GenerateContentConfig = GenerateContentConfig

    def check_claim(self, claim_text):
        """
        Run grounded fact-checking with Gemini and return a structured result.

        Returns a dict with:
            - label: 'supports' | 'contradicts' | 'unrelated'
            - reasoning: short natural language explanation (for supports/contradicts especially)
            - source_urls: list of cited source URLs (required for supports/contradicts when available)
        """
        import json

        prompt = f"""
You are a fact verification expert using grounded web search.

TASK:
1. Perform Google Search.
2. Read the top articles.
3. Decide whether the claim is SUPPORTED, CONTRADICTED, or UNRELATED by currently available evidence.
4. If you label the claim as SUPPORTED or CONTRADICTED, provide:
   - A SHORT reasoning sentence or two that points to the key evidence.
   - At least one or two source URLs from reputable sites (priority: major news outlets, official orgs, academic sources).
5. If you label the claim as UNRELATED, give a brief explanation and you MAY omit sources.

OUTPUT FORMAT (STRICT JSON):
Return ONLY a valid JSON object, no extra text, of the form:
{{
  "label": "supports" | "contradicts" | "unrelated",
  "reasoning": "short explanation of why you chose this label",
  "source_urls": ["https://source1", "https://source2"]
}}

CLAIM:
{claim_text}
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.GenerateContentConfig(
                tools=[self.GoogleSearch],
                temperature=0.1
            )
        )
        print("response from gemini:", response.text)

        raw_text = (response.text or "").strip()
        print("raw_text from gemini:", raw_text)
        try:
            data = json.loads(raw_text)
        except Exception:
            # Very defensive: fall back to simple label only
            label = raw_text.lower().strip()
            if label not in {"supports", "contradicts", "unrelated"}:
                label = "unrelated"
            data = {
                "label": label,
                "reasoning": "",
                "source_urls": []
            }

        label = str(data.get("label", "")).lower().strip()
        if label not in {"supports", "contradicts", "unrelated"}:
            label = "unrelated"

        reasoning = str(data.get("reasoning", "")).strip()
        source_urls = data.get("source_urls") or []
        if not isinstance(source_urls, list):
            source_urls = [str(source_urls)]

        # Keep URLs simple strings
        source_urls = [str(u).strip() for u in source_urls if str(u).strip()]

        return {
            "label": label,
            "reasoning": reasoning,
            "source_urls": source_urls,
        }


class CrisisMonitor:
    """
    Main Crisis Monitoring System
    """
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None,
                 embed_model_name: str = "all-MiniLM-L6-v2",
                 max_clusters: int = 10):
        """
        Initialize Crisis Monitor
        
        Args:
            gemini_api_key: Gemini API key for keyword extraction
            embed_model_name: Sentence transformer model name
            max_clusters: Maximum number of clusters per keyword
        """
        self.embed_model = SentenceTransformer(embed_model_name)
        self.max_clusters = max_clusters
        self.gemini_api_key = gemini_api_key
        
    def complete_pipeline(self, 
                         output_csv: str = "crisis_monitoring_output.csv",
                         max_posts_per_keyword: int = 15,
                         gemini_query: str = "What major crises are happening right now worldwide?") -> pd.DataFrame:
        """
        Run the complete monitoring pipeline
        
        Args:
            output_csv: Output filename
            max_posts_per_keyword: Maximum posts to collect per keyword
            gemini_query: Query for keyword extraction
            
        Returns:
            DataFrame with all collected data
        """
        print("="*80)
        print("STARTING COMPLETE CRISIS MONITORING PIPELINE")
        print("="*80)
        
        # Step 1: Extract keywords
        print("\n[1/6] Extracting crisis keywords...")
        keywords = self.extract_crisis_keywords(gemini_query)
        print(f"Keywords: {keywords}")
        
        # Step 2: Discover sources
        print("\n[2/6] Discovering Reddit subreddits...")
        subreddits = self.discover_relevant_subreddits(keywords, top_n=11)
        
        print("\n[3/6] Discovering Telegram channels...")
        channels = self.discover_telegram_channels()
        
        # Step 3: Scrape data
        print(f"\n[4/6] Scraping Reddit from {len(subreddits)} subreddits...")
        df_reddit = self.scrape_reddit_for_keywords(
            keywords=keywords[:2],
            subreddits=subreddits,
            limit_per_keyword=5
        )
        
        print(f"\n[5/6] Scraping Telegram from {len(channels)} channels...")
        df_telegram = self.scrape_telegram_for_keywords(
            keywords=keywords[:2],
            channels=channels[:13],  # Limit to 13 channels
            limit_per_channel=50
        )
        
        # Step 4: Combine and clean
        print("\n[6/6] Combining and cleaning data...")
        all_data = pd.concat([df_reddit, df_telegram], ignore_index=True)
        
        if 'date' in all_data.columns:
            all_data['date'] = pd.to_datetime(all_data['date'], errors='coerce')
            all_data = all_data.sort_values('date', ascending=False)
        
        # Final cleanup
        columns = ['keyword', 'title', 'selftext', 'platform', 'url', 'date']
        all_data = all_data[[col for col in columns if col in all_data.columns]]
        all_data.drop_duplicates(subset=['url'], inplace=True)
        
        print("\n" + "="*80)
        print(f"PIPELINE COMPLETE!")
        print(f"Total posts collected: {len(all_data)}")
        print(f"  • Reddit: {len(df_reddit)}")
        print(f"  • Telegram: {len(df_telegram)}")
        print("="*80)
        
        # Save to CSV
        all_data.to_csv(output_csv, index=False)
        print(f"\nSaved to: {output_csv}")
        
        return all_data

    def verify_claims_with_gemini(self, clean_claims_by_keyword: dict, gemini_api_key: str) -> dict:
        """
        Verify claims using Gemini web search.
        
        Args:
            clean_claims_by_keyword: Dict mapping keyword to list of claims
            gemini_api_key: Gemini API key
            
        Returns:
            Dict mapping keyword to list of dicts with claim, verdict, reasoning, and source_urls
        """
        verifier = GeminiVerifier(api_key=gemini_api_key)
        results_by_keyword = {}

        for keyword, claims in clean_claims_by_keyword.items():
            print(f"\n=== Processing: {keyword} ===\n")
            keyword_results = []
            for claim in claims[:5]:  # limit to first 5 for speed
                result = verifier.check_claim(claim)
                label = result.get("label", "unrelated")
                reasoning = result.get("reasoning", "")
                source_urls = result.get("source_urls", [])

                print(f"Claim: {claim}")
                print(f"Verdict: {label}")
                if reasoning:
                    print(f"Reasoning: {reasoning}")
                if source_urls:
                    print(f"Sources: {source_urls}")
                print()

                keyword_results.append({
                    "claim": claim,
                    "verdict": label,
                    "reasoning": reasoning,
                    "source_urls": source_urls,
                })
            results_by_keyword[keyword] = keyword_results
        return results_by_keyword

    @staticmethod
    def scrape_telegram_channel(channels: List[str], limit: int = 50) -> pd.DataFrame:
        """
        Scrapes public Telegram channel web previews
        
        Args:
            channels: List of Telegram channel names
            limit: Maximum messages per channel
            
        Returns:
            DataFrame with scraped data
        """
        data = []
        print(f"\n--- Scraping Telegram Public Channels ---")
        
        for channel in channels:
            try:
                url = f"https://t.me/s/{channel}"
                response = requests.get(url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    messages = soup.find_all('div', class_='tgme_widget_message_wrap', limit=limit)

                    for msg in messages:
                        text_elem = msg.find('div', class_='tgme_widget_message_text')
                        date_elem = msg.find('time', class_='time')

                        if text_elem:
                            content = text_elem.get_text()
                            content = content.replace('\n', ' ').strip()
                            date = date_elem['datetime'] if date_elem else None
                            msg_link = msg.find('a', class_='tgme_widget_message_date')['href'] if msg.find('a', class_='tgme_widget_message_date') else url

                            data.append({
                                'platform': 'Telegram',
                                'search_term': channel,
                                'date': date,
                                'username': channel,
                                'content': content[:500],
                                'url': msg_link
                            })
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"Error scraping Telegram channel '{channel}': {e}")

        return pd.DataFrame(data)

    @staticmethod
    def scrape_reddit_rss(subreddits: List[str], terms: List[str]) -> pd.DataFrame:
        """
        Scrape Reddit via RSS feeds
        
        Args:
            subreddits: List of subreddit names
            terms: List of search terms
            
        Returns:
            DataFrame with scraped data
        """
        data = []
        user_agent = 'Mozilla/5.0 (Colab RSS Reader)'

        print(f"--- Starting Reddit RSS Scrape ---")

        for sub in subreddits:
            for term in terms:
                try:
                    encoded_term = urllib.parse.quote_plus(term)
                    rss_url = f"https://www.reddit.com/r/{sub}/search.rss?q={encoded_term}&restrict_sr=1&sort=new"

                    feed = feedparser.parse(rss_url, agent=user_agent)

                    if not feed.entries:
                        continue

                    for entry in feed.entries:
                        raw_summary = getattr(entry, 'summary', '')
                        clean_text = BeautifulSoup(raw_summary, "html.parser").get_text(separator=' ', strip=True)

                        data.append({
                            'platform': 'Reddit (RSS)',
                            'subreddit': sub,
                            'search_term': term,
                            'title': entry.title,
                            'content': clean_text,
                            'link': entry.link,
                            'date': getattr(entry, 'updated', 'Unknown')
                        })

                    time.sleep(2)

                except Exception as e:
                    print(f"Error scraping r/{sub} for '{term}': {e}")

        return pd.DataFrame(data)

    @staticmethod
    def clean_keyword_list(raw_string: str) -> List[str]:
        """
        Clean and parse keyword list from string
        
        Args:
            raw_string: Raw string containing Python list
            
        Returns:
            Cleaned list of keywords
        """
        try:
            cleaned_string = raw_string.replace('```python', '').replace('```', '').strip()
            keywords = ast.literal_eval(cleaned_string)
        except Exception as e:
            raise ValueError(f"Input string is not a valid list literal or could not be parsed: {e}")

        cleaned = []
        seen = set()

        for k in keywords:
            item = k.strip()
            if item and item not in seen:
                seen.add(item)
                cleaned.append(item)

        return cleaned

    @staticmethod
    def discover_relevant_subreddits(keywords: List[str], top_n: int = 12) -> List[str]:
        """
        Auto-discover best Reddit subreddits for crisis topics
        
        Args:
            keywords: List of crisis keywords
            top_n: Number of top subreddits to return
            
        Returns:
            List of relevant subreddit names
        """
        print("Discovering the most relevant subreddits automatically...")
        subreddit_hits = Counter()

        for keyword in keywords:
            try:
                encoded = urllib.parse.quote_plus(keyword)
                search_url = f"https://www.reddit.com/search.rss?q={encoded}&type=sr"
                feed = feedparser.parse(search_url)
                time.sleep(1)

                for entry in feed.entries:
                    match = re.search(r'r/([a-zA-Z0-9_]+)', entry.title + entry.link)
                    if match:
                        sub = match.group(1).lower()
                        if len(sub) > 3 and sub not in ['mod', 'user', 'all', 'popular']:
                            subreddit_hits[sub] += 1
            except:
                continue

        discovered = [sub for sub, count in subreddit_hits.most_common(30)]
        priority_subs = ['worldnews', 'news', 'geopolitics', 'internationalpolitics', 'anarchy101',
                         'credibledefense', 'europe', 'middleeastnews', 'ukraine', 'israel', 'palestine']

        final_subs = list(dict.fromkeys(priority_subs + discovered))[:top_n]
        print(f"Auto-selected subreddits: {final_subs}")
        return final_subs

    @staticmethod
    def discover_telegram_channels() -> List[str]:
        """
        Auto-discover top Telegram news/geopolitics channels
        
        Returns:
            List of Telegram channel names
        """
        print("Fetching latest top Telegram news channels (no hardcoding)...")

        directory_urls = [
            "https://raw.githubusercontent.com/mrandriamaroh/Telegram-News-Channels/main/channels.txt",
            "https://raw.githubusercontent.com/itgoyo/Telegram-Groups/main/News.md",
        ]

        channels = set()

        for url in directory_urls:
            try:
                if "github" in url:
                    text = requests.get(url, timeout=10).text
                    found = re.findall(r'[@t]\.?me[/\w]*([a-zA-Z0-9_]{5,})', text, re.I)
                    for ch in found:
                        ch = ch.lower()
                        if len(ch) >= 5 and ch not in ['join', 'channel', 'group']:
                            channels.add(ch)
                time.sleep(1)
            except:
                continue

        known_good = {'bbcnews', 'reuters', 'cnn', 'apnews', 'rtnews', 'dwnews', 'aljazeeraenglish',
                      'nytimes', 'washingtonpost', 'theeconomist', 'financialtimes', 'warmonitor', 'intelcabal'}

        all_channels = list(channels.union(known_good))
        print(f"Auto-collected {len(all_channels)} Telegram channels")
        return all_channels[:40]

    def scrape_reddit_for_keywords(self, keywords: List[str], subreddits: List[str], 
                                   limit_per_keyword: int = 15) -> pd.DataFrame:
        """
        Scrape Reddit for specific keywords
        
        Args:
            keywords: List of crisis keywords
            subreddits: List of subreddit names
            limit_per_keyword: Maximum posts per keyword
            
        Returns:
            DataFrame with scraped data
        """
        data = []
        user_agent = "CrisisMonitor/1.0"

        print("Scraping Reddit via RSS...")
        for sub in subreddits:
            for keyword in keywords:
                try:
                    encoded = urllib.parse.quote_plus(keyword)
                    rss_url = f"https://www.reddit.com/r/{sub}/search.rss?q={encoded}&restrict_sr=1&sort=new&t=year"

                    feed = feedparser.parse(rss_url, agent=user_agent)
                    time.sleep(1.5)

                    entries_added = 0
                    for entry in feed.entries:
                        if entries_added >= limit_per_keyword:
                            break

                        raw_summary = entry.get('summary', '')
                        clean_text = BeautifulSoup(raw_summary, "html.parser").get_text(separator=' ', strip=True)

                        data.append({
                            'keyword': keyword,
                            'title': entry.title,
                            'selftext': clean_text or "[No selftext]",
                            'platform': 'Reddit',
                            'url': entry.link,
                            'date': entry.get('updated') or entry.get('published') or 'Unknown'
                        })
                        entries_added += 1

                except Exception as e:
                    print(f"Error scraping r/{sub} for '{keyword}': {e}")

        return pd.DataFrame(data)

    def scrape_telegram_for_keywords(self, keywords: List[str], channels: List[str], 
                                    limit_per_channel: int = 50) -> pd.DataFrame:
        """
        Scrape Telegram for specific keywords
        
        Args:
            keywords: List of crisis keywords
            channels: List of Telegram channel names
            limit_per_channel: Maximum messages per channel
            
        Returns:
            DataFrame with scraped data
        """
        data = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        print("\nScraping Telegram public channels...")
        for channel in channels:
            url = f"https://t.me/s/{channel}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                messages = soup.find_all('div', class_='tgme_widget_message_wrap')[:limit_per_channel]

                for msg in messages:
                    text_elem = msg.find('div', class_='tgme_widget_message_text')
                    date_elem = msg.find('time', class_='time')
                    link_elem = msg.find('a', class_='tgme_widget_message_date', href=True)

                    if not text_elem:
                        continue

                    content = text_elem.get_text().replace('\n', ' ').strip()
                    date = date_elem['datetime'] if date_elem else None
                    post_url = "https://t.me" + link_elem['href'] if link_elem else f"https://t.me/{channel}"

                    matched_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
                    if not matched_keywords:
                        continue

                    primary_keyword = max(matched_keywords, key=len)

                    data.append({
                        'keyword': primary_keyword,
                        'title': content[:100] + "..." if len(content) > 100 else content,
                        'selftext': content,
                        'platform': 'Telegram',
                        'url': post_url,
                        'date': date
                    })

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Error scraping @{channel}: {e}")

        return pd.DataFrame(data)

    @staticmethod
    def scrape_telegram_basic(channels: List[str], limit: int = 50) -> pd.DataFrame:
        """
        Basic Telegram scraping without keyword filtering (original method)
        
        Args:
            channels: List of Telegram channel names
            limit: Maximum messages per channel
            
        Returns:
            DataFrame with scraped data
        """
        data = []
        print(f"\n--- Scraping Telegram Public Channels ---")
        
        for channel in channels:
            try:
                url = f"https://t.me/s/{channel}"
                response = requests.get(url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    messages = soup.find_all('div', class_='tgme_widget_message_wrap', limit=limit)

                    for msg in messages:
                        text_elem = msg.find('div', class_='tgme_widget_message_text')
                        date_elem = msg.find('time', class_='time')

                        if text_elem:
                            content = text_elem.get_text()
                            content = content.replace('\n', ' ').strip()
                            date = date_elem['datetime'] if date_elem else None
                            msg_link_elem = msg.find('a', class_='tgme_widget_message_date')
                            msg_link = msg_link_elem['href'] if msg_link_elem else url

                            data.append({
                                'platform': 'Telegram',
                                'search_term': channel,
                                'date': date,
                                'username': channel,
                                'content': content[:500],
                                'url': msg_link
                            })
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"Error scraping Telegram channel '{channel}': {e}")

        return pd.DataFrame(data)

    def cluster_for_keyword(self, keyword: str, docs: List[Dict]) -> np.ndarray:
        """
        Cluster documents for a specific keyword
        
        Args:
            keyword: Crisis keyword
            docs: List of document dictionaries
            
        Returns:
            Array of cluster labels
        """
        from sklearn.cluster import KMeans
        
        texts = [d["selftext"] for d in docs]

        if len(texts) == 1:
            return np.zeros(1, dtype=int)

        embeddings = self.embed_model.encode(texts, show_progress_bar=False)

        n = len(texts)
        dynamic_clusters = min(self.max_clusters, max(2, int(np.sqrt(n))))

        kmeans = KMeans(n_clusters=dynamic_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)

        return labels

    def cluster_all_keywords(self, data_by_keyword: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Cluster documents for all keywords
        
        Args:
            data_by_keyword: Dictionary mapping keywords to document lists
            
        Returns:
            Dictionary mapping keywords to cluster information
        """
        clusters_by_keyword = {}

        for keyword, docs in data_by_keyword.items():
            labels = self.cluster_for_keyword(keyword, docs)

            clusters = defaultdict(list)
            for doc, label in zip(docs, labels):
                clusters[int(label)].append(doc)

            keyword_clusters = []
            for cluster_id, cluster_docs in sorted(clusters.items()):
                keyword_clusters.append({
                    "cluster_id": cluster_id,
                    "docs": cluster_docs,
                    "size": len(cluster_docs),
                })

            clusters_by_keyword[keyword] = keyword_clusters

        return clusters_by_keyword


    def group_by_keyword(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group posts by keyword
        
        Args:
            data: List of post dictionaries
            
        Returns:
            Dictionary mapping keywords to posts
        """
        by_keyword = defaultdict(list)

        for i, item in enumerate(data):
            keyword = item.get("keyword", "NO_KEYWORD")
            text = (item.get("selftext") or "").strip()
            if not text:
                continue

            by_keyword[keyword].append({
                "index": i,
                "title": item.get("title", ""),
                "selftext": text,
                "subreddit": item.get("subreddit"),
                "score": item.get("score"),
                "created_utc": item.get("created_utc"),
                "url": item.get("url"),
            })

        return by_keyword

    def extract_crisis_keywords(self, query: str) -> List[str]:
        """
        Extract crisis keywords using Gemini
        
        Args:
            query: Query describing crisis types
            
        Returns:
            List of crisis keywords
        """
        if not self.gemini_api_key:
            raise ValueError("Gemini API key required for keyword extraction")
        
        bot = WebSearchBot(api_key=self.gemini_api_key)
        
        full_query = f"""{query}
        Output as a concise list of keyword topics.
        Requirements:
        - Return ONLY a Python list of short strings.
        - No explanations.
        - Keywords must be social-media-friendly.
        - Focus on crisis-related, geopolitical, humanitarian, and economic themes."""
        
        answer = bot.ask(full_query)
        return self.clean_keyword_list(answer)


# Example usage of the verify_claims_with_gemini method
#crisis_monitor = CrisisMonitor(gemini_api_key="AIzaSyBztKSScq_lR8ULb2TUI_B9YGgNazIxfgo")
#clean_claims_by_keyword = {
    #"climate change": ["The Arctic ice is melting at an unprecedented rate.", "Global temperatures have risen by 1.5 degrees Celsius."],
    #"economic crisis": ["Inflation rates are at a 40-year high.", "Unemployment rates have significantly increased."]
#}
#results = crisis_monitor.verify_claims_with_gemini(clean_claims_by_keyword, gemini_api_key="AIzaSyBztKSScq_lR8ULb2TUI_B9YGgNazIxfgo")