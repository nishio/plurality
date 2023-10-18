"""
Upload embedding vectors to Qdrant.
Derived from [Omoikane Embed](https://github.com/nishio/omoikane-embed).
It is for [Plurality Vector Search](https://plurality-vecsearch.vercel.app/)
"""

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
import dotenv
import os
import time
import hashlib
import pickle
from tqdm import tqdm

dotenv.load_dotenv()
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_URL = os.environ.get("QDRANT_URL")
assert QDRANT_API_KEY and QDRANT_URL
PROJECT_NAME = "plurality"
COLLECTION_NAME = "plurality"


def recreate():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.DOT),
    )
    print(f"OK, recreated COLLECTION_NAME:{COLLECTION_NAME}")


def get_64bit_hash_from_tuple(input_tuple):
    input_string = "".join(map(str, input_tuple))
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode())
    return int(sha256_hash.hexdigest(), 16) & ((1 << 64) - 1)


def main(pickle_names, IS_LOCAL=False, TO_RESET=False):
    start_time = time.perf_counter()
    if IS_LOCAL:
        client = QdrantClient("localhost", port=6333)
    else:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    if TO_RESET:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.DOT),
        )

    # disable indexing for faster insertion
    client.update_collection(
        collection_name=COLLECTION_NAME,
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0),
    )

    for pickle_name in pickle_names:
        print("uploading", pickle_name)
        data = pickle.load(open(pickle_name, "rb"))
        keys = set(data.keys())
        num_total_keys = len(keys)
        print(f"num_total_keys: {num_total_keys}")
        if os.path.exists("prev.pickle"):
            prev_data = pickle.load(open("prev.pickle", "rb"))
            keys -= set(prev_data.keys())
            num_new_keys = len(keys)
            print(f"num_new_keys: {num_new_keys}")

        keys = list(keys)
        batches = [keys[i : i + 100] for i in range(0, len(keys), 100)]
        for batch in tqdm(batches):
            points = []
            for k in batch:
                # print(k, data[k])
                vec, payload = data[k]
                try:
                    id = get_64bit_hash_from_tuple(
                        (payload["project"], payload["title"], payload["text"])
                    )
                except Exception as e:
                    print(e)
                    print("payload:", payload)
                    break

                points.append(
                    PointStruct(
                        id=id,
                        vector=vec,
                        payload=payload,
                    ),
                )
            while True:
                try:
                    operation_info = client.upsert(
                        collection_name=COLLECTION_NAME,
                        wait=True,  # block until operation is finished
                        points=points,
                    )
                    break
                except Exception as e:
                    print(e)
                    time.sleep(10)

    # enable indexing
    client.update_collection(
        collection_name=COLLECTION_NAME,
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
    )
    print("OK, total time: ", int(time.perf_counter() - start_time), "sec")


if __name__ == "__main__":
    main([f"{PROJECT_NAME}.pickle"], IS_LOCAL=False)
