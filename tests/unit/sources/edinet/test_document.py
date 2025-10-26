from __future__ import annotations


def test_read_csv() -> None:
    from kabukit.sources.edinet.document import read_csv

    data = "col1\tcol2\n1\t2\n3\t4".encode("utf-16-le")
    df = read_csv(data)
    assert df.columns == ["col1", "col2"]
    assert df["col1"].to_list() == [1, 3]
    assert df["col2"].to_list() == [2, 4]
