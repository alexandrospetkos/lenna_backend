import time
import json, re
import requests
from requests.auth import HTTPBasicAuth

class Translate:
    def __init__(self):
        self.service = "https://api.eu-de.language-translator.watson.cloud.ibm.com/instances/[IBM INSTANCE]"
        self.authorization = HTTPBasicAuth("apikey", "[IBM API KEY]")

    def translate(self, text, source_language, target_language):
        t1 = time.time()

        self.headers = {
            'Content-Type': 'application/json',
        }

        body = {
          "text": text,
          "source": source_language,
          "target": target_language
        }

        R = requests.post(self.service + "/v3/translate?version=2018-05-01", headers=self.headers, 
            json=body, auth=self.authorization)

        return R.json()["translations"][0]["translation"]





