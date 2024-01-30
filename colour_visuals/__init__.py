"""
Colour - Visuals
================

WebGPU-based visuals for colour science applications.
"""

from __future__ import annotations

import contextlib
import os
import subprocess

import colour
import numpy as np

from .axes import (
    VisualAxes,
)
from .daylight_locus import (
    VisualDaylightLocus,
)
from .diagrams import (
    VisualChromaticityDiagram,
    VisualChromaticityDiagramCIE1931,
    VisualChromaticityDiagramCIE1960UCS,
    VisualChromaticityDiagramCIE1976UCS,
    VisualSpectralLocus2D,
    VisualSpectralLocus3D,
)
from .grid import (
    VisualGrid,
)
from .patterns import (
    pattern_colour_wheel,
    pattern_hue_stripes,
    pattern_hue_swatches,
)
from .planckian_locus import (
    VisualPlanckianLocus,
)
from .pointer_gamut import (
    VisualPointerGamut2D,
    VisualPointerGamut3D,
)
from .rgb_colourspace import (
    VisualRGBColourspace2D,
    VisualRGBColourspace3D,
)
from .rgb_scatter import (
    VisualRGBScatter3D,
)
from .rosch_macadam import (
    VisualRoschMacAdam,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualAxes",
]
__all__ = [
    "VisualDaylightLocus",
]
__all__ += [
    "VisualSpectralLocus2D",
    "VisualSpectralLocus3D",
    "VisualChromaticityDiagram",
    "VisualChromaticityDiagramCIE1931",
    "VisualChromaticityDiagramCIE1960UCS",
    "VisualChromaticityDiagramCIE1976UCS",
]
__all__ += [
    "VisualGrid",
]
__all__ += [
    "VisualPlanckianLocus",
]
__all__ += [
    "VisualPointerGamut2D",
    "VisualPointerGamut3D",
]
__all__ += [
    "VisualRGBColourspace2D",
    "VisualRGBColourspace3D",
]
__all__ += [
    "VisualRGBScatter3D",
]
__all__ += [
    "VisualRoschMacAdam",
]
__all__ += [
    "pattern_hue_swatches",
    "pattern_hue_stripes",
    "pattern_colour_wheel",
]
__application_name__ = "Colour - Visuals"

__major_version__ = "0"
__minor_version__ = "1"
__change_version__ = "0"
__version__ = ".".join((__major_version__, __minor_version__, __change_version__))

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

colour.utilities.ANCILLARY_COLOUR_SCIENCE_PACKAGES["colour-visuals"] = _version  # pyright: ignore

del _version

# TODO: Remove legacy printing support when deemed appropriate.
with contextlib.suppress(TypeError):
    np.set_printoptions(legacy="1.13")
