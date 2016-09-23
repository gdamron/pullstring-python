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

And here's a simple example of starting a conversation with the
PullString Web API in order to display the initial content under the
default Activity for your Project. Note this code assumes that you
have defined ``MY_API_KEY`` and ``MY_PROJECT_ID``` strings with the
appropriate IDs. You can find these IDs under the settings for your
project under your account on <https://pullstring.ai/>. We've included
the API Key and Project ID for the example **Rock, Paper, Scissors**
chatbot.

.. code-block:: python

    >>> MY_API_KEY="9fd2a189-3d57-4c02-8a55-5f0159bff2cf"
    >>> MY_PROJECT_ID="e50b56df-95b7-4fa1-9061-83a7a9bea372"
    >>> import pullstring
    >>> conv = pullstring.Conversation()
    >>> request = pullstring.Request(api_key=MY_API_KEY)
    >>> response = conv.start(MY_PROJECT_ID, request)
    >>> print [str(x) for x in response.outputs]
    ['RPS Bot: Do you want to play Rock, Paper, Scissors?']

Sample Code
-----------

Run ``make example`` to run a simple text chat client that connects to
a simple **Rock, Paper, Scissors** chatbot, using the above API Key
and Project ID, and lets you hold a converation with the bot.

Run ``make test`` to run an automated test of the SDK that talks to
the same **Rock, Paper, Scissors** chatbot. This shows more examples
of the range of features in the SDK.

Documentation
-------------

The PullString Web API specification can be found at:

   http://docs.pullstring.com/docs/api

For more information about the PullString Platform, refer to:

   http://pullstring.com/
