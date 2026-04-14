# Engine Subject Resolution Flow

## Purpose

This document fixes the current engine-side subject resolution contract.

It exists to keep the subject lookup path stable before any future
multi-subject expansion.

## Fixed Flow

The current allowed flow is:

`app.py -> engine.load_learning_bundle(subject_id, target_node_id) -> registry/resolver -> subject_root -> subject loader -> bundle service`

This flow is intentional and must remain stable.

## Responsibility Boundaries

### `config/subject_registry.json`

Role:

- store subject operations metadata only

Allowed content:

- `subject_id`
- `display_name`
- `subject_root`
- `enabled`
- optional `description`

Not allowed:

- nodes
- relations
- formulas
- learning content
- bundle payloads

### `engine.registry`

Role:

- load registry metadata from `config/subject_registry.json`
- validate that the registry has the expected shape
- resolve `subject_id -> subject_root`

Current public responsibilities:

- `load_subject_registry(...)`
- `load_subject_root(subject_id, ...)`

Error responsibilities:

- raise `SubjectRegistryError` when registry data is invalid
- raise `SubjectNotFoundError` when `subject_id` is missing

### Resolver responsibility

In the current implementation, resolver behavior is represented by:

- `load_subject_root(subject_id)`

Resolver contract:

- input: `subject_id`
- output: `subject_root`
- source of truth: registry only

Resolver rules:

- do not hardcode `data/...` subject paths
- do not inspect `app.py`
- do not derive paths from naming conventions
- always resolve through registry metadata

### `engine.entrypoint`

Role:

- accept application-facing request parameters
- orchestrate subject resolution
- create loader service
- trigger subject loading
- trigger bundle assembly
- return bundle data

Current public entrypoint:

- `load_learning_bundle(subject_id, target_node_id)`

Important limit:

- `entrypoint` coordinates work
- it does not contain registry data itself
- it does not perform raw JSON parsing itself
- it does not format output for console/UI

### `engine.subject_loader`

Role:

- load subject content from the resolved `subject_root`
- read subject metadata
- read node files
- read prerequisite relation files
- expose loaded node lookup

Important limit:

- it receives `subject_root`
- it does not decide how that root is discovered

### `engine.bundle_service`

Role:

- assemble learning bundle data from loaded subject state
- resolve prerequisite node IDs
- resolve prerequisite node payloads
- build the final bundle structure

Important limit:

- it does not read registry
- it does not read files directly
- it does not print output

## App Boundary

`app.py` must remain orchestration-only.

Allowed app responsibilities:

- choose `subject_id`
- choose `target_node_id`
- call `engine.load_learning_bundle(...)`
- pass returned data to presentation/output logic

Disallowed app responsibilities:

- subject path resolution
- registry parsing
- file loading
- bundle composition rules

## Fixed Rules

- subject resolution must always be: `registry -> subject_root`
- engine must not hardcode `data/...` subject paths
- app must not resolve subject paths
- tools must not return to the main execution path
- bundle shape must remain stable unless explicitly changed as a contract update

## Test Responsibilities

### `tests/test_config_registry.py`

Purpose:

- validate the registry file contract itself
- verify required fields exist
- verify registered subject roots point to real directories

This test protects:

- config schema stability
- config/data boundary

### `tests/test_engine_registry.py`

Purpose:

- validate engine-side registry loading and subject resolution
- verify `subject_id -> subject_root` mapping
- verify missing subject errors are raised clearly

This test protects:

- resolver correctness
- registry-driven access rule

### `tests/test_engine_entrypoint.py`

Purpose:

- validate the public engine entrypoint behavior
- verify `subject_id` based loading works end-to-end
- verify bundle structure is returned without changing shape

This test protects:

- app-facing engine contract
- subject resolution plus loader plus bundle orchestration

## Why this matters before multi-subject expansion

Multi-subject support should not start by adding features everywhere.

It should start from a stable engine contract:

- app passes `subject_id`
- engine resolves subject via registry
- loader reads from resolved root
- bundle service returns stable output

That is the current fixed architecture baseline.
