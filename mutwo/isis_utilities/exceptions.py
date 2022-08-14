__all__ = ("MonophonicSynthesizerError",)


class MonophonicSynthesizerError(Exception):
    def __init__(self):
        super().__init__(
            "Can't convert instance of SimultaneousEvent to ISiS "
            "score. ISiS is only a"
            " monophonic synthesizer and can't read "
            "multiple simultaneous voices!"
        )
