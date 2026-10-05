# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Synthetic CTV data generator
# MAGIC
# MAGIC Generates nine months (Jan–Sep 2026) of data for **Apex Exchange**, a fictional CTV SSP, and lands it in
# MAGIC `/Volumes/apex_recon/landing/raw` exactly the way the real sources would arrive:
# MAGIC
# MAGIC | Source | Format | Grain |
# MAGIC |---|---|---|
# MAGIC | `ssp_logs/` | JSON lines, gzip, one file per UTC day | deal × hour (UTC) — Apex's system of record |
# MAGIC | `dsp_reports/<dsp_id>/<YYYY-MM>.csv` | CSV in **3 partner formats**, partner timezone + currency | deal × partner-local day |
# MAGIC | `publisher_reports/<publisher_id>/<YYYY-MM>.csv` | Ad server export (FreeWheel / GAM / SpringServe style) | deal × publisher-local day |
# MAGIC | `reference/` | CSV | DSPs, publishers, deals, contracts, FX rates |
# MAGIC | `history/dispute_resolutions.csv` | CSV | Jan–Jun disputes resolved by analysts (ML training labels) |
# MAGIC
# MAGIC DSP reports are derived from the same ground truth as the SSP logs, then distorted with **planted root causes**
# MAGIC (timezone shift, CTV IVT filtering, SSAI beacon loss, deal-ID mis-mapping, FX mismatch, missing data, genuine billing
# MAGIC errors) so the root-cause model has real signal to learn. Data-quality defects are injected for Lakeflow expectations.
# MAGIC The ground truth for every deal-month is written to `apex_recon.ml.ground_truth_root_causes` for model evaluation only.

# COMMAND ----------

import json
import os
import shutil

import numpy as np
import pandas as pd

try:
    dbutils.widgets.text("catalog", "apex_recon")
    dbutils.widgets.text("seed", "42")
    CATALOG = dbutils.widgets.get("catalog")
    SEED = int(dbutils.widgets.get("seed"))
    ON_DATABRICKS = True
    ROOT = f"/Volumes/{CATALOG}/landing/raw"
except NameError:  # local dry run
    CATALOG, SEED, ON_DATABRICKS = "apex_recon", 42, False
    ROOT = os.environ.get("APEX_LOCAL_ROOT", "/tmp/apex_raw")

rng = np.random.default_rng(SEED)
print(f"catalog={CATALOG} seed={SEED} root={ROOT}")

# COMMAND ----------

# MAGIC %md ## Calendar and constants

# COMMAND ----------

START = pd.Timestamp("2026-01-01", tz="UTC")
HOURS = pd.date_range(START, pd.Timestamp("2026-09-30 23:00", tz="UTC"), freq="h")
N_H = len(HOURS)
N_DAYS = N_H // 24
DAY = np.arange(N_H) // 24
MON = (HOURS.month - 1).to_numpy()  # 0..8 (UTC month)
N_MON = 9
HISTORY_MONTHS = 6  # Jan–Jun resolved; Jul–Sep are the current closes
DATES = pd.date_range("2026-01-01", periods=N_DAYS, freq="D")
DATE_STR = DATES.strftime("%Y-%m-%d").to_numpy()

ET = HOURS.tz_convert("America/New_York")
LH_ET = ET.hour.to_numpy()  # US audience local hour drives viewing
DOW_ET = ET.dayofweek.to_numpy()

TZS = ["UTC", "America/New_York", "America/Los_Angeles"]


def local_day_index(tz):
    """Local calendar day index (0 = 2026-01-01) for every UTC hour; -1 for hours before Jan 1 local."""
    local = HOURS.tz_convert(tz).tz_localize(None).normalize()
    return ((local - pd.Timestamp("2026-01-01")).days).to_numpy()


LOCAL_DAY = np.stack([local_day_index(tz) for tz in TZS])  # [tz, hour]

GENRES = ["sports", "news", "entertainment", "kids"]
CAUSES = ["WITHIN_TOLERANCE", "TIMEZONE_SHIFT", "IVT_FILTERING", "SSAI_BEACON_LOSS",
          "DEAL_ID_MISMAPPING", "FX_MISMATCH", "LATE_OR_MISSING_DATA", "GENUINE_BILLING_ERROR"]
C = {c: i for i, c in enumerate(CAUSES)}

# COMMAND ----------

# MAGIC %md ## Reference entities: DSPs, CTV publishers, deals, contracts, FX

# COMMAND ----------

DSP_NAMES = ["TradeNova", "BidSphere", "Quantive Media", "Reachlytics", "Pixelpath", "SignalForge", "Vantage Demand",
             "Northstar Buy", "Cobalt Ads", "Meridian Buy", "Lumen Programmatic", "Orbit Media", "Helix Demand",
             "Summit Audience", "Keystone Bid", "Bluefin Media", "Atlas Reach", "Ember Ads", "Nimbus Demand",
             "Prism Demand", "Harbor Media", "Ironwood Ads", "Juniper Buy", "Kestrel Demand", "Lattice Media",
             "Mosaic Bid", "Nova Reach", "Onyx Programmatic", "Paragon Ads", "Quill Media", "Redwood Demand",
             "Sable Buy", "Tidal Media", "Umbra Ads", "Vertex Buy", "Willow Demand", "Xenon Media", "Yarrow Ads",
             "Zephyr Demand", "Cascade Reach"]
N_DSP = len(DSP_NAMES)
perm = rng.permutation(N_DSP)
dsp_tz = np.full(N_DSP, "UTC", dtype=object)
dsp_tz[perm[:4]] = "America/New_York"
dsp_tz[perm[4:6]] = "America/Los_Angeles"
dsp_cur = np.full(N_DSP, "USD", dtype=object)
dsp_cur[perm[6:10]] = "EUR"
dsp_cur[perm[10:12]] = "GBP"
dsp_schema = rng.choice(["A", "B", "C"], N_DSP, p=[0.5, 0.2, 0.3]).astype(object)
dsp_schema[dsp_cur != "USD"] = "B"  # the only format that carries a currency column
dsp_team = rng.choice(["Atlantic", "Pacific", "Central"], N_DSP).astype(object)
dsp_team[dsp_cur != "USD"] = "EMEA"
dsps = pd.DataFrame({
    "dsp_id": [f"DSP{i:03d}" for i in range(1, N_DSP + 1)],
    "dsp_name": DSP_NAMES,
    "seat_id": [f"S-{x}" for x in rng.choice(np.arange(1000, 9999), N_DSP, replace=False)],
    "reporting_timezone": dsp_tz,
    "reporting_currency": dsp_cur,
    "report_format": dsp_schema,
    "ivt_vendor_strictness": rng.uniform(0.6, 1.4, N_DSP).round(2),
    "partner_team": dsp_team,
})
dsp_offender = rng.lognormal(0, 0.6, N_DSP)  # some partners are repeat offenders
dsp_size = rng.lognormal(0, 1.0, N_DSP)
dsp_contracts = pd.DataFrame({
    "dsp_id": dsps.dsp_id,
    "discrepancy_threshold_pct": rng.choice([5.0, 7.5, 10.0], N_DSP, p=[0.2, 0.3, 0.5]),
    "billing_count_basis": rng.choice(["SSP", "DSP"], N_DSP, p=[0.6, 0.4]),
    "payment_terms_days": rng.choice([30, 45, 60], N_DSP, p=[0.3, 0.4, 0.3]),
    "contract_reporting_timezone": "UTC",
})

N_PUB = 150
pub_type = rng.choice(["streaming_service", "fast_channel", "device_platform"], N_PUB, p=[0.27, 0.46, 0.27])
WORDS = ["Northwind", "Bluebird", "Summit", "Riverbend", "Lakeshore", "Granite", "Silverline", "Redrock", "Evergreen",
         "Harborview", "Maple", "Coastal", "Prairie", "Ironbridge", "Golden", "Pinecrest", "Clearwater", "Highland",
         "Sunset", "Starlight", "Beacon", "Cedar", "Driftwood", "Falcon", "Glacier"]
SUFFIX = {"streaming_service": ["Stream", "Plus", "Play", "TV+", "Now", "Vision"],
          "fast_channel": ["Sports Network", "News Live", "Classics", "Kids TV", "Comedy Channel", "Movies FAST"],
          "device_platform": ["TV OS", "Smart TV", "Cast", "Home Screen", "Box", "Stick"]}
names, used = [], set()
for t in pub_type:
    while True:
        n = f"{rng.choice(WORDS)} {rng.choice(SUFFIX[t])}"
        if n not in used:
            used.add(n)
            names.append(n)
            break
pub_ivt = rng.beta(2, 12, N_PUB) + np.where(pub_type == "fast_channel", 0.05, 0.0) - np.where(pub_type == "device_platform", 0.03, 0.0)
SSAI = {"Stitchwave": 0.5, "PodForge": 1.0, "Splice Media": 1.7}  # relative beacon-loss propensity
publishers = pd.DataFrame({
    "publisher_id": [f"P{i:04d}" for i in range(1, N_PUB + 1)],
    "publisher_name": names,
    "publisher_type": pub_type,
    "ad_server": rng.choice(["FreeWheel", "Google Ad Manager", "SpringServe"], N_PUB, p=[0.45, 0.35, 0.2]),
    "ssai_vendor": rng.choice(list(SSAI), N_PUB, p=[0.4, 0.35, 0.25]),
    "reporting_timezone": rng.choice(["UTC", "America/New_York"], N_PUB, p=[0.85, 0.15]),
    "ivt_risk_score": np.clip(pub_ivt, 0.01, 0.6).round(3),
})
pub_contracts = pd.DataFrame({
    "publisher_id": publishers.publisher_id,
    "publisher_rev_share_pct": rng.uniform(80, 88, N_PUB).round(1),
    "discrepancy_threshold_pct": rng.choice([5.0, 10.0], N_PUB, p=[0.4, 0.6]),
})
pub_count_loss = rng.uniform(0.005, 0.03, N_PUB)  # publisher ad server counts slightly fewer than the SSP

N_DEAL = 800
d_dsp = rng.choice(N_DSP, N_DEAL, p=dsp_size / dsp_size.sum())
d_pub = rng.integers(0, N_PUB, N_DEAL)
d_genre = rng.choice(4, N_DEAL, p=[0.25, 0.15, 0.45, 0.15])
live_p = np.array([0.8, 0.6, 0.1, 0.0])[d_genre]
d_live = rng.random(N_DEAL) < live_p
d_type = rng.choice(["PG", "PMP", "OPEN"], N_DEAL, p=[0.2, 0.5, 0.3])
type_mult = pd.Series(d_type).map({"PG": 1.35, "PMP": 1.15, "OPEN": 1.0}).to_numpy()
genre_mult = np.array([1.25, 1.0, 1.0, 0.8])[d_genre]
d_cpm = rng.uniform(22, 38, N_DEAL) * type_mult * genre_mult * np.where(d_live, 1.1, 1.0)
d_base = np.clip(rng.lognormal(np.log(4500), 1.0, N_DEAL), 150, 120_000)
always_on = rng.random(N_DEAL) < 0.5
d_start = np.where(always_on, 0, rng.integers(0, 200, N_DEAL))
d_end = np.where(always_on, N_DAYS - 1, np.minimum(d_start + rng.integers(45, N_DAYS, N_DEAL), N_DAYS - 1))
deals = pd.DataFrame({
    "deal_id": [f"D{i:05d}" for i in range(1, N_DEAL + 1)],
    "deal_name": [f"{publishers.publisher_name[p]} · {GENRES[g].title()} · {t}" for p, g, t in zip(d_pub, d_genre, d_type)],
    "dsp_id": dsps.dsp_id.to_numpy()[d_dsp],
    "dsp_deal_code": [f"{dsps.seat_id[k]}-{rng.integers(0, 16**6):06x}" for k in d_dsp],
    "publisher_id": publishers.publisher_id.to_numpy()[d_pub],
    "deal_type": d_type,
    "content_genre": np.array(GENRES)[d_genre],
    "is_live": d_live,
    "device_type": rng.choice(["smart_tv", "streaming_stick", "gaming_console", "set_top_box"], N_DEAL, p=[0.5, 0.3, 0.1, 0.1]),
    "floor_cpm_usd": (d_cpm * 0.7).round(2),
    "flight_start": DATE_STR[d_start],
    "flight_end": DATE_STR[d_end],
})

fx_rates = []
for cur, base in [("EUR", 1.08), ("GBP", 1.27)]:
    walk = base * np.exp(np.cumsum(rng.normal(0, 0.004, N_DAYS)))
    fx_rates.append(pd.DataFrame({"rate_date": DATE_STR, "currency": cur, "usd_per_unit": walk.round(5)}))
fx_rates = pd.concat(fx_rates, ignore_index=True)
FX = {"USD": np.ones(N_DAYS)}
for cur in ["EUR", "GBP"]:
    FX[cur] = fx_rates[fx_rates.currency == cur].usd_per_unit.to_numpy()
print(f"{N_DSP} DSPs, {N_PUB} CTV publishers, {N_DEAL} deals")

# COMMAND ----------

# MAGIC %md ## Ground truth: hourly delivered impressions and revenue
# MAGIC Primetime peak (8–11pm ET), weekend lift, live sports on weekends + Mon/Thu nights, NFL ramp in September.

# COMMAND ----------


def curve(base, bumps):
    x = np.arange(24)
    y = np.full(24, base, dtype=float)
    for c, w, h in bumps:
        d = np.minimum(np.abs(x - c), 24 - np.abs(x - c))
        y += h * np.exp(-0.5 * (d / w) ** 2)
    return y / y.mean()


CURVE = np.stack([
    curve(0.10, [(21, 1.8, 1.6), (14, 2.5, 0.6)]),  # sports
    curve(0.15, [(7, 1.5, 0.7), (18, 1.5, 0.8), (22, 1.5, 0.6)]),  # news
    curve(0.10, [(21, 1.8, 1.6), (15, 3.0, 0.3)]),  # entertainment
    curve(0.15, [(8, 2.0, 0.8), (16, 2.0, 0.9)]),  # kids
])
CURVE01 = (CURVE - CURVE.min(1, keepdims=True)) / np.ptp(CURVE, axis=1, keepdims=True)
WEEK = np.array([
    [1.2, 0.9, 0.9, 1.2, 0.95, 1.4, 1.45],  # sports: MNF/TNF, weekend games
    [1.0, 1.0, 1.0, 1.0, 1.0, 0.85, 0.85],
    [0.95, 0.95, 0.95, 0.95, 1.05, 1.15, 1.15],
    [0.9, 0.9, 0.9, 0.9, 0.95, 1.3, 1.3],
])
SPORTS_MONTH = np.array([1.25, 1.15, 0.95, 0.9, 0.9, 0.85, 0.85, 0.95, 1.6])
TREND = 1 + 0.10 * np.arange(N_H) / N_H

parts = []
for i in range(N_DEAL):
    g = d_genre[i]
    h = np.arange(d_start[i] * 24, (d_end[i] + 1) * 24)
    day_noise = rng.lognormal(0, 0.12, N_DAYS)
    lam = d_base[i] * CURVE[g][LH_ET[h]] * WEEK[g][DOW_ET[h]] * TREND[h] * day_noise[DAY[h]]
    if g == 0:
        lam *= SPORTS_MONTH[MON[h]]
    lam *= rng.random(h.size) < 0.93  # hours with no fill
    imps = rng.poisson(lam)
    keep = imps > 0
    h, imps = h[keep], imps[keep]
    cpm = d_cpm[i] * (1 + 0.15 * (CURVE01[g][LH_ET[h]] - 0.5)) * rng.normal(1, 0.03, h.size)
    parts.append((np.full(h.size, i, np.int32), h.astype(np.int32), imps.astype(np.int64), imps * cpm / 1000))

deal_ix = np.concatenate([p[0] for p in parts])
hour_ix = np.concatenate([p[1] for p in parts])
imps = np.concatenate([p[2] for p in parts])
rev = np.concatenate([p[3] for p in parts])
cpm_row = rev / imps * 1000
print(f"{len(imps):,} deal-hours, {imps.sum():,} impressions, ${rev.sum():,.0f} gross revenue")

# COMMAND ----------

# MAGIC %md ## Plant root causes per deal-month

# COMMAND ----------

dm_key = deal_ix * N_MON + MON[hour_ix]
dm_cause = np.full(N_DEAL * N_MON, -1, np.int16)
dm_param = np.zeros(N_DEAL * N_MON)
dm_partner = np.full(N_DEAL * N_MON, -1, np.int32)
active = np.unique(dm_key)

deal_dsp_tz = dsp_tz[d_dsp]
deal_cur = dsp_cur[d_dsp]
deal_ivt = publishers.ivt_risk_score.to_numpy()[d_pub]
deal_ssai = pd.Series(publishers.ssai_vendor.to_numpy()[d_pub]).map(SSAI).to_numpy()
BASE_P = {"IVT_FILTERING": 0.10, "SSAI_BEACON_LOSS": 0.10, "DEAL_ID_MISMAPPING": 0.03,
          "FX_MISMATCH": 0.06, "LATE_OR_MISSING_DATA": 0.05, "GENUINE_BILLING_ERROR": 0.05}

for k in active:
    i = k // N_MON
    if deal_dsp_tz[i] != "UTC":
        dm_cause[k] = C["TIMEZONE_SHIFT"]
        continue
    w = dsp_offender[d_dsp[i]]
    p = {c: v * w for c, v in BASE_P.items()}
    p["IVT_FILTERING"] *= deal_ivt[i] / 0.14
    p["SSAI_BEACON_LOSS"] *= deal_ssai[i] * (1.5 if d_live[i] else 0.8)
    p["FX_MISMATCH"] = 0.0 if deal_cur[i] == "USD" else 0.30
    p["WITHIN_TOLERANCE"] = max(0.2, 1 - sum(p.values()))
    names_, probs = list(p), np.array(list(p.values()))
    dm_cause[k] = C[names_[rng.choice(len(names_), p=probs / probs.sum())]]

# effect sizes
for k in active:
    c, i = CAUSES[dm_cause[k]], k // N_MON
    if c == "IVT_FILTERING":
        dm_param[k] = np.clip(deal_ivt[i] * dsps.ivt_vendor_strictness[d_dsp[i]] * rng.uniform(0.25, 0.5) + 0.03, 0.04, 0.15)
    elif c == "SSAI_BEACON_LOSS":
        dm_param[k] = rng.uniform(0.04, 0.11)
    elif c == "FX_MISMATCH":
        dm_param[k] = rng.uniform(0.04, 0.10)
    elif c == "GENUINE_BILLING_ERROR":
        dm_param[k] = rng.uniform(0.35, 0.6)  # share of days under-reported
    elif c == "LATE_OR_MISSING_DATA":
        dm_param[k] = rng.integers(2, 7)  # days missing

# pair deal-ID mis-mappings with a same-DSP, same-month sibling that is otherwise clean
deal_dsp_arr = d_dsp
for k in [k for k in active if dm_cause[k] == C["DEAL_ID_MISMAPPING"] and dm_partner[k] == -1]:
    i, m = k // N_MON, k % N_MON
    sib = [j for j in np.flatnonzero(deal_dsp_arr == deal_dsp_arr[i])
           if j != i and dm_cause[j * N_MON + m] == C["WITHIN_TOLERANCE"]]
    if not sib:
        dm_cause[k] = C["WITHIN_TOLERANCE"]
        continue
    j = rng.choice(sib)
    dm_param[k] = rng.uniform(0.2, 0.5)  # share of impressions booked under the wrong deal
    dm_partner[k] = j
    dm_cause[j * N_MON + m] = C["DEAL_ID_MISMAPPING"]
    dm_partner[j * N_MON + m] = -2 - i  # receiver marker, encodes the source deal

print(pd.Series(np.array(CAUSES)[dm_cause[active]]).value_counts().to_string())

# COMMAND ----------

# MAGIC %md ## Build DSP-side counts from ground truth + planted distortions

# COMMAND ----------

row_cause = dm_cause[dm_key]
row_param = dm_param[dm_key]
nat = np.clip(rng.normal(0.012, 0.008, N_DEAL * N_DAYS), -0.01, 0.04)  # normal measurement noise per deal-day
factor = 1 - nat[deal_ix * N_DAYS + DAY[hour_ix]]

m = row_cause == C["IVT_FILTERING"]
factor[m] *= 1 - row_param[m] * rng.normal(1, 0.08, m.sum())
m = row_cause == C["SSAI_BEACON_LOSS"]
load = CURVE01[d_genre[deal_ix[m]], LH_ET[hour_ix[m]]]
factor[m] *= 1 - row_param[m] * (0.5 + 0.9 * load) * np.where(d_live[deal_ix[m]], 1.2, 1.0)
m = row_cause == C["GENUINE_BILLING_ERROR"]
bad_day = rng.random(N_DEAL * N_DAYS)
bad_mult = rng.uniform(0.55, 0.85, N_DEAL * N_DAYS)
idx = deal_ix[m] * N_DAYS + DAY[hour_ix[m]]
factor[m] *= np.where(bad_day[idx] < row_param[m], bad_mult[idx], 1.0)

dsp_imps = np.round(imps * np.clip(factor, 0, None)).astype(np.int64)
dsp_rev = dsp_imps * cpm_row / 1000
rep_deal = deal_ix.copy()

# deal-ID mis-mapping: part of the source deal's delivery is booked under the sibling deal
m = (row_cause == C["DEAL_ID_MISMAPPING"]) & (dm_partner[dm_key] >= 0)
moved = np.round(dsp_imps[m] * row_param[m]).astype(np.int64)
moved_rev = moved * cpm_row[m] / 1000
dsp_imps[m] -= moved
dsp_rev[m] -= moved_rev
extra = (dm_partner[dm_key][m], hour_ix[m], moved, moved_rev, deal_ix[m])

all_src = np.concatenate([deal_ix, extra[4]])  # deal that actually delivered (for FX/tz lookup)
all_rep = np.concatenate([rep_deal, extra[0]])
all_hour = np.concatenate([hour_ix, extra[1]])
all_imps = np.concatenate([dsp_imps, extra[2]])
all_rev = np.concatenate([dsp_rev, extra[3]])

tz_code = pd.Series(deal_dsp_tz[all_rep]).map({t: i for i, t in enumerate(TZS)}).to_numpy()
local_day = LOCAL_DAY[tz_code, all_hour]
fx_delta = np.where(dm_cause[all_src * N_MON + MON[all_hour]] == C["FX_MISMATCH"], dm_param[all_src * N_MON + MON[all_hour]], 0.0)

dsp_hourly = pd.DataFrame({"deal": all_rep, "local_day": local_day, "imps": all_imps, "rev_usd": all_rev, "fx_delta": fx_delta})
dsp_hourly = dsp_hourly[(dsp_hourly.local_day >= 0)]
dsp_daily = dsp_hourly.groupby(["deal", "local_day"], as_index=False).agg(
    imps=("imps", "sum"), rev_usd=("rev_usd", "sum"), fx_delta=("fx_delta", "max"))

# missing days: rows for k random days in the month never arrive
miss = []
for k in [k for k in active if dm_cause[k] == C["LATE_OR_MISSING_DATA"]]:
    i, mo = k // N_MON, k % N_MON
    days = np.flatnonzero((DATES.month - 1) == mo)
    days = days[(days >= d_start[i]) & (days <= d_end[i])]
    if len(days):
        for d in rng.choice(days, min(int(dm_param[k]), len(days)), replace=False):
            miss.append((i, d))
miss = pd.DataFrame(miss, columns=["deal", "local_day"]).assign(_drop=True)
dsp_daily = dsp_daily.merge(miss, how="left", on=["deal", "local_day"])
dsp_daily = dsp_daily[dsp_daily._drop.isna()].drop(columns="_drop")

cur = deal_cur[dsp_daily.deal.to_numpy()]
true_rate = np.select([cur == "EUR", cur == "GBP"], [FX["EUR"][dsp_daily.local_day], FX["GBP"][dsp_daily.local_day]], 1.0)
dsp_daily["native_amount"] = dsp_daily.rev_usd / (true_rate * (1 + dsp_daily.fx_delta))
dsp_daily["currency"] = cur
dsp_daily["dsp"] = d_dsp[dsp_daily.deal.to_numpy()]
print(f"{len(dsp_daily):,} DSP daily report rows")

# COMMAND ----------

# MAGIC %md ## Write landing files

# COMMAND ----------

if os.path.exists(ROOT):
    for sub in ["ssp_logs", "dsp_reports", "publisher_reports", "reference", "history"]:
        shutil.rmtree(os.path.join(ROOT, sub), ignore_errors=True)

ref = os.path.join(ROOT, "reference")
os.makedirs(ref, exist_ok=True)
# Partners' actual reporting timezone and IVT strictness are hidden behaviour, not reference data:
# contracts say "UTC", and the model has to discover a shift from the data itself.
dsps.drop(columns=["reporting_timezone", "ivt_vendor_strictness"]).to_csv(f"{ref}/dsps.csv", index=False)
dsp_contracts.to_csv(f"{ref}/dsp_contracts.csv", index=False)
publishers.drop(columns=["reporting_timezone"]).to_csv(f"{ref}/publishers.csv", index=False)
pub_contracts.to_csv(f"{ref}/publisher_contracts.csv", index=False)
deals.to_csv(f"{ref}/deals.csv", index=False)
fx_rates.to_csv(f"{ref}/fx_rates.csv", index=False)

# SSP logs: one gzip JSON-lines file per UTC day
ssp = pd.DataFrame({
    "event_hour_utc": HOURS.strftime("%Y-%m-%dT%H:00:00Z").to_numpy()[hour_ix],
    "deal_id": deals.deal_id.to_numpy()[deal_ix],
    "dsp_id": deals.dsp_id.to_numpy()[deal_ix],
    "seat_id": dsps.seat_id.to_numpy()[d_dsp[deal_ix]],
    "publisher_id": deals.publisher_id.to_numpy()[deal_ix],
    "impressions": imps,
    "gross_revenue_usd": rev.round(4),
    "log_source": "auction-svc-us-east-1",
})
ssp["_day"] = DAY[hour_ix]
os.makedirs(f"{ROOT}/ssp_logs", exist_ok=True)
for d, part in ssp.groupby("_day"):
    part.drop(columns="_day").to_json(f"{ROOT}/ssp_logs/ssp_auction_log_{DATE_STR[d]}.json.gz",
                                      orient="records", lines=True, compression="gzip")

# DSP reports: three partner formats, one CSV per DSP per partner-local month, with injected DQ defects
dq = {"null_deal_id": 0, "negative_impressions": 0, "bad_date": 0, "duplicate_rows": 0, "unknown_seat": 0}
dsp_daily["month"] = (DATES.month.to_numpy()[dsp_daily.local_day]).astype(int)
for (k, mo), part in dsp_daily.groupby(["dsp", "month"]):
    fmt = dsp_schema[k]
    dates = DATES[part.local_day.to_numpy()]
    if fmt == "A":
        out = pd.DataFrame({"report_date": dates.strftime("%Y-%m-%d"), "deal_id": deals.deal_id.to_numpy()[part.deal],
                            "impressions": part.imps.to_numpy(), "spend_usd": part.native_amount.round(2).to_numpy()})
        date_col, deal_col, imp_col, bad = "report_date", "deal_id", "impressions", "2026-02-30"
    elif fmt == "B":
        out = pd.DataFrame({"Date": dates.strftime("%m/%d/%Y"), "Deal ID": deals.deal_id.to_numpy()[part.deal],
                            "Imps": part.imps.to_numpy(), "Media Cost": part.native_amount.round(2).to_numpy(),
                            "Currency": part.currency.to_numpy()})
        date_col, deal_col, imp_col, bad = "Date", "Deal ID", "Imps", "13/45/2026"
    else:
        out = pd.DataFrame({"day": dates.strftime("%Y%m%d"), "seat_id": dsps.seat_id[k],
                            "deal_code": deals.dsp_deal_code.to_numpy()[part.deal],
                            "impressions_served": part.imps.to_numpy(), "gross_spend": part.native_amount.round(2).to_numpy()})
        date_col, deal_col, imp_col, bad = "day", "deal_code", "impressions_served", "20261341"
        u = rng.random(len(out)) < 0.003
        out.loc[u, "seat_id"] = "S-0000"
        dq["unknown_seat"] += int(u.sum())
    out = out.astype({deal_col: object, date_col: object})
    for key, col, val, p in [("null_deal_id", deal_col, None, 0.004), ("negative_impressions", imp_col, None, 0.002),
                             ("bad_date", date_col, bad, 0.002)]:
        hit = rng.random(len(out)) < p
        if key == "negative_impressions":
            out.loc[hit, col] = -out.loc[hit, col]
        else:
            out.loc[hit, col] = val
        dq[key] += int(hit.sum())
    dup = out.sample(frac=0.003, random_state=int(rng.integers(10**9)))
    dq["duplicate_rows"] += len(dup)
    out = pd.concat([out, dup]).sort_index(kind="stable")
    path = f"{ROOT}/dsp_reports/{dsps.dsp_id[k]}"
    os.makedirs(path, exist_ok=True)
    out.to_csv(f"{path}/{dsps.dsp_id[k]}_billing_2026-{mo:02d}.csv", index=False)

# Publisher ad server exports: publisher-local day, slightly lower counts, estimated payout
pub_tz = publishers.reporting_timezone.map({t: i for i, t in enumerate(TZS)}).to_numpy()
pi = d_pub[deal_ix]
pub = pd.DataFrame({
    "deal": deal_ix, "pub": pi, "local_day": LOCAL_DAY[pub_tz[pi], hour_ix],
    "imps": np.round(imps * (1 - pub_count_loss[pi]) * rng.normal(1, 0.004, len(imps))).astype(np.int64),
    "rev": rev * (1 - pub_count_loss[pi]) * pub_contracts.publisher_rev_share_pct.to_numpy()[pi] / 100,
})
pub = pub[pub.local_day >= 0].groupby(["pub", "deal", "local_day"], as_index=False)[["imps", "rev"]].sum()
pub["month"] = DATES.month.to_numpy()[pub.local_day]
for (p, mo), part in pub.groupby(["pub", "month"]):
    out = pd.DataFrame({
        "Date": DATES[part.local_day.to_numpy()].strftime("%Y-%m-%d"),
        "Ad unit": f"{publishers.publisher_id[p]}/ctv_midroll",
        "Programmatic deal ID": deals.deal_id.to_numpy()[part.deal],
        "Ad server impressions": part.imps.to_numpy(),
        "Estimated revenue ($)": part.rev.round(2).to_numpy(),
    })
    path = f"{ROOT}/publisher_reports/{publishers.publisher_id[p]}"
    os.makedirs(path, exist_ok=True)
    out.to_csv(f"{path}/{publishers.publisher_id[p]}_adserver_2026-{mo:02d}.csv", index=False)
print("landing files written")

# COMMAND ----------

# MAGIC %md ## Historical dispute resolutions (Jan–Jun) and ground truth

# COMMAND ----------

ssp_dm = pd.DataFrame({"k": dm_key, "ssp_impressions": imps, "ssp_revenue_usd": rev}).groupby("k").sum()
dsp_daily["k"] = dsp_daily.deal * N_MON + (dsp_daily.month - 1)
dsp_daily["dsp_revenue_usd"] = dsp_daily.native_amount * true_rate  # what silver will compute after FX
dsp_dm = dsp_daily.rename(columns={"imps": "dsp_impressions"}).groupby("k")[["dsp_impressions", "dsp_revenue_usd"]].sum()
gt = pd.DataFrame({"k": active})
gt["deal_idx"], gt["month_idx"] = gt.k // N_MON, gt.k % N_MON
gt = gt.join(ssp_dm, on="k").join(dsp_dm, on="k").fillna({"dsp_impressions": 0, "dsp_revenue_usd": 0})
gt["root_cause"] = np.array(CAUSES)[dm_cause[gt.k]]
gt["effect_param"] = dm_param[gt.k].round(4)
partner = dm_partner[gt.k]
gt["mismap_partner_deal_id"] = np.where(partner >= 0, deals.deal_id.to_numpy()[np.maximum(partner, 0)],
                                        np.where(partner <= -2, deals.deal_id.to_numpy()[np.maximum(-partner - 2, 0)], None))
gt["deal_id"] = deals.deal_id.to_numpy()[gt.deal_idx]
gt["dsp_id"] = deals.dsp_id.to_numpy()[gt.deal_idx]
gt["billing_month"] = [f"2026-{m + 1:02d}" for m in gt.month_idx]
gt["revenue_gap_usd"] = (gt.ssp_revenue_usd - gt.dsp_revenue_usd).round(2)
gt["revenue_gap_pct"] = (100 * gt.revenue_gap_usd / gt.ssp_revenue_usd).round(3)

hist = gt[(gt.month_idx < HISTORY_MONTHS) & ((gt.root_cause != "WITHIN_TOLERANCE") | (rng.random(len(gt)) < 0.2))].copy()
noisy = rng.random(len(hist)) < 0.05  # analysts occasionally record the wrong cause
hist["resolved_root_cause"] = np.where(noisy, rng.choice(CAUSES, len(hist)), hist.root_cause)
OUTCOME = {"WITHIN_TOLERANCE": ("NO_ADJUSTMENT", 0.0), "TIMEZONE_SHIFT": ("NO_ADJUSTMENT", 0.0),
           "IVT_FILTERING": ("CREDIT_ISSUED", 0.0), "SSAI_BEACON_LOSS": ("PARTIAL_RECOVERY", 0.4),
           "DEAL_ID_MISMAPPING": ("RECOVERED", 0.95), "FX_MISMATCH": ("RECOVERED", 0.9),
           "LATE_OR_MISSING_DATA": ("RECOVERED", 0.9), "GENUINE_BILLING_ERROR": ("PARTIAL_RECOVERY", 0.6)}
hist["resolution_outcome"] = hist.resolved_root_cause.map(lambda c: OUTCOME[c][0])
hist["recovered_usd"] = (hist.revenue_gap_usd.clip(lower=0) * hist.resolved_root_cause.map(lambda c: OUTCOME[c][1])).round(2)
hist["days_to_resolve"] = np.clip(rng.lognormal(np.log(19), 0.45, len(hist)), 2, 75).round().astype(int)
hist["resolved_by"] = rng.choice([f"billing.analyst{i}@apexexchange.example" for i in range(1, 7)], len(hist))
hist.insert(0, "case_id", [f"HC-{i:05d}" for i in range(1, len(hist) + 1)])
os.makedirs(f"{ROOT}/history", exist_ok=True)
hist[["case_id", "dsp_id", "deal_id", "billing_month", "ssp_impressions", "dsp_impressions", "ssp_revenue_usd",
      "dsp_revenue_usd", "revenue_gap_usd", "revenue_gap_pct", "resolved_root_cause", "resolution_outcome",
      "recovered_usd", "days_to_resolve", "resolved_by"]].round(2).to_csv(f"{ROOT}/history/dispute_resolutions.csv", index=False)

gt_out = gt[["deal_id", "dsp_id", "billing_month", "root_cause", "effect_param", "mismap_partner_deal_id",
             "ssp_impressions", "dsp_impressions", "ssp_revenue_usd", "dsp_revenue_usd", "revenue_gap_usd", "revenue_gap_pct"]].copy()
gt_out["is_history"] = gt.month_idx < HISTORY_MONTHS
if ON_DATABRICKS:
    spark.createDataFrame(gt_out).write.mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.ml.ground_truth_root_causes")
    spark.sql(f"COMMENT ON TABLE {CATALOG}.ml.ground_truth_root_causes IS "
              "'Planted root cause per deal-month from the synthetic generator. Evaluation only: never a model feature.'")
else:
    gt_out.to_csv(f"{ROOT}/_ground_truth.csv", index=False)

# COMMAND ----------

# MAGIC %md ## Generation summary

# COMMAND ----------


def count_files(sub):
    return sum(len(f) for _, _, f in os.walk(os.path.join(ROOT, sub)))


cur_gt = gt[gt.month_idx >= HISTORY_MONTHS]
summary = {
    "seed": SEED,
    "window": "2026-01-01..2026-09-30",
    "entities": {"dsps": N_DSP, "ctv_publishers": N_PUB, "deals": N_DEAL},
    "ssp_log_rows": int(len(ssp)),
    "total_impressions": int(imps.sum()),
    "gross_revenue_usd": round(float(rev.sum()), 2),
    "dsp_report_rows": int(len(dsp_daily)),
    "publisher_report_rows": int(len(pub)),
    "files": {s: count_files(s) for s in ["ssp_logs", "dsp_reports", "publisher_reports", "reference", "history"]},
    "dq_defects_injected": dq,
    "deal_months": int(len(gt)),
    "root_cause_distribution_all": gt.root_cause.value_counts().to_dict(),
    "historical_dispute_cases": int(len(hist)),
    "current_months_revenue_gap_usd_by_cause": cur_gt.groupby("root_cause").revenue_gap_usd.sum().round(0).to_dict(),
    "median_abs_gap_pct_by_cause": gt.groupby("root_cause").revenue_gap_pct.apply(lambda s: s.abs().median()).round(2).to_dict(),
}
print(json.dumps(summary, indent=2))

# COMMAND ----------

if ON_DATABRICKS:
    dbutils.notebook.exit(json.dumps(summary))
