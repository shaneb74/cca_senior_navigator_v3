Guided Care Plan & Cost Planner Refactor Overview

Goal – Align both products around the same layered architecture so we can keep JSON-driven assessments, plug in new question sets/weights quickly, and reuse orchestration/persistence logic without Streamlit‐specific hacks. No behavior change; this is a structural refactor.
1. New Layered Topology

Product Shell (Streamlit) → loads module manifest, orchestrates UI containers, but delegates all business logic.
Module Service (Python class, e.g., GCPService / CostPlannerService) → consumes JSON spec, owns deterministic scoring, flag computation, LLM/blending policies, and exposes typed results.
Contracts → shared dataclasses + JSON schema (e.g., CareRecommendation, FinancialProfile) used by both the service and MCIP.
Persistence & Events → services emit events (gcp.careplan.ready, cost.financial_profile.ready). Dedicated listeners handle snapshots, MCIP publication, journey updates. UI layer just listens for completion.
2. Guided Care Plan Changes

Keep module.json and intro override files; config.py continues to convert sections → steps.
Move scoring + LLM adjudication from logic.py into a service with explicit methods: calculate_deterministic, blend_with_llm, publish_recommendation.
Wrap Streamlit session accesses in a typed state manager so downstream code reads GCPState.final_tier instead of poking st.session_state.
Replace direct file writes inside _publish_to_mcip() with a gcp.careplan.ready event handled by user_persist.
Document the full CareRecommendation schema (all 15 fields) and reuse it everywhere.
3. Cost Planner Parallel Refactor

Each assessment (income, assets, etc.) remains JSON configurable; the assessment engine keeps rendering fields from those files.
Introduce CostPlannerService that loads the JSON configs, calculates totals, and produces a FinancialProfile contract.
Move persistence/MCIP publishing behind events just like GCP, so Cost Planner no longer touches session state directly.
Share helper utilities (state manager, contract schema package, event bus patterns) across both products.
4. Benefits

Consistency – Both products follow the same manifest → service → contract pipeline, simplifying onboarding and shared tooling.
Config agility – Product teams can tweak question copy, flags, or weights entirely in JSON without tracing Streamlit code paths.
Testing – Deterministic scoring/LLM blending lives in pure Python services, so unit tests don’t need Streamlit runners.
Observability – Events capture when a plan/profile becomes ready, making it easier to log, replay, or trigger downstream workflows.
Risk reduction – Typed contracts prevent drift; any consumer of CareRecommendation or FinancialProfile speaks the same schema.
5. Non‑Goals

No UI redesign, no new LLM behaviors, no performance tuning—this is a refactor, not an optimization.
JSON assessment files remain the source of truth; we’re not baking logic into code.
6. Next Steps

Define shared contract module (care_contracts.py) with dataclasses + JSON schema tests.
Implement GCPService and migrate logic.py responsibilities into it; wire events for persistence/MCIP.
Introduce GCPStateManager to wrap session interactions and update Streamlit code paths to use it.
Mirror the pattern for Cost Planner (service + event publishing) while leaving assessment JSON untouched.
Update docs/runbooks to describe the new architecture and make sure integration points (PFMA, hub tiles) read from the contracts, not raw session state.