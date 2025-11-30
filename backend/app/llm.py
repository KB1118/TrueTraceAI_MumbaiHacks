"""
LLM integration using Gemini 2.5 Flash and LangChain.
"""
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict, Any, Optional
from app.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    """Get configured Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True,
    )


async def detect_crises() -> List[Dict[str, Any]]:
    """Detect ongoing global crises from news signals."""
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a crisis detection expert. Analyze recent global events and identify ongoing crises that may generate misinformation. Return a JSON list of crises with title, description, and keywords."),
        ("human", "Identify the top 3-5 ongoing global crises that are likely generating misinformation. For each, provide: title, description, and 5-10 relevant keywords.")
    ])
    
    chain = prompt | llm
    response = await chain.ainvoke({})
    
    # Parse response (simplified - in production, use structured output)
    # For now, return mock data structure
    return [
        {
            "title": "Global Health Emergency",
            "description": "Ongoing health crisis generating widespread discussion",
            "keywords": ["health", "emergency", "pandemic", "vaccine", "outbreak"]
        }
    ]


async def expand_keywords(keywords: List[str]) -> List[str]:
    """Expand keywords using semantic embeddings."""
    llm = get_llm()
    
    prompt = f"Given these keywords: {', '.join(keywords)}, generate 10-15 semantically related keywords and phrases that would help find relevant social media posts. Return only a comma-separated list."
    
    response = await llm.ainvoke(prompt)
    expanded = response.content.split(",")
    return [k.strip() for k in expanded if k.strip()]


async def generate_canonical_claim(posts: List[str]) -> str:
    """Convert a cluster of posts into one canonical, fact-checkable claim."""
    llm = get_llm()
    
    posts_text = "\n".join([f"- {post[:200]}" for post in posts[:10]])
    
    prompt = f"""Analyze these social media posts and extract the core factual claim being made. 
Write a single, clear, objective claim that can be fact-checked.

Posts:
{posts_text}

Return only the canonical claim, nothing else."""
    
    response = await llm.ainvoke(prompt)
    return response.content.strip()


async def retrieve_evidence(claim: str) -> List[Dict[str, str]]:
    """Retrieve evidence from authoritative sources."""
    # In production, this would use web search APIs, news APIs, etc.
    # For now, return mock evidence structure
    return [
        {
            "url": "https://example.com/authority-source-1",
            "title": "Official Statement on Claim",
            "snippet": "Relevant evidence snippet..."
        }
    ]


async def verify_claim(claim: str, evidence: List[Dict[str, str]]) -> Dict[str, Any]:
    """Use NLI + LLM reasoning to determine verdict."""
    llm = get_llm()
    
    evidence_text = "\n".join([f"- {e['title']}: {e['snippet']}" for e in evidence])
    
    prompt = f"""You are a fact-checking expert. Analyze this claim against the provided evidence and determine a verdict.

Claim: {claim}

Evidence:
{evidence_text}

Provide your analysis in the following JSON format:
{{
    "verdict": "True" | "False" | "Misleading" | "Uncertain",
    "confidence_score": 0.0-1.0,
    "volatility_score": 0.0-1.0,
    "reasoning": "Detailed explanation of your verdict",
    "evidence_citations": ["url1", "url2"]
}}"""
    
    response = await llm.ainvoke(prompt)
    
    # Parse JSON response (simplified - in production use structured output)
    # For now, return structured response
    import json
    try:
        result = json.loads(response.content)
    except:
        result = {
            "verdict": "Uncertain",
            "confidence_score": 0.5,
            "volatility_score": 0.7,
            "reasoning": response.content,
            "evidence_citations": [e["url"] for e in evidence]
        }
    
    return result


async def generate_result_card(
    claim: str,
    verdict: str,
    reasoning: str,
    evidence: List[str],
    audience_type: str = "general"
) -> Dict[str, Any]:
    """Generate formatted result card for specific audience."""
    llm = get_llm()
    
    audience_prompts = {
        "general": "Write for the general public - clear, concise, accessible language.",
        "journalist": "Write for journalists - include source attribution, context, and verification details.",
        "researcher": "Write for researchers - include methodology, confidence intervals, and detailed analysis."
    }
    
    prompt = f"""Generate a fact-check result card for {audience_type} audience.

Claim: {claim}
Verdict: {verdict}
Reasoning: {reasoning}
Evidence: {', '.join(evidence)}

Audience: {audience_prompts.get(audience_type, audience_prompts['general'])}

Return a JSON object with:
{{
    "title": "Card title",
    "summary": "Brief summary",
    "verdict": "{verdict}",
    "explanation": "Detailed explanation",
    "sources": ["url1", "url2"],
    "timestamp": "ISO timestamp"
}}"""
    
    response = await llm.ainvoke(prompt)
    
    import json
    try:
        card = json.loads(response.content)
    except:
        card = {
            "title": f"Fact Check: {claim[:50]}...",
            "summary": reasoning[:200],
            "verdict": verdict,
            "explanation": reasoning,
            "sources": evidence,
            "timestamp": datetime.now().isoformat()
        }
    
    return card


async def perform_topic_modeling(posts: List[str]) -> List[Dict[str, Any]]:
    """Perform topic modeling to identify rumor clusters."""
    llm = get_llm()
    
    posts_text = "\n".join([f"{i+1}. {post[:150]}" for i, post in enumerate(posts[:50])])
    
    prompt = f"""Analyze these social media posts and group them into topic clusters based on similar claims or themes.

Posts:
{posts_text}

Return a JSON array of clusters, each with:
{{
    "topic_label": "Brief topic description",
    "post_indices": [1, 3, 5]
}}"""
    
    response = await llm.ainvoke(prompt)
    
    import json
    try:
        clusters = json.loads(response.content)
    except:
        # Fallback: create single cluster
        clusters = [{"topic_label": "General Discussion", "post_indices": list(range(len(posts)))}]
    
    return clusters

