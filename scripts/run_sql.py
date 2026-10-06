"""Run a .sql file (statements separated by ';') on a Databricks SQL warehouse and print results.

Usage: python scripts/run_sql.py <file.sql> [--profile megan-fevm2] [--warehouse <id>]
Output is plain text so it can be captured into evidence/.
"""
import argparse
import json
import re
import subprocess
import time


def api(profile, method, path, body=None):
    cmd = ["databricks", "api", method, path, "-p", profile]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return json.loads(out.stdout) if out.stdout.strip() else {}


def split_statements(sql):
    sql = re.sub(r"--[^\n]*", "", sql)
    return [s.strip() for s in re.split(r";[ \t]*(?:\n|$)", sql) if s.strip()]


def run(profile, warehouse, statement):
    resp = api(profile, "post", "/api/2.0/sql/statements",
               {"warehouse_id": warehouse, "statement": statement, "wait_timeout": "50s"})
    while resp["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(3)
        resp = api(profile, "get", f"/api/2.0/sql/statements/{resp['statement_id']}")
    return resp


def fmt(resp):
    state = resp["status"]["state"]
    if state != "SUCCEEDED":
        return f"  -> {state}: {resp['status'].get('error', {}).get('message', '')}"
    cols = [c["name"] for c in resp.get("manifest", {}).get("schema", {}).get("columns", [])]
    rows = resp.get("result", {}).get("data_array", []) or []
    if not cols:
        return "  -> OK"
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join("" if v is None else str(v) for v in r) + " |" for r in rows]
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--profile", default="megan-fevm2")
    p.add_argument("--warehouse", default="93d767746e247a90")
    a = p.parse_args()
    failed = False
    for stmt in split_statements(open(a.file).read()):
        print(f"\n```sql\n{stmt}\n```")
        resp = run(a.profile, a.warehouse, stmt)
        print(fmt(resp))
        failed |= resp["status"]["state"] != "SUCCEEDED"
    raise SystemExit(1 if failed else 0)
