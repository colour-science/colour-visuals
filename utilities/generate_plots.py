#!/usr/bin/env python
"""
Generate Plots
==============
"""

from __future__ import annotations

import matplotlib as mpl

mpl.use("AGG")

import os  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pygfx as gfx  # noqa: E402
import pylinalg as la  # noqa: E402
from colour.io import write_image  # noqa: E402
from colour.plotting import colour_style, plot_image  # noqa: E402
from colour.utilities import filter_warnings  # noqa: E402
from wgpu.gui.offscreen import WgpuCanvas  # noqa: E402

from colour_visuals.axes import VisualAxes  # noqa: E402
from colour_visuals.diagrams import (  # noqa: E402
    VisualChromaticityDiagram,
    VisualChromaticityDiagramCIE1931,
    VisualChromaticityDiagramCIE1960UCS,
    VisualChromaticityDiagramCIE1976UCS,
    VisualSpectralLocus2D,
    VisualSpectralLocus3D,
)
from colour_visuals.grid import VisualGrid  # noqa: E402
from colour_visuals.patterns import (  # noqa: E402
    pattern_colour_wheel,
    pattern_hue_stripes,
    pattern_hue_swatches,
)
from colour_visuals.pointer_gamut import (  # noqa: E402
    VisualPointerGamut2D,
    VisualPointerGamut3D,
)
from colour_visuals.rgb_colourspace import (  # noqa: E402
    VisualRGBColourspace2D,
    VisualRGBColourspace3D,
)
from colour_visuals.rgb_scatter import VisualRGBScatter3D  # noqa: E402
from colour_visuals.rosch_macadam import VisualRoschMacAdam  # noqa: E402

__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "generate_documentation_plots",
]


def generate_documentation_plots(output_directory: str):
    """
    Generate documentation plots.

    Parameters
    ----------
    output_directory
        Output directory.
    """

    filter_warnings()

    colour_style()

    np.random.seed(16)

    # *************************************************************************
    # Documentation
    # *************************************************************************
    canvas = WgpuCanvas(size=(960, 540))
    renderer = gfx.renderers.WgpuRenderer(canvas)
    camera = gfx.PerspectiveCamera(50, 16 / 9)  # pyright: ignore

    scene = gfx.Scene()
    scene.add(
        gfx.Background(
            None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
        )
    )

    canvas.request_draw(lambda: renderer.render(scene, camera))

    for visual_class, arguments, affix in [
        (VisualAxes, {"model": "CIE Lab"}, None),
        (VisualSpectralLocus2D, {}, None),
        (VisualSpectralLocus3D, {}, None),
        (VisualChromaticityDiagram, {}, None),
        (
            VisualChromaticityDiagramCIE1931,
            {"kwargs_visual_chromaticity_diagram": {"opacity": 0.25}},
            None,
        ),
        (
            VisualChromaticityDiagramCIE1960UCS,
            {"kwargs_visual_chromaticity_diagram": {"opacity": 0.25}},
            None,
        ),
        (
            VisualChromaticityDiagramCIE1976UCS,
            {"kwargs_visual_chromaticity_diagram": {"opacity": 0.25}},
            None,
        ),
        (VisualGrid, {}, None),
        (VisualPointerGamut2D, {}, None),
        (VisualPointerGamut3D, {}, None),
        (VisualRGBColourspace2D, {}, None),
        (VisualRGBColourspace3D, {"wireframe": True}, None),
        (VisualRGBScatter3D, {"RGB": np.random.random([24, 32, 3])}, None),
        (VisualRoschMacAdam, {}, None),
        (
            VisualRGBScatter3D,
            {"RGB": pattern_hue_swatches(), "model": "RGB"},
            "HueSwatches",
        ),
        (
            VisualRGBScatter3D,
            {"RGB": pattern_hue_stripes(), "model": "RGB"},
            "HueStripes",
        ),
        (
            VisualRGBScatter3D,
            {"RGB": pattern_colour_wheel(), "model": "RGB"},
            "ColourWheel",
        ),
    ]:
        visual = visual_class(**arguments)

        if isinstance(
            visual,
            (VisualRGBColourspace3D, VisualRGBScatter3D, VisualRoschMacAdam),
        ):
            visual.local.rotation = la.quat_from_euler(
                (-np.pi / 4, 0), order="XY"
            )

        scene.add(visual)
        camera.show_object(
            visual, up=np.array([0, 0, 1]), scale=1.25  # pyright: ignore
        )

        affix = (  # noqa: PLW2901
            visual.__class__.__name__ if affix is None else affix
        )

        write_image(
            np.array(renderer.target.draw()),
            os.path.join(output_directory, f"Plotting_{affix}.png"),
            bit_depth="uint8",
        )
        scene.remove(visual)

    # *************************************************************************
    # README.rst
    # *************************************************************************
    visuals = [
        VisualGrid(size=2),
        VisualChromaticityDiagramCIE1931(
            kwargs_visual_chromaticity_diagram={"opacity": 0.25}
        ),
        VisualRGBColourspace2D("ACEScg"),
        VisualRGBColourspace2D("Display P3", colour=np.array([0.5, 0.5, 0.5])),
        VisualRGBColourspace3D("Display P3", opacity=0.5, wireframe=True),
        VisualRGBScatter3D(np.random.random([24, 32, 3]), "ACEScg"),
    ]

    group = gfx.Group()
    for visual in visuals:
        group.add(visual)
    scene.add(group)

    camera.local.position = np.array([-0.25, -0.5, 2])
    camera.show_pos(np.array([1 / 3, 1 / 3, 0.4]))

    write_image(
        np.array(renderer.target.draw()),
        os.path.join(output_directory, "Visuals_001.png"),
        bit_depth="uint8",
    )
    scene.remove(group)

    visuals = [
        VisualGrid(size=2),
        VisualSpectralLocus2D(),
        VisualSpectralLocus3D(),
        VisualRGBColourspace2D("ACEScg"),
        VisualRGBColourspace2D("Display P3", colour=np.array([0.5, 0.5, 0.5])),
        VisualPointerGamut3D(),
        VisualRGBScatter3D(np.random.random([24, 32, 3]), "ACEScg"),
    ]

    group = gfx.Group()
    for visual in visuals:
        group.add(visual)
    scene.add(group)

    camera.local.position = np.array([0.25, -0.5, 2.25])
    camera.show_pos(np.array([1 / 3, 1 / 3, 0.6]))

    write_image(
        np.array(renderer.target.draw()),
        os.path.join(output_directory, "Visuals_002.png"),
        bit_depth="uint8",
    )
    scene.remove(group)

    visuals = [
        VisualGrid(size=4),
        VisualSpectralLocus3D(model="CIE Lab"),
        VisualPointerGamut3D(model="CIE Lab", colours=np.array([1, 0.5, 0])),
        VisualRGBColourspace3D(
            "Display P3",
            model="CIE Lab",
            opacity=0.5,
            wireframe=True,
            segments=8,
        ),
        VisualRGBScatter3D(
            np.random.random([24, 32, 3]), "Display P3", model="CIE Lab"
        ),
    ]

    group = gfx.Group()
    for visual in visuals:
        group.add(visual)
    scene.add(group)

    camera.local.position = np.array([1.5, -1.5, 5])
    camera.show_pos(np.array([0, 0, 0.5]))

    write_image(
        np.array(renderer.target.draw()),
        os.path.join(output_directory, "Visuals_003.png"),
        bit_depth="uint8",
    )
    scene.remove(group)

    # *************************************************************************
    # Patterns
    # *************************************************************************
    arguments = {
        "tight_layout": True,
        "transparent_background": True,
        "filename": os.path.join(
            output_directory, "Plotting_PatternHueSwatches.png"
        ),
    }
    plt.close(plot_image(pattern_hue_swatches(), **arguments)[0])

    arguments["filename"] = os.path.join(
        output_directory, "Plotting_PatternHueStripes.png"
    )
    plt.close(plot_image(pattern_hue_stripes(), **arguments)[0])

    arguments["filename"] = os.path.join(
        output_directory, "Plotting_PatternColourWheel.png"
    )
    plt.close(plot_image(pattern_colour_wheel(), **arguments)[0])


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    generate_documentation_plots(os.path.join("..", "docs", "_static"))
