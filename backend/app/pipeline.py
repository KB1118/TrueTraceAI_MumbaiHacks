"""
Full agentic pipeline for TrueTrace Radar using LangChain and Gemini.
"""
import asyncio
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Crisis, RumorCluster, Claim, ResultCard
from app.llm import (
    detect_crises,
    expand_keywords,
    generate_canonical_claim,
    retrieve_evidence,
    verify_claim,
    generate_result_card,
    perform_topic_modeling
)
from app.twitter_generator import generate_twitter_stream, generate_keyword_focused_posts
from app.config import settings


logger = logging.getLogger("truetrace.pipeline")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )


async def collect_social_posts(keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Collect posts from social media platforms using keywords.
    Uses LLM-generated fake Twitter stream for testing.
    In production, this would integrate with Twitter/X API, Reddit API, etc.
    """
    logger.info("Collecting social posts with %s keywords using LLM-generated fake stream", len(keywords))
    
    # Generate a mix of casual and crisis posts
    # Use keyword-focused generation for better relevance
    posts = await generate_keyword_focused_posts(
        keywords=keywords,
        posts_per_keyword=15  # Generate 15 posts per keyword
    )
    
    # Also add some general stream posts for variety
    stream_posts = await generate_twitter_stream(
        keywords=keywords,
        num_posts=30,  # Additional general posts
        category_weights={"casual": 0.4, "crisis": 0.6}  # Slightly more crisis-focused
    )
    
    # Combine and return
    all_posts = posts + stream_posts
    logger.info("Collected %s LLM-generated posts (mix of casual and crisis topics)", len(all_posts))
    return all_posts


async def semantic_deduplication(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply semantic deduplication to remove similar posts.
    Simplified implementation - in production, use embeddings and similarity thresholds.
    """
    # Simple deduplication by text similarity (basic)
    logger.info("Running semantic deduplication on %s posts", len(posts))
    seen_texts = set()
    unique_posts = []
    for post in posts:
        text_key = post["text"][:100]  # Use first 100 chars as key
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            unique_posts.append(post)
    logger.info("Deduplicated posts down to %s unique entries", len(unique_posts))
    return unique_posts


async def run_radar_pipeline(db: Session) -> Dict[str, Any]:
    """
    Run the complete TrueTrace Radar pipeline:
    1. Detect crises
    2. Extract and expand keywords
    3. Collect social posts
    4. Deduplicate and filter
    5. Topic modeling/clustering
    6. Generate canonical claims
    7. Retrieve evidence
    8. Verify claims
    9. Generate result cards
    """
    results = {
        "crises_detected": 0,
        "clusters_created": 0,
        "claims_verified": 0,
        "errors": []
    }
    
    logger.info("=== TrueTrace Radar pipeline started ===")
    try:
        # Step 1: Detect crises
        logger.info("Step 1: Detecting crises")
        crises_data = await detect_crises()
        results["crises_detected"] = len(crises_data)
        logger.info("Detected %s crises", len(crises_data))
        
        for crisis_data in crises_data:
            logger.info("Processing crisis: %s", crisis_data["title"])
            # Create or get crisis in database
            crisis = db.query(Crisis).filter(
                Crisis.title == crisis_data["title"]
            ).first()
            
            if not crisis:
                crisis = Crisis(
                    title=crisis_data["title"],
                    description=crisis_data.get("description"),
                    keywords=crisis_data.get("keywords", []),
                    status="active"
                )
                db.add(crisis)
                db.commit()
                db.refresh(crisis)
            
            # Step 2: Expand keywords
            keywords = crisis_data.get("keywords", [])
            logger.info("Step 2: Expanding %s keywords", len(keywords))
            expanded_keywords = await expand_keywords(keywords)
            all_keywords = list(set(keywords + expanded_keywords))
            logger.info("Expanded keyword set size: %s", len(all_keywords))
            
            # Step 3: Collect social posts
            logger.info("Step 3: Collecting social posts")
            posts = await collect_social_posts(all_keywords)
            
            # Step 4: Deduplicate
            logger.info("Step 4: Deduplicating %s posts", len(posts))
            unique_posts = await semantic_deduplication(posts)
            
            if len(unique_posts) < settings.CLUSTERING_MIN_SIZE:
                continue
            
            # Step 5: Topic modeling
            post_texts = [p["text"] for p in unique_posts]
            logger.info("Step 5: Performing topic modeling on %s posts", len(post_texts))
            clusters_data = await perform_topic_modeling(post_texts)
            logger.info("Identified %s clusters", len(clusters_data))
            
            for cluster_data in clusters_data:
                # Create cluster
                post_indices = cluster_data.get("post_indices", [])
                cluster_posts = [unique_posts[i] for i in post_indices if i < len(unique_posts)]
                
                if len(cluster_posts) < settings.CLUSTERING_MIN_SIZE:
                    continue
                
                cluster = RumorCluster(
                    crisis_id=crisis.id,
                    topic_label=cluster_data.get("topic_label", "Unnamed Cluster"),
                    post_ids=[p["id"] for p in cluster_posts]
                )
                db.add(cluster)
                db.commit()
                db.refresh(cluster)
                results["clusters_created"] += 1
                logger.info(
                    "Created cluster %s (id=%s) with %s posts",
                    cluster.topic_label,
                    cluster.id,
                    len(cluster_posts)
                )
                
                # Step 6: Generate canonical claim
                cluster_texts = [p["text"] for p in cluster_posts]
                logger.info("Step 6: Generating canonical claim for cluster %s", cluster.id)
                canonical_claim_text = await generate_canonical_claim(cluster_texts)
                
                # Step 7: Retrieve evidence
                logger.info("Step 7: Retrieving evidence")
                evidence = await retrieve_evidence(canonical_claim_text)
                
                # Step 8: Verify claim
                logger.info("Step 8: Verifying claim via LLM/NLI")
                verification_result = await verify_claim(canonical_claim_text, evidence)
                
                # Create claim record
                claim = Claim(
                    cluster_id=cluster.id,
                    text=canonical_claim_text,
                    verdict=verification_result.get("verdict", "Uncertain"),
                    confidence_score=verification_result.get("confidence_score", 0.5),
                    volatility_score=verification_result.get("volatility_score", 0.5),
                    reasoning=verification_result.get("reasoning", ""),
                    evidence_citations=verification_result.get("evidence_citations", [])
                )
                db.add(claim)
                db.commit()
                db.refresh(claim)
                results["claims_verified"] += 1
                logger.info(
                    "Verified claim %s (verdict=%s, confidence=%.2f)",
                    claim.id,
                    claim.verdict,
                    claim.confidence_score or 0.0
                )
                
                # Step 9: Generate result cards for different audiences
                logger.info("Step 9: Generating result cards for claim %s", claim.id)
                for audience_type in ["general", "journalist", "researcher"]:
                    card_data = await generate_result_card(
                        claim=canonical_claim_text,
                        verdict=verification_result.get("verdict", "Uncertain"),
                        reasoning=verification_result.get("reasoning", ""),
                        evidence=verification_result.get("evidence_citations", []),
                        audience_type=audience_type
                    )
                    
                    card = ResultCard(
                        claim_id=claim.id,
                        audience_type=audience_type,
                        title=card_data.get("title", "Fact Check Result"),
                        content=card_data.get("explanation", ""),
                        formatted_data=card_data
                    )
                    db.add(card)
                
                db.commit()
        
        logger.info(
            "Pipeline completed. Crises: %s, Clusters: %s, Claims: %s",
            results["crises_detected"],
            results["clusters_created"],
            results["claims_verified"]
        )
        return results
        
    except Exception as e:
        logger.exception("Pipeline run failed: %s", e)
        results["errors"].append(str(e))
        db.rollback()
        return results

