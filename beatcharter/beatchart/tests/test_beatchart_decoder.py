import pathlib
from numpy import float64
from numpy.typing import NDArray
import logging
import pytest

from beatcharter.beatchart.audio_analysis.librosa_wrapper import LibrosaWrapper
from beatcharter.beatchart.audio_analysis.aubio_wrapper import AubioWrapper

samples_dir = pathlib.Path(__file__).parent.parent.parent.parent / "samples"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

allowed_bpm_offset = 5.0


def check_if_bpm_within_offset(
    found_bpm: NDArray[float64], correct_bpm: float, offset_bpm: float
):
    for bpm in found_bpm:
        logger.debug(
            f"bpm: {bpm}, correct_bpm: {correct_bpm}, offset_bpm: {offset_bpm}"
        )
        assert bpm > correct_bpm - offset_bpm
        assert bpm < correct_bpm + offset_bpm


def check_bpm_of_file(wrapper: AubioWrapper, file_name, correct_bpm):
    check_if_bpm_within_offset(
        wrapper.calculate_bpm(file_name), correct_bpm, allowed_bpm_offset
    )


def test_decode_song(aubio_wrapper: AubioWrapper):
    assert aubio_wrapper.calculate_bpm(samples_dir / "sample1.mp3")


@pytest.mark.parametrize("wrapper", ["librosa_wrapper", "aubio_wrapper"])
def test_find_bpm(wrapper, request):
    wrapper = request.getfixturevalue(wrapper)  # This gets the actual fixture
    check_bpm_of_file(wrapper, samples_dir / "dixieland.mp3", 114.0)
    check_bpm_of_file(wrapper, samples_dir / "batleh.mp3", 111.0)
    check_bpm_of_file(wrapper, samples_dir / "evelina.mp3", 120.0)
    check_bpm_of_file(wrapper, samples_dir / "grandfather.mp3", 115.0)
    check_bpm_of_file(wrapper, samples_dir / "tenting.mp3", 144.0 / 2)
