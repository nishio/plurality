"""
2023-10-18

On 2023-10-17, upstream  renamed manuscripts for good sorting.
It is nice but the entries in the cache point to the old file names.
This script updates the cache to point to the new file names.

Local cache (plurality.pickle) does not need special treatment. 
`VectorStore` class already implemented the logic to update the payload imformation (including citation) in cache.

I need to update the record in the Qdrant server.
The data is not so large, so I determined to delete old data.
"""

from upload_embedding import recreate

recreate()
