import time

from transformers import AutoTokenizer
from transformers import AutoModelForSeq2SeqLM

class Model:
    def __init__(self, tokenizer_dir=None, model_dir=None):
        t1 = time.time()

        self.tokenizer_dir = tokenizer_dir if tokenizer_dir else "facebook/blenderbot-1B-distill"
        self.model_dir = model_dir if model_dir else "facebook/blenderbot-1B-distill"
  
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_dir)#.to("cuda")

        print("model::initialization finished in", time.time()-t1)

    def generate_simple(self, utterance):
        t1 = time.time()

        inputs = self.tokenizer([utterance], return_tensors='pt')#.to("cuda")
        reply_ids = self.model.generate(**inputs)
        response = self.tokenizer.batch_decode(reply_ids)

        return " ".join(response[0].split("<s>")[1].split("</s>")[0].split()), time.time()-t1
