import time
import numpy as npimport jax


class Model:
    def __init__(self, pretrained):
        from jax.experimental import maps
        import optax, transformers

        from mesh_transformer.checkpoint import read_ckpt
        from mesh_transformer.sampling import nucleaus_sample
        from mesh_transformer.transformer_shard import CausalTransformer

        print("model::installing tpu_driver")

        ###
        # TPU DRIVER / JAX'S BACKEND
        ###

        import os
        import requests 
        from jax.config import config

        colab_tpu_addr = os.environ['COLAB_TPU_ADDR'].split(':')[0]
        url = f'http://{colab_tpu_addr}:8475/requestversion/tpu_driver0.1_dev20210607'
        requests.post(url)

        config.FLAGS.jax_xla_backend = "tpu_driver"
        config.FLAGS.jax_backend_target = "grpc://" + os.environ['COLAB_TPU_ADDR']

        ###
        # END
        ###

        t1 = time.time()
        print("model::initialization started")

        params = {
            "layers": 28,
            "d_model": 4096,
            "n_heads": 16,
            "n_vocab": 50400,
            "norm": "layernorm",
            "pe": "rotary",
            "pe_rotary_dims": 64,

            "seq": 2048,
            "cores_per_replica": 8,
            "per_replica_batch": 1,
        }

        per_replica_batch = params["per_replica_batch"]
        cores_per_replica = params["cores_per_replica"]
        self.seq = params["seq"]

        params["sampler"] = nucleaus_sample
        params["optimizer"] = optax.scale(0)

        mesh_shape = (jax.device_count() // cores_per_replica, cores_per_replica)
        devices = np.array(jax.devices()).reshape(mesh_shape)

        maps.thread_resources.env = maps.ResourceEnv(maps.Mesh(devices, ('dp', 'mp')))
        self.THREAD_RESOURCES_ENV = maps.thread_resources.env 

        self.tokenizer = transformers.GPT2TokenizerFast.from_pretrained('gpt2')
        print("model::tokenizer loaded")

        self.total_batch = per_replica_batch * jax.device_count() // cores_per_replica

        self.network = CausalTransformer(params)
        print("model::network created")
        self.network.state = read_ckpt(self.network.state, pretrained, devices.shape[1])
        del self.network.state["opt_state"]
        print("model::network loaded")
        self.network.state = self.network.move_xmap(self.network.state, np.zeros(cores_per_replica))
        print("model::network finished")

        print("model::initialization finished in", time.time()-t1)

    def set_thread_resources_env(self, thread_resources):
        from jax.experimental import maps
        maps.thread_resources.env = thread_resources

    def inference(self, context, top_p=0.9, temp=1.0, gen_len=512):
        tokens = self.tokenizer.encode(context)

        provided_ctx = len(tokens)
        pad_amount = self.seq - provided_ctx

        padded_tokens = np.pad(tokens, ((pad_amount, 0),)).astype(np.uint32)
        batched_tokens = np.array([padded_tokens] * self.total_batch)
        length = np.ones(self.total_batch, dtype=np.uint32) * len(tokens)

        output = self.network.generate(batched_tokens, length, gen_len,
            {"top_p": np.ones(self.total_batch) * top_p, 
            "temp": np.ones(self.total_batch) * temp}, return_logits=True)
        samples, proba = [], 1.0
        decoded_tokens = output[1][0]
        all_logits = output[1][2]

        for token, logits in zip(decoded_tokens[0], all_logits[0]):
            samples.append(self.tokenizer.decode(token))
            proba *= jax.nn.softmax(logits[0])[token[0]]

        return ''.join(samples), proba

    def generate(self, context, n_samples = 3):
        t1 = time.time()

        #global THREAD_RESOURCES_ENV
        #maps.thread_resources.env = THREAD_RESOURCES_ENV

        shots = [#{'top_p': top_p, 'temp': temp},
        {'top_p': 0.90, 'temp': 0.35},
        {'top_p': 0.90, 'temp': 0.45},
        {'top_p': 0.50, 'temp': 0.65}]

        responses, probas = [], []
        for i, shot in enumerate(shots[:n_samples]):
            response, proba = self.inference(top_p=shot['top_p'], temp=shot['temp'], gen_len=22, context=context)
            #probas.append(float(proba))

            response = response.split('\n')[0]
            responses.append({'TEXT' : response, 'PROBABILITY' : float(proba)})
        ranked_responses = sorted(responses, key = lambda x: 1-x['PROBABILITY'])

        return ranked_responses, time.time()-t1

###############################
## Helper Functions
#####################

kb_headers = [
   {
      "context":"The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. ",
      "paradigms":[
          
      ]
   },
   {
      "context":"The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. ",
      "paradigms":[
         
      ]
   },
   {
      "context":"I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\". ",
      "paradigms":[
         {
            "s1":"What is human life expectancy in the United States?",
            "s2":"Dwight D. Eisenhower was president of the United States in 1955?"
         },
         {
            "s1":"Which party did he belong to?",
            "s2":"He belonged to the Republican Party."
         },
         {
            "s1":"What is the square root of banana?",
            "s2":"Unknown"
         },
         {
            "s1":"How does a telescope work?",
            "s2":"Telescopes use lenses or mirrors to focus light and make objects appear closer."
         },
         {
            "s1":"Where were the 1992 Olympics held?",
            "s2":"The 1992 Olympics were held in Barcelona, Spain."
         },
         {
            "s1":"How many squigs are in a bonk?",
            "s2":"Unknown"
         }
      ]
   }
];
 
def dialog_pair_format(i1, i2, spacing = " "):
    return """\n
Human:""" + spacing + f"""{i1}
Lenna:""" + spacing + f"""{i2}"""

def dialog_pair_list_convert(pairs, k1='s1', k2='s2'):
	return "".join([
		dialog_pair_format(pair[k1], pair[k2]) 
			for pair in pairs])


