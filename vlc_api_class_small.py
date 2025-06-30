import time
import requests
import urllib3
import hashlib
import subprocess
import json

"""
STATUS: this code works.

A small, pared-down version of the VLCRemoteAccessAPI class for small-script usage. 
Using this class requires you to know the API endpoints and parameter formats.
You can delete the staticmethods if you want.
Note: at defaults, this code requires the Termux:API 'termux-notification-list' command to be available and permissioned, unless you call myclass.authenticate() with manual=True. 
If you don't plan on using 'termux-nofitication-list', you can delete get_code_from_android_notifs() and modify authenticate() to only do a manual input.
"""

class VLCRemoteAccessAPI:
    url = "https://localhost:8443"
    session = None

    def __init__(self, url=None):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if url: self.url = url
        self.session = requests.Session()

    def endpoint(self, endpoint):
        return f"{self.url}{endpoint}"

    def build_param_str(self, obj):
        form_params = "?"
        for key in obj: form_params += f"{key}={obj[key]}&"
        return form_params[:-1]  #pop off the last ampersand char.

    def authenticate(self, manual=False):
        data = {"challenge": ""}
        response = requests.post(self.endpoint("/code"), data=data, verify=False)
        if response.status_code != 200:
            raise Exception("Request to generate the code failed. Ensure the RemoteAccess server is running.")
        challenge = response.text
        if manual:
            code = input("Enter code: ")
        else:
            code = self.get_code_from_android_notifs()
        code_out = self.sha256(code + challenge)
        data = {"code": code_out}
        response = self.session.post(self.endpoint("/verify-code"), data=data, verify=False)
        if response.status_code != 200:
            raise Exception("Failed to verify code (authenticate).")
        print(f"Authenticated session with VLC Remote Access. Code: {code}")

    def api_call(self, getpost="get", endpoint="/video-list", **param_obj):
        if endpoint[0] != "/": endpoint = "/" + endpoint
        url = self.endpoint(endpoint)
        if param_obj:
            url += self.build_param_str(param_obj)
        print(f"VLC API to: {url}")
        if getpost == "get":
            response = self.session.get(url=url, verify=False)
        else:
            response = self.session.post(url=url, verify=False)
        return response

    def get(self, endpoint="/video-list", **param_obj):
        return self.api_call("get", endpoint, **param_obj)

    def post(self, endpoint, **param_obj):
        return self.api_call("post", endpoint, **param_obj)

    def sha256(self, data_string):
        # data should be a string, convert to bytes and hash it.
        data = data_string.encode()
        return hashlib.sha256(data).hexdigest()

    def get_code_from_android_notifs(self, waittime=0.5):
        """ Returns the OTP code as a 4 character string. """
        time.sleep(waittime)
        result = subprocess.run(['termux-notification-list'],capture_output=True,text=True)
        notifications = json.loads(result.stdout)  #a list of dicts (array of objects).
        for x in notifications:
            try:
                return x["content"].split("this code: ")[1]
            except: pass

    @staticmethod
    def print_response(self, response):
        print("===============")
        try:
            print(response.status_code)
            print('text: ',response.text)
            print(response.url)
            print(str(response.headers))
            print(response.history)
        except: pass
        print("===============")
