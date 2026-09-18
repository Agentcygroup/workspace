from cli.main import main

def test_hash_known_value(capsys):
    rc = main(["hash", "hello"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

def test_no_args(capsys):
    rc = main([])
    assert rc == 2
