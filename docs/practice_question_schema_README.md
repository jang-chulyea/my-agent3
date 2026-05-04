# Practice Question Schema

This document describes the JSON schema for practice questions in the educational system.

## Schema Overview

The practice question schema is designed to be flexible and consistent with existing exam and lecture material structures. It supports various question types including conceptual, calculation, and multiple choice questions.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (format: `practice_[subject]_[topic]_[number]`) |
| `subject` | string | Subject area (e.g., "thermodynamics", "physics") |
| `topic` | string | Specific topic within the subject |
| `question` | string | The question text |
| `answer` | string/number/boolean/array | The correct answer |
| `explanation` | string | Detailed explanation of the answer |
| `difficulty` | string | Difficulty level: "easy", "medium", "hard", "expert" |
| `source` | string | Origin: "generated", "exam", "textbook", "practice" |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `question_type` | string | Type: "conceptual", "calculation", "multiple_choice", "true_false", "analysis" |
| `choices` | array | Multiple choice options (required for multiple_choice) |
| `given` | object | Data provided for calculation problems |
| `asked` | string | What is being asked (for calculation problems) |
| `concepts` | array | Key concepts covered |
| `tags` | array | Additional tags for categorization |
| `estimated_time` | number | Estimated time to solve in minutes |
| `hints` | array | Optional hints for difficult questions |

## Question Types

### 1. Conceptual Questions
- Focus on understanding concepts
- Answer is typically a string explanation
- No `choices` field required

### 2. Calculation Questions
- Require numerical computation
- Must include `given` (data) and `asked` (what to find) fields
- Answer is typically a number

### 3. Multiple Choice Questions
- Must include `choices` array (2-6 options)
- Answer is the correct choice text
- Good for testing recognition and elimination skills

### 4. True/False Questions
- Answer is boolean (`true` or `false`)
- Good for testing basic understanding

### 5. Analysis Questions
- Complex problems requiring multiple steps
- Answer may be an array of steps or detailed response

## Validation Rules

- **Multiple Choice**: Must have `choices` array when `question_type` is "multiple_choice"
- **Calculation**: Must have `given` and `asked` fields when `question_type` is "calculation"
- **ID Format**: Must follow pattern `practice_[a-zA-Z0-9_-]+`
- **Difficulty**: Must be one of: "easy", "medium", "hard", "expert"
- **Source**: Must be one of: "generated", "exam", "textbook", "practice"

## Examples

See the example files:
- [practice_question_example.json](../examples/practice_question_example.json) - Calculation question
- [practice_question_mc_example.json](../examples/practice_question_mc_example.json) - Multiple choice question

## Usage Guidelines

### Creating Questions

1. **Choose appropriate difficulty**: Easy for basic recall, Hard for synthesis/analysis
2. **Include detailed explanations**: Should teach the concept, not just state the answer
3. **Add concepts and tags**: Help with categorization and search
4. **Estimate time**: Based on typical student completion time
5. **Use hints sparingly**: Only for very challenging questions

### Best Practices

- **Clarity**: Questions should be unambiguous
- **Completeness**: Provide all necessary data in `given` field
- **Educational value**: Explanations should reinforce learning
- **Consistency**: Follow existing subject/topic naming conventions
- **Testing focus**: Each question should test specific learning objectives

### File Organization

Practice questions should be stored in:
```
data/practice_questions/[subject]/[topic]/
```

With filenames following the pattern:
```
practice_[subject]_[topic]_[number].json
```

## Schema Validation

The schema can be validated using JSON Schema validators. The schema file is located at:
[docs/practice_question_schema.json](../docs/practice_question_schema.json)

## Integration

Practice questions integrate with:
- **Exam generation**: Can be used as exam questions
- **Study materials**: Supplement lecture materials
- **Assessment**: Track student progress
- **Analytics**: Analyze topic difficulty and performance