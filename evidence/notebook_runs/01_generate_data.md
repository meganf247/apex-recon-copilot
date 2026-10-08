# Executed notebook: `01_generate_data`

- Task run ID: `1018059793733660` (job run `600343157910371`)
- Result: **SUCCESS**
- Run page: https://fevm-megant-fevm.cloud.databricks.com/?o=7474649371849429#job/800507315624085/run/1018059793733660
- Every cell below is shown with the output it produced in that run.

# 01 · Synthetic CTV data generator

Nine months (Jan–Sep 2026) of data for **Apex Exchange**, a fictional CTV SSP:

| Output | Where | What |
|---|---|---|
| SSP auction logs | `/Volumes/apex_recon/landing/raw/ssp_logs/*.json.gz` | Apex's own count: deal × hour (UTC), one file per day |
| DSP billing reports | `/Volumes/apex_recon/landing/raw/dsp_reports/<dsp_id>/*.csv` | Each DSP's count: deal × day, one file per DSP per month |
| Reference tables | `apex_recon.silver.dsps`, `apex_recon.silver.deals` | Partner contracts and deal attributes |
| Dispute history | `apex_recon.ml.dispute_history` | Jan–Jun disputes resolved by Billing Ops (ML training labels) |
| Ground truth | `apex_recon.ml.ground_truth_root_causes` | Planted cause per deal-month, for model evaluation only |

DSP reports start from the same delivery as Apex's logs, then get distorted by one of **five root causes**
(plus a smaller second cause on ~30% of problem cases, like real disputes). The CSVs also contain bad rows
(missing deal IDs, negative counts, bad dates, duplicates) for the pipeline's data-quality rules to catch.

```python
import json
import os
import shutil

import numpy as np
import pandas as pd

try:
    dbutils.widgets.text("catalog", "apex_recon")
    dbutils.widgets.text("seed", "42")
    CATALOG, SEED, ON_DATABRICKS = dbutils.widgets.get("catalog"), int(dbutils.widgets.get("seed")), True
    ROOT = f"/Volumes/{CATALOG}/landing/raw"
except NameError:  # local dry run: python src/01_generate_data.py
    CATALOG, SEED, ON_DATABRICKS = "apex_recon", 42, False
    ROOT = os.environ.get("APEX_LOCAL_ROOT", "/tmp/apex_raw")
rng = np.random.default_rng(SEED)

CAUSES = ["WITHIN_TOLERANCE", "TIMEZONE_SHIFT", "IVT_FILTERING", "LATE_OR_MISSING_DATA", "GENUINE_BILLING_ERROR"]
C = {c: i for i, c in enumerate(CAUSES)}
```

## Calendar

```python
HOURS = pd.date_range("2026-01-01", "2026-09-30 23:00", freq="h", tz="UTC")
N_H, N_DAYS, N_MON, HISTORY_MONTHS = len(HOURS), len(HOURS) // 24, 9, 6
DAY = np.arange(N_H) // 24
MON = (HOURS.month - 1).to_numpy()
DATES = pd.date_range("2026-01-01", periods=N_DAYS, freq="D")
ET = HOURS.tz_convert("America/New_York")
LH_ET, DOW_ET = ET.hour.to_numpy(), ET.dayofweek.to_numpy()  # US audience time drives viewing
# Day index of each UTC hour as seen by a partner that (wrongly) reports in US Eastern or Pacific time
LOCAL_DAY = {tz: ((HOURS.tz_convert(tz).tz_localize(None).normalize() - pd.Timestamp("2026-01-01")).days).to_numpy()
             for tz in ["UTC", "America/New_York", "America/Los_Angeles"]}
```

## Reference data: 40 DSPs, 800 CTV deals

```python
DSP_NAMES = ["TradeNova", "BidSphere", "Quantive Media", "Reachlytics", "Pixelpath", "SignalForge", "Vantage Demand",
             "Northstar Buy", "Cobalt Ads", "Meridian Buy", "Lumen Programmatic", "Orbit Media", "Helix Demand",
             "Summit Audience", "Keystone Bid", "Bluefin Media", "Atlas Reach", "Ember Ads", "Nimbus Demand",
             "Prism Demand", "Harbor Media", "Ironwood Ads", "Juniper Buy", "Kestrel Demand", "Lattice Media",
             "Mosaic Bid", "Nova Reach", "Onyx Programmatic", "Paragon Ads", "Quill Media", "Redwood Demand",
             "Sable Buy", "Tidal Media", "Umbra Ads", "Vertex Buy", "Willow Demand", "Xenon Media", "Yarrow Ads",
             "Zephyr Demand", "Cascade Reach"]
N_DSP = len(DSP_NAMES)
dsp_tz = np.full(N_DSP, "UTC", dtype=object)  # hidden: contracts say UTC, six partners actually report in US time
perm = rng.permutation(N_DSP)
dsp_tz[perm[:4]], dsp_tz[perm[4:6]] = "America/New_York", "America/Los_Angeles"
dsp_offender = rng.lognormal(0, 0.6, N_DSP)  # some partners cause more problems than others
dsp_size = rng.lognormal(0, 1.0, N_DSP)
dsps = pd.DataFrame({
    "dsp_id": [f"DSP{i:03d}" for i in range(1, N_DSP + 1)],
    "dsp_name": DSP_NAMES,
    "partner_team": rng.choice(["Atlantic", "Pacific", "Central", "EMEA"], N_DSP),
    "discrepancy_threshold_pct": rng.choice([5.0, 7.5, 10.0], N_DSP, p=[0.2, 0.3, 0.5]),
    "billing_count_basis": rng.choice(["SSP", "DSP"], N_DSP, p=[0.6, 0.4]),
    "payment_terms_days": rng.choice([30, 45, 60], N_DSP),
})

N_PUB, N_DEAL = 150, 800
WORDS = ["Northwind", "Bluebird", "Summit", "Riverbend", "Lakeshore", "Granite", "Silverline", "Redrock", "Evergreen",
         "Harborview", "Maple", "Coastal", "Prairie", "Ironbridge", "Golden", "Pinecrest", "Clearwater", "Highland"]
SUFFIX = ["Stream", "Plus", "Sports Network", "News Live", "Classics", "Kids TV", "TV OS", "Smart TV", "Cast"]
pub_names = rng.choice([f"{w} {s}" for w in WORDS for s in SUFFIX], N_PUB, replace=False)
pub_ivt = np.clip(rng.beta(2, 12, N_PUB), 0.01, 0.5)  # Apex's own invalid-traffic risk score per publisher

GENRES = np.array(["sports", "news", "entertainment", "kids"])
d_dsp = rng.choice(N_DSP, N_DEAL, p=dsp_size / dsp_size.sum())
d_pub = rng.integers(0, N_PUB, N_DEAL)
d_genre = rng.choice(4, N_DEAL, p=[0.25, 0.15, 0.45, 0.15])
d_live = rng.random(N_DEAL) < np.array([0.8, 0.6, 0.1, 0.0])[d_genre]
d_type = rng.choice(["PG", "PMP", "OPEN"], N_DEAL, p=[0.2, 0.5, 0.3])
d_cpm = (rng.uniform(22, 38, N_DEAL) * pd.Series(d_type).map({"PG": 1.35, "PMP": 1.15, "OPEN": 1.0}).to_numpy()
         * np.array([1.25, 1.0, 1.0, 0.8])[d_genre])
d_base = np.clip(rng.lognormal(np.log(4500), 1.0, N_DEAL), 150, 120_000)  # impressions per hour
always_on = rng.random(N_DEAL) < 0.5
d_start = np.where(always_on, 0, rng.integers(0, 200, N_DEAL))
d_end = np.where(always_on, N_DAYS - 1, np.minimum(d_start + rng.integers(45, N_DAYS, N_DEAL), N_DAYS - 1))
deals = pd.DataFrame({
    "deal_id": [f"D{i:05d}" for i in range(1, N_DEAL + 1)],
    "dsp_id": dsps.dsp_id.to_numpy()[d_dsp],
    "publisher_name": pub_names[d_pub],
    "deal_name": [f"{pub_names[p]} · {GENRES[g].title()} · {t}" for p, g, t in zip(d_pub, d_genre, d_type)],
    "deal_type": d_type,
    "content_genre": GENRES[d_genre],
    "is_live": d_live,
    "ivt_risk_score": pub_ivt[d_pub].round(3),
})
```

## What Apex actually delivered (hourly)
Primetime peak 8–11pm ET, weekend lift, live sports on weekends and Mon/Thu nights, NFL ramp in September.

```python
def curve(base, bumps):
    x = np.arange(24)
    y = np.full(24, base, dtype=float)
    for c, w, h in bumps:
        d = np.minimum(np.abs(x - c), 24 - np.abs(x - c))
        y += h * np.exp(-0.5 * (d / w) ** 2)
    return y / y.mean()


CURVE = np.stack([curve(0.10, [(21, 1.8, 1.6), (14, 2.5, 0.6)]),                 # sports
                  curve(0.15, [(7, 1.5, 0.7), (18, 1.5, 0.8), (22, 1.5, 0.6)]),  # news
                  curve(0.10, [(21, 1.8, 1.6), (15, 3.0, 0.3)]),                 # entertainment
                  curve(0.15, [(8, 2.0, 0.8), (16, 2.0, 0.9)])])                 # kids
WEEK = np.array([[1.2, 0.9, 0.9, 1.2, 0.95, 1.4, 1.45], [1, 1, 1, 1, 1, 0.85, 0.85],
                 [0.95, 0.95, 0.95, 0.95, 1.05, 1.15, 1.15], [0.9, 0.9, 0.9, 0.9, 0.95, 1.3, 1.3]])
SPORTS_MONTH = np.array([1.25, 1.15, 0.95, 0.9, 0.9, 0.85, 0.85, 0.95, 1.6])
TREND = 1 + 0.10 * np.arange(N_H) / N_H

parts = []
for i in range(N_DEAL):
    g = d_genre[i]
    h = np.arange(d_start[i] * 24, (d_end[i] + 1) * 24)
    lam = (d_base[i] * CURVE[g][LH_ET[h]] * WEEK[g][DOW_ET[h]] * TREND[h]
           * rng.lognormal(0, 0.12, N_DAYS)[DAY[h]] * (SPORTS_MONTH[MON[h]] if g == 0 else 1))
    imps = rng.poisson(lam * (rng.random(h.size) < 0.93))
    keep = imps > 0
    h, imps = h[keep], imps[keep]
    cpm = d_cpm[i] * rng.normal(1, 0.03, h.size)
    parts.append((np.full(h.size, i), h, imps, imps * cpm / 1000))
deal_ix, hour_ix, imps, rev = (np.concatenate([p[k] for p in parts]) for k in range(4))
print(f"{len(imps):,} deal-hours · {imps.sum():,} impressions · ${rev.sum():,.0f} gross revenue")
```

Output:

```text
3,565,876 deal-hours · 31,506,213,513 impressions · $1,132,630,953 gross revenue
```

## Plant a root cause on every deal-month

```python
dm_key = deal_ix * N_MON + MON[hour_ix]
active = np.unique(dm_key)
cause = np.full(N_DEAL * N_MON, -1)
param = np.zeros(N_DEAL * N_MON)
cause2 = np.full(N_DEAL * N_MON, -1)  # smaller secondary cause
param2 = np.zeros(N_DEAL * N_MON)
tz_month = np.zeros(N_DEAL * N_MON, bool)

for k in active:
    i = k // N_MON
    if dsp_tz[d_dsp[i]] != "UTC" and rng.random() < 0.7:  # US-time partners get it right some months
        cause[k], tz_month[k] = C["TIMEZONE_SHIFT"], True
    else:
        w = dsp_offender[d_dsp[i]]
        p = np.array([0, 0, 0.12 * w * (0.5 + 0.5 * deals.ivt_risk_score[i] / 0.14), 0.07 * w, 0.07 * w])
        p[0] = max(0.3, 1 - p.sum())
        cause[k] = rng.choice(5, p=p / p.sum())
    c = CAUSES[cause[k]]
    param[k] = {"IVT_FILTERING": np.clip(deals.ivt_risk_score[i] * rng.uniform(0.3, 0.6) + 0.04 + rng.normal(0, 0.015), 0.04, 0.16),
                "LATE_OR_MISSING_DATA": rng.integers(2, 7),       # days missing from the report
                "GENUINE_BILLING_ERROR": rng.uniform(0.35, 0.6)}.get(c, 0.0)  # share of days under-reported
    if c != "TIMEZONE_SHIFT" and rng.random() < (0.3 if c != "WITHIN_TOLERANCE" else 0.08):
        cause2[k] = C["IVT_FILTERING"] if c != "IVT_FILTERING" else C["GENUINE_BILLING_ERROR"]
        param2[k] = rng.uniform(0.015, 0.045) if cause2[k] == C["IVT_FILTERING"] else rng.uniform(0.12, 0.25)
print(pd.Series(np.array(CAUSES)[cause[active]]).value_counts().to_string())
```

Output:

```text
WITHIN_TOLERANCE         3723
IVT_FILTERING             737
LATE_OR_MISSING_DATA      398
GENUINE_BILLING_ERROR     392
TIMEZONE_SHIFT            312
```

## What each DSP reports

```python
dd = deal_ix * N_DAYS + DAY[hour_ix]
factor = 1 - np.clip(rng.normal(0.015, 0.012, N_DEAL * N_DAYS), -0.02, 0.06)[dd]  # normal measurement noise
ivt_noise = np.clip(rng.normal(1, 0.3, N_DEAL * N_DAYS), 0, None)
bad_day, bad_mult = rng.random(N_DEAL * N_DAYS), rng.uniform(0.55, 0.85, N_DEAL * N_DAYS)
for ca, pa in [(cause, param), (cause2, param2)]:
    rc, rp = ca[dm_key], pa[dm_key]
    m = rc == C["IVT_FILTERING"]
    factor[m] *= 1 - rp[m] * ivt_noise[dd[m]]
    m = rc == C["GENUINE_BILLING_ERROR"]
    factor[m] *= np.where(bad_day[dd[m]] < rp[m], bad_mult[dd[m]], 1.0)
dsp_imps = np.round(imps * factor).astype(np.int64)

# US-time partners bucket hours into their local day in the months they get it wrong
tz = np.where(tz_month[dm_key], dsp_tz[d_dsp[deal_ix]], "UTC")
local_day = np.select([tz == "America/New_York", tz == "America/Los_Angeles"],
                      [LOCAL_DAY["America/New_York"][hour_ix], LOCAL_DAY["America/Los_Angeles"][hour_ix]],
                      LOCAL_DAY["UTC"][hour_ix])
rep = pd.DataFrame({"deal": deal_ix, "day": local_day, "imps": dsp_imps, "spend": dsp_imps * (rev / imps)})
rep = rep[rep.day >= 0].groupby(["deal", "day"], as_index=False).sum()

missing = set()
for k in active[cause[active] == C["LATE_OR_MISSING_DATA"]]:
    i, mo = k // N_MON, k % N_MON
    days = np.flatnonzero((DATES.month - 1 == mo) & (np.arange(N_DAYS) >= d_start[i]) & (np.arange(N_DAYS) <= d_end[i]))
    missing |= {(i, d) for d in rng.choice(days, min(int(param[k]), len(days)), replace=False)}
rep = rep[[(a, b) not in missing for a, b in zip(rep.deal, rep.day)]]
rep["dsp"], rep["month"] = d_dsp[rep.deal], DATES.month.to_numpy()[rep.day]
print(f"{len(rep):,} DSP report rows")
```

Output:

```text
158,242 DSP report rows
```

## Write the landing files

```python
for sub in ["ssp_logs", "dsp_reports", "publisher_reports", "reference", "history"]:
    shutil.rmtree(os.path.join(ROOT, sub), ignore_errors=True)
os.makedirs(f"{ROOT}/ssp_logs", exist_ok=True)

ssp = pd.DataFrame({"event_hour_utc": HOURS.strftime("%Y-%m-%dT%H:00:00Z").to_numpy()[hour_ix],
                    "deal_id": deals.deal_id.to_numpy()[deal_ix], "dsp_id": deals.dsp_id.to_numpy()[deal_ix],
                    "impressions": imps, "gross_revenue_usd": rev.round(4)})
for d, part in ssp.groupby(DAY[hour_ix]):
    part.to_json(f"{ROOT}/ssp_logs/ssp_auction_log_{DATES[d]:%Y-%m-%d}.json.gz", orient="records", lines=True,
                 compression="gzip")

dq = {"missing_deal_id": 0, "negative_impressions": 0, "bad_date": 0, "duplicate_rows": 0}
for (k, mo), part in rep.groupby(["dsp", "month"]):
    out = pd.DataFrame({"report_date": DATES[part.day.to_numpy()].strftime("%Y-%m-%d"),
                        "deal_id": deals.deal_id.to_numpy()[part.deal],
                        "impressions": part.imps.to_numpy(), "spend_usd": part.spend.round(2).to_numpy()}).astype(object)
    for key, p in [("missing_deal_id", 0.004), ("negative_impressions", 0.002), ("bad_date", 0.002)]:
        hit = rng.random(len(out)) < p
        dq[key] += int(hit.sum())
        if key == "missing_deal_id":
            out.loc[hit, "deal_id"] = None
        elif key == "negative_impressions":
            out.loc[hit, "impressions"] = -out.loc[hit, "impressions"]
        else:
            out.loc[hit, "report_date"] = "2026-02-30"
    dup = out.sample(frac=0.003, random_state=int(rng.integers(10**9)))
    dq["duplicate_rows"] += len(dup)
    path = f"{ROOT}/dsp_reports/{dsps.dsp_id[k]}"
    os.makedirs(path, exist_ok=True)
    pd.concat([out, dup]).to_csv(f"{path}/{dsps.dsp_id[k]}_billing_2026-{mo:02d}.csv", index=False)
```

## Dispute history (Jan–Jun, the ML labels) and ground truth

```python
ssp_dm = pd.DataFrame({"k": dm_key, "ssp_impressions": imps, "ssp_revenue_usd": rev}).groupby("k").sum()
rep["k"] = rep.deal * N_MON + rep.month - 1
dsp_dm = rep.groupby("k").agg(dsp_impressions=("imps", "sum"), dsp_revenue_usd=("spend", "sum"))
gt = pd.DataFrame({"k": active}).join(ssp_dm, on="k").join(dsp_dm, on="k").fillna(0)
gt["deal_id"] = deals.deal_id.to_numpy()[gt.k // N_MON]
gt["dsp_id"] = deals.dsp_id.to_numpy()[gt.k // N_MON]
gt["billing_month"] = [f"2026-{m + 1:02d}" for m in gt.k % N_MON]
gt["root_cause"] = np.array(CAUSES)[cause[gt.k]]
gt["secondary_cause"] = np.where(cause2[gt.k] >= 0, np.array(CAUSES)[np.maximum(cause2[gt.k], 0)], None)
gt["revenue_gap_usd"] = (gt.ssp_revenue_usd - gt.dsp_revenue_usd).round(2)
gt["revenue_gap_pct"] = (100 * gt.revenue_gap_usd / gt.ssp_revenue_usd).round(3)

is_hist = (gt.k % N_MON) < HISTORY_MONTHS
hist = gt[is_hist & ((gt.root_cause != "WITHIN_TOLERANCE") | (rng.random(len(gt)) < 0.2))].copy()
CONFUSABLE = {"IVT_FILTERING": ["GENUINE_BILLING_ERROR"], "GENUINE_BILLING_ERROR": ["IVT_FILTERING", "LATE_OR_MISSING_DATA"],
              "LATE_OR_MISSING_DATA": ["GENUINE_BILLING_ERROR"], "TIMEZONE_SHIFT": ["WITHIN_TOLERANCE"],
              "WITHIN_TOLERANCE": ["TIMEZONE_SHIFT", "IVT_FILTERING"]}
noisy = rng.random(len(hist)) < 0.12  # analysts sometimes record a look-alike cause
hist["resolved_root_cause"] = [rng.choice(CONFUSABLE[c]) if n else c for c, n in zip(hist.root_cause, noisy)]
RECOVERY = {"WITHIN_TOLERANCE": 0.0, "TIMEZONE_SHIFT": 0.0, "IVT_FILTERING": 0.0,
            "LATE_OR_MISSING_DATA": 0.9, "GENUINE_BILLING_ERROR": 0.6}
hist["recovered_usd"] = (hist.revenue_gap_usd.clip(lower=0) * hist.resolved_root_cause.map(RECOVERY)).round(2)
hist["days_to_resolve"] = np.clip(rng.lognormal(np.log(19), 0.45, len(hist)), 2, 75).round().astype(int)
hist.insert(0, "case_id", [f"HC-{i:05d}" for i in range(1, len(hist) + 1)])

hist_cols = ["case_id", "dsp_id", "deal_id", "billing_month", "ssp_revenue_usd", "dsp_revenue_usd", "revenue_gap_usd",
             "resolved_root_cause", "recovered_usd", "days_to_resolve"]
gt_cols = ["deal_id", "dsp_id", "billing_month", "root_cause", "secondary_cause", "ssp_impressions", "dsp_impressions",
           "ssp_revenue_usd", "dsp_revenue_usd", "revenue_gap_usd", "revenue_gap_pct"]
TABLES = {"silver.dsps": (dsps, "DSP partners and contract terms (discrepancy threshold, billing basis, payment terms)."),
          "silver.deals": (deals, "CTV deals: DSP, publisher, deal type, content genre, live flag, publisher IVT risk score."),
          "ml.dispute_history": (hist[hist_cols], "Jan-Jun 2026 disputes resolved by Billing Ops. resolved_root_cause is the ML label."),
          "ml.ground_truth_root_causes": (gt[gt_cols], "Planted cause per deal-month from the generator. Evaluation only, never a feature.")}
if ON_DATABRICKS:
    for name, (df, comment) in TABLES.items():
        spark.createDataFrame(df).write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{CATALOG}.{name}")
        spark.sql(f"COMMENT ON TABLE {CATALOG}.{name} IS '{comment}'")
else:
    for name, (df, _) in TABLES.items():
        df.to_csv(f"{ROOT}/{name}.csv", index=False)
```

```python
summary = {
    "ssp_log_rows": int(len(ssp)), "impressions": int(imps.sum()), "gross_revenue_usd": round(float(rev.sum()), 2),
    "dsp_report_rows": int(len(rep)), "dsp_report_files": int(rep.groupby(["dsp", "month"]).ngroups),
    "bad_rows_injected": dq, "deal_months": int(len(gt)),
    "root_causes": gt.root_cause.value_counts().to_dict(),
    "with_secondary_cause": int(gt.secondary_cause.notna().sum()),
    "history_cases": int(len(hist)), "history_label_noise": round(float(noisy.mean()), 3),
}
print(json.dumps(summary, indent=2))
if ON_DATABRICKS:
    dbutils.notebook.exit(json.dumps(summary))
```

Output:

```text
Notebook exit value:
{"ssp_log_rows": 3565876, "impressions": 31506213513, "gross_revenue_usd": 1132630952.61, "dsp_report_rows": 158242, "dsp_report_files": 360, "bad_rows_injected": {"missing_deal_id": 631, "negative_impressions": 290, "bad_date": 330, "duplicate_rows": 481}, "deal_months": 5562, "root_causes": {"WITHIN_TOLERANCE": 3723, "IVT_FILTERING": 737, "LATE_OR_MISSING_DATA": 398, "GENUINE_BILLING_ERROR": 392, "TIMEZONE_SHIFT": 312}, "with_secondary_cause": 779, "history_cases": 1615, "history_label_noise": 0.11}
```
