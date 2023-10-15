"""
Colour - Visuals
================

WebGPU-based visuals for colour science applications.
"""

from __future__ import annotations

import contextlib
import numpy as np
import os
import subprocess

import colour

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = []

__application_name__ = "Colour - Visuals"

__major_version__ = "0"
__minor_version__ = "1"
__change_version__ = "0"
__version__ = ".".join(
    (__major_version__, __minor_version__, __change_version__)
)

try:
    _version: str = (
        subprocess.check_output(
            ["git", "describe"],  # noqa: S603, S607
            cwd=os.path.dirname(__file__),
            stderr=subprocess.STDOUT,
        )
        .strip()
        .decode("utf-8")
    )
except Exception:
    _version: str = __version__

colour.utilities.ANCILLARY_COLOUR_SCIENCE_PACKAGES[  # pyright: ignore
    "colour-visuals"
] = _version

del _version

# TODO: Remove legacy printing support when deemed appropriate.
with contextlib.suppress(TypeError):
    np.set_printoptions(legacy="1.13")
