"""
Pattern Generators
==================

Defines various pattern generators:

-   :func:`colour_visuals.pattern_hue_swatches`
-   :func:`colour_visuals.pattern_hue_stripes`
-   :func:`colour_visuals.pattern_colour_wheel`

"""

from __future__ import annotations

import numpy as np
from colour.hints import Literal, NDArray
from colour.models import HSV_to_RGB
from colour.utilities import full, orient, tstack

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "pattern_hue_swatches",
    "pattern_hue_stripes",
    "pattern_colour_wheel",
]


def pattern_hue_swatches(count: int = 12, samples: int = 256) -> NDArray:
    """
    Generate a given count of hue swatches.

    Parameters
    ----------
    count
        Hue swatch count.
    samples
        Hue swatch samples.

    Examples
    --------
    >>> import os
    >>> import pygfx as gfx
    >>> import pylinalg as la
    >>> from colour.plotting import plot_image
    >>> from colour.utilities import suppress_stdout
    >>> from colour_visuals import VisualRGBScatter3D, VisualRGBColourspace3D
    >>> from wgpu.gui.auto import WgpuCanvas
    >>> plot_image(pattern_hue_swatches())  # doctest: +SKIP
    ... # doctest: +ELLIPSIS
    (<Figure size ... with 1 Axes>, <...Axes...>)

    .. image:: ../_static/Plotting_PatternHueSwatches.png
        :align: center
        :alt: pattern-hue-swatches

    >>> with suppress_stdout():
    ...     canvas = WgpuCanvas(size=(960, 540))
    ...     scene = gfx.Scene()
    ...     scene.add(
    ...         gfx.Background(
    ...             None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...         )
    ...     )
    ...     visual = VisualRGBScatter3D(pattern_hue_swatches(), model="RGB")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_HueSwatches.png
        :align: center
        :alt: hue-swatches
    """

    H = np.linspace(0, 1, count + 1)

    xv, yv = np.meshgrid(np.linspace(0, 1, samples), np.linspace(0, 1, samples))

    slices = []
    for i in range(count + 1):
        slices.append(tstack([full(xv.shape, H[i]), xv, yv]))

    RGB = HSV_to_RGB(np.hstack(slices))

    return RGB


def pattern_hue_stripes(count: int = 6, samples=256):
    """
    Generate a given count of hue stripes.

    Parameters
    ----------
    count
        Hue stripe count.
    samples
        Hue stripe samples.

    Examples
    --------
    >>> import os
    >>> import pygfx as gfx
    >>> import pylinalg as la
    >>> from colour.plotting import plot_image
    >>> from colour.utilities import suppress_stdout
    >>> from colour_visuals import VisualRGBScatter3D, VisualRGBColourspace3D
    >>> from wgpu.gui.auto import WgpuCanvas
    >>> plot_image(pattern_hue_stripes())  # doctest: +SKIP
    ... # doctest: +ELLIPSIS
    (<Figure size ... with 1 Axes>, <...Axes...>)

    .. image:: ../_static/Plotting_PatternHueStripes.png
        :align: center
        :alt: pattern-hue-stripes

    >>> with suppress_stdout():
    ...     canvas = WgpuCanvas(size=(960, 540))
    ...     scene = gfx.Scene()
    ...     scene.add(
    ...         gfx.Background(
    ...             None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...         )
    ...     )
    ...     visual = VisualRGBScatter3D(pattern_hue_stripes(), model="RGB")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_HueStripes.png
        :align: center
        :alt: hue-stripes
    """

    H = np.linspace(0, 1, count + 1)
    V = np.linspace(0, 1, samples)

    xv, yv = np.meshgrid(H, V)

    RGB = HSV_to_RGB(tstack([xv, np.ones(xv.shape), yv]))

    return orient(RGB, "90 CCW")


def pattern_colour_wheel(
    samples: int = 256,
    method: Literal["Colour", "Nuke"] = "Colour",
    clip_circle: bool = True,
) -> NDArray:
    """
    Generate a colour wheel.

    Parameters
    ----------
    samples
        Colour wheel samples.
    method
        Colour wheel method.
    clip_circle
        Whether to clip the colour wheel to a circle shape.

    Examples
    --------
    >>> import os
    >>> import pygfx as gfx
    >>> import pylinalg as la
    >>> from colour.plotting import plot_image
    >>> from colour.utilities import suppress_stdout
    >>> from colour_visuals import VisualRGBScatter3D, VisualRGBColourspace3D
    >>> from wgpu.gui.auto import WgpuCanvas
    >>> plot_image(pattern_colour_wheel())  # doctest: +SKIP
    ... # doctest: +ELLIPSIS
    (<Figure size ... with 1 Axes>, <...Axes...>)

    .. image:: ../_static/Plotting_PatternColourWheel.png
        :align: center
        :alt: pattern-colour-wheel

    >>> with suppress_stdout():
    ...     canvas = WgpuCanvas(size=(960, 540))
    ...     scene = gfx.Scene()
    ...     scene.add(
    ...         gfx.Background(
    ...             None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...         )
    ...     )
    ...     visual = VisualRGBScatter3D(pattern_colour_wheel(), model="RGB")
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_ColourWheel.png
        :align: center
        :alt: colour_wheel
    """

    xx, yy = np.meshgrid(np.linspace(-1, 1, samples), np.linspace(-1, 1, samples))

    S = np.sqrt(xx**2 + yy**2)
    H = (np.arctan2(xx, yy) + np.pi) / (np.pi * 2)

    HSV = tstack([H, S, np.ones(H.shape)])
    RGB = HSV_to_RGB(HSV)

    if clip_circle:
        RGB[S > 1] = 0

    if method.lower() == "nuke":
        RGB = orient(RGB, "Flip")
        RGB = orient(RGB, "90 CW")

    return RGB
