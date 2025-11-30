"""
Fake Twitter/X data stream generator using LLM.
Generates realistic social media posts across various topics (casual, crisis).
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
from app.ollama_client import call_ollama_chat, OllamaAPIError
from app.config import settings

logger = logging.getLogger("truetrace.twitter_generator")


# Topic categories for generating diverse content
TOPIC_CATEGORIES = {
    "casual": [
        "daily life and routines",
        "food and cooking",
        "entertainment and movies",
        "sports and games",
        "travel and vacations",
        "technology gadgets",
        "fashion and style",
        "pets and animals",
        "hobbies and interests",
        "weather and seasons"
    ],
    "crisis": [
        "health emergencies and outbreaks",
        "natural disasters",
        "political conflicts",
        "economic crises",
        "cybersecurity incidents",
        "environmental disasters",
        "social unrest",
        "terrorism threats",
        "pandemic-related concerns",
        "infrastructure failures"
    ]
}

# Twitter-like usernames for variety
SAMPLE_USERNAMES = [
    "user123", "jane_doe", "tech_guru", "news_watcher", "traveler99",
    "foodie_lover", "sports_fan", "crypto_trader", "health_advocate",
    "climate_activist", "parent_life", "student_2024", "entrepreneur",
    "artist_creative", "fitness_coach", "bookworm", "gamer_pro",
    "music_lover", "pet_owner", "car_enthusiast", "fashionista"
]


async def generate_twitter_post(
    topic: str,
    category: str = "casual",
    keywords: Optional[List[str]] = None,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a single realistic Twitter/X post using LLM.
    
    Args:
        topic: The topic or theme for the post
        category: "casual" or "crisis"
        keywords: Optional keywords to incorporate
        username: Optional username, otherwise random
    
    Returns:
        Dict with id, text, platform, timestamp, username, etc.
    """
    # Determine tone and style based on category
    if category == "crisis":
        system_instruction = (
            "You are simulating crisis-related social media chatter. "
            "Compose authentic-feeling posts that reflect concern, urgency, or speculation while remaining conversational."
        )
    else:
        system_instruction = (
            "You are simulating casual social media chatter. "
            "Compose everyday, conversational posts that feel authentic and varied."
        )
    
    keyword_text = ""
    if keywords:
        keyword_text = f" Try to naturally incorporate some of these keywords: {', '.join(keywords[:5])}."
    
    prompt = f"""Generate a realistic Twitter/X post about: {topic}

{keyword_text}

Requirements:
- Keep it under 280 characters (Twitter limit)
- Use natural, conversational language
- Include hashtags if appropriate (1-3 max)
- Sound authentic and human-like
- Do not wrap the response in quotes or special formatting.
- Return only the post text."""
    
    try:
        post_text = await call_ollama_chat(
            prompt,
            system=system_instruction,
            temperature=0.85 if category == "casual" else 0.7,
        )
        
        # Clean up any markdown or quotes
        post_text = post_text.replace('"', '').replace("'", '').strip()
        if post_text.startswith("Post:"):
            post_text = post_text[5:].strip()
        
        # Ensure it's within Twitter character limit
        if len(post_text) > 280:
            post_text = post_text[:277] + "..."
        
        # Generate timestamp (within last 7 days)
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        
        # Generate post ID (Twitter-like format)
        post_id = f"tweet_{random.randint(1000000000000000000, 9999999999999999999)}"
        
        return {
            "id": post_id,
            "text": post_text,
            "platform": "twitter",
            "timestamp": timestamp.isoformat() + "Z",
            "username": username or random.choice(SAMPLE_USERNAMES),
            "category": category,
            "topic": topic
        }
    except Exception as e:
        logger.error(f"Error generating post: {e}")
        # Fallback post
        return {
            "id": f"tweet_{random.randint(1000000000000000000, 9999999999999999999)}",
            "text": f"Sample post about {topic} - generated content unavailable.",
            "platform": "twitter",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "username": username or random.choice(SAMPLE_USERNAMES),
            "category": category,
            "topic": topic
        }


async def generate_twitter_stream(
    keywords: List[str],
    num_posts: int = 50,
    category_weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Generate a stream of fake Twitter posts using LLM.
    
    Args:
        keywords: Keywords to generate posts around
        num_posts: Total number of posts to generate
        category_weights: Dict with "casual" and "crisis" weights (default: 50/50)
    
    Returns:
        List of post dictionaries
    """
    if category_weights is None:
        category_weights = {"casual": 0.5, "crisis": 0.5}
    
    logger.info(f"Generating {num_posts} fake Twitter posts with keywords: {keywords[:5]}...")
    
    posts = []
    
    # Determine how many posts per category
    num_casual = int(num_posts * category_weights.get("casual", 0.5))
    num_crisis = num_posts - num_casual
    
    # Select topics for each category
    casual_topics = random.sample(TOPIC_CATEGORIES["casual"], min(num_casual, len(TOPIC_CATEGORIES["casual"])))
    crisis_topics = random.sample(TOPIC_CATEGORIES["crisis"], min(num_crisis, len(TOPIC_CATEGORIES["crisis"])))
    
    # Generate casual posts
    logger.info(f"Generating {num_casual} casual posts...")
    casual_tasks = []
    for i in range(num_casual):
        topic = casual_topics[i % len(casual_topics)]
        # Sometimes incorporate keywords, sometimes not
        use_keywords = keywords if random.random() < 0.3 else None
        casual_tasks.append(generate_twitter_post(
            topic=topic,
            category="casual",
            keywords=use_keywords
        ))
    
    # Generate crisis posts
    logger.info(f"Generating {num_crisis} crisis posts...")
    crisis_tasks = []
    for i in range(num_crisis):
        topic = crisis_topics[i % len(crisis_topics)]
        # Crisis posts more likely to use keywords
        use_keywords = keywords if random.random() < 0.7 else None
        crisis_tasks.append(generate_twitter_post(
            topic=topic,
            category="crisis",
            keywords=use_keywords
        ))
    
    # Generate all posts concurrently (with rate limiting)
    all_tasks = casual_tasks + crisis_tasks
    
    # Process in batches to avoid overwhelming the API
    batch_size = 10
    for i in range(0, len(all_tasks), batch_size):
        batch = all_tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Error generating post: {result}")
            else:
                posts.append(result)
        
        # Small delay between batches
        if i + batch_size < len(all_tasks):
            await asyncio.sleep(0.5)
    
    # Shuffle posts to mix casual and crisis
    random.shuffle(posts)
    
    logger.info(f"Generated {len(posts)} fake Twitter posts")
    return posts


async def generate_keyword_focused_posts(
    keywords: List[str],
    posts_per_keyword: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate posts specifically focused on given keywords.
    Useful for testing pipeline with crisis-related content.
    
    Args:
        keywords: Keywords to focus on
        posts_per_keyword: Number of posts per keyword
    
    Returns:
        List of post dictionaries
    """
    logger.info(f"Generating keyword-focused posts for {len(keywords)} keywords...")
    
    posts = []
    tasks = []
    
    for keyword in keywords[:10]:  # Limit to first 10 keywords
        # Mix of casual and crisis posts for each keyword
        for i in range(posts_per_keyword):
            category = "crisis" if i < posts_per_keyword * 0.6 else "casual"
            tasks.append(generate_twitter_post(
                topic=f"discussion about {keyword}",
                category=category,
                keywords=[keyword]
            ))
    
    # Generate in batches
    batch_size = 10
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = await asyncio.gather(*batch, return_exceptions=True)
        
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Error generating post: {result}")
            else:
                posts.append(result)
        
        if i + batch_size < len(tasks):
            await asyncio.sleep(0.5)
    
    logger.info(f"Generated {len(posts)} keyword-focused posts")
    return posts

