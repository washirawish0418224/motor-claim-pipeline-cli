
from src/mcd.py import main, Const
import pytest
import sys
from pathlib import Path
@pytest.mark.parametrize(
    "code, expected, test_type",
    [
        (['mcd.py', '-i', 'sample.csv'], "The result is successfully", 'print'), # (["mcd.py", "-i", "sample.csv"], "The result is successfully created in the folder")
        (['mcd.py', '-i', 'sample2.csv'], "does not include the same set of fields", ValueError),
        (['mcd.py'], "2", SystemExit),
        (['mcd.py', '-i', 'unknown.csv'], "The file \"unknown.csv\" could not be found.", FileNotFoundError), 
        (['mcd.py', '-i', 'README.md'], "Expecting .csv file type but got .md file type instead.", TypeError),
        (['mcd.py', '-i', 'sample.csv', '-o', 'my_new_folder'], "The result is successfully created in the folder \"my_new_folder\".", 'print'),
        (['mcd.py', '-i', 'sample.csv', '-o', 'existed_result'], "successfully created in the folder \"existed_result\"", 'print'),
        (['mcd.py', '-c'], 'is successfully cleared', 'print')
    ],
    ids=["normal",
         "missing_field_file",
         "no_argument",
         "file_not_found",
         "wrong_file_type",
         "custom_result_folder_name",
         "existed_folder_name",
         "clear_directory"] # Names for each test case
)
def test_end2end(code, expected, test_type, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(Const, "RESULT_DIR_PATH", tmp_path / "Result")
    monkeypatch.setattr(sys, "argv", code)
    monkeypatch.setattr("builtins.input", lambda _: "Y")

    # make a fake folder for testing existed folder error handling
    new_fake_result_dir = Const.RESULT_DIR_PATH / "existed_result"
    new_fake_result_dir.mkdir(parents=True, exist_ok=True)
    if test_type == 'print': 
        main()
        text_printed = capsys.readouterr()
        assert expected in text_printed.out
    else:
        with pytest.raises(test_type) as exc_info:
            main()
        assert expected in str(exc_info.value)



