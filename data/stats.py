import pathlib
import collections
import tqdm
import pandas as pd

import tiktoken
import random

# find all markdown files
md_files = list(pathlib.Path(__file__).parent.rglob("*.md"))

random.shuffle(md_files)

# count the number of times each word appears
counter = collections.Counter()
files = 0
encoding = tiktoken.get_encoding("o200k_base")

try:
    for md_file in tqdm.tqdm(md_files):
        text = md_file.read_text().lower()
        words = encoding.decode_tokens_bytes(encoding.encode(text))
        # words = text.split()
        counter.update(words)
        files += 1
except KeyboardInterrupt:
    pass

# print the total number of different words
print("Different words =", len(counter))

# print the total number of tokens
print("Tokens = {:,}".format(sum(counter.values())))

if files != len(md_files):
    print("Tokens (estimated) = {:,}".format(int(sum(counter.values()) / files * len(md_files))))
