# 🔒 Critical Documents Protection Index

> **PURPOSE:** Permanent archive of essential documents that must never be lost during cleanup activities.

---

## 🚨 **NEVER DELETE THESE FILES**

| Document | Location | Purpose | Protection Level |
|----------|----------|---------|------------------|
| **QUICKBASE_API_GUIDE.md** | `.github/docs/` | Complete QuickBase connection guide with credentials | 🔴 **CRITICAL** |
| **BRANCH_POLICY_CRM.md** | `.github/` | CRM branch protection rules | 🟡 **IMPORTANT** |
| **COPILOT_SETUP.md** | `.github/` | Repository setup instructions | 🟡 **IMPORTANT** |
| **BRANCH_SETUP_COMPLETE.md** | `.github/` | Branch hierarchy status | 🟡 **IMPORTANT** |

---

## 🛡️ **Protection Strategy**

### **Directory Safety Levels:**

1. **🔴 MAXIMUM PROTECTION:** `.github/docs/`
   - Never touched by cleanup scripts
   - Survives branch switches and merges
   - Safe from automated deletions
   - Perfect for credentials and API guides

2. **🟡 HIGH PROTECTION:** `.github/`
   - Protected from most cleanup activities
   - Contains repository configuration
   - Preserved across branches

3. **🟢 STANDARD:** `docs/`
   - May be cleaned during major reorganizations
   - Good for general documentation

4. **🟠 MODERATE RISK:** Root level
   - May be moved or cleaned
   - Not ideal for permanent documents

---

## 📋 **Cleanup Activity Safeguards**

### **Always Check Before Cleanup:**
```bash
# Verify these files exist before any cleanup
ls -la .github/docs/QUICKBASE_API_GUIDE.md
ls -la .github/BRANCH_POLICY_CRM.md
ls -la .github/COPILOT_SETUP.md
```

### **Backup Command:**
```bash
# Create safety backup before major changes
cp -r .github/docs/ .github/docs_backup_$(date +%Y%m%d)/
```

---

## 🔑 **QuickBase Credentials Location**

**PRIMARY:** `.github/docs/QUICKBASE_API_GUIDE.md`
**BACKUP:** Consider adding to password manager

**Contains:**
- Realm: marclilly.quickbase.com
- User Token: `capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8`
- App Token: `cnnkxpkdi9f4d9c4rp2wy89dde`
- Table DBIDs and field mappings
- Complete API usage examples

---

## ⚠️ **Repository Maintainer Notes**

1. **Never delete `.github/docs/` directory**
2. **Check this index before any major cleanup**
3. **Move critical docs here, don't copy elsewhere**
4. **Update this index when adding new critical documents**

---

## 🚀 **Access Instructions**

```bash
# Always access QuickBase guide from protected location
cat .github/docs/QUICKBASE_API_GUIDE.md

# Copy for development use (don't edit original)
cp .github/docs/QUICKBASE_API_GUIDE.md temp_quickbase_work.md
```

---

**REMINDER:** This directory (`.github/docs/`) is the **PERMANENT ARCHIVE** for mission-critical documents. Treat it as write-once, reference-always.

---

*Last Updated: November 5, 2025*  
*Protection Level: MAXIMUM*