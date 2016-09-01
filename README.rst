Python SDK for the PullString Web API
=====================================

Overview
--------

This package provides a module to access the PullString Web API.

The PullString Web API lets you add text or audio conversational
capabilities to your apps, based upon content that you write in the
PullString Author environment and publish to the PullString Platform.

Package
-------

The Python SDK is provided as a module called `pullstring` with no
dependencies on modules outside of the standard library. You can run
the following command from this directory to get the package docs.

.. code-block:: python

    >>> import pullstring
    >>> help(pullstring)

Sample Code
-----------

Run `make example` to run a simple text chat client that connects to a
simple Rock, Paper, Scissors chatbot.

Run `make test` to run an automated test of the SDK that talks to the
same Rock, Paper, Scissors chatbot.

Documentation
-------------

The PullString Web API specification can be found at:

   http://docs.pullstring.ai/docs/api

For more information about the PullString Platfrom, refer to:

   http://pullstring.ai/
