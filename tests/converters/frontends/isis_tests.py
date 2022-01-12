import configparser
import os
import typing
import unittest

from mutwo.core import events
from mutwo.core.utilities import constants

from mutwo.ext import parameters as ext_parameters
from mutwo.ext import converters


class NoteLikeWithText(events.basic.SimpleEvent):
    """NoteLike with additional consonants and vowel attributes.

    Mocking class (only for testing purposes).
    """

    def __init__(
        self,
        pitch_list,
        duration: constants.DurationType,
        volume,
        consonant_tuple: typing.Tuple[str],
        vowel: str,
    ):
        super().__init__(duration)
        self.pitch_list = pitch_list
        self.volume = ext_parameters.volumes.DirectVolume(volume)
        self.consonant_tuple = consonant_tuple
        self.vowel = vowel


class IsisScoreConverterTest(unittest.TestCase):
    score_path = "tests/converters/frontends/isis-score.cfg"

    LyricSection = configparser.SectionProxy
    ScoreSection = configparser.SectionProxy

    @classmethod
    def setUpClass(cls):
        cls.converter = converters.frontends.isis.IsisScoreConverter()

    @classmethod
    def tearDownClass(cls):
        # remove score files
        os.remove(cls.score_path)

    def fetch_result_score_section_tuple(self) -> tuple[LyricSection, ScoreSection]:
        result_score = configparser.ConfigParser()
        result_score.read(self.score_path)
        result_lyric_section = result_score[
            converters.frontends.isis_constants.SECTION_LYRIC_NAME
        ]
        result_score_section = result_score[
            converters.frontends.isis_constants.SECTION_SCORE_NAME
        ]
        return result_lyric_section, result_score_section

    def test_convert_simple_event(self):
        simple_event = NoteLikeWithText(
            [ext_parameters.pitches.WesternPitch()], 2, 0.5, ("t",), "a"
        )
        self.converter.convert(simple_event, self.score_path)
        (
            result_lyric_section,
            result_score_section,
        ) = self.fetch_result_score_section_tuple()

        # check if lyric section is correct
        self.assertEqual(result_lyric_section["xsampa"], "t a")

        # check if score section is correct
        self.assertEqual(
            result_score_section["midiNotes"],
            f"{simple_event.pitch_list[0].midi_pitch_number}",
        )
        self.assertEqual(result_score_section["globalTransposition"], "0")
        self.assertEqual(result_score_section["rhythm"], "2")
        self.assertEqual(result_score_section["loud_accents"], "0.5")
        self.assertEqual(result_score_section["tempo"], str(self.converter._tempo))

    def test_convert_sequential_event(self):
        # Test if auto tie works!
        sequential_event = events.basic.SequentialEvent(
            [
                NoteLikeWithText(
                    [ext_parameters.pitches.WesternPitch()], 2, 0.5, ("t",), "a"
                ),
                events.basic.SimpleEvent(4),
                NoteLikeWithText([], 3, 1, tuple([]), ""),
                NoteLikeWithText(
                    [ext_parameters.pitches.WesternPitch()], 2, 0.5, ("t",), "a"
                ),
            ]
        )
        self.converter.convert(sequential_event, self.score_path)
        (
            result_lyric_section,
            result_score_section,
        ) = self.fetch_result_score_section_tuple()

        # check if lyric section is correct
        self.assertEqual(result_lyric_section["xsampa"], "t a _ t a")

        # check if score section is correct
        self.assertEqual(
            result_score_section["midiNotes"],
            ", ".join(
                str(sequential_event[index].pitch_list[0].midi_pitch_number)
                if hasattr(sequential_event[index], "pitch_list")
                else "0.0"
                for index in (0, 1, 3)
            ),
        )
        self.assertEqual(result_score_section["globalTransposition"], "0")
        self.assertEqual(result_score_section["rhythm"], "2, 7, 2")
        self.assertEqual(result_score_section["loud_accents"], "0.5, 0, 0.5")
        self.assertEqual(result_score_section["tempo"], str(self.converter._tempo))

    def test_convert_rest(self):
        simple_event = events.basic.SimpleEvent(3)
        self.converter.convert(simple_event, self.score_path)
        (
            result_lyric_section,
            result_score_section,
        ) = self.fetch_result_score_section_tuple()

        # check if lyric section is correct
        self.assertEqual(result_lyric_section["xsampa"], "_")

        # check if score section is correct
        self.assertEqual(result_score_section["midiNotes"], "0.0")
        self.assertEqual(result_score_section["globalTransposition"], "0")
        self.assertEqual(result_score_section["rhythm"], "3")
        self.assertEqual(result_score_section["loud_accents"], "0")
        self.assertEqual(result_score_section["tempo"], str(self.converter._tempo))


if __name__ == "__main__":
    unittest.main()
