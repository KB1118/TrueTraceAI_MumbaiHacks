"""
Test script for the fake Twitter stream generator.
Run this to see sample generated posts before running the full pipeline.
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.twitter_generator import generate_twitter_stream, generate_keyword_focused_posts


async def test_generator():
    """Test the Twitter generator with sample keywords."""
    print("=" * 60)
    print("Testing Fake Twitter Stream Generator")
    print("=" * 60)
    
    # Sample keywords (crisis-related)
    keywords = ["health emergency", "outbreak", "vaccine", "pandemic", "crisis"]
    
    print(f"\n1. Generating keyword-focused posts for: {keywords[:3]}...")
    print("-" * 60)
    
    keyword_posts = await generate_keyword_focused_posts(
        keywords=keywords[:3],  # Test with first 3 keywords
        posts_per_keyword=5  # Small number for testing
    )
    
    print(f"\nGenerated {len(keyword_posts)} keyword-focused posts:\n")
    for i, post in enumerate(keyword_posts[:5], 1):  # Show first 5
        print(f"Post {i} ({post['category']}):")
        print(f"  Username: @{post['username']}")
        print(f"  Text: {post['text']}")
        print(f"  Timestamp: {post['timestamp']}")
        print()
    
    print("\n2. Generating general stream posts...")
    print("-" * 60)
    
    stream_posts = await generate_twitter_stream(
        keywords=keywords,
        num_posts=10,  # Small number for testing
        category_weights={"casual": 0.5, "crisis": 0.5}
    )
    
    print(f"\nGenerated {len(stream_posts)} stream posts:\n")
    for i, post in enumerate(stream_posts[:5], 1):  # Show first 5
        print(f"Post {i} ({post['category']}):")
        print(f"  Username: @{post['username']}")
        print(f"  Text: {post['text']}")
        print(f"  Timestamp: {post['timestamp']}")
        print()
    
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\nTo run the full pipeline with this generator:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Trigger the pipeline via POST /api/v1/pipeline/trigger")
    print("   (requires authentication)")


if __name__ == "__main__":
    # Check if GEMINI_API_KEY is set
    from app.config import settings
    if not settings.GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set in environment variables or .env file")
        print("Please set it before running this test.")
        sys.exit(1)
    
    asyncio.run(test_generator())

