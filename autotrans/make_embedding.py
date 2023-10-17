"""
Make embedding vectors for each line in the manuscript.
Derived from [Omoikane Embed](https://github.com/nishio/omoikane-embed).

"""

import os
import json
import dotenv
import openai
import tiktoken
import time
import signal
import pickle
from tqdm import tqdm
import numpy as np

"""
# Targets
When same content exist in multiple files, preceding target will be shown as a reference. So:
- English should be the first
- Auto-translated contents should be the bottom
"""
dirs = [
    "../contents/english",
    "../contents/traditional-mandarin",
    "../contents/japanese-auto",
]
targets = []
for d in dirs:
    targets += list(sorted(f"{d}/{f}" for f in os.listdir(d)))
print(targets)


def to_skip(line):
    if not line:
        return True
    if line.strip() == "":
        return True
    if line.startswith("<img src="):
        return True
    if "| 作者" in line or "| 譯者" in line:
        return True

    return False


"""
# Check repeatedly occuring lines
the result is saved to `not_to_embed.json` and reused.
"""
if 0:
    used = set()
    not_to_embed = set()
    for page in targets:
        with open(page, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.rstrip("\n")
            if to_skip(line):
                continue
            if line in used:
                print(repr(line))
                not_to_embed.add(line)
            else:
                used.add(line)

    json.dump(
        list(not_to_embed),
        open("not_to_embed.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )


dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT = os.getenv("PROJECT_NAME")
openai.api_key = OPENAI_API_KEY
enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    return len(enc.encode(text))


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


def main(
    out_index,
    cache_index=None,
    dry_run=False,
):
    """
    out_index: output index file name
    jsonfile: input json file name (from scrapbox)
    in_index: input index file name (it is not modified, but used as cache)

    # usage
    ## create new index
    update_from_scrapbox(
        "nishio.pickle",
        "from_scrapbox/nishio.json")
    ## update index
    update_from_scrapbox(
        "nishio-0314.pickle", "from_scrapbox/nishio-0314.json", "nishio-0310.pickle")
    """
    tokens = 0
    api_tasks = []

    def add(body, payload):
        nonlocal tokens
        tokens += get_size(body)
        api_tasks.append((body, payload))

    cache = None
    if cache_index is not None:
        cache = VectorStore(cache_index, create_if_not_exist=False).cache
    vs = VectorStore(out_index)

    data = []
    not_to_embed = json.load(open("not_to_embed.json", "r", encoding="utf-8"))
    x = []
    for page in targets:
        with open(page, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.rstrip("\n")
            if to_skip(line):
                continue
            if line in not_to_embed:
                continue
            title = page.replace("../contents/", "").replace(".md", "")
            data.append((line, title))

    for p in tqdm(data):
        line, title = p
        # replace special token
        line = line.replace("<|endoftext|>", " ")
        payload = {
            "title": title,
            "project": "pluralitybook",
            "text": line,
            "is_public": True,
        }
        add(line, payload)

    if dry_run:
        cost = tokens * 0.0001 / 1000  # $0.0001 / 1K tokens
        print("tokens:", tokens, f"cost: {cost:.2f} USD")
        if cache_index is None:
            cache = vs.cache
        in_cache = 0
        not_in_cache = 0
        for body, payload in api_tasks:
            if body in cache:
                in_cache += 1
            else:
                not_in_cache += 1
        print("in cache:", in_cache, ", not in cache:", not_in_cache)

    else:
        vs.batch(api_tasks, cache)
        vs.save()


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


if __name__ == "__main__":
    main("plurality.pickle")
