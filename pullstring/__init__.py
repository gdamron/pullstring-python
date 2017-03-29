# -*- coding: utf-8 -*-
#
# A module to interface with PullString's Web API.
#
# Copyright (c) 2016 PullString, Inc.
#
# The following source code is licensed under the MIT license.
# See the LICENSE file, or https://opensource.org/licenses/MIT.
#

"""
PullString Python SDK

This package provides a module to access the PullString Web API.
For more details, see http://pullstring.com/.
"""

# Define the module metadata
__copyright__            = "Copyright 2016 PullString, Inc."
__version__              = "1.0.1"
__license__              = "MIT"
__contributors__         = []

# Define the set of outputs
OUTPUT_DIALOG            = "dialog"
OUTPUT_BEHAVIOR          = "behavior"

# Define the list of entity types
ENTITY_LABEL             = "label"
ENTITY_COUNTER           = "counter"
ENTITY_FLAG              = "flag"

# Define the audio formats for sending audio to the server
FORMAT_RAW_PCM_16K       = "raw_pcm_16k"
FORMAT_WAV_16K           = "wav_16k"

# The asset build type to request for Web API requests
BUILD_SANDBOX            = "sandbox"
BUILD_STAGING            = "staging"
BUILD_PRODUCTION         = "production"

# The Action to take for a conversation when new content is published
IF_MODIFIED_RESTART      = "restart"
IF_MODIFIED_UPDATE       = "update"
IF_MODIFIED_NOTHING      = "nothing"

# Define the various feature sets that this SDK can support
FEATURE_STREAMING_ASR    = "streaming-asr"


class Phoneme(object):
    """
    Describe a single phoneme for an audio response, e.g., to drive automatic lip sync.
    """
    def __init__(self, name="", secs_since_start=0.0):
        self.name = name
        self.seconds_since_start = secs_since_start

class Entity(object):
    """
    Base class to describe a single entity, such as a label, counter, or flag.
    """
    def __init__(self, name, type):
        self.name = name
        self.type = type
        
class Label(Entity):
    """
    Subclass of Entity to describe a single Label.
    """
    def __init__(self, name="", value=""):
        Entity.__init__(self, name, ENTITY_LABEL)
        self.value = value

class Counter(Entity):
    """
    Subclass of Entity to describe a single Counter.
    """
    def __init__(self, name="", value=0):
        Entity.__init__(self, name, ENTITY_COUNTER)
        self.value = value

class Flag(Entity):
    """
    Subclass of Entity to describe a single Flag.
    """
    def __init__(self, name="", value=False):
        Entity.__init__(self, name, ENTITY_FLAG)
        self.value = value

class Output(object):
    """
    Base class for outputs that are of type dialog or behavior.
    """
    def __init__(self, output_id, type):
        self.id = output_id
        self.type = type

class DialogOutput(Output):
    """
    Subclass of Output that represents a dialog response.
    """
    def __init__(self, output_id=""):
        Output.__init__(self, output_id, OUTPUT_DIALOG)
        self.text = ""
        self.uri = ""
        self.duration = 0.0
        self.phonemes = []
        self.character = ""
        self.user_data = ""

    def __str__(self):
        str = self.text
        if self.character:
            str = self.character + ": " + str
        return str

class BehaviorOutput(Output):
    """
    Subclass of Output that represents a behavior response.
    """
    def __init__(self, output_id=""):
        Output.__init__(self, output_id, OUTPUT_BEHAVIOR)
        self.behavior = ""
        self.parameters = {}

    def __str__(self):
        result = self.behavior
        if self.parameters:
            result += ": " + str(self.parameters)
        return result

class Status(object):
    """
    Describe the status and any errors from a Web API response.
    """
    def __init__(self, code=200, message="success"):
        self.status_code = code
        self.error_message = message

    @property
    def success(self):
        return self.error_message == "success"

class Response(object):
    """
    Describe a single response from the PullString Web API.
    """
    def __init__(self):
        self.outputs = []
        self.entities = []
        self.status = Status()
        self.conversation_endpoint = ""
        self.last_modified = ""
        self.etag = ""
        self.conversation_id = ""
        self.participant_id = ""
        self.timed_response_interval = -1
        self.asr_hypothesis = ""

class Request(object):
    """
    Describe the parameters for a request to the PullString Web API.
    """
    def __init__(self, api_key="", participant_id=""):
        self.api_key = api_key
        self.participant_id = participant_id
        self.build_type = BUILD_PRODUCTION
        self.time_zone_offset = 0
        self.conversation_id = ""
        self.language = ""
        self.locale = ""
        self.if_modified = IF_MODIFIED_NOTHING
        self.restart_if_modified = True

class VersionInfo(object):
    """
    A class to provide version information about this implementation of the PullString SDK.
    """

    # class variable to store the API base URL for all requests
    __API_BASE_URL = "https://conversation.pullstring.ai/v1"

    # class variable to store the API base headers for all requests
    __API_BASE_HEADERS = {}

    @property
    def api_base_url(self):
        return VersionInfo.__API_BASE_URL

    @api_base_url.setter
    def api_base_url(self, new_url):
        VersionInfo.__API_BASE_URL = new_url

    @property
    def api_base_headers(self):
        return VersionInfo.__API_BASE_HEADERS

    @api_base_headers.setter
    def api_base_headers(self, new_headers):
        VersionInfo.__API_BASE_HEADERS = new_headers

    def __get_api_version(self):
        """
        Return the current Web API version number, e.g., "1".
        """
        try:
            import re
            return int(re.sub(r'.*/v([0-9]+).*', r'\1', self.api_base_url))
        except:
            return 0
    api_version = property(__get_api_version)

    def has_feature(self, feature_name):
        """
        Return True if the specified feature is supported by this implementation.
        """
        if feature_name == FEATURE_STREAMING_ASR:
            return False
        return False

class Conversation(object):
    """
    The Conversation object lets you interface with PullString's Web API.

    To initiate a conversation, you call the start() function, providing
    the PullString project ID and a Request() object that must specify
    your API Key. The API Key will be remembered for future requests to
    the same Conversation instance.

    The response from the Web API is returned as a Response() object,
    which can contain zero or more outputs, including lines of dialog
    or behaviors.

    You can send input to the Web API using the various send_XXX()
    functions, e.g., use send_text() to send a text input string
    or send_audio() to send 16-bit LinearPCM audio data.
    """
    
    def __init__(self):
        self.__last_request = None
        self.__last_response = None

    def start(self, project_id, request=None):
        """
        Start a new conversation with the Web API and return the response.

        You must specify the PullString project ID and a Request
        object that specifies your valid API key.
        """
        import json

        # get the project ID into a canonical form
        project_id = project_id.lower().strip()

        # setup the parameters to start a new conversation
        body = {}
        body['project'] = project_id
        if request and request.time_zone_offset >= 0:
            body['time_zone_offset'] = request.time_zone_offset
        if request and request.participant_id:
            body['participant'] = request.participant_id
        if request and request.build_type == BUILD_SANDBOX:
            body['build_type'] = 'sandbox'
        if request and request.build_type == BUILD_STAGING:
            body['build_type'] = 'staging'

        # calling start clears out any previous request/response state
        self.__last_request = None
        self.__last_response = None

        # send the request to the Web API
        endpoint = self.__get_endpoint(add_id=False)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def send_text(self, text, request=None):
        """
        Send user input text to the Web API and return the response.
        """
        import json
        body = { "text" : text }
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def send_activity(self, activity, request=None):
        """
        Send an activity name or ID to the Web API and return the response.
        """
        import json
        body = { "activity" : activity }
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def send_event(self, event, parameters={}, request=None):
        """
        Send a named event to the Web API and return the response.
        """
        import json

        ev = {}
        ev['name'] = event
        ev['parameters'] = parameters
        body = {'event': ev}
        
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def check_for_timed_responses(self, request=None):
        """
        Call the Web API to see if there is a time-based response to process.
        You only need to call this if the previous response returned a value
        for timed_response_interval >= 0. In which case, you should set a timer
        for that number of seconds and then call this function.
        This function will return None if there is no time-based response.
        """
        # nothing to do if no previous response, or it had no time based interval
        if not self.__last_response or self.__last_response.timed_response_interval < 0:
            return None

        # send an empty body to trigger the Web API checking for a timed response
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body="{}", request=request)

    def goto(self, response_id, request=None):
        """
        Jump the conversation directly to the response with the specified GUID.
        """
        import json
        body = { "goto" : response_id }
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def get_entities(self, entities, request=None):
        """
        Request the value of the specified entities from the Web API.
        """
        import json

        names = []
        for entity in entities:
            names.append(entity.name)
        body = { 'get_entities': names }
        
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def set_entities(self, entities, request=None):
        """
        Change the value of the specified entities via the Web API.
        """
        import json

        values = {}
        for entity in entities:
            values[entity.name] = entity.value
        body = { 'set_entities': values }
        
        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=json.dumps(body), request=request)

    def send_audio(self, bytes, format=FORMAT_RAW_PCM_16K, request=None):
        """
        Send an entire audio sample of the user speaking to the Web
        API.  The default format of the audio (FORMAT_RAW_PCM_16K)
        must be mono 16-bit LinearPCM audio data at a sample rate of
        16000 samples per second. Alternatively, you can provide a WAV
        file with mono 16-bit LinearPCM audio at 16000 sample rate.
        """
        # strip the WAV header if given a WAV file
        if format == FORMAT_WAV_16K:
            bytes = self.__get_wav_data(bytes)

        if bytes is None:
            return None

        headers = VersionInfo().api_base_headers
        headers["Content-Type"] = "audio/l16; rate=16000"
        headers["Accept"] = "application/json"
        headers["Transfer-Encoding"] = "chunked"

        endpoint = self.__get_endpoint(add_id=True)
        return self.__send_request(endpoint=endpoint, body=bytes, headers=headers, request=request)

    def start_audio(self, request=None):
        """
        Initiate a progressive (chunked) streaming of audio data.

        Note, chunked streaming is not currently implemented, so this will
        batch up all audio and send it all at once when end_audio() is called.
        """
        self.audio_request = request
        self.audio_bytes = b""

    def add_audio(self, bytes):
        """
        Add a chunk of audio. You must call start_audio() first.  The
        format of the audio must be mono 16-bit LinearPCM audio data
        at a sample rate of 16000 samples per second.
        """
        self.audio_bytes += bytes

    def end_audio(self):
        """
        Signal that all audio has been provided via add_audio() calls.
        This will complete the audio request and return the Web API response.
        """
        return self.send_audio(self.audio_bytes, self.audio_request)

    def get_conversation_id(self):
        """
        Return the current conversation ID for clients to persist across sessions if desired.
        """
        return self.__last_response.conversation_id if self.__last_response else ""

    def get_participant_id(self):
        """
        Return the current participant ID for clients to persist across sessions if desired.
        """
        return self.__last_response.participant_id if self.__last_response else ""

    def __get_endpoint(self, add_id=False):
        """
        Return either the 'conversation' or 'conversation/<UUID>' endpoint name.
        """
        endpoint = 'conversation'
        if add_id and self.__last_response and self.__last_response.conversation_id:
            endpoint += '/' + self.__last_response.conversation_id
        return endpoint

    def __get_wav_data(self, bytes):
        """
        Read a WAV header, check it's valid, and return the data section.
        """
        import struct 

        # check the RIFF header
        if len(bytes) < 36 or bytes[0:4] != b"RIFF":
            return self.__error("Data is not a WAV file")

        # check that we have 16-bit mono at 16000 samples/sec
        channels = struct.unpack('<H', bytes[22:24])[0]
        sample_rate = struct.unpack('<L', bytes[24:28])[0]
        bits_per_sample = struct.unpack('<H', bytes[34:36])[0]
        if bits_per_sample != 16 or sample_rate != 16000 or channels != 1:
            return self.__error("WAV data is not mono 16-bit data at 16000 sample rate")
        
        # find the data chunk in the WAV file by iterating through the
        # subchunks looking for a chunk called 'data' (don't assume 44
        # bytes). First chunk at 12 bytes (4 bytes name, 4 bytes size).
        offset = 12
        chunk_name = bytes[offset:offset+4]
        chunk_size = struct.unpack('<L', bytes[offset+4:offset+8])[0]
        file_size = struct.unpack('<L', bytes[4:8])[0]
        while chunk_name != b'data':
            if offset > file_size:
                return self.__error("Cannot find data segment in WAV data")
            offset += chunk_size + 8
            chunk_name = bytes[offset:offset+4]
            chunk_size = struct.unpack('<L', bytes[offset+4:offset+8])[0]

        data_start = offset + 8
        return bytes[data_start:]

    def __error(self, msg):
        """
        Output an error message.
        """
        import sys
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()
        return None

    def __get_request(self, new_request, old_request):
        """
        Create a request that has all of the set fields from new_request,
        and where not set it uses the value of the field from old_request.
        That is, use the previous request settings but let the client
        override those on a per-request basis.
        """
        # handle no new or old request
        r = Request()
        if old_request is None:
            old_request = Request()
        if new_request is None:
            new_request = old_request

        # prefer the value from the new request, otherwise use the old request value
        for attribute in r.__dict__.keys():
            new_value = getattr(new_request, attribute)
            old_value = getattr(old_request, attribute)
            setattr(r, attribute, new_value if new_value else old_value)

        return r

    def __send_request(self, endpoint, query_params={}, body="", headers=None, request=None):
        """
        Send a request to PullString's Web API and return a Response object.
        """
        import posixpath

        # get all of the request settings for this call
        request = self.__get_request(request, self.__last_request)
        
        # fill in some default values for most requests
        if headers is None:
            headers = VersionInfo().api_base_headers
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"

        headers['Authorization'] = "Bearer " + request.api_key

        # only set restart_if_modified or if_modified if value is not default
        # the legacy behavior of restart_if_modified takes precedence
        if not request.restart_if_modified:
            query_params['restart_if_modified'] = "false"
        elif request.if_modified is not IF_MODIFIED_NOTHING:
            query_params['if_modified'] = request.if_modified

        if request.language:
            query_params['language'] = request.language
        else:
            query_params['language'] = "en-US"

        if request.locale:
            query_params['locale'] = request.locale

        # do the HTTPS POST call with all the query params, header, and body content
        url = posixpath.join(VersionInfo().api_base_url, endpoint)
        data, status = self.__http_helper(url, query_params=query_params, headers=headers, data=body)

        # convert the JSON response body to our Response object
        response = self.__json_to_response(data)
        response.status = status

        # save the last request and response to remember settings
        self.__last_request = request
        self.__last_response = response

        return response

    def __json_to_response(self, data):
        """
        Convert JSON that conforms to PullString's Web API spec into a Response object.
        """
        response = Response()

        # parse the simple top-level fields from the response
        response.conversation_id = data.get('conversation', '')
        response.participant_id = data.get('participant', '')
        response.timed_response_interval = data.get('timed_response_interval', -1)
        response.last_modified = data.get('last_modified', '')
        response.etag = data.get('etag', '')
        response.asr_hypothesis = data.get('asr_hypothesis', '')

        # parse out the outputs array, i.e., dialog or behavior responses
        for output_data in data.get('outputs', []):
            output_type = output_data.get('type', '').lower().strip()
            if output_type == OUTPUT_DIALOG:
                output = DialogOutput()
                output.id = output_data.get('id', '')
                output.text = output_data.get('text', '')
                output.uri = output_data.get('uri', '')
                output.duration = output_data.get('duration', 0)
                output.character = output_data.get('character', '')
                output.user_data = output_data.get('user_data', '')

                for phoneme_data in output_data.get('phonemes', []):
                    phoneme = Phoneme()
                    phoneme.name = phoneme_data.get('name', '')
                    phoneme.seconds_since_start = phoneme_data.get('seconds_since_start', 0)
                    if phoneme.name:
                        output.phonemes.append(phoneme)

            elif output_type == OUTPUT_BEHAVIOR:
                output = BehaviorOutput()
                output.behavior = output_data.get('behavior', '')
                output.parameters = output_data.get('parameters', {})

            else:
                output = None

            if output:
                response.outputs.append(output)

        # handle Python2 vs Python3 string types
        try:
            string_types = [str, unicode]  # Python2
        except Exception as e:
            string_types = [str]           # Python3

        # parse all of the entity information (counters, flags, labels)
        entities = data.get('entities', {})
        for name in entities.keys():
            value = entities[name]

            if type(value) in [int, float]:
                counter = Counter(name, value)
                response.entities.append(counter)

            elif type(value) in [bool]:
                flag = Flag(name, value)
                response.entities.append(flag)

            elif type(value) in string_types:
                label = Label(name, value)
                response.entities.append(label)

        return response
            
    def __http_helper(self, url, query_params, headers, data):
        """
        Performs an HTTPS request and returns a tuple of (json_dict, status).
        """
        import sys
        if sys.version_info >= (3, 0):
            # python3 imports
            import http.client as httplib
            import urllib.parse as urlparse
            import urllib.parse as urllib

        else:
            # python2 imports
            import httplib
            import urlparse
            import urllib

        # parse out the URL components
        purl = urlparse.urlparse(url)
        path = purl.path
        if query_params:
            path += "?" + urllib.urlencode(query_params)

        # open a POST connection to the HTTPS server
        conn = httplib.HTTPSConnection(purl.netloc)
        
        if isinstance(data, type(u"")):
            data = data.encode('utf-8')

        # are we doing chunked encoding of audio data, or just regular POST?
        chunked = (headers.get("Transfer-Encoding", "") == "chunked")
        if chunked:
            # send the data in a chunked encoded format
            conn.putrequest('POST', path)
            for key in headers.keys():
                conn.putheader(key, headers[key])
            conn.endheaders()

            conn.send(b"%x\r\n" % len(data))
            conn.send(b"%s\r\n" % data)
            conn.send(b"0\r\n\r\n")

        else:
            # open a standard POST connection to the server
            conn = httplib.HTTPSConnection(purl.netloc)
            conn.request("POST", path, data, headers)

        # get the response code and content
        http_response = conn.getresponse()
        content = http_response.read()

        # create a Status() object to describe the HTTP success/error
        status = Status(http_response.status)
        if status.status_code >= 300:
            status.error_message = http_response.reason

        conn.close()

        # try to parse the server result as a JSON response
        try:
            import json
            content = json.loads(content.decode("utf-8"))

            # parse out errors reported back in the JSON
            error = content.get('error')
            if error:
                status.error_message = error.get('message', status.error_message)
                status.status_code = error.get('status', status.status_code)
                content = {}

            return content, status
        except Exception as e:
            self.__error("Failed to parse JSON response: %s" % content)
            status.error_message = content.strip()
            return {}, status
