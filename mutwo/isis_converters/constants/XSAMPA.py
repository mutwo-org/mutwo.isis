"""This namespace contains all ISiS supported `XSAMPA <https://en.wikipedia.org/wiki/X-SAMPA>`_ signs.

See the `official ISiS documentation <https://isis-documentation.readthedocs.io/en/latest/score.html>`_
where everything is defined.
"""

vowel_tuple = tuple("a, e, E, 2, 9, @, i, o, O, u, y, o~, a~, e~, 9~".split(", "))
"""All by ISiS supported vowels."""

semi_vowel_tuple = tuple("w, j, H".split(", "))
"""All by ISiS supported semi vowels."""

voiced_fricative_tuple = tuple("v, z, Z".split(", "))
"""All by ISiS supported voiced fricatives."""

unvoiced_fricative_tuple = tuple("f, s, S".split(", "))
"""All by ISiS supported unvoiced fricatives."""

voiced_plosive_tuple = tuple("b, d, g".split(", "))
"""All by ISiS supported voiced plosives."""

unvoiced_plosive_tuple = tuple("p, t, k".split(", "))
"""All by ISiS supported unvoiced plosives."""

nasal_tuple = tuple("m, n, N".split(", "))
"""All by ISiS supported nasals."""

other_tuple = tuple("R, l".split(", "))
"""All by ISiS supported other phonems."""
