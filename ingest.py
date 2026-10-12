import pymupdf  # PyMuPDF (formerly imported as "fitz")


def extract_pages(pdf_path):
    """Return a list of {page, text} dictionaries, one per PDF page."""
    doc = pymupdf.open(pdf_path)
    pages = [{"page": i + 1, "text": page.get_text()} for i, page in enumerate(doc)]
    doc.close()
    return pages


def pages_with_figures(pdf_path, min_drawings=30):
    """Return 0-based indices of pages with images or many vector drawings."""
    doc = pymupdf.open(pdf_path)
    result = []
    for i, page in enumerate(doc):
        if len(page.get_drawings()) >= min_drawings or len(page.get_images()) > 0:
            result.append(i)
    doc.close()
    return result


def render_page_png(pdf_path, page_index, dpi=150):
    """Take a picture of one page and return PNG bytes."""
    doc = pymupdf.open(pdf_path)
    png_bytes = doc[page_index].get_pixmap(dpi=dpi).tobytes("png")
    doc.close()
    return png_bytes