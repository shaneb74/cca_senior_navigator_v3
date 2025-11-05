# Quickbase API: Full Connection & Query Guide  
*(Save this — never lose it again)*

---

## 1. Your Credentials (Never Share)

```text
Realm: marclilly.quickbase.com
User Token: capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8
App Token: cnnkxpkdi9f4d9c4rp2wy89dde
```

> **Store in `.env` or password manager** — never in code.

---

## 2. Test Connection (Run This First)

```bash
curl -X POST "https://marclilly.quickbase.com/db/main" \
  -H "QB-Realm-Hostname: marclilly.quickbase.com" \
  -H "Authorization: QB-USER-TOKEN capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8" \
  -H "QB-AppToken: cnnkxpkdi9f4d9c4rp2wy89dde" \
  -H "Content-Type: application/xml" \
  -d '<qdbapi><a>API_Authenticate</a></qdbapi>'
```

**Success = `<ticket>` in response**

---

## 3. Key Table DBIDs (Bookmark This)

| Table | DBID |
|------|------|
| **WA Clients** | `bkqfsmeuq` |
| **Intake Forms** | `bkpvi5e32` |
| **Activities** | `bkpvi3btn` |
| **Communities** | `bkp5hn255` |

---

## 4. Pull Full Schema (Structure Only)

```bash
curl -X POST "https://marclilly.quickbase.com/db/bkpvi3bsx" \
  -H "QB-Realm-Hostname: marclilly.quickbase.com" \
  -H "Authorization: QB-USER-TOKEN capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8" \
  -H "QB-AppToken: cnnkxpkdi9f4d9c4rp2wy89dde" \
  -H "Content-Type: application/xml" \
  -d '<qdbapi><usertoken>capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8</usertoken><apptoken>cnnkxpkdi9f4d9c4rp2wy89dde</apptoken><a>API_GetSchema</a></qdbapi>' \
  > quickbase_schema.xml
```

---

## 5. Query Any Table (Example: WA Clients)

```bash
curl -X POST "https://marclilly.quickbase.com/db/bkqfsmeuq" \
  -H "QB-Realm-Hostname: marclilly.quickbase.com" \
  -H "Authorization: QB-USER-TOKEN capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8" \
  -H "QB-AppToken: cnnkxpkdi9f4d9c4rp2wy89dde" \
  -H "Content-Type: application/xml" \
  -d '<qdbapi><usertoken>capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8</usertoken><apptoken>cnnkxpkdi9f4d9c4rp2wy89dde</apptoken><a>API_DoQuery</a><query>{6.GTE."2025-09-01"}AND{6.LTE."2025-09-30"}</query><clist>3.47.6.171.143.142</clist><options>num-1000</options></qdbapi>' \
  > september_closes.xml
```

---

## 6. Field IDs (Critical Ones)

| ID | Label |
|----|-------|
| 3 | Record ID |
| 4 | Record Owner |
| 6 | Date of Intake |
| 47 | Name of Advisor |
| 142 | Stage |
| 143 | Move-In Amount |
| 171 | Closing Date |

---

## 7. Convert XML → CSV (Python)

```python
import xml.etree.ElementTree as ET
import csv

tree = ET.parse('september_closes.xml')
root = tree.getroot()

with open('september.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Advisor', 'Intake', 'Stage', 'Closing', 'Amount'])
    for rec in root.findall('.//record'):
        writer.writerow([
            rec.find('f[@id="3"]').text,
            rec.find('f[@id="47"]').text if rec.find('f[@id="47"]') is not None else '',
            rec.find('f[@id="6"]').text if rec.find('f[@id="6"]') is not None else '',
            rec.find('f[@id="142"]').text if rec.find('f[@id="142"]') is not None else '',
            rec.find('f[@id="171"]').text if rec.find('f[@id="171"]') is not None else '',
            rec.find('f[@id="143"]').text if rec.find('f[@id="143"]') is not None else ''
        ])
```

---

## 8. Monthly Revenue Report (Template)

```bash
MONTH="2025-09"
curl -X POST "https://marclilly.quickbase.com/db/bkqfsmeuq" \
  -H "QB-Realm-Hostname: marclilly.quickbase.com" \
  -H "Authorization: QB-USER-TOKEN capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8" \
  -H "QB-AppToken: cnnkxpkdi9f4d9c4rp2wy89dde" \
  -d "<qdbapi><usertoken>capxhv_iaf4_0_cww8jfnbjpfkhvd7752udkw3wv8</usertoken><apptoken>cnnkxpkdi9f4d9c4rp2wy89dde</apptoken><a>API_DoQuery</a><query>{6.GTE.\"$MONTH-01\"}AND{6.LTE.\"$MONTH-31\"}</query><clist>143</clist></qdbapi>" \
  > month.xml

grep -o '<f id="143">[^<]*</f>' month.xml | sed 's/.*>\(.*\)<.*/\1/' | awk '{sum+=$1} END {print "$" sum}'
```

---

## 9. Troubleshooting

| Issue | Fix |
|------|-----|
| `errcode 4` | Bad token — regenerate |
| Empty fields | Use **Intake Forms** (`bkpvi5e32`) |
| Too much data | Add `skip=1000` and loop |
| No names | Field 47 is **User ID** — map via Users export |

---

## 10. Save This File

**Name:** `quickbase_api_guide.md`  
**Location:** Your project root

---

**You’re now self-sufficient.**  
**Copy, run, query — anytime.**

Need **Python script**, **cron job**, or **dashboard** next?  
Just ask.