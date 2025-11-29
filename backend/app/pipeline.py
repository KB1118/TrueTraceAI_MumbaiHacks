"""
Full agentic pipeline for TrueTrace Radar using Gemini-powered
data extraction utilities.
"""
import asyncio
import logging
import re
from collections import defaultdict
from typing import Dict, Any, List, Tuple

from sqlalchemy.orm import Session

from app.models import Crisis, RumorCluster, Claim, ResultCard
from app.llm import generate_result_card
from app.config import settings
from app.services.data_extraction_service import CrisisMonitor, ClaimBot


logger = logging.getLogger("truetrace.pipeline")
if not logger.handlers:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
logger.setLevel(logging.DEBUG)


VERDICT_MAPPING = {
    "supports": "True",
    "contradicts": "False",
    "unrelated": "Uncertain"
}

CONFIDENCE_MAPPING = {
    "supports": 0.85,
    "contradicts": 0.8,
    "unrelated": 0.45
}

VOLATILITY_MAPPING = {
    "supports": 0.35,
    "contradicts": 0.5,
    "unrelated": 0.6
}


def _parse_numbered_claims(raw_block: str) -> List[str]:
    """Extract numbered claims (1., 2., etc.) from ClaimBot output."""
    claims: List[str] = []
    if not raw_block:
        return claims
    
    for line in raw_block.splitlines():
        stripped = line.strip()
        match = re.match(r"^(\d+)[\).\s-]+(.+)", stripped)
        if match:
            claim_text = match.group(2).strip()
            if claim_text:
                claims.append(claim_text)
    return claims


def _build_reasoning(keyword: str, verdict_raw: str) -> str:
    """Create a short reasoning string for storage and cards."""
    if not verdict_raw:
        return f"Gemini web search could not confidently classify the claim about {keyword}."
    return f"Gemini web search judged this {keyword} claim as '{verdict_raw}'."


async def _run_sync(func, *args, **kwargs):
    """Run blocking functions in a thread to avoid blocking the event loop."""
    return await asyncio.to_thread(func, *args, **kwargs)


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
    
    logger.info("=== TrueTrace Radar pipeline (Gemini data extraction) started ===")
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required to run the data extraction pipeline.")
    
    try:
        crisis_monitor = CrisisMonitor(
            gemini_api_key=settings.GEMINI_API_KEY,
            embed_model_name=settings.SENTENCE_TRANSFORMER_MODEL,
            max_clusters=settings.MAX_PIPELINE_CLUSTERS
        )
    except Exception as exc:
        logger.exception("Failed to initialize CrisisMonitor: %s", exc)
        results["errors"].append(str(exc))
        return results
    
    try:
        claim_bot = ClaimBot(model=settings.OLLAMA_MODEL or "gpt-oss:20b-cloud")
    except Exception as exc:
        logger.exception("Failed to initialize ClaimBot (ensure Ollama client is installed): %s", exc)
        results["errors"].append(str(exc))
        return results
    
    try:
        # Step 1: extract crisis keywords
        logger.info("Step 1: Extracting crisis keywords with Gemini search")
        keywords = await _run_sync(
            crisis_monitor.extract_crisis_keywords,
            settings.CRISIS_KEYWORD_QUERY
        )
        if not keywords:
            logger.warning("No crisis keywords returned by Gemini.")
            return results
        results["crises_detected"] = len(keywords)
        logger.info("Gemini produced %s crisis keywords", len(keywords))
        
        # Step 2: discover sources
        logger.info("Step 2: Discovering relevant Reddit subreddits")
        subreddits = await _run_sync(
            crisis_monitor.discover_relevant_subreddits,
            keywords,
            settings.REDDIT_SUBREDDIT_LIMIT
        )
        logger.info("Auto-selected %s Reddit subreddits", len(subreddits))
        
        logger.info("Step 3: Discovering Telegram channels")
        channels = await _run_sync(crisis_monitor.discover_telegram_channels)
        channel_slice = channels[:settings.TELEGRAM_CHANNEL_LIMIT]
        logger.info("Using %s Telegram channels", len(channel_slice))
        
        keywords_for_scrape = keywords[:settings.SCRAPE_KEYWORD_LIMIT]
        if not keywords_for_scrape:
            keywords_for_scrape = keywords
        
        # Step 4: scrape Reddit & Telegram
        logger.info(
            "Step 4: Scraping Reddit for %s keywords across %s subreddits",
            len(keywords_for_scrape),
            len(subreddits)
        )
        df_reddit = await _run_sync(
            crisis_monitor.scrape_reddit_for_keywords,
            keywords_for_scrape,
            subreddits,
            settings.REDDIT_POST_LIMIT
        )
        
        logger.info(
            "Step 5: Scraping Telegram for %s keywords across %s channels",
            len(keywords_for_scrape),
            len(channel_slice)
        )
        df_telegram = await _run_sync(
            crisis_monitor.scrape_telegram_for_keywords,
            keywords_for_scrape,
            channel_slice,
            settings.TELEGRAM_POST_LIMIT
        )
        
        records: List[Dict[str, Any]] = []
        for df in (df_reddit, df_telegram):
            if df is not None and not df.empty:
                records.extend(df.to_dict(orient="records"))
        
        if not records:
            logger.warning("Scrapers returned no data. Aborting pipeline run.")
            return results
        
        # Deduplicate by URL
        seen_urls = set()
        unique_records: List[Dict[str, Any]] = []
        for rec in records:
            url = rec.get("url")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            unique_records.append(rec)
        
        logger.info("Collected %s unique social posts.", len(unique_records))
        
        # Step 6: group + cluster
        logger.info("Step 6: Grouping posts by keyword")
        grouped = await _run_sync(crisis_monitor.group_by_keyword, unique_records)
        logger.info("Grouping produced %s keyword buckets", len(grouped))
        
        logger.info("Step 7: Clustering posts per keyword")
        clusters_by_keyword = await _run_sync(crisis_monitor.cluster_all_keywords, grouped)
        
        clean_claims_by_keyword: Dict[str, List[str]] = defaultdict(list)
        claim_records: List[Tuple[str, int, str]] = []
        
        for keyword, keyword_clusters in clusters_by_keyword.items():
            if keyword == "NO_KEYWORD":
                continue
            
            crisis = db.query(Crisis).filter(Crisis.title == keyword).first()
            if not crisis:
                crisis = Crisis(
                    title=keyword,
                    description=f"Auto-detected crisis keyword '{keyword}' from Gemini web search.",
                    keywords=[keyword],
                    status="active",
                    crisis_metadata={"source": "Gemini WebSearch"}
                )
                db.add(crisis)
                db.commit()
                db.refresh(crisis)
            
            for cluster_info in keyword_clusters:
                docs = cluster_info.get("docs", [])
                if len(docs) < settings.CLUSTERING_MIN_SIZE:
                    continue
                
                topic_label = docs[0].get("title") or docs[0].get("selftext", "")[:80] or f"{keyword} Cluster {cluster_info['cluster_id']}"
                post_ids = [doc.get("url") for doc in docs if doc.get("url")]
                
                cluster = RumorCluster(
                    crisis_id=crisis.id,
                    topic_label=topic_label,
                    post_ids=post_ids
                )
                db.add(cluster)
                db.commit()
                db.refresh(cluster)
                results["clusters_created"] += 1
                
                raw_claim_text = await _run_sync(
                    claim_bot.extract_claims,
                    keyword,
                    cluster_info["cluster_id"],
                    docs,
                    settings.CLAIMS_PER_CLUSTER
                )
                parsed_claims = _parse_numbered_claims(raw_claim_text)
                for claim_text in parsed_claims:
                    clean_claims_by_keyword[keyword].append(claim_text)
                    claim_records.append((keyword, cluster.id, claim_text))
        
        if not claim_records:
            logger.warning("ClaimBot did not return any claims; skipping verification.")
            return results
        
        # ------------------------------------------------------------------
        # STEP 8: VERIFICATION – EXTREMELY VERBOSE DEBUG LOGGING
        # ------------------------------------------------------------------
        logger.info("Step 8: Verifying %s claims with Gemini web search", len(claim_records))
        logger.debug("Step 8 - Raw clean_claims_by_keyword structure:")
        for kw, claims in clean_claims_by_keyword.items():
            logger.debug("  Keyword '%s' has %d cleaned claims:", kw, len(claims))
            for idx, c in enumerate(claims, start=1):
                logger.debug("    [%s] %s", idx, c)

        verification_payload = {k: v for k, v in clean_claims_by_keyword.items() if v}
        logger.debug("Step 8 - Verification payload being sent to GeminiVerifier (per keyword counts only):")
        for kw, claims in verification_payload.items():
            logger.debug("  Keyword '%s' => %d claims to verify", kw, len(claims))

        verification_results = await _run_sync(
            crisis_monitor.verify_claims_with_gemini,
            verification_payload,
            settings.GEMINI_API_KEY
        )
        
        verdict_lookup: Dict[Tuple[str, str], str] = {}
        for keyword, verdict_entries in verification_results.items():
            logger.debug("Step 8 - Raw verification results for keyword '%s': %s", keyword, verdict_entries)
            for entry in verdict_entries:
                normalized = entry.get("claim", "").strip().lower()
                if not normalized:
                    continue
                verdict_value = entry.get("verdict", "unrelated")
                verdict_lookup[(keyword, normalized)] = verdict_value
                logger.debug(
                    "Step 8 - Mapping verification result: keyword='%s', claim='%s', verdict_raw='%s'",
                    keyword,
                    normalized,
                    verdict_value,
                )
        
        # ------------------------------------------------------------------
        # STEP 9: PERSISTENCE – EXTREMELY VERBOSE DEBUG LOGGING
        # ------------------------------------------------------------------
        logger.info("Step 9: Persisting claims and result cards")
        logger.debug("Step 9 - Total claim_records to persist: %d", len(claim_records))
        for keyword, cluster_id, claim_text in claim_records:
            normalized = claim_text.strip()
            if not normalized:
                continue
            verdict_raw = verdict_lookup.get((keyword, normalized.lower()), "unrelated")
            verdict = VERDICT_MAPPING.get(verdict_raw, "Uncertain")
            confidence = CONFIDENCE_MAPPING.get(verdict_raw, 0.5)
            volatility = VOLATILITY_MAPPING.get(verdict_raw, 0.6)
            reasoning = _build_reasoning(keyword, verdict_raw)
            logger.debug(
                "Step 9 - Preparing Claim object:\n"
                "  keyword      = %s\n"
                "  cluster_id   = %s\n"
                "  raw_text     = %s\n"
                "  normalized   = %s\n"
                "  verdict_raw  = 
                %s\n"
                "  verdict_mapped = %s\n"
                "  confidence   = %.3f\n"
                "  volatility   = %.3f\n"
                "  reasoning    = %s",
                keyword,
                cluster_id,
                claim_text,
                normalized,
                verdict_raw,
                verdict,
                confidence,
                volatility,
                reasoning,
            )
            
            claim = Claim(
                cluster_id=cluster_id,
                text=normalized,
                verdict=verdict,
                confidence_score=confidence,
                volatility_score=volatility,
                reasoning=reasoning,
                evidence_citations=[]
            )
            db.add(claim)
            db.commit()
            db.refresh(claim)
            logger.debug(
                "Step 9 - Persisted Claim row: id=%s, crisis_keyword=%s, cluster_id=%s, verdict=%s, confidence=%.3f, volatility=%.3f",
                claim.id,
                keyword,
                cluster_id,
                claim.verdict,
                claim.confidence_score or 0.0,
                claim.volatility_score or 0.0,
            )
            results["claims_verified"] += 1
            
            for audience_type in ["general", "journalist", "researcher"]:
                card_data = await generate_result_card(
                    claim=normalized,
                    verdict=verdict,
                    reasoning=reasoning,
                    evidence=[],
                    audience_type=audience_type
                )
                logger.debug(
                    "Step 9 - Generated result card data for audience '%s': %s",
                    audience_type,
                    card_data,
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
            logger.debug(
                "Step 9 - All result cards committed for claim_id=%s (audiences: general, journalist, researcher)",
                claim.id,
            )
        
        logger.info(
            "Pipeline complete. Keywords: %s, Clusters: %s, Claims: %s",
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

