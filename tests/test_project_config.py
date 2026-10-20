from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_streamlit_pin_supports_documented_python_310():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text(
        encoding="utf-8"
    )

    assert 'python-version: ["3.10", "3.12"]' in workflow
    assert "streamlit==1.65.0" in requirements
