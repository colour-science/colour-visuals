# !/usr/bin/env python
"""
Grid Visuals
============

Defines the grid visuals:

-   :class:`colour_visuals.VisualGrid`
"""

from __future__ import annotations

import numpy as np
import pygfx as gfx
from colour.geometry import primitive_grid
from colour.hints import ArrayLike
from colour.plotting import CONSTANTS_COLOUR_STYLE

from colour_visuals.common import (
    DEFAULT_FLOAT_DTYPE_WGPU,
    append_channel,
    as_contiguous_array,
    conform_primitive_dtype,
)
from colour_visuals.visual import MixinPropertySize, Visual, visual_property

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = ["VisualGrid"]


class VisualGrid(MixinPropertySize, Visual):
    """
    Create a 3D grid.

    Parameters
    ----------
    size
        Size of the grid.
    centred
        Whether to create the grid centred at the origin.
    major_grid_colours
        Colour of the major grid lines.
    minor_grid_colours
        Colour of the minor grid lines.
    major_tick_labels
        Whether to draw the major tick labels.
    major_tick_label_colours
        Colour of the major tick labels.
    minor_tick_labels
        Whether to draw the minor tick labels.
    minor_tick_label_colours
        Colour of the minor tick labels.

    Attributes
    ----------
    -   :attr:`~colour_visuals.VisualGrid.size`
    -   :attr:`~colour_visuals.VisualGrid.centred`
    -   :attr:`~colour_visuals.VisualGrid.major_grid_colours`
    -   :attr:`~colour_visuals.VisualGrid.minor_grid_colours`
    -   :attr:`~colour_visuals.VisualGrid.major_tick_labels`
    -   :attr:`~colour_visuals.VisualGrid.major_tick_label_colours`
    -   :attr:`~colour_visuals.VisualGrid.minor_tick_labels`
    -   :attr:`~colour_visuals.VisualGrid.minor_tick_label_colours`

    Methods
    -------
    -   :meth:`~colour_visuals.VisualGrid.__init__`
    -   :meth:`~colour_visuals.VisualGrid.update`

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
    ...     visual = VisualGrid()
    ...     camera = gfx.PerspectiveCamera(50, 16 / 9)
    ...     camera.show_object(visual, up=np.array([0, 0, 1]), scale=1.25)
    ...     scene.add(visual)
    ...     if os.environ.get("CI") is None:
    ...         gfx.show(scene, camera=camera, canvas=canvas)

    .. image:: ../_static/Plotting_VisualGrid.png
        :align: center
        :alt: visual-grid
    """

    def __init__(
        self,
        size: float = 20,
        centred: bool = True,
        major_grid_colours: ArrayLike = np.array([0.5, 0.5, 0.5]),
        minor_grid_colours: ArrayLike = np.array([0.25, 0.25, 0.25]),
        major_tick_labels=True,
        major_tick_label_colours: ArrayLike = np.array([0.75, 0.75, 0.75]),
        minor_tick_labels=True,
        minor_tick_label_colours: ArrayLike = np.array([0.5, 0.5, 0.5]),
    ):
        super().__init__()

        self._centred = True
        self._major_grid_colours = np.array([0.5, 0.5, 0.5])
        self._minor_grid_colours = np.array([0.25, 0.25, 0.25])
        self._major_tick_labels = True
        self._major_tick_label_colours = np.array([0.75, 0.75, 0.75])
        self._minor_tick_labels = True
        self._minor_tick_label_colours = np.array([0.5, 0.5, 0.5])

        self._axes_helper = None
        self._ticks_major_x = None
        self._ticks_major_y = None
        self._ticks_minor_x = None
        self._ticks_minor_y = None

        with self.block_update():
            self.size = size
            self.centred = centred
            self.major_grid_colours = major_grid_colours
            self.minor_grid_colours = minor_grid_colours
            self.major_tick_labels = major_tick_labels
            self.major_tick_label_colours = major_tick_label_colours
            self.minor_tick_labels = minor_tick_labels
            self.minor_tick_label_colours = minor_tick_label_colours

        self.update()

    @visual_property
    def centred(self) -> bool:
        """
        Getter and setter property to create the grid centred at the origin.

        Parameters
        ----------
        value
            Value to create the grid centred at the origin.

        Returns
        -------
        :class:`bool`
             Create the grid centred at the origin.
        """

        return self._centred

    @centred.setter
    def centred(self, value: bool):
        """Setter for the **self.centred** property."""

        self._centred = value

    @visual_property
    def major_grid_colours(self) -> ArrayLike:
        """
        Getter and setter property for the major grid colour.

        Parameters
        ----------
        value
            Value to set the major grid colour with.

        Returns
        -------
        ArrayLike
            Major grid colour.
        """

        return self._major_grid_colours

    @major_grid_colours.setter
    def major_grid_colours(self, value: ArrayLike):
        """Setter for the **self.major_grid_colours** property."""

        self._major_grid_colours = value

    @visual_property
    def minor_grid_colours(self) -> ArrayLike:
        """
        Getter and setter property for the minor grid colour.

        Parameters
        ----------
        value
            Value to set the minor grid colour with.

        Returns
        -------
        ArrayLike
            Major grid colour.
        """

        return self._minor_grid_colours

    @minor_grid_colours.setter
    def minor_grid_colours(self, value: ArrayLike):
        """Setter for the **self.minor_grid_colours** property."""

        self._minor_grid_colours = value

    @visual_property
    def major_tick_labels(self) -> bool:
        """
        Getter and setter property for the major tick labels state.

        Parameters
        ----------
        value
            Value to set major tick labels state with.

        Returns
        -------
        :class:`bool`
            Major tick labels state.
        """

        return self._major_tick_labels

    @major_tick_labels.setter
    def major_tick_labels(self, value: bool):
        """Setter for the **self.major_tick_labels** property."""

        self._major_tick_labels = value

    @visual_property
    def major_tick_label_colours(self) -> ArrayLike:
        """
        Getter and setter property for the major tick label colour.

        Parameters
        ----------
        value
            Value to set the major tick label colour with.

        Returns
        -------
        ArrayLike
            Major tick label colour.
        """

        return self._major_tick_label_colours

    @major_tick_label_colours.setter
    def major_tick_label_colours(self, value: ArrayLike):
        """Setter for the **self.major_tick_label_colours** property."""

        self._major_tick_label_colours = value

    @visual_property
    def minor_tick_labels(self) -> bool:
        """
        Getter and setter property for the minor tick labels state.

        Parameters
        ----------
        value
            Value to set minor tick labels state with.

        Returns
        -------
        :class:`bool`
            Minor tick labels state.
        """

        return self._minor_tick_labels

    @minor_tick_labels.setter
    def minor_tick_labels(self, value: bool):
        """Setter for the **self.minor_tick_labels** property."""

        self._minor_tick_labels = value

    @visual_property
    def minor_tick_label_colours(self) -> ArrayLike:
        """
        Getter and setter property for the minor tick label colour.

        Parameters
        ----------
        value
            Value to set the minor tick label colour with.

        Returns
        -------
        ArrayLike
            Minor tick label colour.
        """

        return self._minor_tick_label_colours

    @minor_tick_label_colours.setter
    def minor_tick_label_colours(self, value: ArrayLike):
        """Setter for the **self.minor_tick_label_colours** property."""

        self._minor_tick_label_colours = value

    def update(self):
        """Update the visual."""

        if self._is_update_blocked:
            return

        self.clear()

        size = int(self._size)

        vertices, faces, outline = conform_primitive_dtype(
            primitive_grid(
                width_segments=size,
                height_segments=size,
            )
        )
        positions = vertices["position"]

        self._grid_major = gfx.Mesh(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                indices=np.reshape(outline[..., 1], (-1, 4)),
                colors=as_contiguous_array(
                    append_channel(
                        np.tile(self._major_grid_colours, (positions.shape[0], 1)),
                        1,
                    )
                ),
            ),
            gfx.MeshBasicMaterial(color_mode="vertex", wireframe=True),
        )
        self._grid_major.local.scale = np.array([size, size, 1])
        if not self._centred:
            self._grid_major.local.position = np.array([size / 2, size / 2, 0])

        self.add(self._grid_major)

        vertices, faces, outline = conform_primitive_dtype(
            primitive_grid(
                width_segments=size * 10,
                height_segments=size * 10,
            )
        )
        positions = vertices["position"]

        self._grid_minor = gfx.Mesh(
            gfx.Geometry(
                positions=as_contiguous_array(positions),
                indices=np.reshape(outline[..., 1], (-1, 4)),
                colors=as_contiguous_array(
                    append_channel(
                        np.tile(self._minor_grid_colours, (positions.shape[0], 1)),
                        1,
                    )
                ),
            ),
            gfx.MeshBasicMaterial(color_mode="vertex", wireframe=True),
        )
        self._grid_minor.local.scale = np.array([size, size, 1])
        self._grid_minor.local.position = np.array([0, 0, -1e-3])
        if not self._centred:
            self._grid_minor.local.position = np.array([size / 2, size / 2, -1e-3])

        self.add(self._grid_minor)

        axes_positions = np.array(
            [
                [0, 0, 0],
                [1, 0, 0],
                [0, 0, 0],
                [0, 1, 0],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )
        axes_positions *= size / 2

        axes_colours = np.array(
            [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
            ],
            dtype=DEFAULT_FLOAT_DTYPE_WGPU,
        )

        self._axes_helper = gfx.Line(
            gfx.Geometry(positions=axes_positions, colors=axes_colours),
            gfx.LineSegmentMaterial(color_mode="vertex", thickness=2),
        )
        self.add(self._axes_helper)

        if self._major_tick_labels:
            self._ticks_major_x, self._ticks_major_y = [], []

            start, end = -size / 2, size / 2 + 1
            if not self._centred:
                start = 0
                end = size + 1

            for i in np.arange(start, end, 1):
                x_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} " if i == 0 else str(i),
                        font_size=CONSTANTS_COLOUR_STYLE.font.size,
                        screen_space=True,
                        anchor="Top-Right" if i == 0 else "Top-Center",
                    ),
                    gfx.TextMaterial(color=self._major_tick_label_colours),
                )
                x_text.local.position = np.array([i, 0, 1e-3])
                self.add(x_text)
                self._ticks_major_x.append(x_text)

                if i == 0:
                    continue

                y_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} ",
                        font_size=CONSTANTS_COLOUR_STYLE.font.size,
                        screen_space=True,
                        anchor="Center-Right",
                    ),
                    gfx.TextMaterial(color=self._major_tick_label_colours),
                )
                y_text.local.position = np.array([0, i, 1e-3])
                self.add(y_text)
                self._ticks_major_y.append(y_text)

        if self._minor_tick_labels:
            self._ticks_minor_x, self._ticks_minor_y = [], []

            start, end = -size / 2, size / 2 + 0.1
            if not self._centred:
                start = 0
                end = size + 0.1

            for i in np.arange(start, end, 0.1):
                if np.around(i, 0) == np.around(i, 1):
                    continue

                i = np.around(i, 1)  # noqa: PLW2901

                x_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} " if i == 0 else str(i),
                        font_size=CONSTANTS_COLOUR_STYLE.font.size
                        * CONSTANTS_COLOUR_STYLE.font.scaling.small,
                        screen_space=True,
                        anchor="Top-Right" if i == 0 else "Top-Center",
                    ),
                    gfx.TextMaterial(color=self._minor_tick_label_colours),
                )
                x_text.local.position = np.array([i, 0, 1e-3])
                self.add(x_text)
                self._ticks_minor_x.append(x_text)

                if i == 0:
                    continue

                y_text = gfx.Text(
                    gfx.TextGeometry(
                        f"{i} ",
                        font_size=CONSTANTS_COLOUR_STYLE.font.size
                        * CONSTANTS_COLOUR_STYLE.font.scaling.small,
                        screen_space=True,
                        anchor="Center-Right",
                    ),
                    gfx.TextMaterial(color=self._minor_tick_label_colours),
                )
                y_text.local.position = np.array([0, i, 1e-3])
                self.add(y_text)
                self._ticks_minor_y.append(y_text)


if __name__ == "__main__":
    scene = gfx.Scene()

    scene.add(
        gfx.Background(None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18])))
    )

    visual_1 = VisualGrid()
    scene.add(visual_1)

    gfx.show(scene, up=np.array([0, 0, 1]))
