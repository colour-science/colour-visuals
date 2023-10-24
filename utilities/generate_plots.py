#!/usr/bin/env python
"""
Generate Plots
==============
"""

from __future__ import annotations

import os

import numpy as np
import pygfx as gfx
import pylinalg as la
from colour.io import write_image
from wgpu.gui.offscreen import WgpuCanvas

from colour_visuals.axes import VisualAxes
from colour_visuals.diagrams import (
    VisualChromaticityDiagram,
    VisualChromaticityDiagramCIE1931,
    VisualChromaticityDiagramCIE1960UCS,
    VisualChromaticityDiagramCIE1976UCS,
    VisualSpectralLocus2D,
    VisualSpectralLocus3D,
)
from colour_visuals.grid import VisualGrid
from colour_visuals.pointer_gamut import (
    VisualPointerGamut2D,
    VisualPointerGamut3D,
)
from colour_visuals.rgb_colourspace import (
    VisualRGBColourspace2D,
    VisualRGBColourspace3D,
)
from colour_visuals.rgb_scatter import VisualRGBScatter3D
from colour_visuals.rosch_macadam import VisualRoschMacAdam

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

    for visual_class, arguments in [
        (VisualAxes, {"model": "CIE Lab"}),
        (VisualSpectralLocus2D, {}),
        (VisualSpectralLocus3D, {}),
        (VisualChromaticityDiagram, {}),
        (
            VisualChromaticityDiagramCIE1931,
            {"kwargs_visual_chromaticity_diagram": {"opacity": 0.25}},
        ),
        (
            VisualChromaticityDiagramCIE1960UCS,
            {"kwargs_visual_chromaticity_diagram": {"opacity": 0.25}},
        ),
        (
            VisualChromaticityDiagramCIE1976UCS,
            {"kwargs_visual_chromaticity_diagram": {"opacity": 0.25}},
        ),
        (VisualGrid, {}),
        (VisualPointerGamut2D, {}),
        (VisualPointerGamut3D, {}),
        (VisualRGBColourspace2D, {}),
        (VisualRGBColourspace3D, {"wireframe": True}),
        (VisualRGBScatter3D, {"RGB": np.random.random([24, 32, 3])}),
        (VisualRoschMacAdam, {}),
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

        write_image(
            np.array(renderer.target.draw()),
            os.path.join(
                output_directory, f"Plotting_{visual.__class__.__name__}.png"
            ),
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
        VisualRGBColourspace2D(
            "Display P3", colours=np.array([0.5, 0.5, 0.5])
        ),
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
        VisualRGBColourspace2D(
            "Display P3", colours=np.array([0.5, 0.5, 0.5])
        ),
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


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    generate_documentation_plots(os.path.join("..", "docs", "_static"))
