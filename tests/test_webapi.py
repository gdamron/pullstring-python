#!/usr/bin/env python
#
# Automated tests for the PullString Web API
#
# Copyright (c) 2016, PullString, Inc. All rights reserved.
#
# The following source code is licensed under the MIT license.
# See the LICENSE file, or https://opensource.org/licenses/MIT.
#

import os
import sys
import unittest
sys.path.insert(0, os.path.abspath('..'))
import pullstring

# API Key and Project ID for the example PullString Web API content
API_KEY = "9fd2a189-3d57-4c02-8a55-5f0159bff2cf"
PROJECT = "e50b56df-95b7-4fa1-9061-83a7a9bea372"

class TestClass(unittest.TestCase):
    """
    Play through the Rock Paper Scissors example content.
    """

    def does_contain(self, response, text):
        if response is None:
            return False
        all_lines = [x.text.lower() for x in response.outputs if x.type == pullstring.OUTPUT_DIALOG]
        return text.lower() in " ".join(all_lines)

    def assert_contains(self, response, text):
        self.assertNotEqual(response, None)
        all_lines = [x.text.lower() for x in response.outputs if x.type == pullstring.OUTPUT_DIALOG]
        self.assertIn(text.lower(), " ".join(all_lines))

    def test_rock_paper_scissors(self):
        """
        Start the default activity and parse out a name from the user
        """

        # start a new conversation
        conv = pullstring.Conversation()
        response = conv.start(PROJECT, pullstring.Request(api_key=API_KEY))
        self.assert_contains(response, "Do you want to play")
        
        # say that we don't want to play to start with
        response = conv.send_text("no")
        self.assert_contains(response, "was that a yes")

        # now concede and accept to play
        response = conv.send_text("yes")
        self.assert_contains(response, "great!")
        self.assert_contains(response, "rock, paper or scissors?")

        # ask how to play the game to get some information
        response = conv.send_text("how do I play this game?")
        self.assert_contains(response, "a game of chance")

        # query the current value of the Player Score counter (it's 4 at the start)
        response = conv.get_entities([pullstring.Counter("Player Score")])
        self.assertEqual(len(response.entities), 1)
        self.assertEqual(response.entities[0].name, 'Player Score')
        self.assertEqual(response.entities[0].value, 4)

        # let's start playing... keep choosing until we win or lose
        finished = False
        choices = ['paper', 'rock', 'scissors', 'paper']
        for choice in choices:
            response = conv.send_text(choice)
            if self.does_contain(response, "lost") or \
               self.does_contain(response, "won") or \
               self.does_contain(response, "good game"):
                finished = True
                break
        if not finished:
            self.fail("Game did not finish after %d iterations" % len(choices))

        # set the Name label and confirm that we can get back the new value
        conv.set_entities([pullstring.Label("NAME", "Jack")])
        response = conv.get_entities([pullstring.Label("NAME")])
        self.assertEqual(len(response.entities), 1)
        self.assertEqual(response.entities[0].value, "Jack")

        # trigger a custom event to restart the experience
        response = conv.send_event('restart_game')
        self.assert_contains(response, "Do you want to play")

        # start a new conversation but carry over the participant from above
        participant_id = conv.get_participant_id()
        response = conv.start(PROJECT, pullstring.Request(api_key=API_KEY, participant_id=participant_id))
        self.assert_contains(response, "Do you want to play")

        # because we preserved the participant state, the Name should be the same as above
        response = conv.get_entities([pullstring.Label("NAME")])
        self.assertEqual(len(response.entities), 1)
        self.assertEqual(response.entities[0].value, "Jack")

        # say that we're done
        response = conv.send_text("quit")
        self.assert_contains(response, "Bye")


if __name__ == '__main__':
    print("Running test...")
    unittest.main()
