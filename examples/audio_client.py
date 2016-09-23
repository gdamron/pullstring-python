#!/usr/bin/env python
#
# An audio chat example that uses the PullString Web API.
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

class AudioClient(object):
    """
    A simple audio chat client that uses the PullString Web API.
    For any given project, you can only answer yes or no to each
    input by sending the audio data from the yes.wav or no.wav
    audio files to the Web API to perform speech recognition.
    """

    def __init__(self, api_key, project_id):
        self.ps = pullstring.Conversation()
        self.api_key = api_key
        self.project_id = project_id

    def get_audio_file(self):
        # force the user to answer yes or no and return a WAV
        # filename with audio of a person speaking that word
        while True:
            prompt = "[y/n]> "
            if sys.version_info >= (3, 0):
                user_input = input(prompt).strip().lower()
            else:
                user_input = raw_input(prompt).strip().lower()
            if user_input in ["y", "yes"]:
                return "yes.wav"
            if user_input in ["n", "no"]:
                return "no.wav"
            print("You must answer either 'y' or 'n'.")

    def read_file(self, filename):
        # return the binary contents of a file
        with open(filename, "rb") as f:
            return f.read()

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

    def run(self):
        # start a new conversation
        response = self.ps.start(self.project_id, pullstring.Request(api_key=self.api_key))

        while True:
            # display any outputs from the last API request
            self.show_outputs(response)

            # get the name of a 16-bit 16k WAV file to send
            audio_file = self.get_audio_file()

            # send the WAV audio data to the Web API
            print("Sending %s..." % audio_file)
            response = self.ps.send_audio(self.read_file(audio_file))

if __name__ == "__main__":
    # parse the command line arguments
    if len(sys.argv) != 3:
        sys.exit("Usage: chatclient.py <api-key> <project-id>")

    api_key = sys.argv[1]
    project_id = sys.argv[2]
    if len(api_key) != 36 or len(project_id) != 36:
        sys.exit("ERROR: keys are 36-character long GUIDs")

    # enter the main chat client loop
    try:
        AudioClient(api_key, project_id).run()
    except KeyboardInterrupt:
        sys.exit("Aborting...")
