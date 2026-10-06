"""Capture a Databricks job run as text evidence: task states and durations, each notebook's exit summary,
and, for pipeline tasks, the update state. Row counts and expectation results for pipeline updates come from the
pipeline event log via SQL (see evidence/sql/02_pipeline_evidence.sql), because the CLI event listing omits metrics.

Usage: python scripts/capture_job_run.py <run_id> evidence/<file>.md [--profile megan-fevm2]
"""
import argparse
import datetime as dt
import json
import subprocess


def cli(profile, *args):
    out = subprocess.run(["databricks", *args, "-p", profile, "-o", "json"], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return json.loads(out.stdout)


def ts(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if ms else ""


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("run_id")
    p.add_argument("out")
    p.add_argument("--profile", default="megan-fevm2")
    a = p.parse_args()
    run = cli(a.profile, "jobs", "get-run", a.run_id)
    md = [f"# Job run evidence: {run['run_name']}", "",
          f"- Run ID: `{run['run_id']}`  ",
          f"- Result: **{run['state'].get('result_state')}**  ",
          f"- Started: {ts(run.get('start_time'))}  ",
          f"- Ended: {ts(run.get('end_time'))}  ",
          f"- Run page: {run.get('run_page_url')}", "",
          "| Task | Result | Duration (min) |", "|---|---|---:|"]
    for t in run["tasks"]:
        dur = ((t.get("end_time") or 0) - (t.get("start_time") or 0)) / 60000
        md.append(f"| `{t['task_key']}` | {t['state'].get('result_state')} | {dur:.1f} |")
    for t in run["tasks"]:
        md += ["", f"## Task `{t['task_key']}`", ""]
        if "pipeline_task" in t:
            info = t.get("pipeline_task", {})
            upd = cli(a.profile, "pipelines", "list-updates", info["pipeline_id"]).get("updates", [{}])[0]
            md += [f"Pipeline `{info['pipeline_id']}`, update `{upd.get('update_id')}` → **{upd.get('state')}**", "",
                   "Rows written and expectation results: see `evidence/02_pipeline_evidence.md`."]
            continue
        out = cli(a.profile, "jobs", "get-run-output", str(t["run_id"]))
        result = out.get("notebook_output", {}).get("result")
        if out.get("error"):
            md += ["```", out["error"], out.get("error_trace", "")[-3000:], "```"]
        elif result:
            try:
                md += ["```json", json.dumps(json.loads(result), indent=2), "```"]
            except json.JSONDecodeError:
                md += ["```", result, "```"]
    open(a.out, "w").write("\n".join(md) + "\n")
    print(f"wrote {a.out}")
