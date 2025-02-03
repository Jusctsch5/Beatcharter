import pytest
import logging

from beatcharter.beatchart.audio_analysis.librosa_wrapper import LibrosaWrapper
from beatcharter.beatchart.audio_analysis.aubio_wrapper import AubioWrapper

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def aubio_wrapper():
    """Fixture that yields a mocked AubioWrapper instance"""
    yield AubioWrapper()
    

@pytest.fixture
def librosa_wrapper():
    """Fixture that yields a mocked LibrosaWrapper instance"""
    yield LibrosaWrapper()

