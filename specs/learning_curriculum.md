# Specification: Learning Curriculum

## Artifact
A curriculum file `curriculum.yaml` with a list of items, each having:
- `id`
- `title`
- `prerequisites`: list of ids
- `duration_hours`: float
- `resource`: URL or reference

## Interface
    from curriculum import load

    c = load("curriculum.yaml")
    plan = c.schedule(available_hours_per_week=10)
    # returns ordered list of (week, item)

## Evidence
- The file parses and every prerequisite points to a declared item
- There are no cycles in the prerequisite graph
- The schedule respects prerequisite ordering
- Total hours match sum of duration_hours

## Verification
    python -m pytest packages/curriculum/tests/test_curriculum.py -q

## Current state
Not done. The curriculum exists only as prose.

## Status
state: not-done
