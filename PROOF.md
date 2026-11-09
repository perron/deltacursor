# deltacursor proof

Captured 2026-11-09 12:13 PST on the box.

```
journal /tmp/ai-tools-demo/events.jsonl
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
