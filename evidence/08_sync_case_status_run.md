# Job run evidence: [dev megan_fogal] apex-recon-build

- Run ID: `414831119517187`  
- Result: **SUCCESS**  
- Started: 2026-10-05 16:01:34 UTC  
- Ended: 2026-10-05 16:03:13 UTC  
- Run page: https://fevm-serverless-3dmees.cloud.databricks.com/?o=7474652285429726#job/602392988880313/run/414831119517187

| Task | Result | Duration (min) |
|---|---|---:|
| `generate_data` | DISABLED | 0.0 |
| `ingest_and_reconcile` | DISABLED | 0.0 |
| `sync_case_status_to_uc` | FAILED | 0.5 |
| `sync_case_status_to_uc` | SUCCESS | 1.1 |
| `train_root_cause_model` | DISABLED | 0.0 |
| `score_and_draft_disputes` | DISABLED | 0.0 |

## Task `generate_data`


## Task `ingest_and_reconcile`

Pipeline `5d44a671-5813-463d-903e-33ca04bb3376`, update `b22496e9-3dfb-44ba-9e37-b8a8fc495095` → **COMPLETED**

Rows written and expectation results: see `evidence/02_pipeline_evidence.md`.

## Task `sync_case_status_to_uc`

```
The Python process exited unexpectedly with an abort signal (SIGABRT).
Please contact Databricks support and provide the trace ID: 7474652285429726/602392988880313/414831119517187/486557697904058.
[0m
[0;31m  File "/databricks/python/lib/python3.12/site-packages/ipykernel/kernelbase.py", line 508 in process_one[0m
[0;31m  File "/databricks/python/lib/python3.12/site-packages/ipykernel/kernelbase.py", line 519 in dispatch_queue[0m
[0;31m  File "/usr/lib/python3.12/asyncio/events.py", line 88 in _run[0m
[0;31m  File "/usr/lib/python3.12/asyncio/base_events.py", line 1987 in _run_once[0m
[0;31m  File "/usr/lib/python3.12/asyncio/base_events.py", line 641 in run_forever[0m
[0;31m  File "/databricks/python/lib/python3.12/site-packages/tornado/platform/asyncio.py", line 211 in start[0m
[0;31m  File "/databricks/python/lib/python3.12/site-packages/ipykernel/kernelapp.py", line 739 in start[0m
[0;31m  File "/databricks/python/lib/python3.12/site-packages/traitlets/config/application.py", line 1075 in launch_instance[0m
[0;31m  File "/databricks/python_shell/scripts/db_ipykernel_launcher.py", line 76 in main[0m
[0;31m  File "/databricks/python_shell/scripts/db_ipykernel_launcher.py", line 80 in <module>[0m
[0;31m[0m
[0;31mExtension modules: zmq.backend.cython._zmq, tornado.speedups, psutil._psutil_linux, psutil._psutil_posix, google._upb._message, _cython.cygrpc, third_party.python.vendor.grpc._cython.cygrpc, numpy._core._multiarray_umath, numpy.linalg._umath_linalg, pyarrow.lib, numpy.random._common, numpy.random.bit_generator, numpy.random._bounded_integers, numpy.random._pcg64, numpy.random._mt19937, numpy.random._generator, numpy.random._philox, numpy.random._sfc64, numpy.random.mtrand, pandas._libs.tslibs.ccalendar, pandas._libs.tslibs.np_datetime, pandas._libs.tslibs.dtypes, pandas._libs.tslibs.base, pandas._libs.tslibs.nattype, pandas._libs.tslibs.timezones, pandas._libs.tslibs.fields, pandas._libs.tslibs.timedeltas, pandas._libs.tslibs.tzconversion, pandas._libs.tslibs.timestamps, pandas._libs.properties, pandas._libs.tslibs.offsets, pandas._libs.tslibs.strptime, pandas._libs.tslibs.parsing, pandas._libs.tslibs.conversion, pandas._libs.tslibs.period, pandas._libs.tslibs.vectorized, pandas._libs.ops_dispatch, pandas._libs.missing, pandas._libs.hashtable, pandas._libs.algos, pandas._libs.interval, pandas._libs.lib, pyarrow._compute, pandas._libs.ops, pandas._libs.hashing, pandas._libs.arrays, pandas._libs.tslib, pandas._libs.sparse, pandas._libs.internals, pandas._libs.indexing, pandas._libs.index, pandas._libs.writers, pandas._libs.join, pandas._libs.window.aggregations, pandas._libs.window.indexers, pandas._libs.reshape, pandas._libs.groupby, pandas._libs.json, pandas._libs.parsers, pandas._libs.testing, grpc._cython.cygrpc, zstandard.backend_c, charset_normalizer.md, requests.packages.charset_normalizer.md, requests.packages.chardet.md (total: 65)[0m
[0;31m---------------------------------------------------------------------------[0m
[0;31mLast messages on stdout:[0m
[0;31m1[0m
[0;31mNote: you may need to restart the kernel using %restart_python or dbutils.library.restartPython() to use updated packages.[0m
```

## Task `sync_case_status_to_uc`

```json
{
  "rows_snapshotted": {
    "dispute_cases": 2,
    "case_events": 7,
    "credit_approvals": 1
  },
  "status_summary": [
    {
      "status": "OPEN",
      "cases": 919,
      "revenue_at_risk_usd": 22082660.0,
      "recovered_usd": 0.0,
      "credited_usd": 0.0
    },
    {
      "status": "RESOLVED",
      "cases": 2,
      "revenue_at_risk_usd": 562710.0,
      "recovered_usd": 423608.0,
      "credited_usd": 139101.0
    }
  ]
}
```

## Task `train_root_cause_model`


## Task `score_and_draft_disputes`

