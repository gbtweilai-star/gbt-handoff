# Changelog

All notable changes to this package. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-10-28

### Added

- Capability contract for `handoff` (`system` domain), copied verbatim from the
  GBT V8 registry snapshot.
- `check()` — non-throwing contract validation.
- `run()` — validate-then-execute with a `Result` envelope that distinguishes
  `validated` from `ok`.
- `Backend` protocol plus `StubBackend`, so the package is usable as a typed
  seam before any implementation exists.
- CLI: `info`, `spec`, `check`, `run`.
- 18 tests, including a drift guard that pins the spec to the registry snapshot.
