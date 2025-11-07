Fix Plan

pages/faq.py (line 74), pages/faq.py (line 96), pages/faq.py (line 114), pages/faq.py (line 147), pages/faq.py (line 346)

Introduce cache-busting inputs (e.g., file mtime or hash) to every @st.cache_data loader so updating config/faq*.json or config/corp_mini_faq.json automatically invalidates cached answers/policy/recos/easter eggs/mini FAQ.
Expose a lightweight “Reload FAQ config” admin control (or CLI task) that calls the cache-clearing helper Streamlit provides (st.cache_data.clear()) as a manual fallback.
pages/faq.py (lines 239-267)

Split TF-IDF vectorizer building from query-time retrieval: cache the fitted vectorizer + matrix keyed off the FAQ corpus mtime via @st.cache_resource, and have retrieve_faq() depend on that cached object so each query does only a .transform plus cosine similarity.
Add a guard that short-circuits when the corpus is empty to avoid useless cache entries for each query string.
pages/faq.py (lines 274-324) and pages/faq.py (lines 370-393)

Track both config/corp_index.pkl and config/corp_knowledge.jsonl modification times; include whichever actually feeds the chunks in the cache key so publishing a new prebuilt index is respected without restarting Streamlit.
When a prebuilt index is present, surface its metadata (built timestamp, version) for logging/telemetry so stale loads are obvious.
pages/faq.py (lines 370-410)

When config/corp_index.pkl exists, verify that the embedded chunk list matches the currently requested corpus (e.g., compare hash/length, or rehydrate chunks from callers if different). If it differs, rebuild the vectorizer with the provided chunks so similarity scores align with what was loaded.
Add error handling/logging that explicitly states when the pickle is stale or mismatched, prompting the sync process to regenerate it.