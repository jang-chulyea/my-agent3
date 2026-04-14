# Subject Registry Spec

## Purpose

`config/subject_registry.json` is an operations metadata file.

It exists to answer only this question:

- which subjects are available to the system, and where is each subject root?

It must **not** contain subject knowledge content.

## Fixed Boundary

| Layer | Responsibility |
|---|---|
| `config/subject_registry.json` | subject registration and discovery metadata |
| `data/subject_xx/...` | actual subject content such as subject metadata, nodes, and relations |

This boundary is fixed:

- registry stores discovery metadata only
- data stores learning content only

## Required Access Flow

The only allowed resolution flow is:

`registry -> subject_root -> data access`

This means:

- `engine` must not hardcode `data/...` paths directly
- `app.py` must not resolve subject paths directly
- subject resolution must always start from registry metadata

## Minimal JSON Shape

```json
{
  "subjects": [
    {
      "subject_id": "subject_02_hvac",
      "display_name": "공조냉동설계",
      "subject_root": "data/subject_02_hvac",
      "enabled": true,
      "description": "공조냉동설계 학습 subject"
    }
  ]
}
```

## Top-level Fields

### Required

| Field | Type | Reason |
|---|---|---|
| `subjects` | array | Registry must expose one or more registered subjects. |

### Optional

No optional top-level fields are defined in the current contract.

Reason:

- The current goal is to keep the registry minimal.
- Versioning or richer metadata can be added later only if migration pressure appears.

## Subject Entry Fields

### Required

| Field | Type | Reason |
|---|---|---|
| `subject_id` | string | Stable identifier used by the app and engine to request a subject. |
| `display_name` | string | Human-readable subject name for menus, logs, and UI. |
| `subject_root` | string | Root path to the subject content directory under `data/`. |
| `enabled` | boolean | Allows a subject to exist in the registry without being selectable. |

### Optional

| Field | Type | Reason |
|---|---|---|
| `description` | string | Short operator-facing or UI-facing description of the subject. |

## Explicitly Forbidden in Registry

The following must not be stored in `config/subject_registry.json`:

- node content
- relation content
- formulas
- learning bundle content
- entry node graphs
- prerequisite rules
- any per-node or per-relation knowledge payload

Those belong under `data/subject_xx/...`.

## Validation Rules

| Rule | Description |
|---|---|
| `subjects` must be a list | Registry must be machine-readable in a predictable shape. |
| `subjects` must not be empty | At least one subject must be registered. |
| `subject_id` must be unique | Prevents ambiguous subject resolution. |
| `subject_root` must be unique or intentionally shared | Default expectation is one root per subject. |
| `subject_root` should point to a subject directory under `data/` | Keeps content ownership in the data layer. |
| `enabled` must be boolean | Keeps subject availability simple and explicit. |

## Single-subject Today, Multi-subject Later

### Current project state

- The project currently has one real subject: `data/subject_02_hvac`
- The app is still effectively single-subject at runtime

### Why this registry contract still matters now

- it removes direct path knowledge from future app logic
- it gives engine one stable place to resolve subjects
- it prepares multi-subject expansion without implementing it yet

## MVP Simplicity Rules

- keep one flat `subjects` array
- do not add category trees
- do not add environment overrides
- do not add per-subject engine settings
- do not add content-derived fields that duplicate data-layer knowledge

## Summary

The current contract is intentionally small.

Allowed subject fields:

- `subject_id`
- `display_name`
- `subject_root`
- `enabled`
- optional `description`

Everything else stays out until there is a concrete operational need.
