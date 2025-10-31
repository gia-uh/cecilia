from pathlib import Path
import argparse
import sys
import os

#!/usr/bin/env python3
"""
pdf_to_md.py

Scan the "data" folder next to this script for PDF files and convert each to a Markdown (.md) file.
Extracts page text and images (saved to data/images/<pdf_stem>/) and embeds image links in the markdown.

Requires: PyMuPDF (pip install pymupdf)
"""


try:
    import fitz  # PyMuPDF
except Exception as e:
    print("Error: PyMuPDF is required. Install with: pip install pymupdf", file=sys.stderr)
    raise

def pdf_to_md(pdf_path: Path, md_path: Path, images_root: Path):
    pdf_stem = pdf_path.stem
    # Ensure output dirs exist
    md_path.parent.mkdir(parents=True, exist_ok=True)
    img_dir = images_root / pdf_stem
    img_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    if doc.needs_pass:
        print(f"Skipping encrypted PDF (needs password): {pdf_path}", file=sys.stderr)
        return

    md_lines = []
    title = pdf_stem
    md_lines.append(f"# {title}\n")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        md_lines.append(f"## Page {page_num + 1}\n")
        if page_text.strip():
            md_lines.append(page_text.rstrip() + "\n")
        else:
            md_lines.append("_No extractable text on this page._\n")

        images = page.get_images(full=True)
        if images:
            for img_idx, img in enumerate(images, start=1):
                xref = img[0]
                try:
                    img_dict = doc.extract_image(xref)
                except Exception:
                    # fallback: try to create a pixmap and save as png
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha < 4:  # CMYK or grayscale without alpha
                        img_bytes = pix.tobytes("png")
                        img_ext = "png"
                    else:
                        pix0 = fitz.Pixmap(fitz.csRGB, pix)
                        img_bytes = pix0.tobytes("png")
                        img_ext = "png"
                        pix0 = None
                    pix = None
                else:
                    img_bytes = img_dict["image"]
                    img_ext = img_dict.get("ext", "png")

                img_name = f"{pdf_stem}_page{page_num + 1}_{img_idx}.{img_ext}"
                img_path = img_dir / img_name
                with open(img_path, "wb") as f:
                    f.write(img_bytes)

                # relative path from md file to image
                rel_path = Path(os_path_relpath(img_path, md_path.parent))
                md_lines.append(f"![{img_name}]({rel_path.as_posix()})\n")
    # write markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

def os_path_relpath(target: Path, start: Path) -> str:
    # pathlib.Path.relative_to can fail if not a subpath; fallback to os.path.relpath
    try:
        return target.relative_to(start).as_posix()
    except Exception:
        return os.path.relpath(str(target), start=str(start)).replace("\\", "/")

def find_pdfs(src_dir: Path):
    return sorted(p for p in src_dir.rglob("*.pdf"))

def main():
    parser = argparse.ArgumentParser(description="Convert all PDFs in a data folder to Markdown.")
    parser.add_argument("--data", "-d", type=Path, default=Path(__file__).parent / "data",
                        help="Path to the data folder containing PDFs (default: ./data)")
    parser.add_argument("--out", "-o", type=Path, default=None,
                        help="Output folder for markdown files (default: <data>/md)")
    parser.add_argument("--images", "-i", type=Path, default=None,
                        help="Images root folder (default: <data>/images)")
    args = parser.parse_args()

    data_dir = args.data.resolve()
    if not data_dir.exists():
        print(f"Data folder not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    md_root = args.out.resolve() if args.out else data_dir / "md"
    images_root = args.images.resolve() if args.images else data_dir / "images"

    pdfs = find_pdfs(data_dir)
    if not pdfs:
        print(f"No PDFs found in: {data_dir}", file=sys.stderr)
        sys.exit(0)

    for pdf in pdfs:
        rel = pdf.relative_to(data_dir)
        md_out = (md_root / rel).with_suffix(".md")
        md_out.parent.mkdir(parents=True, exist_ok=True)
        try:
            pdf_to_md(pdf, md_out, images_root)
            print(f"Converted: {pdf} -> {md_out}")
        except Exception as e:
            print(f"Failed to convert {pdf}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()