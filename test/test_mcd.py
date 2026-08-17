from mcd import main

@pytest.mark.parametrize(
    "code, expected",
    [
        ("1234", True),
        ("999", False),
        ("abcd", False),
    ],
    ids=["valid_4_digits", "too_short", "contains_letters"] # Names for each test case!
)
def test_verify_code(code, expected, monkeypatch):
    monkeypatch.setattr(sys, "argv", code)

    result = main()
    assert result == expected