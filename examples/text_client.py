#!/usr/bin/env python
#
# A simple text chat client that uses the PullString Web API.
#
# Copyright (c) 2016, PullString, Inc.
#
# The following source code is licensed under the MIT license.
# See the LICENSE file, or https://opensource.org/licenses/MIT.
#

import os
import sys
import time
sys.path.insert(0, os.path.abspath('..'))
import pullstring

class TextClient(object):
    """
    A simple text chat client that uses the PullString Web API.
    You must provide the API Key and Project ID of the content
    that you want to chat with.
    """

    def __init__(self, api_key, project_id):
        self.ps = pullstring.Conversation()
        self.api_key = api_key
        self.project_id = project_id
        self.last_response_time = self.get_current_time()

    def get_current_time(self):
        # return the current time in (floating point) seconds
        return time.time()

    def get_user_input(self):
        # wait for the user to enter some text at the terminal
        if sys.version_info >= (3, 0):
            return input("> ").strip()
        else:
            return raw_input("> ").strip()

    def show_outputs(self, response):
        # nothing to do if there's no response object
        if response is None:
            return

        # check for any Web API errors and display them
        if not response.status.success:
            print("ERROR: %s" % response.status.error_message)

        # display all dialog text outputs from the response
        for output in response.outputs:
            if output.type == pullstring.OUTPUT_DIALOG:
                print(output)

        # reset the timestamp of the last output
        self.last_response_time = self.get_current_time()

    def run(self):
        # start a new conversation
        response = self.ps.start(self.project_id, pullstring.Request(api_key=self.api_key))

        while True:
            # display any outputs from the last API request
            self.show_outputs(response)

            # let the user enter input to respond to the bot
            user_input = self.get_user_input()
            if user_input:
                # send the user input
                response = self.ps.send_text(user_input)
            else:
                # if no input text, then check for a timed response
                response = self.ps.check_for_timed_responses()

if __name__ == "__main__":
    # parse the command line arguments
    if len(sys.argv) != 3:
        sys.exit("Usage: text_client.py <api-key> <project-id>")

    api_key = sys.argv[1]
    project_id = sys.argv[2]
    if len(api_key) != 36 or len(project_id) != 36:
        sys.exit("ERROR: keys are 36-character long GUIDs")

    # enter the main chat client loop
    try:
        TextClient(api_key, project_id).run()
    except KeyboardInterrupt:
        sys.exit("Aborting...")
