# Runbook

Every task a user of this repo does, in order, with the exact commands
and the shape of the expected output. Step count is the number of
shell commands.

## Task 1: classify a spec corpus

1. `cd ~/workspace`
2. `. .venv/bin/activate`
3. `python -m buildability.classify mesh/specs_uci`
4. expected: a line per spec, then `distribution:` and a count per regime

Step count: 3.

## Task 2: verify the repository

1. `cd ~/workspace`
2. `./scripts/verify.sh`
3. expected: eleven lines, each PASS, then `pass: 11 fail: 0 skip: 0`

Step count: 2.

## Task 3: run the autonomous pipe

1. `cd ~/workspace`
2. `python pipe/autonomous_pipe.py`
3. expected: eight lines `plan ... feedback`, then `passed: True`

Step count: 2.

## Task 4: read the standards index

1. `cd ~/workspace`
2. `./cli/sovereign standards`
3. expected: `generated: N`, `omitted: 0`, then N artifact names

Step count: 2.

## Task 5: open the dashboard

1. `cd ~/workspace`
2. `./cli/sovereign dashboard`
3. expected: the browser opens dxp/dashboard.html

Step count: 2.
