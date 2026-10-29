# Contributing

Start with `xp-github-prompt.md` and `docs/DESIGN.md`. The initial portable skill is implemented. Read `docs/VERIFY.md` for its tested behavior and remaining limits; do not represent smoke tests as full client integration tests.

Prefer a small change tied to a concrete XP use case. Explain the user-visible behavior and how you verified it. Keep shared skill content host-neutral and API facts linked to current official documentation. Do not add a local planning database or model-specific runtime dependency.

Keep source checkouts in ignored `_sources/`. Do not commit supplied PDFs or screenshots without verifying redistribution rights. Record copied or adapted material, its pinned source, and license in `NOTICE.md` and retain required license notices.

For the implementation, follow the offline and sandbox verification requirements in the build prompt. Never run integration tests against an arbitrary repository or Project; use the explicitly named test targets. Documentation-only contributions need link and consistency checks, not a live GitHub mutation test.
