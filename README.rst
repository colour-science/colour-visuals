Colour - Visuals
================

.. start-badges

|actions| |coveralls| |codacy| |version|

.. |actions| image:: https://img.shields.io/github/actions/workflow/status/colour-science/colour-visuals/.github/workflows/continuous-integration-quality-unit-tests.yml?branch=develop&style=flat-square
    :target: https://github.com/colour-science/colour-visuals/actions
    :alt: Develop Build Status
.. |coveralls| image:: http://img.shields.io/coveralls/colour-science/colour-visuals/develop.svg?style=flat-square
    :target: https://coveralls.io/r/colour-science/colour-visuals
    :alt: Coverage Status
.. |codacy| image:: https://img.shields.io/codacy/grade/2862b4f2217742ae83c972d7e3af44d7/develop.svg?style=flat-square
    :target: https://www.codacy.com/app/colour-science/colour-visuals
    :alt: Code Grade
.. |version| image:: https://img.shields.io/pypi/v/colour-visuals.svg?style=flat-square
    :target: https://pypi.org/project/colour-visuals
    :alt: Package Version

.. end-badges

A `Python <https://www.python.org>`__ package implementing various
`WebGPU-based <https://github.com/gpuweb/gpuweb>`__ visuals on top of
`pygfx <https://github.com/pygfx/pygfx>`__ for colour science applications.

It is open source and freely available under the
`BSD-3-Clause <https://opensource.org/licenses/BSD-3-Clause>`__ terms.

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Visuals_001.png

.. contents:: **Table of Contents**
    :backlinks: none
    :depth: 2

.. sectnum::

Features
--------

Most of the objects are available from the ``colour_visuals`` namespace:

.. code-block:: python

    >>> import colour_visuals

Examples
^^^^^^^^

.. code-block:: python

    >>> import colour_visuals
    >>> import numpy as np
    >>> import pygfx as gfx
    >>> from wgpu.gui.auto import WgpuCanvas, run

    >>> canvas = WgpuCanvas(size=(960, 540))
    >>> renderer = gfx.renderers.WgpuRenderer(canvas)
    >>> camera = gfx.PerspectiveCamera(50, 16 / 9)
    >>> controller = gfx.OrbitController(camera)
    >>> controller.register_events(renderer)

    >>> scene = gfx.Scene()
    >>> scene.add(
    ...     gfx.Background(
    ...         None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...     )
    ... )

    >>> visuals = [
    ...     colour_visuals.VisualGrid(size=2),
    ...     colour_visuals.VisualChromaticityDiagramCIE1931(
    ...         kwargs_visual_chromaticity_diagram={"opacity": 0.25}
    ...     ),
    ...     colour_visuals.VisualRGBColourspace2D("ACEScg"),
    ...     colour_visuals.VisualRGBColourspace2D(
    ...         "Display P3", colours=np.array([0.5, 0.5, 0.5])
    ...     ),
    ...     colour_visuals.VisualRGBColourspace3D(
    ...         "Display P3", opacity=0.5, wireframe=True
    ...     ),
    ...     colour_visuals.VisualRGBScatter3D(
    ...         np.random.random([24, 32, 3]), "ACEScg"
    ...     ),
    ... ]

    >>> group = gfx.Group()
    >>> for visual in visuals:
    ...     group.add(visual)
    ...
    >>> scene.add(group)

    >>> camera.local.position = np.array([-0.25, -0.5, 2])
    >>> camera.show_pos(np.array([1 / 3, 1 / 3, 0.4]))

    >>> canvas.request_draw(lambda: renderer.render(scene, camera))
    >>> run()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Visuals_002.png

.. code-block:: python

    >>> import colour_visuals
    >>> import numpy as np
    >>> import pygfx as gfx
    >>> from wgpu.gui.auto import WgpuCanvas, run

    >>> canvas = WgpuCanvas(size=(960, 540))
    >>> renderer = gfx.renderers.WgpuRenderer(canvas)
    >>> camera = gfx.PerspectiveCamera(50, 16 / 9)
    >>> controller = gfx.OrbitController(camera)
    >>> controller.register_events(renderer)

    >>> scene = gfx.Scene()
    >>> scene.add(
    ...     gfx.Background(
    ...         None, gfx.BackgroundMaterial(np.array([0.18, 0.18, 0.18]))
    ...     )
    ... )

    >>> visuals = [
    ...     VisualGrid(size=4),
    ...     VisualSpectralLocus3D(model="CIE Lab"),
    ...     VisualPointerGamut3D(
    ...         model="CIE Lab", colours=np.array([1, 0.5, 0])
    ...     ),
    ...     VisualRGBColourspace3D(
    ...         "Display P3",
    ...         model="CIE Lab",
    ...         opacity=0.5,
    ...         wireframe=True,
    ...         segments=8,
    ...     ),
    ...     VisualRGBScatter3D(
    ...         np.random.random([24, 32, 3]), "Display P3", model="CIE Lab"
    ...     ),
    ... ]

    >>> group = gfx.Group()
    >>> for visual in visuals:
    ...     group.add(visual)
    ...
    >>> scene.add(group)

    >>> camera.local.position = np.array([1.5, -1.5, 5])
    >>> camera.show_pos(np.array([0, 0, 0.5]))

    >>> canvas.request_draw(lambda: renderer.render(scene, camera))
    >>> run()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Visuals_003.png

Daylight Locus Visuals
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.Plotting_VisualDaylightLocus()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualDaylightLocus.png

Chromaticity Diagram Visuals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.Plotting_VisualSpectralLocus2D()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualSpectralLocus2D.png

.. code-block:: python

    >>> colour_visuals.VisualChromaticityDiagramCIE1931(
    ...     kwargs_visual_chromaticity_diagram={"opacity": 0.25}
    ... )

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualChromaticityDiagramCIE1931.png

Planckian Locus Visuals
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.VisualPlanckianLocus()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualPlanckianLocus.png

Pointer's Gamut Visuals
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.VisualPointerGamut2D()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualPointerGamut2D.png

.. code-block:: python

    >>> colour_visuals.VisualPointerGamut3D()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualPointerGamut3D.png

RGB Colourspace Visuals
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.VisualRGBColourspace2D()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualRGBColourspace2D.png

.. code-block:: python

    >>> colour_visuals.VisualRGBColourspace3D()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualRGBColourspace3D.png

RGB Scatter Visuals
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.VisualRGBScatter3D(np.random.random([24, 32, 3]))

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualRGBScatter3D.png

Rösch-MacAdam Visuals
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> colour_visuals.VisualRoschMacAdam()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_VisualRoschMacAdam.png

Patterns
~~~~~~~~

.. code-block:: python

    >>> colour_visuals.pattern_hue_swatches()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_PatternHueSwatches.png

.. code-block:: python

    >>> colour_visuals.pattern_hue_stripes()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_PatternHueStripes.png

.. code-block:: python

    >>> colour_visuals.pattern_colour_wheel()

..  image:: https://raw.githubusercontent.com/colour-science/colour-visuals/develop/docs/_static/Plotting_PatternColourWheel.png

User Guide
----------

Installation
^^^^^^^^^^^^

Primary Dependencies
~~~~~~~~~~~~~~~~~~~~

- `python >= 3.9, < 4 <https://www.python.org/download/releases>`__
- `colour-science (git) <https://github.com/colour-science/colour.git>`__
- `imageio >= 2, < 3 <https://imageio.github.io>`__
- `networkx >= 2.7, < 3 <https://pypi.org/project/networkx>`__
- `numpy >= 1.22, < 2 <https://pypi.org/project/numpy>`__
- `pygfx <https://pypi.org/project/pygfx>`__
- `pyside >= 6, < 7 <https://pypi.org/project/pygfx>`__
- `scipy >= 1.8, < 2 <https://pypi.org/project/scipy>`__

Pypi
~~~~

**colour-visuals** is not available on Pypi yet.

Contributing
^^^^^^^^^^^^

If you would like to contribute to `Colour - Visuals <https://github.com/colour-science/colour-visuals>`__,
please refer to the following `Contributing <https://www.colour-science.org/contributing>`__
guide for `Colour <https://github.com/colour-science/colour>`__.

API Reference
-------------

The main technical reference for `Colour - Visuals <https://github.com/colour-science/colour-visuals>`__
is the `API Reference <https://colour-visuals.readthedocs.io/en/latest/reference.html>`__.

Code of Conduct
---------------

The *Code of Conduct*, adapted from the `Contributor Covenant 1.4 <https://www.contributor-covenant.org/version/1/4/code-of-conduct.html>`__,
is available on the `Code of Conduct <https://www.colour-science.org/code-of-conduct>`__ page.

Contact & Social
----------------

The *Colour Developers* can be reached via different means:

- `Email <mailto:colour-developers@colour-science.org>`__
- `Facebook <https://www.facebook.com/python.colour.science>`__
- `Github Discussions <https://github.com/colour-science/colour-visuals/discussions>`__
- `Gitter <https://gitter.im/colour-science/colour>`__
- `Twitter <https://twitter.com/colour_science>`__

About
-----

| **Colour - Visuals** by Colour Developers
| Copyright 2023 Colour Developers – `colour-developers@colour-science.org <colour-developers@colour-science.org>`__
| This software is released under terms of BSD-3-Clause: https://opensource.org/licenses/BSD-3-Clause
| `https://github.com/colour-science/colour-visuals <https://github.com/colour-science/colour-visuals>`__
