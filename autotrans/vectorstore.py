import signal
import pickle
import openai
import time
import tiktoken
from tqdm import tqdm
import numpy as np


enc = tiktoken.get_encoding("cl100k_base")


def embed_texts(texts, sleep_after_sucess=1):
    EMBED_MAX_SIZE = 8150  # actual limit is 8191
    if isinstance(texts, str):
        texts = [texts]
    for i, text in enumerate(texts):
        text = text.replace("\n", " ")
        tokens = enc.encode(text)
        if len(tokens) > EMBED_MAX_SIZE:
            text = enc.decode(tokens[:EMBED_MAX_SIZE])
        texts[i] = text

    while True:
        try:
            res = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
            time.sleep(sleep_after_sucess)
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        break

    return res


def embed(text, sleep_after_sucess=0):
    # short hand for single text
    r = embed_texts(text, sleep_after_sucess=sleep_after_sucess)["data"][0]["embedding"]


def safe_write(obj, name):
    to_exit = False

    def change_state(signum, frame):
        nonlocal to_exit
        to_exit = True

    signal.signal(signal.SIGINT, change_state)
    pickle.dump(obj, open(name, "wb"))
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if to_exit:
        raise KeyboardInterrupt


class VectorStore:
    def __init__(self, name, create_if_not_exist=True):
        self.name = name
        try:
            self.cache = pickle.load(open(self.name, "rb"))
        except FileNotFoundError as e:
            if create_if_not_exist:
                self.cache = {}
            else:
                raise

    def get_or_make(self, body, payload, cache=None):
        if cache is None:
            cache = self.cache
        if body not in cache:
            print("not in cache")
            print(payload["title"], body[:20])
            self.cache[body] = (embed(body), payload)
        elif body not in self.cache:
            # print("in cache")
            self.cache[body] = (cache[body][0], payload)
        else:
            print("already have")

        return self.cache[body]

    def get_sorted(self, query):
        q = np.array(embed(query, sleep_after_sucess=0))
        buf = []
        for body, (v, title) in tqdm(self.cache.items()):
            buf.append((q.dot(v), body, title))
        buf.sort(reverse=True)
        return buf

    def batch(self, api_tasks, cache=None):
        if cache is None:
            cache = self.cache

        to_call_api = []
        all_tasks = len(api_tasks)
        for body, payload in api_tasks:
            if body not in cache:
                # print("not in cache")
                # print(payload["title"], body[:20])
                # we need to call embedding api
                to_call_api.append((body, payload))
            elif body not in self.cache:
                # print("in cache")
                self.cache[body] = (cache[body][0], payload)
            else:
                # even if body in cache, we need to update payload
                self.cache[body] = (self.cache[body][0], payload)

        BATCH_SIZE = 50
        num_tasks = len(to_call_api)
        # make 50 requests at once
        batches = [
            to_call_api[i : i + BATCH_SIZE]
            for i in range(0, len(to_call_api), BATCH_SIZE)
        ]
        print(
            f"total tasks: {all_tasks}, ",
            f"{100 - 100 * (num_tasks / all_tasks):.1f}% was cached",
        )
        print(f"processing {num_tasks} tasks in {len(batches)} batches")
        for batch in tqdm(batches):
            texts = [body for body, _payload in batch]
            res = embed_texts(texts)
            for i, data in enumerate(res["data"]):
                vec = data["embedding"]
                body, payload = batch[i]
                self.cache[body] = (vec, payload)

    def get_or_make(self, body, payload, cache=None):
        if cache is None:
            cache = self.cache
        if body not in cache:
            # print("not in cache")
            print(payload["title"], body[:20])
            self.cache[body] = (embed_texts(body), payload)
        elif body not in self.cache:
            self.cache[body] = (cache[body][0], payload)
        else:
            # even if body in cache, we need to update payload
            self.cache[body] = (self.cache[body][0], payload)

        return self.cache[body]

    def save(self):
        safe_write(self.cache, self.name)
