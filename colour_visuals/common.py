"""
Common Utilities
================

Defines the common utilities objects that don't fall in any specific category.
"""

from __future__ import annotations

import numpy as np
from colour.graph import convert
from colour.hints import (
    ArrayLike,
    DType,
    LiteralColourspaceModel,
    NDArray,
    Tuple,
    Type,
)
from colour.models import (
    XYZ_to_ICtCp,
    XYZ_to_Jzazbz,
    XYZ_to_OSA_UCS,
)
from colour.utilities import full

__author__ = "Colour Developers"
__copyright__ = "Copyright 2023 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "DEFAULT_FLOAT_DTYPE_WGPU",
    "DEFAULT_INT_DTYPE_WGPU",
    "XYZ_to_colourspace_model",
    "as_contiguous_array",
    "conform_primitive_dtype",
    "append_channel",
]

DEFAULT_FLOAT_DTYPE_WGPU = np.float32
"""Default int number dtype."""

DEFAULT_INT_DTYPE_WGPU = np.uint32
"""Default floating point number dtype."""


def XYZ_to_colourspace_model(
    XYZ: ArrayLike,
    illuminant: ArrayLike,
    model: LiteralColourspaceModel | str = "CIE xyY",
    **kwargs,
) -> NDArray:
    """
    Convert from *CIE XYZ* tristimulus values to given colourspace model while
    normalising some of the absolute models.

    Parameters
    ----------
    XYZ
        *CIE XYZ* tristimulus values to convert to  given colourspace model.
    illuminant
        Reference *illuminant* *CIE xy* chromaticity coordinates or *CIE xyY*
        colourspace array.
    model
        Colourspace model, see :attr:`colour.COLOURSPACE_MODELS` attribute for
        the list of supported colourspace models.
    """

    ijk = convert(
        XYZ,
        "CIE XYZ",
        model,
        illuminant=illuminant,
        verbose={"mode": "Short"},
        **kwargs,
    )

    if model == "ICtCp":
        ijk /= XYZ_to_ICtCp([1, 1, 1])[0]
    elif model == "JzAzBz":
        ijk /= XYZ_to_Jzazbz([1, 1, 1])[0]
    elif model == "OSA UCS":
        ijk /= XYZ_to_OSA_UCS([1, 1, 1])[0]

    return ijk


def as_contiguous_array(
    a: NDArray, dtype: Type[DType] = DEFAULT_FLOAT_DTYPE_WGPU
) -> NDArray:
    """
    Convert given array to a contiguous array (ndim >= 1) in memory (C order).

    Parameters
    ----------
    a
        Variable :math:`a` to convert.
    dtype
        :class:`numpy.dtype` to use for conversion, default to the
        :class:`numpy.dtype` defined by the
        :attr:`colour.constant.DEFAULT_FLOAT_DTYPE_WGPU` attribute.

    Returns
    -------
    :class:`numpy.ndarray`
        Converted variable :math:`a`.
    """

    return np.ascontiguousarray(a.astype(dtype))


def conform_primitive_dtype(
    primitive: Tuple[NDArray, NDArray, NDArray]
) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Conform the given primitive to the required *WebGPU* dtype.

    Parameters
    ----------
    primitive
        Primitive to conform the dtype of.

    Returns
    -------
    :class:`numpy.ndarray`
        Conformed primitive.
    """

    vertices, faces, outline = primitive

    return (
        vertices.astype(
            [
                ("position", DEFAULT_FLOAT_DTYPE_WGPU, (3,)),
                ("uv", DEFAULT_FLOAT_DTYPE_WGPU, (2,)),
                ("normal", DEFAULT_FLOAT_DTYPE_WGPU, (3,)),
                ("colour", DEFAULT_FLOAT_DTYPE_WGPU, (4,)),
            ]
        ),
        faces.astype(DEFAULT_INT_DTYPE_WGPU),
        outline.astype(DEFAULT_INT_DTYPE_WGPU),
    )


def append_channel(a: ArrayLike, value: float = 1) -> NDArray:
    """
    Append a channel to given variable :math:`a`.

    Parameters
    ----------
    a
        Variable :math:`a` to append a channel to.
    value
        Channel value.

    Returns
    -------
    :class:`numpy.ndarray`
        Variable :math:`a` with appended channel.
    """

    a = np.copy(a)

    return np.hstack(  # pyright: ignore
        [
            a,
            full(
                (*list(a.shape[:-1]), 1),
                value,
                dtype=a.dtype,  # pyright: ignore
            ),
        ]
    )
