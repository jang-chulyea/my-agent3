# simple_subject_loader Migration Checklist

## Scope

This document breaks down the responsibilities currently inside
`tools/simple_subject_loader.py` and proposes where each responsibility should
move during the staged architecture transition.

This is a planning artifact only.

- No runtime behavior changes are introduced by this document.
- Existing files remain unchanged.
- The current tools-based loader remains the source of truth until migration is
  explicitly executed and verified.

## Responsibility Breakdown Table

| Current unit | Responsibility | Proposed destination | Priority | Why |
|---|---|---|---|---|
| `SubjectLoader.__init__` | Store subject root and initialize in-memory state containers | `engine/subject_loader.py` | High | This is part of the loader's core runtime state and belongs with subject loading, not with tools. |
| `SubjectLoader.load_subject` | Orchestrate metadata, node, and relation loading | `engine/subject_loader.py` | High | This is the main subject-loading entry point and should become an engine concern first. |
| `SubjectLoader._load_subject_meta` | Read and validate `subject.json` | `engine/subject_loader.py` | High | Reading subject metadata is a core loading responsibility, not a bundle concern. |
| `SubjectLoader._load_nodes` | Read node files and build node map | `engine/subject_loader.py` | High | Node loading is a central part of subject ingestion and belongs in the loader service. |
| `SubjectLoader._load_prerequisite_edges` | Read prerequisite relation data | `engine/subject_loader.py` | High | Relation ingestion should stay close to file loading and validation. |
| `SubjectLoader.get_node` | Return one node from loaded state | `engine/subject_loader.py` | High | This is direct access to loaded subject state and naturally belongs to the loader. |
| `SubjectLoader.get_prerequisite_node_ids` | Resolve prerequisite node IDs for a target node | `engine/bundle_service.py` | Medium | It participates in bundle composition logic, but could temporarily remain in the loader until bundle assembly is fully separated. |
| `SubjectLoader.get_prerequisite_nodes` | Materialize prerequisite node payloads from IDs | `engine/bundle_service.py` | Medium | This is closer to query/composition behavior than raw file loading. |
| `SubjectLoader.get_learning_bundle` | Assemble subject summary, target node, and prerequisite nodes into one response | `engine/bundle_service.py` | High | This is the clearest bundle assembly responsibility and should become the first formal bundle service use case. |
| `print_learning_bundle` | Format and print a bundle for CLI/debug output | `tools` or `app.py` | Low | This is presentation/debug behavior and should not move into engine services. |
| `if __name__ == "__main__": ...` block | Manual script execution for local inspection | `tools` | Low | This is a developer convenience path, not part of the application architecture. |

## Destination Guidance

### Move to `engine/subject_loader.py`

These responsibilities are about reading, validating, and exposing subject data:

- `SubjectLoader.__init__`
- `SubjectLoader.load_subject`
- `SubjectLoader._load_subject_meta`
- `SubjectLoader._load_nodes`
- `SubjectLoader._load_prerequisite_edges`
- `SubjectLoader.get_node`

Reason:

- They are all loader-centric.
- They depend on subject file structure.
- They should remain separated from presentation and bundle response composition.

### Move to `engine/bundle_service.py`

These responsibilities are about assembling a learning-oriented output from
already loaded data:

- `SubjectLoader.get_learning_bundle`
- `SubjectLoader.get_prerequisite_nodes`
- `SubjectLoader.get_prerequisite_node_ids`

Reason:

- They are query/composition responsibilities.
- They sit above raw data ingestion.
- They will be easier to test and evolve if separated from file loading.

### Leave in `app.py`

Nothing from `tools/simple_subject_loader.py` should move directly into `app.py`
except, potentially, the final top-level execution flow that calls engine
services.

What `app.py` should do instead:

- choose which subject to load
- call the engine layer
- decide how to present the result

What `app.py` should not inherit:

- raw JSON loading logic
- node/relation parsing logic
- bundle assembly logic

### Leave in `tools`

These responsibilities should remain in tools or be replaced by equivalent
debug-only helpers:

- `print_learning_bundle`
- script-style `__main__` execution block

Reason:

- They are development-facing utilities.
- They do not belong to the long-term engine boundary.

## Why the priorities differ

| Priority | Meaning |
|---|---|
| High | Should move early because it defines the real engine boundary or carries core loading behavior. |
| Medium | Should move after the loader/service split is established because it depends on the shape of both sides. |
| Low | Can stay where it is longer because it is presentation or developer utility behavior. |

## Migration Checklist

### Loader migration checklist

- [ ] Define the engine loader state shape.
- [ ] Move constructor state ownership.
- [ ] Move subject metadata loading.
- [ ] Move node loading.
- [ ] Move prerequisite edge loading.
- [ ] Move node lookup access.
- [ ] Verify parity with tools-based loader.

### Bundle migration checklist

- [ ] Define the bundle response contract.
- [ ] Move target node resolution.
- [ ] Move prerequisite resolution.
- [ ] Move learning bundle composition.
- [ ] Verify bundle shape parity with the tools-based implementation.

### Presentation/tooling checklist

- [ ] Keep CLI/debug printing outside engine.
- [ ] Preserve a manual inspection path in tools if still useful.
- [ ] Make sure app-facing output does not require engine to print directly.

## Proposed Real Migration Order

### 1. Move pure loading responsibilities first

Move into `engine/subject_loader.py`:

- constructor state setup
- subject metadata loading
- node loading
- prerequisite relation loading
- node lookup

Why first:

- These are the least ambiguous responsibilities.
- They create the stable base that bundle assembly can depend on.

### 2. Move bundle composition responsibilities second

Move into `engine/bundle_service.py`:

- prerequisite ID resolution
- prerequisite node resolution
- learning bundle assembly

Why second:

- These depend on the loader boundary being stable.
- They should be implemented against a loader contract, not mixed into raw file I/O.

### 3. Move or retire presentation-only helpers last

Leave in `tools` or convert app-facing presentation flow later:

- `print_learning_bundle`
- script-style main block

Why last:

- They do not block the engine transition.
- They are optional utilities, not architecture-critical logic.
