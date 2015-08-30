.. JSON Transporter documentation master file, created by
   sphinx-quickstart on Sat Aug 29 16:58:16 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst

.. toctree::
   :hidden:
   :maxdepth: 1

   topics/tport
   topics/tools

:doc:`topics/tport`
-------------------------------------

Once installed, ``tport`` takes serialized JSON text files from the command line
and transporter it to a supported tool.

:doc:`topics/tools`
--------------------

If you wish to create your own CLI scripts you can `from transporter import tools`
in your code to leverage the JSON transporter API.


