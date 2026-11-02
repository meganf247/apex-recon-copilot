"""Build the business deck (deck/apex_recon_deck.pptx). Every number comes from the committed evidence:
evidence/10_business_impact.md, 11_build_cost.md, 02_pipeline_evidence.md, 06_genie_benchmark.md,
01_build_job_run.md and evidence/notebook_runs/03_ml_and_disputes.md (job run 542978415804640).

Usage: python deck/build_deck.py            (needs python-pptx)
       soffice --headless --convert-to pdf --outdir deck deck/apex_recon_deck.pptx
"""
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# Brand + chart tokens. Data marks: slot-1 blue for the series that matters, recessive gray for context;
# the shortfall -> at risk -> exposure funnel uses a validated ordinal blue ramp. Red is a brand accent, never data.
NAVY, RED, INK, INK2, MUTED = "1B3139", "FF3621", "0B0B0B", "52514E", "898781"
SURFACE, PLANE, HAIR, GRAY = "FFFFFF", "F5F4F0", "E1E0D9", "C3C2B7"
BLUE, RAMP = "2A78D6", ["86B6EF", "3987E5", "1C5CAB"]
FONT = "Arial"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 12


def rgb(h):
    return RGBColor.from_string(h)


def text(slide, x, y, w, h, runs, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         spacing=1.1):
    """runs: a string, or a list of paragraphs, each a string or a list of (text, overrides) tuples."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap, tf.vertical_anchor = True, anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing = align, spacing
        for seg in (para if isinstance(para, list) else [(para, {})]):
            t, o = seg if isinstance(seg, tuple) else (seg, {})
            r = p.add_run()
            r.text = t
            f = r.font
            f.name, f.size = FONT, Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.color.rgb = rgb(o.get("color", color))
        if i < len(paras) - 1:
            p.space_after = Pt(o.get("after", 6) if paras else 6)
    return tb


def box(slide, x, y, w, h, fill=SURFACE, line=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    style = s._element.find(qn("p:style"))  # drop the theme style so no renderer adds a drop shadow
    if style is not None:
        s._element.remove(style)
    return s


def slide(kicker, headline, n):
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, 13.333, 7.5, fill=SURFACE)
    box(s, 0.6, 0.55, 0.08, 0.95, fill=RED)
    text(s, 0.85, 0.5, 11.5, 0.3, kicker.upper(), size=12, color=RED, bold=True)
    text(s, 0.85, 0.8, 11.8, 0.9, headline, size=26, color=NAVY, bold=True, spacing=1.0)
    text(s, 0.6, 7.05, 9, 0.25, "Apex Exchange · CTV Revenue Reconciliation Copilot · synthetic data", size=9, color=MUTED)
    text(s, 12.2, 7.05, 0.55, 0.25, f"{n} / {TOTAL}", size=9, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


def tile(s, x, y, w, h, value, label, sub=None, value_color=NAVY, fill=PLANE, vsize=36):
    box(s, x, y, w, h, fill=fill)
    text(s, x + 0.25, y + 0.2, w - 0.5, 0.75, value, size=vsize, color=value_color, bold=True)
    text(s, x + 0.25, y + 0.2 + vsize / 72 * 1.25, w - 0.5, 0.5, label, size=13, color=INK, bold=True)
    if sub:
        text(s, x + 0.25, y + 0.2 + vsize / 72 * 1.25 + 0.38, w - 0.5, h - 1.2, sub, size=11, color=INK2)


def bar_chart(s, x, y, w, h, cats, vals, colors, fmt='"$"0.0"M"', horizontal=True, label_size=12, max_v=None):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series("v", vals)
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    ch = s.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    ch.has_legend, ch.has_title = False, False
    ch.font.name, ch.font.size = FONT, Pt(label_size)
    ch.font.color.rgb = rgb(INK2)
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size, dl.font.bold = Pt(label_size), True
    dl.font.color.rgb = rgb(INK)
    ser = plot.series[0]
    for i, c in enumerate(colors):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(c)
        pt.format.line.fill.background()
    va, ca = ch.value_axis, ch.category_axis
    va.visible, va.has_major_gridlines = False, False
    va.minimum_scale = 0
    if max_v:
        va.maximum_scale = max_v
    ca.format.line.color.rgb = rgb(GRAY)
    ca.tick_labels.font.size = Pt(label_size)
    ca.tick_labels.font.color.rgb = rgb(INK)
    if horizontal:
        ca.reverse_order = True
    return ch


# ---------------- 1 · Title ----------------
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 13.333, 7.5, fill=NAVY)
box(s, 0.8, 2.0, 0.1, 2.4, fill=RED)
text(s, 1.15, 1.95, 11, 0.4, "APEX EXCHANGE · CTV REVENUE RECONCILIATION", size=14, color=RED, bold=True)
text(s, 1.15, 2.4, 11.2, 1.6, "Recover $4.7M a year that DSP billing gaps take from Apex's P&L",
     size=40, color="FFFFFF", bold=True, spacing=1.0)
text(s, 1.15, 3.85, 11, 0.6, "Close faster, recover more: an AI copilot for Finance and Billing Operations, on one governed platform",
     size=18, color="D9DEE2")
text(s, 1.15, 5.6, 11, 0.4, "For: CFO / VP Revenue Accounting · Director of Billing Operations · VP Data Engineering",
     size=13, color="AEB8BF")
text(s, 1.15, 6.0, 11, 0.4, "Apex Exchange is fictional; all data is synthetic.", size=11, color="AEB8BF")

# ---------------- 2 · Executive summary ----------------
s = slide("Executive summary", "Apex loses 14% of its net revenue to DSP billing gaps each quarter. Most of it is recoverable faster.", 2)
text(s, 0.85, 1.85, 6, 0.35, "TODAY (Q3 2026)", size=12, color=MUTED, bold=True)
tile(s, 0.85, 2.25, 3.75, 2.05, "$8.9M", "Apex net exposure per quarter", "14% of Q3 net revenue ($61.9M), after publisher pass-through", value_color=RED)
tile(s, 4.8, 2.25, 3.75, 2.05, "21 days", "to resolve one dispute", "p90: 33 days · ~270 cases a month")
tile(s, 8.75, 2.25, 3.75, 2.05, "55%", "right root cause on first look", "Analysts' rules of thumb on the 715 Q3 cases")
text(s, 0.85, 4.55, 6, 0.35, "WITH THE COPILOT", size=12, color=MUTED, bold=True)
tile(s, 0.85, 4.95, 3.75, 1.85, "$4.7M / yr", "back to Apex's P&L", "Every recoverable case pursued, not ~60%", value_color=BLUE, vsize=32)
tile(s, 4.8, 4.95, 3.75, 1.85, "≤ 7 days", "dispute cycle target", "≈ $2.8M cash released once", value_color=BLUE, vsize=32)
tile(s, 8.75, 4.95, 3.75, 1.85, "92%", "right root cause", "Model on the same 715 cases · ≈ 3 FTE redeployed", value_color=BLUE, vsize=32)

# ---------------- 3 · The problem: how the gap reaches the P&L ----------------
s = slide("The problem", "A $24M billing shortfall in Q3. $8.9M of it comes out of Apex's own P&L.", 3)
text(s, 0.85, 1.85, 6.4, 0.6, [[("From the gap with DSPs to Apex's own loss, Q3 2026", {"bold": True, "color": INK})]], size=14)
bar_chart(s, 0.7, 2.25, 6.6, 3.6, ["Billing shortfall\n(all deals)", "Revenue at risk\n(715 cases over tolerance)", "Apex net exposure\n(after publisher pass-through)"],
          [24.4, 18.1, 8.9], RAMP, max_v=30, label_size=13)
text(s, 0.85, 6.0, 6.4, 0.9, "Gross CTV spend in Q3 was $432M; Apex keeps a 14.3% take ($61.9M net revenue). "
     "The shortfall is 5.7% of gross; the exposure is 14% of Apex's net.", size=11, color=INK2)
box(s, 7.75, 1.95, 4.95, 4.85, fill=PLANE)
text(s, 8.05, 2.15, 4.4, 0.4, "Who absorbs the gap depends on the publisher's terms", size=14, color=NAVY, bold=True)
text(s, 8.05, 2.85, 4.4, 1.6, [
    [("Paid on Apex's count", {"bold": True, "color": INK})],
    [("279 cases · $7.3M at risk", {"color": INK2})],
    [("Apex still owes the publisher: ", {"color": INK2}), ("all $7.3M is Apex's loss", {"bold": True, "color": RED})],
], size=13)
text(s, 8.05, 4.45, 4.4, 1.6, [
    [("Paid on cleared revenue", {"bold": True, "color": INK})],
    [("436 cases · $10.8M at risk", {"color": INK2})],
    [("The publisher absorbs most of it: ", {"color": INK2}), ("Apex loses $1.6M", {"bold": True, "color": NAVY}),
     (" (its take), plus publisher goodwill", {"color": INK2})],
], size=13)
text(s, 8.05, 6.2, 4.4, 0.5, "39 of 40 DSPs had at least one case. Top 5 DSPs = 38% of revenue at risk.", size=11, color=INK2)

# ---------------- 4 · Root causes ----------------
s = slide("Why the counts don't match", "Five root causes, each with a different fix. Only two are worth chasing.", 4)
causes = ["IVT filtering", "Billing error", "Missing data", "Within tolerance", "Timezone shift"]
bar_chart(s, 0.7, 2.25, 6.3, 4.2, causes, [7.9, 5.2, 3.5, 0.8, 0.6], [GRAY, BLUE, BLUE, GRAY, GRAY], max_v=10, label_size=13)
text(s, 0.85, 6.5, 6.2, 0.4, [[("■ ", {"color": BLUE, "size": 14}), ("Chase: dispute and recover", {"color": INK}),
                              ("     ■ ", {"color": GRAY, "size": 14}), ("Credit, reporting fix or no action", {"color": INK})]], size=11)
text(s, 0.85, 1.85, 6, 0.3, "Q3 revenue at risk by root cause (model's call)", size=13, color=INK, bold=True)
rows = [("Billing error", "Unexplained under-reporting on some days", "Dispute with log evidence · 60% recovered historically"),
        ("Missing data", "Days missing from the DSP's report", "Get the days, then bill · 90% recovered"),
        ("IVT filtering", "DSP's fraud vendor removes spoofed CTV traffic", "Credit only third-party-verified IVT"),
        ("Timezone shift", "DSP reports in US time; primetime crosses midnight UTC", "Ask for UTC reporting; no billing change"),
        ("Within tolerance", "Daily noise flagged the deal; the month is within contract", "No action")]
y = 1.95
for name, what, fix in rows:
    chase = name in ("Billing error", "Missing data")
    box(s, 7.45, y, 0.07, 0.8, fill=BLUE if chase else GRAY)
    text(s, 7.7, y, 5.1, 0.85, [[(name, {"bold": True, "color": INK, "size": 13})], [(what, {"color": INK2})],
                                [(fix, {"color": NAVY if chase else INK2, "bold": chase})]], size=11, spacing=1.0)
    y += 0.97
text(s, 7.45, 6.8 - 0.05, 5.4, 0.3, "348 cases / $8.5M are IVT or timezone: a credit or a reporting fix, not a chase.", size=11, color=INK2)

# ---------------- 5 · Today vs tomorrow ----------------
s = slide("How it works for Billing Ops", "From spreadsheets and guesswork to one ranked queue with the cause and the draft ready", 5)
box(s, 0.85, 1.95, 11.65, 1.15, fill=PLANE)
text(s, 1.1, 2.08, 1.6, 0.9, "TODAY", size=13, color=MUTED, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 2.6, 2.08, 9.7, 0.9, "Download each DSP's file  →  spreadsheet lookups  →  guess the cause (right 55% of the time)  →  "
     "email back and forth for 21 days  →  write off what's left", size=14, color=INK2, anchor=MSO_ANCHOR.MIDDLE)
steps = [("1", "Ingest & check", "Partner files land and are quality-checked the same day", "Lakeflow"),
         ("2", "Reconcile", "Every deal vs. Apex's logs, daily and monthly, with Apex's net exposure", "Unity Catalog"),
         ("3", "Explain", "A model names the root cause; AI drafts the dispute from the evidence", "ML + GenAI"),
         ("4", "Resolve", "Analysts work one ranked queue; every action is logged", "App + Lakebase"),
         ("5", "Ask", "Finance asks questions in plain English, on governed numbers", "Genie")]
x = 0.85
for num, title, body, tech in steps:
    box(s, x, 3.45, 2.17, 3.25, fill=SURFACE, line=HAIR)
    c = box(s, x + 0.2, 3.65, 0.5, 0.5, fill=BLUE, shape=MSO_SHAPE.OVAL)
    text(s, x + 0.2, 3.65, 0.5, 0.5, num, size=16, color="FFFFFF", bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.2, 4.35, 1.85, 0.4, title, size=16, color=NAVY, bold=True)
    text(s, x + 0.2, 4.85, 1.85, 1.3, body, size=12, color=INK2)
    text(s, x + 0.2, 6.25, 1.85, 0.3, tech, size=11, color=BLUE, bold=True)
    x += 2.37

# ---------------- 6 · The workbench: same gap, different P&L ----------------
s = slide("The Reconciliation Workbench", "Two September cases with similar gaps: one costs Apex 6× more than the other", 6)
for i, (name, deal, gap, gap_pct, cause, terms, exp, note) in enumerate([
        ("Mosaic Bid", "Bluebird TV OS · Entertainment PMP", 252_043, "23% gap vs 5% threshold", "Billing error (100%)",
         "Publisher paid on cleared revenue · 13.4% take", 33_774, "Dispute it, but it's not the priority for Apex's P&L"),
        ("Umbra Ads", "Pinecrest Kids TV · Sports PMP", 203_794, "16% gap vs 5% threshold", "IVT filtering (100%)",
         "Publisher paid on Apex's count", 203_794, "Every dollar is Apex's: credit only verified IVT, recover the rest")]):
    x = 0.85 + i * 6.0
    box(s, x, 1.95, 5.65, 4.05, fill=PLANE)
    text(s, x + 0.3, 2.1, 5.1, 0.7, [[(name, {"bold": True, "color": NAVY, "size": 18})], [(deal, {"color": INK2, "size": 12})]], size=12)
    text(s, x + 0.3, 2.95, 2.5, 0.3, "Gap with the DSP", size=11, color=MUTED, bold=True)
    text(s, x + 0.3, 3.2, 2.5, 0.6, f"${gap:,.0f}", size=26, color=INK, bold=True)
    text(s, x + 2.9, 2.95, 2.5, 0.3, "Apex net exposure", size=11, color=MUTED, bold=True)
    text(s, x + 2.9, 3.2, 2.5, 0.6, f"${exp:,.0f}", size=26, color=RED if exp == gap else BLUE, bold=True)
    full = 4.9
    box(s, x + 0.3, 4.0, full, 0.22, fill=GRAY)
    box(s, x + 0.3, 4.0, full * exp / gap, 0.22, fill=BLUE)
    text(s, x + 0.3, 4.3, 5.1, 0.3, f"{exp / gap:.0%} of the gap hits Apex's P&L", size=11, color=INK2)
    text(s, x + 0.3, 4.75, 5.1, 1.2, [[("Model: ", {"color": INK2}), (cause, {"bold": True, "color": INK})],
                                       [(gap_pct + " · " + terms, {"color": INK2})],
                                       [(note, {"bold": True, "color": NAVY})]], size=12)
text(s, 0.85, 6.2, 11.7, 0.7, [[("In the app: ", {"bold": True, "color": INK}),
     ("Close overview (shortfall, revenue at risk, Apex exposure, recovered)  ·  Triage queue ranked by dollars, with the model's cause  ·  "
      "Case detail with evidence, AI summary and an editable dispute email  ·  Ask Genie", {"color": INK2})]], size=12)

# ---------------- 7 · AI you can trust ----------------
s = slide("AI you can check", "The model is right 92% of the time on the cases analysts work, vs. 55% today", 7)
text(s, 0.85, 1.85, 6, 0.3, "Right root cause on the 715 Q3 review cases (vs. true cause)", size=13, color=INK, bold=True)
bar_chart(s, 0.7, 2.2, 6.0, 3.3, ["Today's rules of thumb", "Copilot model"], [0.55, 0.92], [GRAY, BLUE],
          fmt="0%", max_v=1.1, label_size=14)
text(s, 0.85, 5.6, 5.9, 1.2, "Macro F1 0.91 vs 0.41. Trained on 1,615 resolved Jan–Jun disputes (with ~11% analyst labelling "
     "mistakes, like real life), tested on Jul–Sep. Analysts confirm or override every call, and that feedback retrains the model.",
     size=11, color=INK2)
checks = [("250", "dispute drafts from a JSON evidence pack, Claude via ai_query"),
          ("100%", "of dollar figures traced back to the evidence"),
          ("100%", "consistent with each contract's billing basis"),
          ("4.7 / 5", "accuracy from an independent AI judge (n = 30)"),
          ("14 / 14", "finance questions Genie answered correctly vs. reference SQL")]
y = 1.95
for v, l in checks:
    box(s, 7.45, y, 5.05, 0.85, fill=PLANE)
    text(s, 7.7, y, 1.45, 0.85, v, size=22, color=BLUE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 9.2, y, 3.15, 0.85, l, size=12, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    y += 0.97

# ---------------- 8 · KPI impact ----------------
s = slide("Impact on your KPIs", "≈ $4.7M a year to Apex's P&L, ≈ $2.8M of cash released and ≈ 3 analysts' capacity back", 8)
rows = [("KPI", "Owner", "Baseline (Q3 2026)", "Target", "Annual value"),
        ("Net revenue recovered", "CFO", "$3.0M recoverable to Apex's P&L per quarter; ~60% of cases worked today*", "Pursue every recoverable case", "≈ $4.7M / year to P&L (≈ $10M gross cash)"),
        ("Dispute cycle time / DSO", "CFO", "21 days avg · 33 days p90", "≤ 7 days", "≈ $2.8M cash released once (~$200K/day × 14 days)"),
        ("Analyst effort", "Billing Ops", "~270 cases/month × ~2.5 h* ≈ 4.2 FTE", "~45 min per case", "≈ 3 FTE redeployed"),
        ("Right fix first time", "Billing Ops", "Right cause 55% of the time", "92% (model)", "348 cases/quarter go straight to a credit or reporting fix"),
        ("Month-end close", "CFO", "~10 business days*", "~4 days", "Faster, auditable close")]
tbl = s.shapes.add_table(len(rows), 5, Inches(0.85), Inches(1.95), Inches(11.65), Inches(4.4)).table
for c, wdt in enumerate([2.2, 1.25, 3.4, 2.2, 2.6]):
    tbl.columns[c].width = Inches(wdt)
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(NAVY if r == 0 else (PLANE if r % 2 == 0 else SURFACE))
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = val
        run.font.name, run.font.size = FONT, Pt(12 if r else 12)
        run.font.bold = r == 0 or c in (0, 4)
        run.font.color.rgb = rgb("FFFFFF" if r == 0 else (BLUE if c == 4 else INK))
text(s, 0.85, 6.5, 11.6, 0.4, "* Assumptions to validate in discovery: today's coverage (60%), effort per case (2.5 h), close length (10 days), "
     "and publisher payment terms by deal. Everything else is computed from the build's data.", size=10, color=INK2)

# ---------------- 9 · Cost and ROI ----------------
s = slide("What it costs to run", "≈ $55K a year to run at full volume, for ≈ $4.7M a year to the P&L", 9)
tile(s, 0.85, 1.95, 3.6, 2.2, "~85×", "annual return", "$4.7M to Apex's P&L vs ≈ $55K run cost, before cash and capacity gains", value_color=BLUE, vsize=44)
tile(s, 0.85, 4.35, 3.6, 2.35, "$3.80", "per full daily run, measured", "Ingest, reconcile, retrain the model and draft 250 disputes in ~9 minutes", vsize=36)
rows = [("Component", "Measured on this build (list price)", "Annual estimate"),
        ("Daily build: pipeline, model, AI drafts", "≈ $3.80 per run (6 runs in October)", "≈ $1.4K"),
        ("Reconciliation Workbench app", "≈ $11 per day, always on", "≈ $4K"),
        ("Lakebase case store + sync", "< $1 for the month", "negligible"),
        ("Total at build scale", "", "≈ $5.4K"),
        ("Budget at Apex's full volume (10×)", "", "≈ $55K")]
tbl = s.shapes.add_table(len(rows), 3, Inches(4.75), Inches(1.95), Inches(7.75), Inches(3.6)).table
for c, wdt in enumerate([3.2, 3.0, 1.55]):
    tbl.columns[c].width = Inches(wdt)
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(NAVY if r == 0 else (PLANE if r >= 4 else SURFACE))
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        run = cell.text_frame.paragraphs[0].add_run()
        run.text = val
        run.font.name, run.font.size = FONT, Pt(13)
        run.font.bold = r == 0 or r >= 4
        run.font.color.rgb = rgb("FFFFFF" if r == 0 else INK)
        if c == 2:
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT
text(s, 4.75, 5.8, 7.75, 0.9, "Measured from Databricks system billing tables for this build (evidence/11_build_cost). All compute is "
     "serverless and can be capped with budget policies. The SQL warehouse is shared, so it isn't included.", size=11, color=INK2)

# ---------------- 10 · For each stakeholder ----------------
s = slide("What each of you gets", "One platform, three wins", 10)
cols = [("CFO / VP Revenue Accounting", [
            ("More net revenue, sooner", "≈ $4.7M a year to the P&L, plus faster collection"),
            ("Your real exposure", "Every gap split into what Apex absorbs vs. what passes through, by partner, deal and cause"),
            ("Audit-ready controls", "Lineage from partner file to invoice; every analyst action logged; Finance-only dollars")]),
        ("Director of Billing Operations", [
            ("One ranked queue", "Work the dollars that hit Apex first"),
            ("Right cause, ready draft", "92% right on first look; dispute drafted from evidence and contract"),
            ("By the book", "Credit only verified IVT; bad partner files caught on arrival")]),
        ("VP Data Engineering", [
            ("One governed platform", "Ingest, ML, case workflow and NL questions without copying data across tools"),
            ("Policies in the platform", "Row filters and masks on every table, including Genie's"),
            ("Simple to run", "One bundle, one serverless job, ~9 minutes a day")])]
for i, (who, items) in enumerate(cols):
    x = 0.85 + i * 3.95
    box(s, x, 1.95, 3.7, 4.85, fill=PLANE)
    box(s, x, 1.95, 3.7, 0.08, fill=BLUE)
    text(s, x + 0.25, 2.2, 3.2, 0.5, who, size=15, color=NAVY, bold=True)
    y = 2.85
    for head, body in items:
        text(s, x + 0.25, y, 3.2, 1.25, [[(head, {"bold": True, "color": INK, "size": 13})], [(body, {"color": INK2})]], size=12)
        y += 1.3

# ---------------- 11 · Architecture and proof ----------------
s = slide("How it's built, and proof it runs", "End to end on Databricks, from raw partner files to the analyst's workbench", 11)
stages = [("Lakeflow", "Auto Loader + declarative pipeline · bronze → silver → gold · 4 data-quality rules"),
          ("Unity Catalog", "Row filters + column masks on every queryable table · tags · lineage"),
          ("ML + GenAI", "Root-cause model in MLflow @champion · Claude drafts via ai_query, auto-checked"),
          ("Lakebase", "Postgres case store: status, audit trail, credits · live in Unity Catalog"),
          ("Genie", "Plain-English questions on the same governed numbers"),
          ("Databricks App", "Reconciliation Workbench for Finance and Billing Ops")]
x = 0.85
for i, (name, body) in enumerate(stages):
    box(s, x, 1.95, 1.8, 2.3, fill=PLANE)
    box(s, x, 1.95, 1.8, 0.08, fill=BLUE)
    text(s, x + 0.15, 2.15, 1.55, 0.4, name, size=14, color=NAVY, bold=True)
    text(s, x + 0.15, 2.6, 1.55, 1.6, body, size=11, color=INK2)
    if i < len(stages) - 1:
        text(s, x + 1.8, 2.85, 0.17, 0.4, "›", size=20, color=MUTED, align=PP_ALIGN.CENTER)
    x += 1.97
text(s, 0.85, 4.5, 11.6, 0.35, "PROOF FROM THE COMMITTED RUN OUTPUT", size=12, color=MUTED, bold=True)
proof = [("3.57M", "hourly log rows · 158K DSP report rows · 9 months · 40 DSPs · 800 deals"),
         ("1,728", "bad partner rows caught by the quality rules before billing"),
         ("92% · 0.91", "model accuracy · macro F1 on the 715 Q3 cases"),
         ("14 / 14", "Genie answers match reference SQL"),
         ("PASS", "app test: open → send → resolve with a verified IVT credit, live in Lakebase and UC")]
x = 0.85
for v, l in proof:
    text(s, x, 4.95, 2.2, 0.55, v, size=24, color=BLUE, bold=True)
    text(s, x, 5.55, 2.15, 1.2, l, size=11, color=INK2)
    x += 2.37

# ---------------- 12 · Rollout and ask ----------------
s = slide("Rollout plan and next steps", "A 30-day pilot on the top 5 DSPs, with success criteria agreed up front", 12)
phases = [("Days 0–30", "Pilot", "Top 5 DSPs (38% of revenue at risk) on Apex's real files, alongside the spreadsheets",
           "Root-cause agreement with analysts ≥ 85%"),
          ("Days 31–60", "Scale", "All 40 DSPs; analysts sign in with their own access (on-behalf-of-user)", "Cycle time ≤ 10 days"),
          ("Days 61–90", "Run", "Retire the spreadsheet process; retrain on analyst-confirmed causes", "Cycle time ≤ 7 days, close ≤ 4 days")]
box(s, 0.85, 2.35, 11.65, 0.06, fill=HAIR)
x = 0.85
for when, name, what, ok in phases:
    box(s, x, 2.2, 0.35, 0.35, fill=BLUE, shape=MSO_SHAPE.OVAL)
    text(s, x, 1.85, 3.6, 0.3, when.upper(), size=11, color=MUTED, bold=True)
    text(s, x, 2.7, 3.6, 0.4, name, size=18, color=NAVY, bold=True)
    text(s, x, 3.15, 3.6, 0.9, what, size=12, color=INK2)
    text(s, x, 4.05, 3.6, 0.6, [[("Success: ", {"bold": True, "color": INK}), (ok, {"color": INK})]], size=12)
    x += 3.95
box(s, 0.85, 4.95, 11.65, 1.85, fill=NAVY)
text(s, 1.15, 5.1, 3.0, 0.4, "WHAT WE'RE ASKING FOR", size=12, color=RED, bold=True)
text(s, 1.15, 5.5, 11.1, 1.3, [
    [("1  Discovery session with Billing Ops ", {"bold": True, "color": "FFFFFF"}),
     ("to confirm coverage, effort per case, close length and publisher payment terms", {"color": "D9DEE2"})],
    [("2  One month of data ", {"bold": True, "color": "FFFFFF"}), ("auction log extracts + billing files for the top 5 DSPs", {"color": "D9DEE2"})],
    [("3  A pilot sponsor ", {"bold": True, "color": "FFFFFF"}),
     ("in Revenue Accounting, with a day-30 readout on recovered dollars and cycle time", {"color": "D9DEE2"})],
], size=13)

out = Path(__file__).with_name("apex_recon_deck.pptx")
prs.save(out)
print(f"wrote {out} ({len(prs.slides)} slides)")
