"""
Make embedding vectors for each line in the manuscript of RxC blog.
Derived from make_embedding.py

$ git clone https://github.com/RadicalxChange/www.git

"""

import os
import json
import dotenv
import openai
import tiktoken
from tqdm import tqdm
from vectorstore import VectorStore

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


def main(
    out_index,
    cache_index=None,
    dry_run=False,
):
    """
    out_index: output index file name
    cache_index: input index file name (it is not modified, but used as cache)
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


if __name__ == "__main__":
    main("plurality.pickle")
