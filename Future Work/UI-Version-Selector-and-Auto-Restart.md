# Future idea: a small desktop tool to select and switch mock API versions

**Status:** idea only, not built, not scheduled. Captured here so it isn't
lost, not because it's blocking anything — the manual version of this
(edit a JSON, click restart in Docker Desktop) already works fine.

## The idea

A small desktop app (the owner's own idea to build this in C#, as a
personal/fun toolkit project) that:

1. Reads the local version-registry file at the repo root (whatever it
   ends up being named — see the "current manual mechanism" note below)
   listing which `versions/vX.Y/` folders exist and which Docker Compose
   project + port each one runs on.
2. Shows the available versions in a simple UI (a list or a couple of
   buttons — "v1.1 (stable, :6000)", "v1.2-draft (dev, :6001)").
3. On selection, does what a human currently does by hand: brings up the
   chosen version's Docker Compose project (`docker compose -p <name> up -d`
   in the right worktree folder) and optionally stops others if the goal
   is "only one running at a time" rather than "both always running."
4. Shows current status per version (running / stopped), so it doubles as
   the "what's currently active" dashboard this project doesn't have yet.

## Why this is genuinely a future item, not a now item

The problem it solves — "which port is which version" — is already solved
today by: naming Docker Compose projects clearly (`mock-v11`, `mock-v12-dev`)
and using Docker Desktop's own UI to start/stop/restart them. A GUI on top
of that is a nice-to-have that removes a small amount of friction, not a
missing capability. Worth building when it sounds fun to build, not before.

## Where this would plug in, when it happens

- Reads the same local, gitignored JSON that names "which version is on
  which port" (see the repo root — this file is the source of truth this
  tool would consume, not something the tool invents its own format for).
- Acts entirely through `docker compose -p <name> ...` commands against
  the relevant `git worktree` checkout directory for each version — no new
  server-side mechanism, no changes to the mock's own code, no changes to
  what gets shown to the vendor. Purely a local convenience layer on top
  of tooling that already exists.
- Not part of any version's contract, requirements, or acceptance tests —
  this is developer tooling, never something 3iSoft would see or care
  about.

## Open design questions, for whenever this gets picked up

- One-running-at-a-time (simpler dashboard, saner resource use) vs.
  always-both-running (nothing to switch, but doesn't scale past a
  couple of versions) — probably worth making this a setting rather than
  picking one forever.
- Whether it should also *create* a new worktree for a brand-new version
  folder, or only manage versions that already exist.
- Whether "restart" should be a real Docker API call (via the Docker
  Engine API/SDK) or just shelling out to `docker compose` under the
  hood — shelling out is simpler and probably fine for a personal tool.
