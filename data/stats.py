import pathlib
import collections
import tqdm
import pandas as pd

import tiktoken


# find all markdown files
md_files = list(pathlib.Path(__file__).parent.rglob("*.md"))

# count the number of times each word appears
counter = collections.Counter()
encoding = tiktoken.get_encoding("o200k_base")

for md_file in tqdm.tqdm(md_files):
    text = md_file.read_text().lower()
    words = encoding.decode_tokens_bytes(encoding.encode(text))
    # words = text.split()
    counter.update(words)

# print the total number of different words
print("Different words =", len(counter))

# print the total number of tokens
print( "Tokens =", sum(counter.values()))

# print the 100 most common words
print( "Most common 100 words")
print(pd.DataFrame(counter.most_common(100), columns=["word", "count"]).to_markdown())
