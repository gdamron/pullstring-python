#!/usr/bin/env python
#
# A command-line debugger for the PullString Web API
#
# Copyright (c) 2016, PullString, Inc.
#
# The following source code is licensed under the MIT license.
# See the LICENSE file, or https://opensource.org/licenses/MIT.
#

import re
import os
import sys
import time
sys.path.insert(0, os.path.abspath('..'))
import pullstring

class Debugger(object):
    """
    A text chat client that provides in-depth debugging information
    about all Web API requests and responses, as well as a suite of
    commands to access the main Web API calls (/help for details).
    """

    def __init__(self, api_key, project_id, build_type=pullstring.BUILD_PRODUCTION):
        self.ps = pullstring.Conversation()
        self.ps.debug_mode = True
        self.build_type = build_type
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
            elif output.type == pullstring.OUTPUT_BEHAVIOR:
                print("Behavior: %s" % output)

        # reset the timestamp of the last output
        self.last_response_time = self.get_current_time()

    def debugger_command(self, user_input):
        if not user_input.startswith("/"):
            return False

        cmd = user_input.lstrip("/").split(" ")
        name = cmd[0].lower()
        args = cmd[1:]

        if name == "event" and args:
            # send an event to the Web API, plus optional parameters
            event_name = args[0]
            params = {}
            for arg in args[1:]:
                key, value = arg.split("=")
                key = key.strip()
                value = value.strip()

                # set the type of the variable implicitly
                if value in ["true", "false"]:
                    params[key] = (value == "true")
                elif any(c.isdigit() for c in value):
                    params[key] = int(value)
                elif any(c.isdigit() or c == "." for c in value):
                    params[key] = float(value)
                else:
                    params[key] = value
                    
            self.ps.send_event(event_name, params)

        elif name == "intent" and args:
            # send a named intent to the Web API
            self.ps.send_intent(" ".join(args))

        elif name == "activity" and args:
            # send a named acitivity to the Web API
            self.ps.send_activity(" ".join(args))

        elif name == "goto" and args:
            # jump to the line with the given GUID
            self.ps.goto(args[0])

        elif name == "get" and args:
            # return the value of the specified entities
            entities = [pullstring.Entity(x, "") for x in args]
            self.ps.get_entities(entities)

        elif name == "set" and len(args) > 2:
            # set the value of a single entity
            entity_type = args[0].lower()
            entity = None
            if entity_type == "label":
                entity = pullstring.Label(args[1], args[2])
            elif entity_type == "counter":
                entity = pullstring.Counter(args[1], float(args[2]))
            elif entity_type == "flag":
                entity = pullstring.Flag(args[1], args[2].lower() in ["true", "yes", "1"])
            elif entity_type == "list":
                entity = pullstring.List(args[1], args[2:])
            else:
                print("Unknown entity type: %s" % entity_type)
            if entity:
                self.ps.set_entities([entity])

        elif name == "help":
            # display the script's usage information
            print("USAGE:")
            print("  /intent <intent-name>")
            print("  /activity <activity-id>")
            print("  /event <name> [<param-name>=<value> ...]")
            print("  /get <entity-name1> [<entity-name2> ...]")
            print("  /set [label|counter|flag|list] <entity-name> <entity-value>")
            print("  /goto <response-id>")
            print("  /help")

        else:
            print("ERROR: Unhandled debugger command")

        return True
        
    def run(self):
        print("Starting conversation... (%s). Type '/help' for options." % self.build_type)

        # start a new conversation
        request = pullstring.Request(api_key=self.api_key)
        request.build_type = self.build_type
        response = self.ps.start(self.project_id, request)

        while True:
            # display any outputs from the last API request
            self.show_outputs(response)

            # let the user enter input to respond to the bot
            user_input = self.get_user_input()
            if user_input:
                # handle debugger commands
                if not self.debugger_command(user_input):
                    # other send the user input to the conversation
                    response = self.ps.send_text(user_input)
            else:
                # if no input text, then check for a timed response
                response = self.ps.check_for_timed_responses()

if __name__ == "__main__":
    # parse the command line arguments
    if len(sys.argv) < 3:
        sys.exit("Usage: webapi_debugger.py <api-key> <project-id> [--staging|--sandbox]")

    api_key = sys.argv[1]
    project_id = sys.argv[2]
    if len(api_key) != 36 or len(project_id) != 36:
        sys.exit("ERROR: keys are 36-character long GUIDs")

    build_type = pullstring.BUILD_PRODUCTION
    if "--staging" in sys.argv:
        build_type = pullstring.BUILD_STAGING
    elif "--sandbox" in sys.argv:
        build_type = pullstring.BUILD_SANDBOX
        
    # enter the main debugger loop
    try:
        Debugger(api_key, project_id, build_type).run()
    except KeyboardInterrupt:
        sys.exit("Aborting...")
