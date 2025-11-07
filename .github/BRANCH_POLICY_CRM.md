Perfect — here’s **the exact, copy-ready content** for your first file:
✅ **`.github/BRANCH_POLICY_CRM.md`**

---

````markdown
# 🔒 CCACRM Branch & Protection Policy

> Defines precise branch protection, merge paths, and developer workflow.  
> **Copilot:** interpret these declaratively and apply them to GitHub branch settings.

---

## 1️⃣ Senior Navigator Branch Rules

| Branch | Protection | Rules |
|---------|-------------|-------|
| `main` | ✅ | PR + review + status checks + no force push |
| `dev` | ✅ | PR + review + status checks + no force push |
| `apzumi` | ✅ | PR + review + no force push |

**Copilot YAML Equivalent:**
```yaml
branches:
  - name: main
    protection:
      required_pull_request_reviews: { required_approving_review_count: 1 }
      required_status_checks: { strict: true }
      required_linear_history: true
      allow_force_pushes: false
      allow_deletions: false
  - name: dev
    protection:
      required_pull_request_reviews: { required_approving_review_count: 1 }
      required_status_checks: { strict: true }
      required_linear_history: true
      allow_force_pushes: false
      allow_deletions: false
  - name: apzumi
    protection:
      required_pull_request_reviews: { required_approving_review_count: 1 }
      required_linear_history: true
      allow_force_pushes: false
      allow_deletions: false
````

---

## 2️⃣ CRM Branch Hierarchy

| Branch           | Role             | Protection | Merge Target       | Description                    |
| ---------------- | ---------------- | ---------- | ------------------ | ------------------------------ |
| `cca_crm`        | Sandbox          | ❌          | → `cca_crm_dev`    | Free-form experimental work    |
| `cca_crm_dev`    | Integration / QA | ✅          | → `cca_crm_demo`   | Controlled merges from sandbox |
| `cca_crm_demo`   | Demo / staging   | ✅          | → `cca_crm_stable` | Used for demos and reviews     |
| `cca_crm_stable` | Release snapshot | ✅          | → `dev` (manual)   | Final tested CRM build         |

**Copilot YAML Equivalent:**

```yaml
branches:
  - name: cca_crm_dev
    protection:
      required_pull_request_reviews: { required_approving_review_count: 1 }
      required_linear_history: true
      allow_force_pushes: false
  - name: cca_crm_demo
    protection:
      required_pull_request_reviews: { required_approving_review_count: 1 }
      required_linear_history: true
      allow_force_pushes: false
  - name: cca_crm_stable
    protection:
      required_pull_request_reviews: { required_approving_review_count: 1 }
      required_linear_history: true
      allow_force_pushes: false
```

---

## 3️⃣ Merge-Path Rules

**Copilot**, enforce this directed graph:

```text
feature/*        → dev
bugfix/*         → dev
cca_crm          → cca_crm_dev
cca_crm_dev      → cca_crm_demo
cca_crm_demo     → cca_crm_stable
cca_crm_stable   → dev (optional, after QA)
dev              → main
```

* ❌ No direct merges between `cca_crm*` and `main` or `apzumi`
* ✅ All merges occur through Pull Requests with at least one approval

---

## 4️⃣ Developer Workflow Summary

| Action                 | Command                                     | Target             |
| ---------------------- | ------------------------------------------- | ------------------ |
| Work on CRM            | `git checkout cca_crm`                      | local sandbox      |
| Promote to integration | PR → `cca_crm_dev`                          | test               |
| Promote to demo        | PR → `cca_crm_demo`                         | stakeholder review |
| Promote to stable      | PR → `cca_crm_stable`                       | ready for merge    |
| Sync Navigator updates | `git fetch origin && git rebase origin/dev` | keep CRM current   |

---

## 5️⃣ Rollback Strategy

* Reset sandbox to last good state:

  ```bash
  git checkout cca_crm
  git reset --hard origin/cca_crm_dev
  ```

* Reset demo to last stable snapshot:

  ```bash
  git checkout cca_crm_demo
  git reset --hard origin/cca_crm_stable
  ```

---

## 6️⃣ Cross-Contamination Guardrails

* Never merge any `cca_crm*` branch directly into `main`, `dev`, or `apzumi`.
* Use Pull Requests exclusively.
* Keep Navigator and CRM Streamlit apps on separate ports (e.g., 8501 vs 8502).

---

## ✅ Copilot Summary Instruction

> **Copilot:**
>
> * Enforce all branch protection and merge rules defined in this document.
> * Create missing branches under the `cca_crm*` namespace.
> * Apply PR review and linear-history requirements to protected branches.
> * Keep `cca_crm` unprotected.
> * Confirm configuration once complete.

---

```


