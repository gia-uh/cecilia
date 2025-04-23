import markitdown
import pathlib

pdfs = sorted(pathlib.Path(__file__).parent.rglob("*.pdf"))

for pdf in pdfs:
    print(pdf)
    md_path = pdf.with_suffix(".md")

    if md_path.exists():
        continue

    md = markitdown.MarkItDown().convert_local(pdf).text_content
    md_path.write_text(md)
