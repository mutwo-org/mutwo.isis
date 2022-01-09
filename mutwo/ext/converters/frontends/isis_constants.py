"""Constants to be used for and with :mod:`mutwo.ext.converters.frontends.isis`.

The file mostly contains different flags for running ISiS.
The flag definitions are documented
`here <https://isis-documentation.readthedocs.io/en/latest/CmdLineArgs.html>`_.
"""

ISIS_PATH = "isis.sh"
"""The path to the ISiS shell script. When installing ISiS with the packed
'Install_ISiS_commandline.sh' script, the path should be 'isis.sh'."""


SILENT_FLAG = "--quiet"
"""Flag for preventing ISiS from printing any information
during rendering."""


SECTION_LYRIC_NAME = "lyrics"
"""Section name for lyrics in score config file"""


SECTION_SCORE_NAME = "score"
"""Section name for score in score config file"""
