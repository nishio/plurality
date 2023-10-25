"""
Make embedding vectors for each line in the manuscript of RxC blog.
Derived from make_embedding.py
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

$ git clone https://github.com/RadicalxChange/www.git

When same content exist in multiple files, last target will be shown as a reference.
It is sorted by file name, and the name starts with date, so the latest blog will be the last.
"""
dirs = [
    "www/src/site/media/blog",
]
targets = []
for d in dirs:
    targets += list(sorted(f"{d}/{f}" for f in os.listdir(d)))
print(targets)

not_to_embed = json.load(open("not_to_embed.json", "r", encoding="utf-8"))


def to_skip(line):
    if not line:
        return True
    line = line.strip()
    if line == "":
        return True
    if line.startswith("<img src="):
        return True
    if line.startswith("<div"):
        return True
    if line.startswith("<ol"):
        return True
    if line.startswith("layout: "):
        return True
    if line.startswith("postAuthor: "):
        return True
    if line.startswith("style="):
        return True
    if line.startswith("date: "):
        return True
    if line.startswith('<p class="youtube-container">'):
        return True

    if "| 作者" in line or "| 譯者" in line:
        return True
    if line in not_to_embed:
        return True
    return False


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
    for page in targets:
        with open(page, "r", encoding="utf-8") as f:
            lines = f.readlines()
        basename = page.replace("www/src/site/media/blog/", "").replace(".md", "")
        # print(basename)
        assert basename[10] in "-_"
        url_id = basename[11:]
        url = f"https://www.radicalxchange.org/media/blog/{url_id}/"
        print(url)

        for line in lines:
            line = line.rstrip("\n")
            if line.startswith("title: "):
                title = line.replace('title: "', "").rstrip('"')
                print(title)
            if to_skip(line):
                continue
            if line in not_to_embed:
                continue
            # url = https://www.radicalxchange.org/media/blog/2018-11-26-4m9b8b/
            data.append((line, title, url))

    for p in tqdm(data):
        line, title, url = p
        # replace special token
        line = line.replace("<|endoftext|>", " ")
        payload = {
            "title": title,
            "project": "rxc_blog",
            "text": line,
            "is_public": True,
            "url": url,
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
    main("rxc_blog.pickle")
    import upload_embedding

    upload_embedding.main(["rxc_blog.pickle"], IS_LOCAL=False)
