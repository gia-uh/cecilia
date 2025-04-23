from libzim.reader import Archive
import markitdown
import tempfile
import os
import pathlib
import tqdm


archive = Archive("ecured_es_all_2022-03.zim")

count = archive.all_entry_count
print(count)


for i in tqdm.tqdm(range(count), total=count):
    entry = archive._get_entry_by_id(i)
    item = entry.get_item()

    try:
        # print(item.title)

        title = item.title
        # keep letters and numbers
        letters = [s for s in title.lower() if ord(s) in range(97, 123) or ord(s) in range(48, 58)]

        filename = pathlib.Path(f"{letters[0]}/{letters[1]}/{title}.md")

        if filename.exists():
            continue

        content = item.content
        markup = bytes(content).decode("UTF-8")

        # save tempfile
        with tempfile.NamedTemporaryFile(suffix=".html") as f:
            f.write(markup.encode("UTF-8"))
            f.flush()

            text = markitdown.MarkItDown().convert(f.name).text_content

        if text:
            filename.parent.mkdir(parents=True, exist_ok=True)

            # save markdown
            with filename.open("w") as f:
                f.write(text)

    except Exception as e:
        pass
