# deltacursor

An append-only journal that returns only what changed since an opaque
cursor. Mid-loop agents should not reread a whole task list, test log, or
event file on every turn.

## Install

Python 3.10 or later.

From a checkout:

```bash
python3 -m pip install .
python3 -m pip install -e ".[dev]"  # optional, for tests
deltacursor --journal ./events.jsonl init
```

## 30-second quick start

```bash
deltacursor --journal ./events.jsonl init
# prints a cursor

deltacursor --journal ./events.jsonl append --kind test '{"passed": 3}'
deltacursor --journal ./events.jsonl append --kind test '{"passed": 4}'

deltacursor --journal ./events.jsonl since 'eyJzZXEiOjB9' --json
# two events, plus a new cursor

deltacursor --journal ./events.jsonl since 'eyJzZXEiOjJ9' --json
# count 0 — nothing new
```

Sample output from that exact example:

```
$ deltacursor --journal ./events.jsonl init
journal events.jsonl
cursor eyJzZXEiOjB9
$ deltacursor --journal ./events.jsonl append --kind test '{"passed": 3}'
seq 1
cursor eyJzZXEiOjF9
$ deltacursor --journal ./events.jsonl append --kind test '{"passed": 4}'
seq 2
cursor eyJzZXEiOjJ9

$ deltacursor --journal ./events.jsonl since 'eyJzZXEiOjB9' --json
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

$ deltacursor --journal ./events.jsonl since 'eyJzZXEiOjJ9' --json
{
  "events": [],
  "count": 0,
  "cursor": "eyJzZXEiOjJ9",
  "from": 2
}
```

Cursors encode a sequence number (`eyJzZXEiOjB9` is seq 0, `eyJzZXEiOjJ9` is seq 2). After `init` and two appends, those exact cursors are what you should see.

`since` is idempotent for a given cursor: calling it twice without a new
append returns the same empty set and the same cursor.

## Credit

Motivated by the mid-loop "return only the delta since the last cursor"
design note circulating in Nov 2026. Original JSONL journal; no source was
copied from any MCP server.

## Limits

- The journal is a local JSONL file (default `./.deltacursor.jsonl`). It is not safe for concurrent writers.
- Cursors are opaque-looking encodings of a sequence number; they are not a security boundary.
- Invalid JSON or an event missing `seq` is an error and stops the read.
- `init` will not truncate an existing journal.

From GitHub you can also install with:

```bash
python3 -m pip install git+https://github.com/perron/deltacursor.git
```

This package is not published to PyPI.

## Use it with your agent

You can point a coding agent at this repository and ask it to use the tool, adapt it, or write a small tool in the same style. That works with Claude Code, Codex, Cursor, Grok Bot, and anything else that can clone a git repo and run a Python CLI.

A short prompt you can paste:

> Clone https://github.com/perron/deltacursor, install it, and use a journal at ./events.jsonl so I can append test results and later ask only for events since the last cursor I give you.

If you want a new tool in this style, say so explicitly: one job, standard-library Python, pytest first, no API key, and an honest Limits section.

## Contributing / how you can help

Bug reports, tight tests, and small honest features are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to run the suite and for pull request guidelines.

Good first issues:

- Add an optional `--kind` filter to `since`.
- Lock the journal file during `append` so two cooperative writers fail clearly instead of interleaving lines.
- Add a `compact` command that rewrites seqs and prints the new cursor, with tests.

If you are unsure whether an idea fits, open an issue before writing a large patch.

## License

MIT. See `LICENSE`. Please read `SECURITY.md` before filing a vulnerability report. Agents should also read `AGENTS.md`.
