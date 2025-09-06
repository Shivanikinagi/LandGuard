import os
from click.testing import CliRunner
from ppc.cli.main import compress, decompress


def test_roundtrip_text(tmp_path):
    p = tmp_path / "hello.txt"
    p.write_text("hello pied piper " * 20)

    out_ppc = tmp_path / "hello.ppc"
    runner = CliRunner()

    r1 = runner.invoke(compress, [str(p), "-p", "pass", "-o", str(out_ppc), "--model", "text-huffman"])
    assert r1.exit_code == 0, r1.output

    out_txt = tmp_path / "restored.txt"
    r2 = runner.invoke(decompress, [str(out_ppc), "-p", "pass", "-o", str(out_txt)])
    assert r2.exit_code == 0, r2.output
    assert out_txt.read_text() == p.read_text()