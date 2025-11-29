from data_extraction_service import CrisisMonitor, ClaimBot, GeminiVerifier

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------
GEMINI_KEY = "AIzaSyBztKSScq_lR8ULb2TUI_B9YGgNazIxfgo"

# Initialize objects
crisis_monitor = CrisisMonitor(gemini_api_key=GEMINI_KEY)
claim_bot = ClaimBot(model="gpt-oss:20b-cloud")
verifier = GeminiVerifier(api_key=GEMINI_KEY)

# ---------------------------------------------------
# 1. Extract Crisis Keywords
# ---------------------------------------------------
print("\nExtracting global crisis keywords...")
keywords = crisis_monitor.extract_crisis_keywords(
    "What major crises are happening right now worldwide?"
)
print("Keywords:", keywords)

# ---------------------------------------------------
# 2. Scrape Reddit + Telegram
# ---------------------------------------------------
print("\nScraping social media...")
all_data = crisis_monitor.complete_pipeline(
    output_csv="raw_scraped_data.csv",
    max_posts_per_keyword=10
)

# Convert DF to list of dict
records = all_data.to_dict(orient="records")

# ---------------------------------------------------
# 3. Group Posts by Keyword → Produce clusters
# ---------------------------------------------------
print("\nGrouping posts...")
grouped = crisis_monitor.group_by_keyword(records)

print("\nClustering content...")
clusters = crisis_monitor.cluster_all_keywords(grouped)

# ---------------------------------------------------
# 4. Extract Claims per Cluster
# ---------------------------------------------------
print("\nExtracting claims from clusters...")

claim_results = {}

for keyword, keyword_clusters in clusters.items():
    claim_results[keyword] = []

    for cl in keyword_clusters:
        cluster_id = cl["cluster_id"]
        docs = cl["docs"]

        if not docs:
            continue

        claims = claim_bot.extract_claims(
            keyword=keyword,
            cluster_id=cluster_id,
            docs=docs,
            num_claims=5
        )

        claim_results[keyword].append({
            "cluster_id": cluster_id,
            "claims_raw": claims
        })

print("\nFinished extracting claims.")

# ---------------------------------------------------
# 5. Convert Claims to Clean List → Verify with Gemini
# ---------------------------------------------------
print("\nCleaning and verifying claims...")

clean_claims_by_keyword = {}

for keyword, cluster_list in claim_results.items():
    clean_claims_by_keyword[keyword] = []

    for cluster_entry in cluster_list:
        raw_block = cluster_entry["claims_raw"]
        
        # Extract numbered list lines
        lines = raw_block.split("\n")
        for line in lines:
            if line.strip().startswith(tuple([f"{i}." for i in range(1, 11)])):
                claim_text = line.split(".", 1)[1].strip()
                clean_claims_by_keyword[keyword].append(claim_text)

verified = crisis_monitor.verify_claims_with_gemini(
    clean_claims_by_keyword,
    gemini_api_key=GEMINI_KEY
)

print("\n=== FINAL VERIFIED CLAIM RESULTS ===")
print(verified)
