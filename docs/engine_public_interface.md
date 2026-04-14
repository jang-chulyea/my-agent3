# Engine Public Interface Draft

## Goal

Define a small, stable engine-facing API so that `app.py` eventually depends on
engine entry points only, instead of importing implementation details from
`tools/`.

This draft does **not** change the current runtime path.

- Current runtime path stays: `app.py -> tools.simple_subject_loader`
- Future runtime path should become: `app.py -> engine`

## Recommended Public Interface

### Public exports from `engine`

Recommended app-facing symbols:

| Public symbol | Type | Purpose |
|---|---|---|
| `create_subject_loader(subject_root)` | function | Create the loader service without exposing path-handling details in `app.py`. |
| `SubjectLoaderService` | class | Engine service for subject metadata, nodes, and relation loading. |
| `BundleService` | class | Engine service for assembling learning bundle output from loaded data. |

### Why keep the interface this small

- It prevents `app.py` from binding to internal file layout details.
- It preserves the loader/bundle responsibility split.
- It keeps the future migration from `tools` to `engine` low-risk.
- It avoids creating `core` too early.

## Recommended Future Call Pattern for `app.py`

### Stage A: loader-first engine usage

When only loading is implemented in `engine`, `app.py` should eventually look
conceptually like this:

```python
from engine import create_subject_loader


def main():
    loader = create_subject_loader("data/subject_02_hvac")
    loader.load_subject()
    # bundle creation still handled elsewhere until BundleService is implemented
```

### Stage B: full engine usage

After `BundleService` is implemented, `app.py` should only coordinate the flow:

```python
from engine import BundleService, create_subject_loader


def main():
    loader = create_subject_loader("data/subject_02_hvac")
    loader.load_subject()

    bundle_service = BundleService(loader)
    bundle = bundle_service.build_learning_bundle("TD-01-PRESSURE")
    # app handles presentation
```

## What `app.py` Should Own in the Future

`app.py` should keep only these responsibilities:

- choose subject path or subject ID
- trigger subject loading
- request a learning bundle
- decide how to print or return the result

`app.py` should not own:

- JSON parsing
- node loading rules
- relation loading rules
- bundle assembly rules

## Responsibility Boundary

| Layer | Owns |
|---|---|
| `app.py` | execution flow and presentation decisions |
| `engine.subject_loader` | loading and exposing subject data |
| `engine.bundle_service` | composing learning bundle outputs |
| `tools` | temporary scripts and debug helpers |

## Why not expose more right now

The engine is still in transition.

So the public interface should not expose:

- internal private loading helpers
- relation traversal internals
- ad hoc utility functions
- future abstractions that do not exist yet

Keeping the API narrow now makes refactoring safer later.

## Recommended Migration Rule

When `app.py` is eventually changed, it should import from `engine` only:

```python
from engine import BundleService, create_subject_loader
```

It should not import:

```python
from engine.subject_loader import ...
from engine.bundle_service import ...
```

This keeps the application coupled to a stable engine entry layer rather than
to internal module structure.
