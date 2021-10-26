import time
import json, re
import requests

class Model:
    def __init__(self):
        self.service = "https://api.nlpcloud.io/v1/gpu/gpt-j/generation"
        self.authorization = { "Authorization" : "Token fb1c3e8990338de9811440e2c45def6c88add5c0" }

    def generate(self, text, 
        max_length=32, 
        top_k=6, 
        top_p=0.9, 
        temperature=0.45, 
        repetition_penalty=1.10, 
        length_penalty=0.96):

        t1 = time.time()

        text = re.sub(r'(?:\s([.,?!])|\s([\'])\s?)', r'\1\2', text)

        print(text, end =" ")

        post = {
            "text" : text,
            "max_length" : max_length,
            "length_no_input" : True,
            "remove_input" : True,
            #"top_k" : top_k,
            "top_p" : top_p,
            "temperature" :temperature,
            "repetition_penalty" : repetition_penalty,
            "length_penalty" : length_penalty
        }

        R = requests.post(self.service, headers=self.authorization, data=json.dumps(post))

        response = R.json()["generated_text"][1:]

        #raise ValueError('engines::lenna_gate Error, Input format is incompatible.')

        response = list(filter(None, response.split('\n')))

        return response, time.time()-t1





