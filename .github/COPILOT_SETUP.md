Perfect 👍 — here’s the **exact content** for your second file:
✅ **`.github/COPILOT_SETUP.md`**

---

```markdown
# 🤖 Copilot Repository Setup Instructions

> **Goal:**  
> Configure safe branch protections and multi-stage workflows for both the **Senior Navigator** app and the new **Advisor CRM** app.

---

## 🚦 Step 1 – General Protection Rules

**Copilot, apply the following rules on GitHub:**

- Protect branches: `main`, `dev`, and `apzumi`
- Require:
  - Pull Request reviews (≥ 1 approval)
  - Status checks to pass
  - Linear history (no merge commits)
  - No force pushes
  - No deletions
- Keep `cca_crm` unprotected (sandbox only)

---

## 🧱 Step 2 – CRM Branch Hierarchy

**Copilot, create and manage these additional branches (if not already present):**

| Branch | Purpose | Protection | Notes |
|---------|----------|-------------|-------|
| `cca_crm` | Experimental sandbox | ❌ | You commit here freely |
| `cca_crm_dev` | Integration / QA | ✅ | Merge via PR only |
| `cca_crm_demo` | Demo / staging | ✅ | Used for stakeholder review |
| `cca_crm_stable` | Production-ready CRM snapshot | ✅ | Promoted from demo after approval |

All new branches should be created from the current `cca_crm` head.

---

## 🧩 Step 3 – Apply Detailed Policy

After branch creation, **apply all rules defined in**  
`.github/BRANCH_POLICY_CRM.md`.

These include:
- Merge direction restrictions  
- Developer workflow commands  
- Rollback strategies  
- Cross-contamination guardrails  

---

## 🧰 Step 4 – Optional Enhancements

**Copilot may additionally:**
- Add branch protection via GitHub REST API  
- Configure workflows to auto-sync `dev → cca_crm_dev`  
- Enforce Pull Request title conventions (e.g., “Feature:” or “Fix:”)  
- Validate that all CRM branches maintain linear history

---

## ✅ Step 5 – Confirmation & Output

After execution, Copilot should provide a confirmation report including:

1. ✅ List of all protected branches and their rules  
2. ✅ Confirmation that `cca_crm*` branches exist and follow policy  
3. ✅ Confirmation that PR review rules and merge paths are enforced  
4. ✅ A summary message:  
```

CRM branch hierarchy configured successfully.

````

---

## 🧩 Summary for Copilot

> **Copilot, perform these actions now:**
> 1. Read this `.github/COPILOT_SETUP.md` file.  
> 2. Create and protect branches per Step 2.  
> 3. Apply detailed policies from `.github/BRANCH_POLICY_CRM.md`.  
> 4. Confirm configuration with a summary output listing branch rules.

---

## 🧭 Developer Notes

Once setup is complete, developers can safely:

- Work freely in `cca_crm` without risk to production branches  
- Use Pull Requests to promote tested work upward (→ `cca_crm_dev`, → `cca_crm_demo`, → `cca_crm_stable`)  
- Merge into `dev` only after CRM features are stable and approved  

This setup ensures **CRM and Senior Navigator stay isolated** yet integrated within the same repository.

---

## 💡 How to Run This

After committing both setup files:

```bash
git add .github/COPILOT_SETUP.md .github/BRANCH_POLICY_CRM.md
git commit -m "Add Copilot branch protection setup for CRM"
git push origin cca_crm
````

Then, in **GitHub Copilot Chat** (inside VS Code or GitHub):

```
Apply the instructions in .github/COPILOT_SETUP.md
```

Copilot will create branches, apply protection rules, and confirm.

---

✅ **Result:**
Your repo now has a complete **multi-branch protection system** for both Senior Navigator and the new CRM — with full rollback, isolation, and promotion paths.

```