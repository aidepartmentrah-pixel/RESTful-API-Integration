Source: `C:\Users\it\Desktop\New API Check\Thought on Workers API.txt` (verbatim,
copied 2026-08-25). This is the analysis written right after the first
real-server captures (see `raw-http-capture.txt` in this folder) showed the
worker endpoint behaving suspiciously. It was later independently reconfirmed
by `Test-HospitalDirectoryAPI-Full.ps1` on 2026-08-25 — see
`../2026-08-25_muslim-arabic-toolkit-run/report.md`, area `worker_search`,
which found `q='بلال' total=1668; no-q total=1668; SAME=True`.

---

Idea for workers, to save for later:

Workers is a fundamentally different problem than patients — patients was a
validation fix (reject bad input); workers has no server-side search at all.
Confirmed: `/workers?q=Abbas` and `/workers?q=` (nothing) return the identical
total and identical items — the real API silently ignores `q` entirely.

That means the fix can't live in validation — there's nothing to validate
against. The only path is client-side filtering: pull a batch of workers from
the real API and filter by name yourself, since the server won't do it for
you. Two things to decide when we get there:

- Where to filter: in HCAT's backend (`hospital_directory_client.py` fetches a
  page/list and filters before returning to the frontend) rather than the
  frontend, so the browser never sees an unfiltered dump.
- How much to fetch: the real system has ~1,668 workers total. Pulling all of
  them on every keystroke is wasteful. Realistic options: (a) fetch once,
  cache in memory/DB with a refresh interval, then filter the cache — most
  correct, more work; (b) fetch a single large page (e.g. `limit=500`) per
  search and filter just that batch — simpler, but could miss matches outside
  the first batch. Worth deciding once we're actually there.

Also, the mock currently does filter on `q` for workers — which is itself now
a similar mismatch to what patients had, just in the opposite direction (mock
does something the real server doesn't). We'll likely want to make the mock
stop honoring `q` for workers too, so testing against the mock doesn't give
false confidence — same "spitting image" logic as the patients fix, just
inverted.

That's the shape of it — nothing built yet, just the plan to pick up once
patients is fully closed out on your end.
