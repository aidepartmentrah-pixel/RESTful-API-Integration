# Version Selector

A small WinForms desktop app for starting/stopping/restarting the
different locally-running versions of this mock API (v1.1 stable in its
own `git worktree`, v1.2-dev in the main working directory, etc.) without
memorizing `docker compose -p <project> up -d` for each one.

See the root-level plan (Period F) for why this exists: running multiple
API versions side by side (one stable for HCAT/HCopilot to build against,
one in active development) via `git worktree` + Docker Compose project
naming + per-version ports.

## Setup

1. Copy `local.versions.json.example` to `local.versions.json` at the
   **repo root** (not in this folder) and fill in your own worktree paths
   and ports. This file is gitignored — it's machine-specific.
2. `dotnet build VersionSelector.sln`
3. Run `VersionSelector/bin/Debug/net8.0-windows/VersionSelector.exe`, or
   `dotnet run --project VersionSelector`.

Requires Docker Desktop running and `docker` on `PATH`.

## How it finds the registry

By default the app walks up from its own `.exe` location looking for
`local.versions.json`, stopping at the repo root (the first `.git` folder
it finds). Override with the `VERSION_SELECTOR_REGISTRY` environment
variable (mainly used by tests).

## Architecture (why it's testable without real Docker)

`IDockerRunner` is the one seam between the UI and the actual `docker`
process:

- `RealDockerRunner` shells out to `docker` for real (`Process.Start`).
- `FakeDockerRunner` is an in-memory stand-in. The compiled EXE itself can
  be switched into using it via two environment variables
  (`VERSION_SELECTOR_FAKE_DOCKER_STATE` pointing at a small JSON fixture,
  `VERSION_SELECTOR_FAKE_DOCKER_LOG` where every invoked command gets
  appended as one JSON line) — this is what lets the fast FlaUI suite
  drive the real compiled app through real UI Automation clicks without
  ever touching real Docker.

Command construction (`DockerComposeCommandBuilder`) and `docker ps`
output parsing (`DockerPsParser`) are both pure, dependency-free classes,
unit-tested directly.

## Running the tests

```
cd tools/version-selector
dotnet test                              # everything, including the slow real one
dotnet test --filter "Category!=Slow"    # fast suite only (unit tests + FlaUI, fake Docker)
dotnet test --filter "Category=Slow"     # the one real end-to-end test
```

The **fast suite** (unit tests + FlaUI against `FakeDockerRunner`) has no
external dependencies and is safe to run anywhere, including CI.

The **slow suite** is one test:
`UiSlowEndToEndTests.StartAndStop_ThroughRealUi_ActuallyControlsThePort`.
It drives the real compiled EXE against real Docker and the real `mock-v11`
worktree from Period A (expects `../RESTful-API-Integration-v1.1` to
exist, per that worktree setup) — clicks Stop through the real UI and
confirms port 6000 actually stops responding, then clicks Start and
confirms it comes back. It leaves `mock-v11` running when it finishes
(best-effort, in a `finally`), matching this repo's normal working state.
Requires Docker Desktop running; skipped automatically if the v1.1
worktree isn't present.

## What's deliberately not here

No auto-update, no notion of "the current version" beyond what's in the
registry, no telemetry, no config beyond the one JSON file. This is a
convenience tool for local development, not a deployed product.
