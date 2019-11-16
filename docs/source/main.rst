================================
Command-Line Interface
================================

Grade is executable as a module, similarly to `unittest`.

You can control what gets executed, and how it gets reported quite easily:

.. code:: bash

    python -m grade .
    python -m grade ./project/folder/test
    python -m grade . --json
    python -m grade . --markdown

For full details on the command line interface, run `python -m grade -h`
