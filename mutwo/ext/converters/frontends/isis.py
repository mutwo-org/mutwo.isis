"""Render singing signals from mutwo data via `ISiS <https://forum.ircam.fr/projects/detail/isis/>`_.

ISiS (IRCAM Singing Synthesis) is a `"command line application for singing
synthesis that can be used to generate singing signals by means of synthesizing
them from melody and lyrics."
<https://isis-documentation.readthedocs.io/en/latest/Intro.html#the-isis-command-line>`_.
"""

import configparser
import os
import typing

from mutwo.core import converters
from mutwo.core import events
from mutwo.core.utilities import constants

from mutwo.ext.converters.frontends import isis_constants
from mutwo.ext import parameters as ext_parameters

__all__ = ("IsisScoreConverter", "IsisConverter")

ConvertableEventUnion = typing.Union[
    events.basic.SimpleEvent,
    events.basic.SequentialEvent[events.basic.SimpleEvent],
]
ExtractedDataDict = dict[
    # duration, consonants, vowel, pitch, volume
    str,
    typing.Any,
]


class IsisScoreConverter(converters.abc.EventConverter):
    """Class to convert mutwo events to a `ISiS score file. <https://isis-documentation.readthedocs.io/en/latest/score.html>`_

    :param simple_event_to_pitch: Function to extract an instance of
        :class:`mutwo.ext.parameters.abc.Pitch` from a simple event.
    :param simple_event_to_volume:
    :param simple_event_to_vowel:
    :param simple_event_to_consonant_tuple:
    :param is_simple_event_rest:
    :param tempo: Tempo in beats per minute (BPM). Defaults to 60.
    :param global_transposition: global transposition in midi numbers. Defaults to 0.
    :param n_events_per_line: How many events the score shall contain per line.
        Defaults to 5.
    """

    _extracted_data_dict_rest = {
        "consonant_tuple": tuple([]),
        "vowel": "_",
        "pitch": ext_parameters.pitches.WesternPitch(
            "c",
            -1,
            concert_pitch=440,
            concert_pitch_octave=4,
            concert_pitch_pitch_class=9,
        ),
        "volume": ext_parameters.volumes.DirectVolume(0),
    }

    def __init__(
        self,
        simple_event_to_pitch: typing.Callable[
            [events.basic.SimpleEvent], ext_parameters.abc.Pitch
        ] = lambda simple_event: simple_event.pitch_list[  # type: ignore
            0
        ],
        simple_event_to_volume: typing.Callable[
            [events.basic.SimpleEvent], ext_parameters.abc.Volume
        ] = lambda simple_event: simple_event.volume,  # type: ignore
        simple_event_to_vowel: typing.Callable[
            [events.basic.SimpleEvent], str
        ] = lambda simple_event: simple_event.vowel,  # type: ignore
        simple_event_to_consonant_tuple: typing.Callable[
            [events.basic.SimpleEvent], tuple[str, ...]
        ] = lambda simple_event: simple_event.consonant_tuple,  # type: ignore
        is_simple_event_rest: typing.Callable[
            [events.basic.SimpleEvent], bool
        ] = lambda simple_event: not (
            hasattr(simple_event, "pitch_list")
            and simple_event.pitch_list  # type: ignore
        ),
        tempo: constants.Real = 60,
        global_transposition: int = 0,
        default_sentence_loudness: typing.Union[constants.Real, None] = None,
        n_events_per_line: int = 5,
    ):
        self._tempo = tempo
        self._global_transposition = global_transposition
        self._default_sentence_loudness = default_sentence_loudness
        self._n_events_per_line = n_events_per_line
        self._is_simple_event_rest = is_simple_event_rest

        self._extraction_function_dict = {
            "consonant_tuple": simple_event_to_consonant_tuple,
            "vowel": simple_event_to_vowel,
            "pitch": simple_event_to_pitch,
            "volume": simple_event_to_volume,
        }

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _add_lyric_section(
        self,
        score_config_file: configparser.ConfigParser,
        extracted_data_dict_per_event_tuple: tuple[ExtractedDataDict, ...],
    ):
        score_config_file[isis_constants.SECTION_LYRIC_NAME] = {
            "xsampa": " ".join(
                map(
                    lambda extracted_data: " ".join(
                        extracted_data["consonant_tuple"] + (extracted_data["vowel"],)
                    ),
                    extracted_data_dict_per_event_tuple,
                )
            )
        }

    def _add_score_section(
        self,
        score_config_file: configparser.ConfigParser,
        extracted_data_dict_per_event_tuple: tuple[ExtractedDataDict, ...],
    ):
        score_section = {
            "globalTransposition": self._global_transposition,
            "tempo": self._tempo,
        }
        for parameter_name, lambda_function in (
            (
                "midiNotes",
                lambda extracted_data: str(extracted_data["pitch"].midi_pitch_number),
            ),
            (
                "rhythm",
                lambda extracted_data: str(extracted_data["duration"]),
            ),
            (
                "loud_accents",
                lambda extracted_data: str(extracted_data["volume"].amplitude),
            ),
        ):
            score_section.update(
                {
                    parameter_name: ", ".join(
                        map(lambda_function, extracted_data_dict_per_event_tuple)
                    )
                }
            )
        score_config_file[isis_constants.SECTION_SCORE_NAME] = score_section

    def _convert_simple_event(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        _: constants.DurationType,
    ) -> tuple[ExtractedDataDict]:
        duration = simple_event_to_convert.duration
        extracted_data_dict: dict[str, typing.Any] = {"duration": duration}
        for (
            extracted_data_name,
            extraction_function,
        ) in self._extraction_function_dict.items():
            try:
                extracted_information = extraction_function(simple_event_to_convert)
            except AttributeError:
                return (dict(duration=duration, **self._extracted_data_dict_rest),)

            extracted_data_dict.update({extracted_data_name: extracted_information})

        return (extracted_data_dict,)

    def _convert_simultaneous_event(
        self,
        _: events.basic.SimultaneousEvent,
        __: constants.DurationType,
    ):
        raise NotImplementedError(
            "Can't convert instance of SimultaneousEvent to ISiS "
            "Score. ISiS is only a"
            " monophonic synthesizer and can't read "
            "multiple simultaneous voices!"
        )

    # ###################################################################### #
    #                             public api                                 #
    # ###################################################################### #

    def convert(self, event_to_convert: ConvertableEventUnion, path: str) -> None:
        """Render ISiS score file from the passed event.

        :param event_to_convert: The event that shall be rendered to a ISiS score
            file.
        :type event_to_convert: typing.Union[events.basic.SimpleEvent, events.basic.SequentialEvent[events.basic.SimpleEvent]]
        :param path: where to write the ISiS score file
        :type path: str

        **Example:**

        >>> from mutwo.events import events.basic, music
        >>> from mutwo.ext.parameters import pitches
        >>> from mutwo.ext.converters.frontends import isis
        >>> notes = events.basic.SequentialEvent(
        >>>    [
        >>>         music.NoteLike(pitches.WesternPitch(pitch_name), 0.5, 0.5)
        >>>         for pitch_name in 'c f d g'.split(' ')
        >>>    ]
        >>> )
        >>> for consonants, vowel, note in zip([[], [], ['t'], []], ['a', 'o', 'e', 'a'], notes):
        >>>     note.vowel = vowel
        >>>     note.consonants = consonants
        >>> isis_score_converter = isis.IsisScoreConverter('my_singing_score')
        >>> isis_score_converter.convert(notes)
        """

        # ISiS can't handle two sequental rests, therefore we have to tie two
        # adjacent rests together.
        if isinstance(event_to_convert, events.abc.ComplexEvent):
            event_to_convert = event_to_convert.tie_by(
                lambda event0, event1: self._is_simple_event_rest(event0)
                and self._is_simple_event_rest(event1),
                event_type_to_examine=events.basic.SimpleEvent,
                mutate=False,  # type: ignore
            )

        extracted_data_dict_per_event_tuple = self._convert_event(event_to_convert, 0)

        # ":" delimiter is used in ISiS example score files
        # see https://isis-documentation.readthedocs.io/en/latest/score.html#score-example
        score_config_file = configparser.ConfigParser(delimiters=":")

        self._add_lyric_section(score_config_file, extracted_data_dict_per_event_tuple)
        self._add_score_section(score_config_file, extracted_data_dict_per_event_tuple)

        with open(path, "w") as f:
            score_config_file.write(f)


class IsisConverter(converters.abc.Converter):
    """Generate audio files with `ISiS <https://forum.ircam.fr/projects/detail/isis/>`_.

    :param isis_score_converter: The :class:`IsisScoreConverter` that shall be used
        to render the ISiS score file from a mutwo event.
    :param *flag: Flag that shall be added when calling ISiS. Several of the supported
        ISiS flags can be found in :mod:`mutwo.ext.converters.frontends.isis_constants`.
    :param remove_score_file: Set to True if :class:`IsisConverter` shall remove the
        ISiS score file after rendering. Defaults to False.

    **Disclaimer:** Before using the :class:`IsisConverter`, make sure ISiS has been
    correctly installed on your system.
    """

    def __init__(
        self,
        isis_score_converter: IsisScoreConverter,
        *flag: str,
        remove_score_file: bool = False,
    ):
        self.flags = flag
        self.isis_score_converter = isis_score_converter
        self.remove_score_file = remove_score_file

    def convert(
        self,
        event_to_convert: ConvertableEventUnion,
        path: str,
        score_path: typing.Optional[str] = None,
    ) -> None:
        """Render sound file via ISiS from mutwo event.

        :param event_to_convert: The event that shall be rendered.
        :param path: The path / filename of the resulting sound file
        :param score_path: The path where the score file shall be written to.

        **Disclaimer:** Before using the :class:`IsisConverter`, make sure
        `ISiS <https://forum.ircam.fr/projects/detail/isis/>`_ has been
        correctly installed on your system.
        """

        if not score_path:
            score_path = f"{path.split('.')[0]}.isis_score.cfg"

        self.isis_score_converter.convert(event_to_convert, score_path)
        command = "{} -m {} -o {}".format(
            isis_constants.ISIS_PATH,
            score_path,
            path,
        )
        for flag in self.flags:
            command += " {} ".format(flag)

        os.system(command)

        if self.remove_score_file:
            os.remove(score_path)
