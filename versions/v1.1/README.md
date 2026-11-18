# v1.1 — currently deployed baseline

**Status: live.** This is the contract currently deployed in the air-gapped
production environment. Both HCAT and HCopilot are built against this
version today.

- Spec: `Hospital_Directory_API_OpenAPI_v1.1.yaml` (verbatim copy of what
  the vendor sent).
- Rationale for how this differs from the earlier v1.0.0 spec and from
  real-server evidence: see
  `vendor-deliverable/2026-09-08_v1.1-gap-analysis.md` (not duplicated
  here — that document already covers it in full).
- Evidence citations specific to this version: `evidence.md`.
- Acceptance test: `acceptance_tests/verify_contract_alignment.ps1` — run
  it against any instance claiming to implement v1.1.

## Confirmed working

Run against a locally built instance of this exact tag (`git worktree` from
the `v1.1.0` git tag, port 6000 in this project's local dev setup):

```
34 passed, 0 failed — 100% pass
```

No open items for this version — it is not under active change.

## Maintenance (18 Nov 2026)

The v1.1 mock (port 6000) runs from branch `v1.1-maint` (starts at the
v1.1 contract commit `5924328`). One change: it also answers on the real
Directory path `/his-general/api/directory/v1`, so clients switch between
mock and real (`http://malin:8080/his-general/api/directory/v1`) by
changing only the host. Its key is now `dev-secret-key`, like the real
server. The contract itself is unchanged.
