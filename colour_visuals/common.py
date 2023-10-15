"""
Common Utilities
================

Defines the common utilities objects that don't fall in any specific category.
"""

from __future__ import annotations

import numpy as np

from colour.graph import convert
from colour.hints import ArrayLike, NDArray, Tuple
from colour.models import (
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
    "append_alpha_channel",
]

DEFAULT_FLOAT_DTYPE_WGPU = np.float32
DEFAULT_INT_DTYPE_WGPU = np.uint32


def XYZ_to_colourspace_model(
    XYZ: ArrayLike, illuminant: ArrayLike, model: str, **kwargs
) -> NDArray:
    """
    Converts from *CIE XYZ* tristimulus values to given colourspace model while
    normalising for visual convenience some of the models.
    """

    ijk = convert(
        XYZ,
        "CIE XYZ",
        model,
        illuminant=illuminant,
        verbose={"mode": "Short"},
        **kwargs,
    )

    # TODO: ICtCp?
    if model == "JzAzBz":
        ijk /= XYZ_to_Jzazbz([1, 1, 1])[0]
    elif model == "OSA UCS":
        ijk /= XYZ_to_OSA_UCS([1, 1, 1])[0]

    return ijk


def as_contiguous_array(a, dtype=DEFAULT_FLOAT_DTYPE_WGPU):
    return np.ascontiguousarray(a.astype(dtype))


def conform_primitive_dtype(
    primitive: Tuple[NDArray, NDArray, NDArray]
) -> Tuple[NDArray, NDArray, NDArray]:
    """
    Conform the given primitive to the required dtype.
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


def append_alpha_channel(a: ArrayLike, alpha: float = 1) -> NDArray:
    a = np.copy(a)

    return np.hstack([a, full(list(a.shape[:-1]) + [1], alpha, dtype=a.dtype)])
