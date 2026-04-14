# My_Agent 3.0 Standard Handover

## 1. Final Objective

The long-term objective is to run My_Agent 3.0 on an engine-centered
architecture where:

- `app.py` selects the subject and target only
- `engine` resolves the subject, loads subject data, and builds the learning bundle
- `config` stores subject discovery metadata only
- `data` stores real learning content only

The current architecture baseline is:

`registry -> resolver -> subject_root -> loader -> bundle`

This flow is fixed and should be preserved.

## 2. Confirmed Current Structure

The current execution model is:

`app.py -> engine.load_learning_bundle(subject_id, target_node_id) -> engine.registry.load_subject_root(subject_id) -> subject_root -> engine.subject_loader -> engine.bundle_service`

Meaning:

- `app.py` is orchestration only
- `engine` performs the actual work
- `tools` is no longer part of the main loading path

## 3. Current File Architecture

```text
My_agent3.0/
├─ app.py
├─ requirements.txt
├─ config/
│  └─ subject_registry.json
├─ data/
│  ├─ subject_02_hvac/
│  │  ├─ subject.json
│  │  ├─ nodes/
│  │  └─ relations/
│  └─ subject_03_basic_math/
│     ├─ subject.json
│     ├─ nodes/
│     └─ relations/
├─ docs/
│  ├─ subject_registry_spec.md
│  ├─ engine_public_interface.md
│  ├─ engine_subject_resolution_flow.md
│  ├─ simple_subject_loader_migration_checklist.md
│  └─ standard_handover.md
├─ engine/
│  ├─ __init__.py
│  ├─ entrypoint.py
│  ├─ registry.py
│  ├─ subject_loader.py
│  └─ bundle_service.py
├─ tests/
│  ├─ test_subject_loader.py
│  ├─ test_data_integrity.py
│  ├─ test_config_registry.py
│  ├─ test_engine_subject_loader.py
│  ├─ test_bundle_service.py
│  ├─ test_engine_registry.py
│  ├─ test_engine_entrypoint.py
│  └─ test_engine_multi_subject.py
└─ tools/
   └─ simple_subject_loader.py
```

## 4. Current Stage

Current stage:

- engine-centered architecture transition completed
- registry contract fixed
- subject resolution contract fixed
- subject_id-based entrypoint fixed
- minimal multi-subject readiness verified

Not started yet:

- full multi-subject user-facing selection flow
- richer registry features
- `core` introduction

## 5. Completed Key Changes

- Moved the main application path from tools-centered loading to engine-centered loading.
- Changed `app.py` to pass `subject_id` and `target_node_id` only.
- Added engine loader and bundle service structure.
- Added engine registry loader and subject resolver.
- Removed direct-path fallback from the engine entrypoint.
- Fixed `config/subject_registry.json` to a real JSON contract.
- Added a second minimal subject to confirm multi-subject readiness.
- Protected the architecture with tests.

## 6. Fixed Principles

- `app.py` must choose only `subject_id` and `target_node_id`.
- `app.py` must not resolve filesystem paths.
- `engine` must own resolution, loading, and bundle assembly.
- `engine` must not hardcode `data/...` subject paths.
- subject resolution must always be:
  `registry -> resolver -> subject_root -> data access`
- `config/subject_registry.json` stores operations metadata only.
- `data/subject_xx/...` stores actual learning content only.
- `tools` is legacy support and debug/reference only.
- `tools` must not return to the main execution path.
- `core` is intentionally not created yet.

## 7. Next Work Priorities

1. Keep multi-subject expansion incremental.
2. Add subject selection flow only through engine contracts.
3. Extend registry safely only if there is a clear operational need.
4. Add more subject-level tests before adding richer engine behavior.
5. Delay `core` until repeated shared contracts appear in multiple modules.

## 8. Issues / Checks

- Console output can still show encoding issues in the current terminal when
  Korean text is printed through `print_learning_bundle`. This is an output
  environment issue, not a bundle-generation issue.
- `tools/simple_subject_loader.py` still exists and remains useful as a legacy
  reference and output helper, but it is no longer the main architecture path.
- `subject_03_basic_math` is intentionally minimal and exists only to validate
  multi-subject readiness, not to model a full production subject.

## 9. Test Status

Current test set:

- `tests/test_subject_loader.py`
- `tests/test_data_integrity.py`
- `tests/test_config_registry.py`
- `tests/test_engine_subject_loader.py`
- `tests/test_bundle_service.py`
- `tests/test_engine_registry.py`
- `tests/test_engine_entrypoint.py`
- `tests/test_engine_multi_subject.py`

Current result:

- full test suite passes
- verified with:
  `.venv\Scripts\python.exe -m pytest tests`

At handover time, the suite passes with all current tests green.

## 10. Codex Collaboration Rules

- Do not reintroduce path resolution into `app.py`.
- Do not bypass registry when resolving subjects.
- Do not hardcode `data/...` subject paths inside engine logic.
- Do not move tools back into the main runtime path.
- Do not introduce `core` early.
- Do not change bundle shape without explicit contract agreement.
- Prefer small, step-based changes with tests after each step.
- When expanding behavior, add or update tests first if the contract changes.
- Preserve `subject_02_hvac` as the baseline reference subject unless explicitly instructed otherwise.

## Summary

The current architecture is stable and intentional.

The main contract is now:

`app selects -> engine resolves -> loader reads -> bundle service assembles`

And the fixed resolution path is:

`registry -> resolver -> subject_root -> loader -> bundle`

This is the baseline for all future work.
