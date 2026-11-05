# GitHub Copilot Instructions — CHAMP_SUPER_ANTELLIGENT

## Canonical identity and architecture

- The canonical system name is `CHAMP_SUPER_ANTELLIGENT`. Never rename it unless the owner explicitly requests that change.
- Current AI providers are Meta, Gemini, and Modal (`meta`, `gemini`, `modal`).
- Preserve the deterministic-first pipeline:

  ```text
  USER INPUT
  -> VALIDATION
  -> DETERMINISTIC DOMAIN ENGINES
  -> VERIFIED DOMAIN RESULT
  -> AI EXPLANATION ONLY
  -> STRUCTURED RESPONSE
  -> AUDIT
  ```

- Core principle: **Evidence > Claims**.
- Deterministic engines calculate. AI providers explain verified deterministic results.
- AI must never invent or silently alter BOQ, costs, quantities, soil data, foundation data, plant data, material data, sustainability scores, or engineering values.

## Maintenance behavior

For each maintenance task:

1. Inspect the existing source before editing.
2. Inspect relevant tests and repository instructions.
3. Prefer repairing existing implementation over rebuilding; update existing files in place when practical.
4. Avoid duplicate implementations and preserve canonical names.
5. Make the smallest sufficient patch.
6. Add or update tests for behavioral changes.
7. Run tests when execution tools are available and report exact execution evidence. If unavailable, say `BLOCKED` or `UNKNOWN`; never imply tests passed.
8. Check whether README documentation needs an update when executable behavior changes.

## Evidence and claims

Use only evidence-supported classifications: `VERIFIED`, `PARTIAL`, `NOT VERIFIED`, `BLOCKED`, `DOCUMENTATION ONLY`, and `UNKNOWN`. Do not upgrade a classification without relevant execution evidence. Keep historical evidence clearly historical; do not present it as a new/current run.

Do not claim `PRODUCTION READY`, `LIVE VERIFIED`, `CERTIFIED`, or `FULLY COMPLIANT` unless direct evidence proves that exact claim.

For provider readiness, distinguish code presence/configuration from a successful live request. Use `CODE READY`, `CONFIGURED`, `NOT CONFIGURED`, `BLOCKED`, or `UNKNOWN` as warranted. Call a provider `LIVE VERIFIED` only after an actual authenticated request succeeds and its evidence is captured.

## Deterministic engine protection

Treat these as protected domain logic:

- `engines/boq_engine.py`
- `engines/soil_engine.py`
- `engines/foundation_engine.py`
- `engines/plant_engine.py`
- `engines/material_engine.py`
- `engines/leed_engine.py`

Do not change deterministic formulas or business values merely to make tests pass or match historical targets. If a test conflicts with domain output, stop and report the failing test, expected value, actual value, relevant deterministic source, and root cause. Do not silently tune domain values.

## AI provider rules

- Supported provider identifiers are `meta`, `gemini`, and `modal`.
- Keep provider routing explicit. Never silently route an unknown provider to another provider; return a controlled unsupported-provider error.
- Provider failure must not destroy, replace, or modify deterministic results.
- External AI calls may explain only the verified deterministic context.
- Unit tests must mock external AI APIs unless explicitly authorized as live integration tests.

## Test policy

Maintain coverage for Flask health, deterministic BOQ, DATA_GATE #4231, the full deterministic pipeline, Meta/Gemini/Modal routing, unknown-provider rejection, default-provider behavior, provider-failure isolation, and deterministic-result preservation.

When test execution is available, report:

- Python version
- tests collected
- passed, failed, and skipped counts
- collection errors
- exit code

Never report PASS unless the command actually ran and passed. Do not delete, skip, xfail, weaken, or hide legitimate failing tests to obtain a green result.

## Failure diagnosis

Diagnose failures before patching. Classify them as `REGRESSION`, `TEST DEFECT`, `DOMAIN MISMATCH`, `PROVIDER ERROR`, `ENVIRONMENT FAILURE`, `CI FAILURE`, `SECURITY BLOCK`, or `UNKNOWN`. Fix only when evidence identifies the required change; avoid broad speculative refactoring.

## Security

- Never commit or disclose API keys, proxy tokens, passwords, private keys, credentials, or real `.env` values.
- `.env.example` may contain variable names and empty or clearly safe synthetic placeholders only.
- Run available secret scanning before finalizing security-sensitive changes. Never print secrets in logs or reports.

## Branches and reviews

Prefer a review branch, tests, CI, pull request, and human review before changes reach `main`. Do not force-push without explicit owner instruction, erase Git history, automatically merge a failing branch, or hide test failures. Do not merge automatically unless explicitly requested.

## README and current implementation

README must reflect executable reality. The current implementation has six deterministic engines and three AI adapters: Meta, Gemini, and Modal. Update stale current-system descriptions when supported by source code, but preserve historical evidence and its original classifications; do not rewrite it as current execution evidence.

## Google Drive and competition artifacts

- Treat Google Drive references as evidence/data sources only unless Drive tools are explicitly authorized. A URL does not imply write access. Never modify Drive submission artifacts without explicit authority.
- Competition submission artifacts are protected. Do not rename, replace, delete, or reorganize them unless the owner explicitly requests that exact action.
- Repository maintenance must not manufacture or rewrite historical submission evidence.

## CI and deployment

- Respect the existing CI workflow; do not rewrite it merely because tests fail.
- Repository readiness and public deployment are separate gates. Never invent a public URL or claim deployment succeeded without checking the deployed endpoint.
- Preserve Flask/Gunicorn compatibility with `gunicorn app:app --bind 0.0.0.0:$PORT` and the canonical health path `/api/health`.

## Final report for substantial maintenance tasks

Report these sections:

```text
FILES_CHANGED
FILES_NOT_CHANGED
TEST_RESULTS
CI_STATUS
PROVIDER_STATUS
SECRET_SCAN
EVIDENCE_CLASSIFICATION
REMAINING_BLOCKERS
```

State `UNKNOWN` or `BLOCKED` wherever execution or verification was not possible.
