# deltacursor proof

Captured 2026-11-09 13:27 PST.

Fresh-venv install: `pip install .` succeeded and `deltacursor --version` printed `deltacursor 0.1.1`.

Tests: 11 passed in 0.03s

```
journal /tmp/ai-tools-proof/events.jsonl
cursor eyJzZXEiOjB9
seq 1
cursor eyJzZXEiOjF9
seq 2
cursor eyJzZXEiOjJ9

# since init cursor
{
  "events": [
    {
      "seq": 1,
      "kind": "test",
      "body": {
        "passed": 3
      }
    },
    {
      "seq": 2,
      "kind": "test",
      "body": {
        "passed": 4
      }
    }
  ],
  "count": 2,
  "cursor": "eyJzZXEiOjJ9",
  "from": 0
}

# since latest cursor (expect count 0)
{
  "events": [],
  "count": 0,
  "cursor": "eyJzZXEiOjJ9",
  "from": 2
}
```
