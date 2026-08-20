from mcd import main, Const
import pytest
import sys

@pytest.mark.parametrize(
    "code, expected, type",
    [
        (['mcd.py', '-i', 'sample.csv'], "The result is successfully", 'print'), # (["mcd.py", "-i", "sample.csv"], "The result is successfully created in the folder")
        (['mcd.py', '-i', 'sample2.csv'], "does not include the same set of fields", 'exception')
    ],
    ids=["normal",
         "missing_field_file"] # Names for each test case
)
def test_verify_code(code, expected, type, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", code)
    if type == 'print': 
        result = main()
        text_printed = capsys.readouterr()
        assert expected in text_printed.out
    if type == 'exception':
        with pytest.raises(ValueError) as exc_info:
            main()
        # breakpoint()
        assert expected in str(exc_info.value)