"""Export an executed notebook task run as text: a Markdown file and an .ipynb, both with cell outputs.

Usage: python3 scripts/export_notebook_run.py <task_run_id> <out_basename> [--job-run <id>] [--profile megan-fevm2]
Writes <out_basename>.md and <out_basename>.ipynb.
"""
import argparse
import base64
import json
import re
import subprocess
import urllib.parse

p = argparse.ArgumentParser()
p.add_argument("run_id")
p.add_argument("out")
p.add_argument("--profile", default="megan-fevm2")
p.add_argument("--job-run", default="", help="parent job run ID, for the header")
a = p.parse_args()

run = json.loads(subprocess.check_output(["databricks", "jobs", "get-run", a.run_id, "-p", a.profile, "-o", "json"]))
export = json.loads(subprocess.check_output(["databricks", "jobs", "export-run", a.run_id, "--views-to-export", "CODE",
                                             "-p", a.profile, "-o", "json"]))
html = export["views"][0]["content"]
encoded = re.search(r"__DATABRICKS_NOTEBOOK_MODEL = '([^']+)'", html).group(1)
model = json.loads(urllib.parse.unquote(base64.b64decode(encoded).decode()))
cells = sorted(model["commands"], key=lambda c: c["position"])


def output_text(c):
    r = c.get("results") or {}
    if r.get("type") == "listResults":
        text = "".join(x["data"] for x in r["data"] if isinstance(x.get("data"), str))
        return "\n".join(l for l in text.split("\n") if "Effective usage policy" not in l)  # Spark Connect session noise
    if r.get("type") in ("raw", "html") and isinstance(r.get("data"), str):
        return ("Notebook exit value:\n" if "dbutils.notebook.exit" in c["command"] else "") + r["data"]
    return ""


notebook = run["task"]["notebook_task"]["notebook_path"] if "task" in run else ""
notebook = run.get("tasks", [{}])[0].get("notebook_task", {}).get("notebook_path", notebook)
md = [f"# Executed notebook: `{notebook.split('/')[-1]}`", "",
      f"- Task run ID: `{a.run_id}`" + (f" (job run `{a.job_run}`)" if a.job_run else ""),
      f"- Result: **{run['state'].get('result_state')}**",
      f"- Run page: {run.get('run_page_url', '')}",
      "- Every cell below is shown with the output it produced in that run.", ""]
nb_cells = []
for c in cells:
    src = c["command"]
    out = output_text(c)
    if src.lstrip().startswith("%md"):
        body = re.sub(r"^\s*%md ?", "", src)
        md += [body.strip(), ""]
        nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": body.strip()})
        continue
    md += ["```python", src.strip(), "```", ""]
    if out.strip():
        md += ["Output:", "", "```text", out.rstrip(), "```", ""]
    nb_cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "source": src.strip(),
                     "outputs": [{"output_type": "stream", "name": "stdout", "text": out}] if out.strip() else []})

open(f"{a.out}.md", "w").write("\n".join(md))
json.dump({"cells": nb_cells, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                                           "language_info": {"name": "python"}},
           "nbformat": 4, "nbformat_minor": 5}, open(f"{a.out}.ipynb", "w"), indent=1)
print(f"{len(cells)} cells -> {a.out}.md, {a.out}.ipynb")
