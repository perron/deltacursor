from pathlib import Path
import json
import deltacursor.cli as dc


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
