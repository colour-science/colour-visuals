# !/usr/bin/env python
"""
Planckian Locus Visuals
=======================

Defines the *Planckian Locus* visuals:

-   :class:`colour_visuals.VisualPlanckianLocus`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.hints import (
    ArrayLike,
    Literal,
    Sequence,
    cast,
)
from colour.plotting import (
    CONSTANTS_COLOUR_STYLE,
    LABELS_PLANCKIAN_LOCUS_DEFAULT,
    lines_planckian_locus,
)
from colour.utilities import (
    as_int_scalar,
    optional,
)

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    append_channel,
    as_contiguous_array,
)
from colour_visuals.visual import (
    MixinPropertyColour,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
    visual_property,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "VisualPlanckianLocus",
]


class VisualPlanckianLocus(
    MixinPropertyColour,
    MixinPropertyMethod,
    MixinPropertyOpacity,
    MixinPropertyThickness,
    Visual,
):
    """
    Create a *Planckian Locus* visual.

    Parameters
    ----------
    method
        *Planckian Locus* method.
    labels
        Array of labels used to customise which iso-temperature lines will be
        drawn along the *Planckian Locus*. Passing an empty array will result
        in no iso-temperature lines being drawn.
    mireds
        Whether to use micro reciprocal degrees for the iso-temperature lines.
    colour
        Colour of the visual, if *None*, the colour is computed from the visual
        geometry.
    opacity
        Opacity of the visual.
    thickness
        Thickness of the visual lines.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualPlanckianLocus.method`
    -   :attr:`~colour_visuals.VisualPlanckianLocus.labels`
    -   :attr:`~colour_visuals.VisualPlanckianLocus.mireds`
    -   :attr:`~colour_visuals.VisualPlanckianLocus.colour`
    -   :attr:`~colour_visuals.VisualPlanckianLocus.opacity`
    -   :attr:`~colour_visuals.VisualPlanckianLocus.thickness`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualPlanckianLocus.__init__`
    -   :meth:`~colour_visuals.VisualPlanckianLocus.update`

    Examples
    --------
    >>> import os
    >>> from colour.utilities import suppress_stdout
    >>> from wgpu.gui.auto import WgpuCanvas
    >>> with suppress_stdout():
    ...     canvas = WgpuCanvas(size=(960, 540))
    ...     scene = gfx.Scene()
    ...     scene.add(
    ...         gfx.Background(
    ...             None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...         )
    ...     )
    ...     visual = VisualPlanckianLocus()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualPlanckianLocus.png
        :align: center
        :alt: visual-planckian-locus
    """

    def __init__(
        self,
        method: (
            Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"] | str
        ) = "CIE 1931",
        labels: Sequence | None = None,
        mireds: bool = False,
        colour: ArrayLike | None = None,
        opacity: float = 1,
        thickness: float = 1,
    ):
        super().__init__()

        self._planckian_locus = None
        self._iso_temperature_lines = []
        self._texts = []

        self._labels = None
        self._mireds = False

        with self.block_update():
            self.method = method
            self.labels = labels
            self.mireds = mireds
            self.colour = colour
            self.opacity = opacity
            self.thickness = thickness

        self.update()

    @visual_property
    def labels(
        self,
    ) -> Sequence | None:
        """
        Getter and setter property for the labels.

        Parameters
        ----------
        value
            Value to set the labels with.

        Returns
        -------
        :class:`str`
            Labels.
        """

        return self._labels

    @labels.setter
    def labels(self, value: Sequence | None):
        """Setter for the **self.labels** property."""

        self._labels = cast(
            Sequence,
            optional(
                value,
                LABELS_PLANCKIAN_LOCUS_DEFAULT["Mireds" if self._mireds else "Default"],
            ),
        )

    @visual_property
    def mireds(
        self,
    ) -> bool:
        """
        Getter and setter property for the mireds state.

        Parameters
        ----------
        value
            Value to set the mireds state with.

        Returns
        -------
        :class:`bool`
             Mireds state.
        """

        return self._mireds

    @mireds.setter
    def mireds(self, value: bool):
        """Setter for the **self.mireds** property."""

        self._mireds = value

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        lines_pl, lines_l = lines_planckian_locus(
            self._labels,
            self._mireds,
            method=self._method,
        )

        # Planckian Locus
        positions = np.reshape(
            np.concatenate(
                [lines_pl["position"][:-1], lines_pl["position"][1:]], axis=1
            ),
            (-1, 2),
        )

        positions = np.hstack(
            [
                positions,
                np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
            ]
        )

        if self._colour is None:
            colour_sl = np.reshape(
                np.concatenate(
                    [lines_pl["colour"][:-1], lines_pl["colour"][1:]], axis=1
                ),
                (-1, 3),
            )
        else:
            colour_sl = np.tile(self._colour, (positions.shape[0], 1))

        self._planckian_locus = gfx.Line(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                colors=as_contiguous_array(append_channel(colour_sl, self._opacity)),
            ),
            gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
        )
        self.add(self._planckian_locus)

        if not self._labels:
            return

        # Labels
        lines_itl = np.reshape(lines_l["position"], (len(self._labels), 20, 2))
        colours_itl = np.reshape(lines_l["colour"], (len(self._labels), 20, 3))
        self._iso_temperature_lines = []
        self._texts = []
        for i, label in enumerate(self._labels):
            positions = np.reshape(
                np.concatenate([lines_itl[i][:-1], lines_itl[i][1:]], axis=1), (-1, 2)
            )
            positions = np.hstack(
                [
                    positions,
                    np.full((positions.shape[0], 1), 0, DEFAULT_FLOAT_DTYPE_WGPU),
                ]
            )

            if self._colour is None:
                colour_w = np.reshape(
                    np.concatenate([colours_itl[i][:-1], colours_itl[i][1:]], axis=1),
                    (-1, 3),
                )
            else:
                colour_w = np.tile(self._colour, (positions.shape[0], 1))

            iso_temperature_line = gfx.Line(
                gfx.Geometry(
                    positions=as_contiguous_array(positions),
                    colors=as_contiguous_array(append_channel(colour_w, self._opacity)),
                ),
                gfx.LineSegmentMaterial(thickness=self._thickness, color_mode="vertex"),
            )
            self._iso_temperature_lines.append(iso_temperature_line)
            self.add(iso_temperature_line)

            text = gfx.Text(
                gfx.TextGeometry(
                    f'{as_int_scalar(label)}{"M" if self._mireds else "K"}',
                    font_size=CONSTANTS_COLOUR_STYLE.font.size,
                    screen_space=True,
                    anchor="Bottom-Left",
                ),
                gfx.TextMaterial(color=CONSTANTS_COLOUR_STYLE.colour.light),
            )

            text.local.position = np.array(
                [
                    lines_itl[i][-1, 0],
                    lines_itl[i][-1, 1],
                    0,
                ]
            )
            self._texts.append(text)
            self.add(text)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualPlanckianLocus()
    scene.add(visual_1)

    gfx.show(scene, up=np.array([0, 0, 1]))
