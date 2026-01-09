import sys
from pathlib import Path
import pytest
import asyncio

# Add project root to sys.path to allow importing 'zen' module
sys.path.insert(0, str(Path(__file__).parent.parent))

from zen.pkm.config import PKMConfig
from zen.pkm.storage import PKMStorage
from zen.utils.config import Config

@pytest.fixture
def config():
    """Fixture to provide PKMConfig instance."""
    return PKMConfig.load()

@pytest.fixture
def zen_config():
    """Fixture to provide ZenConfig instance."""
    return Config()

@pytest.fixture
def storage(config):
    """Fixture to provide PKMStorage instance."""
    return PKMStorage(config)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
