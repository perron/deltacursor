from pathlib import Path
import json
import pytest
import deltacursor.cli as dc


def test_help_and_version():
    with pytest.raises(SystemExit) as exc:
        dc.main(["--help"])
    assert exc.value.code == 0
    with pytest.raises(SystemExit) as exc:
        dc.main(["--version"])
    assert exc.value.code == 0


def test_append_and_since(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    assert dc.main(["--journal", str(journal), "init"]) == 0
    start = capsys.readouterr().out.strip().split()[-1]
    assert dc.main(["--journal", str(journal), "append", "--kind", "test", '{"passed": 3}']) == 0
    assert dc.main(["--journal", str(journal), "append", "--kind", "test", '{"passed": 4}']) == 0
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "since", start, "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["count"] == 2
    mid = first["cursor"]
    assert dc.main(["--journal", str(journal), "since", mid, "--json"]) == 0
    empty = json.loads(capsys.readouterr().out)
    assert empty["count"] == 0
    assert empty["cursor"] == mid
    assert dc.main(["--journal", str(journal), "append", "--kind", "note", "hello"]) == 0
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "since", mid, "--json"]) == 0
    again = json.loads(capsys.readouterr().out)
    assert again["count"] == 1
    assert again["events"][0]["body"]["text"] == "hello"


def test_bad_cursor(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    journal.write_text("")
    assert dc.main(["--journal", str(journal), "since", "not-a-cursor"]) == 1
    assert "invalid cursor" in capsys.readouterr().err


def test_empty_journal_since(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    assert dc.main(["--journal", str(journal), "init"]) == 0
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "since", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["count"] == 0
    assert data["from"] == 0


def test_invalid_json_line(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    journal.write_text('{"seq":1,"kind":"ok","body":{}}\nthis is not json\n')
    assert dc.main(["--journal", str(journal), "since"]) == 1
    assert "invalid JSON on journal line 2" in capsys.readouterr().err


def test_unicode_body(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    dc.main(["--journal", str(journal), "init"])
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "append", "--kind", "note", "日本語 ✅"]) == 0
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "since", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["events"][0]["body"]["text"] == "日本語 ✅"


def test_cursor_command(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    dc.main(["--journal", str(journal), "init"])
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "cursor"]) == 0
    empty = capsys.readouterr().out.strip()
    assert empty == dc.encode_cursor(0)
    dc.main(["--journal", str(journal), "append", "hello"])
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "cursor"]) == 0
    assert capsys.readouterr().out.strip() == dc.encode_cursor(1)


def test_init_existing(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    dc.main(["--journal", str(journal), "init"])
    dc.main(["--journal", str(journal), "append", "keep me"])
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "init"]) == 0
    assert "keep me" in journal.read_text()


def test_missing_journal_since(tmp_path, capsys):
    journal = tmp_path / "missing.jsonl"
    assert dc.main(["--journal", str(journal), "since", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["count"] == 0
    assert data["cursor"] == dc.encode_cursor(0)


def test_encode_decode_roundtrip():
    token = dc.encode_cursor(42)
    assert dc.decode_cursor(token) == 42


def test_since_idempotent(tmp_path, capsys):
    journal = tmp_path / "log.jsonl"
    dc.main(["--journal", str(journal), "append", "one"])
    capsys.readouterr()
    assert dc.main(["--journal", str(journal), "cursor"]) == 0
    cur = capsys.readouterr().out.strip()
    assert dc.main(["--journal", str(journal), "since", cur, "--json"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert dc.main(["--journal", str(journal), "since", cur, "--json"]) == 0
    second = json.loads(capsys.readouterr().out)
    assert first == second
    assert first["count"] == 0
