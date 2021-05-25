Creating Assets
---------------

Repository Path
~~~~~~~~~~~~~~~

Creating assets requires a repository path to be set. This change lasts during the duration of the current application (or python process), so it is needed only once.

**API:**  ``grill.write.Repository``

.. code-block::  python

    >>> import tempfile
    >>> from pathlib import Path
    >>> from grill import write
    >>> write.Repository.set(Path(tempfile.mkdtemp()))
    <Token var=<ContextVar name='Repository' at 0x00000213A46FF900> at 0x00000213C6A9F0C0>
    >>> write.Repository.get()
    WindowsPath('C:/Users/CHRIST~1/AppData/Local/Temp/tmp767wqaya')

**GUI:** Repository Path

If not set, a dialog to set it will be prompted upon creation request on any relevant widget (e.g. ``Create Assets``, ``Taxonomy Editor``).

To set the repository path at any point, go to ``Grill -> Preferences -> Repository Path``:

.. image:: https://user-images.githubusercontent.com/8294116/114215808-681a2a00-99a9-11eb-85c2-04d45d5a3aef.gif

Defining Taxonomy
~~~~~~~~~~~~~~~~~

For asset organization, ``The Grill`` uses the concept of asset `taxonomy`_. This is a hierarchy for organizing assets into groups (``Taxa``) where members of each individual group (``Taxon``) share characteristics (e.g. ``Characters``, ``Props`` and ``Shots`` are common organizational groups found on ``Film`` and ``Animation`` projects).

**API:**  ``grill.write.define_taxon``

.. code-block::  python

    >>> from grill import write
    >>> character = write.define_taxon(stage, "Character")
    >>> character
    Usd.Prim(</Taxonomy/Character>)
    >>> write.define_taxon(stage, "SecondaryCharacter", references=(character,))
    Usd.Prim(</Taxonomy/SecondaryCharacter>)

**GUI:** Taxonomy Editor

On the upper left, all existing ``taxa`` in the current `stage`_ are listed. On the lower left, a graph with ancestors and successors of selected existing ``taxa`` is displayed. On the right, details for new ``taxa`` to be created. The following are optional:

- ``References`` provides a selection dialog for new ``taxa`` to inherit properties from existing ones. This helps compose and extend asset ``taxonomy``.
- ``ID Fields`` are additional key=value asset field identifiers.

By default, the amount of new ``taxa`` to be created is one, but any number can be created at the same time by changing the ``Amount`` field at the top:

.. image:: https://user-images.githubusercontent.com/8294116/119262723-94b79780-bc1f-11eb-89bb-2eddb63ca2e5.gif

Creating Asset Units
~~~~~~~~~~~~~~~~~~~~

An ``Asset Unit`` is considered to be a meaningful, unique member for each ``taxon``. A ``taxon`` can contain any number of individual ``units``.

In the example below, 240 ``City`` assets are created, copied from a CSV file and pasted directly on the ``Create Assets`` table.

All created asset units are saved to disk on the current repository path.

.. image:: https://user-images.githubusercontent.com/8294116/112751505-263ccb80-901a-11eb-8a64-d46ef43dd087.gif


Modifying Assets
~~~~~~~~~~~~~~~~

Any USD application should be able to modify the grill assets.

In the example below, an asset defined on USDView (on the right) is opened and modified in Maya (on the left). Once Maya changes are saved, USDView can pickup the edits.
In a similar way, asset taxonomy is modified in Maya, then USDView loads the updates.

.. image:: https://user-images.githubusercontent.com/8294116/119356500-d6147980-bce9-11eb-946e-486986071ef8.gif

.. _taxonomy: https://en.wikipedia.org/wiki/Taxonomy
.. _stage: https://graphics.pixar.com/usd/docs/USD-Glossary.html#USDGlossary-Stage
