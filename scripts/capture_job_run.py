"""Capture a Databricks job run as text evidence: task states and durations, each notebook's exit summary,
and, for pipeline tasks, row counts and data-quality expectation results from the pipeline event log.

Usage: python scripts/capture_job_run.py <run_id> evidence/<file>.md [--profile megan-fevm]
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


def pipeline_section(profile, pipeline_id, update_id):
    events = cli(profile, "pipelines", "list-pipeline-events", pipeline_id, "--max-results", "250")
    events = [e for e in events if e.get("origin", {}).get("update_id") == update_id]
    flows = {}
    for e in events:
        if e.get("event_type") != "flow_progress":
            continue
        fp = e.get("details", {}).get("flow_progress", {})
        if fp.get("status") != "COMPLETED":
            continue
        name = e["origin"].get("flow_name") or e["origin"].get("dataset_name")
        flows[name] = {"rows": fp.get("metrics", {}).get("num_output_rows"),
                       "dropped": fp.get("data_quality", {}).get("dropped_records"),
                       "expectations": fp.get("data_quality", {}).get("expectations", [])}
    lines = ["| Dataset | Output rows | Dropped by expectations |", "|---|---:|---:|"]
    for name in sorted(flows):
        f = flows[name]
        lines.append(f"| `{name}` | {f['rows'] if f['rows'] is not None else ''} | {f['dropped'] or ''} |")
    exp = [(n, x) for n, f in flows.items() for x in f["expectations"]]
    if exp:
        lines += ["", "**Expectation results**", "", "| Dataset | Expectation | Passed | Failed |", "|---|---|---:|---:|"]
        lines += [f"| `{n}` | {x['name']} | {x.get('passed_records', 0)} | {x.get('failed_records', 0)} |" for n, x in sorted(exp)]
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("run_id")
    p.add_argument("out")
    p.add_argument("--profile", default="megan-fevm")
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
                   pipeline_section(a.profile, info["pipeline_id"], upd.get("update_id"))]
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
