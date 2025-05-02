import markitdown
import pathlib
import tqdm

pdfs = list(sorted(pathlib.Path(__file__).parent.rglob("*.pdf")))

for pdf in tqdm.tqdm(pdfs):
    md_path = pdf.with_suffix(".md")

    if md_path.exists():
        continue

    print(pdf)

    try:
        md = markitdown.MarkItDown().convert_local(pdf).text_content
        md_path.write_text(md)
    except markitdown._exceptions.MarkItDownException:
        print("Error converting", pdf)
