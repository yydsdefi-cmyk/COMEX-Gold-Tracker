# COMEX-Gold-Tracker

Official CME Gold Stocks collection and public data feed.

See [CLOUD.md](CLOUD.md) for cloud schedules, consumer freshness checks and troubleshooting.

Local: Python 3.12+, `python -m pip install -r requirements.txt`, `python -m unittest discover -q`, `python -m comex_gold update`.

Free historical backfill: 26 original CME reports, Activity Dates 2026-08-28 through 2026-10-05. Latest 20 weekday candidates verified: 20/20. Archive copies retain original CME URLs, Internet Archive capture URLs/timestamps and verified hashes. Latest archived file matches current direct CME bytes. See [BACKFILL_VALIDATION.md](BACKFILL_VALIDATION.md).

5D and 10D are available for Total, Registered and Eligible, with separate absolute/percentage changes and baseline dates. Daily briefs read 1D/5D/10D/20D from the fresh cloud snapshot. 20D remains null because the window contains an unclassified holiday gap and a previous-balance discontinuity; the unexplained difference is not classified as physical withdrawal. Synthetic test dates never count as official reports.

40 offline tests pass. Daily collection and the original morning brief's cloud-data reading have been tested. No paid data or billed APIs are permitted; see [OPERATING_POLICY.md](OPERATING_POLICY.md).
