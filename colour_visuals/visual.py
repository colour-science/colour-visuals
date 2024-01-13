"""
Visual Utilities
================

Defines the visual utilities.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

import pygfx as gfx
from colour.colorimetry import (
    MSDS_CMFS,
    SDS_ILLUMINANTS,
    MultiSpectralDistributions,
    SpectralDistribution,
)
from colour.hints import (
    ArrayLike,
    Generator,
    Literal,
    LiteralColourspaceModel,
    LiteralRGBColourspace,
    Sequence,
    Type,
    cast,
)
from colour.models import (
    COLOURSPACE_MODELS,
    RGB_Colourspace,
    RGB_COLOURSPACE_sRGB,
)
from colour.plotting import (
    METHODS_CHROMATICITY_DIAGRAM,
    filter_cmfs,
    filter_illuminants,
    filter_RGB_colourspaces,
)
from colour.utilities import first_item, validate_method

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "visual_property",
    "Visual",
    "MixinPropertyCMFS",
    "MixinPropertyColour",
    "MixinPropertyColourspace",
    "MixinPropertyIlluminant",
    "MixinPropertyKwargs",
    "MixinPropertyTypeMaterial",
    "MixinPropertyMethod",
    "MixinPropertyModel",
    "MixinPropertyOpacity",
    "MixinPropertySamples",
    "MixinPropertySegments",
    "MixinPropertySize",
    "MixinPropertyThickness",
    "MixinPropertyWireframe",
]


class visual_property(property):
    """
    Define a :class:`property` sub-class calling the
    :class:`colour_visuals.Visual.update` method.
    """

    def __set__(self, obj, value):
        """Reimplement the :class:`property.__set__` method."""
        super().__set__(obj, value)

        obj.update()


class Visual(gfx.Group, metaclass=ABCMeta):
    """Define the base class for the visuals."""

    def __init__(self):
        self._is_update_blocked = False

        super().__init__()

    @contextmanager
    def block_update(self) -> Generator:
        """Define a context manager that blocks the visual updates."""
        self._is_update_blocked = True

        yield

        self._is_update_blocked = False

    @abstractmethod
    def update(self):
        """
        Update the visual.

        Notes
        -----
        -   Must be reimplemented by sub-classes.
        """


class MixinPropertyCMFS:
    """
    Define a mixin for a standard observer colour matching functions,
    default to the *CIE 1931 2 Degree Standard Observer*.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyCMFS.cmfs`
    """

    def __init__(self):
        self._cmfs = MSDS_CMFS["CIE 1931 2 Degree Standard Observer"]

        super().__init__()

    @visual_property
    def cmfs(
        self,
    ) -> (
        MultiSpectralDistributions
        | str
        | Sequence[MultiSpectralDistributions | str]
    ):
        """
        Getter and setter property for the standard observer colour matching
        functions.

        Parameters
        ----------
        value
            Value to set the standard observer colour matching functions with.

        Returns
        -------
        :class:`colour.MultiSpectralDistributions` or :class:`str` or \
:class:`Sequence`
            Standard observer colour matching functions.
        """

        return self._cmfs

    @cmfs.setter
    def cmfs(
        self,
        value: MultiSpectralDistributions
        | str
        | Sequence[MultiSpectralDistributions | str],
    ):
        """Setter for the **self.cmfs** property."""

        self._cmfs = cast(
            MultiSpectralDistributions,
            first_item(filter_cmfs(value).values()),
        )


class MixinPropertyColour:
    """
    Define a mixin for a colour.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyColour.colour`
    """

    def __init__(self):
        self._colour = None

        super().__init__()

    @visual_property
    def colour(self) -> ArrayLike | None:
        """
        Getter and setter property for the colour.

        Parameters
        ----------
        value
            Value to set the colour with.

        Returns
        -------
        ArrayLike or None
            Visual colour.
        """

        return self._colour

    @colour.setter
    def colour(self, value: ArrayLike | None):
        """Setter for the **self.colour** property."""

        self._colour = value


class MixinPropertyColourspace:
    """
    Define a mixin for a *RGB* colourspace.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyColour.colour`
    """

    def __init__(self):
        self._colourspace = RGB_COLOURSPACE_sRGB

        super().__init__()

    @visual_property
    def colourspace(
        self,
    ) -> (
        RGB_Colourspace
        | LiteralRGBColourspace
        | str
        | Sequence[RGB_Colourspace | LiteralRGBColourspace | str]
    ):
        """
        Getter and setter property for the *RGB* colourspace.

        Parameters
        ----------
        value
            Value to set the *RGB* colourspace with.

        Returns
        -------
        :class:`colour.RGB_Colourspace` or :class:`str` or :class:`Sequence`
            Colourspace.
        """

        return self._colourspace

    @colourspace.setter
    def colourspace(
        self,
        value: (
            RGB_Colourspace
            | LiteralRGBColourspace
            | str
            | Sequence[RGB_Colourspace | LiteralRGBColourspace | str]
        ),
    ):
        """Setter for the **self.colourspace** property."""

        self._colourspace = cast(
            RGB_Colourspace,
            first_item(filter_RGB_colourspaces(value).values()),
        )


class MixinPropertyIlluminant:
    """
    Define a mixin for an illuminant spectral distribution.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyIlluminant.illuminant`
    """

    def __init__(self):
        self._illuminant = SDS_ILLUMINANTS["E"]

        super().__init__()

    @visual_property
    def illuminant(
        self,
    ) -> SpectralDistribution | str | Sequence[SpectralDistribution | str]:
        """
        Getter and setter property for the illuminant spectral distribution.

        Parameters
        ----------
        value
            Value to set the illuminant spectral distribution with.

        Returns
        -------
        :class:`colour.SpectralDistribution` or :class:`str` or \
:class:`Sequence`
            Illuminant spectral distribution.
        """

        return self._illuminant

    @illuminant.setter
    def illuminant(
        self,
        value: (
            SpectralDistribution | str | Sequence[SpectralDistribution | str]
        ) = "E",
    ):
        """Setter for the **self.illuminant** property."""

        self._illuminant = cast(
            SpectralDistribution,
            first_item(filter_illuminants(value).values()),
        )


class MixinPropertyKwargs:
    """
    Define a mixin for keyword arguments.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyKwargs.kwargs`
    """

    def __init__(self):
        self._kwargs = {}

        super().__init__()

    @visual_property
    def kwargs(self) -> dict:
        """
        Getter and setter property for the keyword arguments.

        Parameters
        ----------
        value
            Value to set keyword arguments with.

        Returns
        -------
        :class:`dict`
            Keyword arguments.
        """

        return self._kwargs

    @kwargs.setter
    def kwargs(self, value: dict):
        """Setter for the **self.kwargs** property."""

        self._kwargs = value


class MixinPropertyTypeMaterial:
    """
    Define a mixin for a material type.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyTypeMaterial.type_material`
    """

    def __init__(self):
        self._type_material = gfx.MeshBasicMaterial

        super().__init__()

    @visual_property
    def type_material(
        self,
    ) -> Type[gfx.MeshAbstractMaterial]:
        """
        Getter and setter property for the material type.

        Parameters
        ----------
        value
            Value to set the material type with.

        Returns
        -------
        :class:`gfx.MeshAbstractMaterial`
            Material type.
        """

        return self._type_material

    @type_material.setter
    def type_material(self, value: Type[gfx.MeshAbstractMaterial]):
        """Setter for the **self.material** property."""

        self._type_material = value


class MixinPropertyMethod:
    """
    Define a mixin for a *Chromaticity Diagram* method.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyMethod.method`
    """

    def __init__(self):
        self._method = "CIE 1931"

        super().__init__()

    @visual_property
    def method(
        self,
    ) -> Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"] | str:
        """
        Getter and setter property for the *Chromaticity Diagram* method.

        Parameters
        ----------
        value
            Value to set the *Chromaticity Diagram* method with.

        Returns
        -------
        :class:`str`
            *Chromaticity Diagram* method.
        """

        return self._method

    @method.setter
    def method(
        self, value: Literal["CIE 1931", "CIE 1960 UCS", "CIE 1976 UCS"] | str
    ):
        """Setter for the **self.method** property."""

        self._method = validate_method(
            value, tuple(METHODS_CHROMATICITY_DIAGRAM)
        )


class MixinPropertyModel:
    """
    Define a mixin for a colourspace model.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyModel.model`
    """

    def __init__(self):
        self._model = "CIE xyY"

        super().__init__()

    @visual_property
    def model(self) -> LiteralColourspaceModel | str:
        """
        Getter and setter property for the colourspace model.

        Parameters
        ----------
        value
            Value to set the colourspace model with.

        Returns
        -------
        :class:`str`
            Colourspace model.
        """

        return self._model

    @model.setter
    def model(self, value: LiteralColourspaceModel | str):
        """Setter for the **self.model** property."""

        self._model = validate_method(value, tuple(COLOURSPACE_MODELS))


class MixinPropertyOpacity:
    """
    Define a mixin for an opacity value.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyOpacity.opacity`
    """

    def __init__(self):
        self._opacity = 1

        super().__init__()

    @visual_property
    def opacity(self) -> float:
        """
        Getter and setter property for the opacity value.

        Parameters
        ----------
        value
            Value to set the opacity value with.

        Returns
        -------
        :class:`float`
            Visual opacity.
        """

        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        """Setter for the **self.opacity** property."""

        self._opacity = value


class MixinPropertySamples:
    """
    Define a mixin for a sample count.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertySamples.samples`
    """

    def __init__(self):
        self._samples = 1

        super().__init__()

    @visual_property
    def samples(self) -> int:
        """
        Getter and setter property for the sample count.

        Parameters
        ----------
        value
            Value to set sample count with.

        Returns
        -------
        :class:`int`
            Sample count.
        """

        return self._samples

    @samples.setter
    def samples(self, value: int):
        """Setter for the **self.samples** property."""

        self._samples = value


class MixinPropertySegments:
    """
    Define a mixin for a segment count.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertySegments.segments`
    """

    def __init__(self):
        self._segments = 16

        super().__init__()

    @visual_property
    def segments(self) -> int:
        """
        Getter and setter property for the segment count.

        Parameters
        ----------
        value
            Value to set segment count with.

        Returns
        -------
        :class:`int`
            Sample count.
        """

        return self._segments

    @segments.setter
    def segments(self, value: int):
        """Setter for the **self.segments** property."""

        self._segments = value


class MixinPropertySize:
    """
    Define a mixin for a size value.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertySize.size`
    """

    def __init__(self):
        self._size = 1

        super().__init__()

    @visual_property
    def size(self) -> float:
        """
        Getter and setter property for the size value.

        Parameters
        ----------
        value
            Value to set size value with.

        Returns
        -------
        :class:`int`
            Size value.
        """

        return self._size

    @size.setter
    def size(self, value: float):
        """Setter for the **self.size** property."""

        self._size = value


class MixinPropertyThickness:
    """
    Define a mixin for a thickness value.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyThickness.thickness`
    """

    def __init__(self):
        self._thickness = 1

        super().__init__()

    @visual_property
    def thickness(self) -> float:
        """
        Getter and setter property for the thickness value.

        Parameters
        ----------
        value
            Value to set the thickness value with.

        Returns
        -------
        :class:`float`
            Thickness value.
        """

        return self._thickness

    @thickness.setter
    def thickness(self, value: float):
        """Setter for the **self.thickness** property."""

        self._thickness = value


class MixinPropertyWireframe:
    """
    Define a mixin for a wireframe state.

    Attributes
    ----------
    -   :attr:`~colour_visuals.visual.MixinPropertyWireframe.wireframe`
    """

    def __init__(self):
        self._wireframe = False

        super().__init__()

    @visual_property
    def wireframe(self) -> bool:
        """
        Getter and setter property for the wireframe state.

        Parameters
        ----------
        value
            Value to set wireframe state with.

        Returns
        -------
        :class:`bool`
            Wireframe state.
        """

        return self._wireframe

    @wireframe.setter
    def wireframe(self, value: bool):
        """Setter for the **self.wireframe** property."""

        self._wireframe = value
