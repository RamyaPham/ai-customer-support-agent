import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.db import reload_data


@pytest.fixture(autouse=True)
def reset_data():
    """Reset seed data before each test to prevent mutation side effects."""
    reload_data()
