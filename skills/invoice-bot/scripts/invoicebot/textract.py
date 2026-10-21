"""Get the text out of an invoice file.

Order of preference (layout-preserving extraction matters: labels and values in tables must stay on
the same lines and columns):
  1. pdftotext -layout (poppler)            best; on Linux/macOS it is usually installed or one package away
  2. pypdf layout mode                      pure Python fallback
  3. OCR with tesseract (+ pdftoppm)        for scanned PDFs and photos, only when installed
Without a text layer and without OCR the invoice goes to review, where an admin (or Claude, who can
read the PDF visually) types the fields in.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

PDF_MAGIC = b'%PDF'
IMAGE_MAGIC = {b'\xff\xd8\xff': 'jpg', b'\x89PNG\r\n\x1a\n': 'png', b'II*\x00': 'tif', b'MM\x00*': 'tif'}


def sniff(data, name=''):
    """Kind of file from its bytes: pdf / image / eml / zip / None."""
    head = data[:1024]
    if PDF_MAGIC in head:
        return 'pdf'
    for magic in IMAGE_MAGIC:
        if data.startswith(magic):
            return 'image'
    if data.startswith(b'PK\x03\x04'):
        return 'zip'
    low = name.lower()
    if low.endswith(('.eml', '.msg.eml')) or _looks_like_mime(head):
        return 'eml'
    return None


def _looks_like_mime(head):
    try:
        txt = head.decode('ascii', 'ignore').lower()
    except Exception:
        return False
    return ('\nfrom:' in '\n' + txt or 'mime-version:' in txt) and 'content-type:' in txt


def meaningful(text):
    return sum(c.isalpha() for c in text or '') >= 25


def pdf_text(path, max_pages=10, ocr=True, ocr_langs='hun+eng+deu'):
    """(text, method). method is pdftotext / pypdf / ocr / none / encrypted."""
    path = str(path)
    exe = shutil.which('pdftotext')
    if exe:
        try:
            r = subprocess.run([exe, '-layout', '-enc', 'UTF-8', '-l', str(max_pages), path, '-'],
                               capture_output=True, timeout=90)
            text = r.stdout.decode('utf-8', 'replace')
            if r.returncode == 0 and meaningful(text):
                return text, 'pdftotext'
            if b'Incorrect password' in r.stderr or b'encrypted' in r.stderr.lower():
                return '', 'encrypted'
        except (OSError, subprocess.TimeoutExpired):
            pass
    text = _pypdf_text(path, max_pages)
    if text is None:
        return '', 'encrypted'
    if meaningful(text):
        return text, 'pypdf'
    if ocr:
        text = _ocr_pdf(path, min(max_pages, 3), ocr_langs)
        if meaningful(text):
            return text, 'ocr'
    return '', 'none'


def _pypdf_text(path, max_pages):
    try:
        import pypdf
    except ImportError:
        return ''
    try:
        reader = pypdf.PdfReader(path)
        if reader.is_encrypted:
            try:
                if not reader.decrypt(''):
                    return None
            except Exception:
                return None
        pages = []
        for page in reader.pages[:max_pages]:
            try:
                pages.append(page.extract_text(extraction_mode='layout') or '')
            except TypeError:
                pages.append(page.extract_text() or '')
            except Exception:
                pages.append(page.extract_text() or '')
        return '\f'.join(pages)
    except Exception:
        return ''


_LANGS = None


def _tesseract_langs(wanted):
    global _LANGS
    if _LANGS is None:
        try:
            r = subprocess.run(['tesseract', '--list-langs'], capture_output=True, timeout=20)
            _LANGS = set(r.stdout.decode('utf-8', 'ignore').split()[1:])
        except (OSError, subprocess.TimeoutExpired):
            _LANGS = set()
    have = [l for l in wanted.split('+') if l in _LANGS]
    return '+'.join(have) or 'eng'


def ocr_available():
    return bool(shutil.which('tesseract'))


def _ocr_image(path, langs):
    try:
        r = subprocess.run(['tesseract', str(path), '-', '-l', _tesseract_langs(langs), '--psm', '6'],
                           capture_output=True, timeout=180)
        return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def _ocr_pdf(path, pages, langs):
    if not (ocr_available() and shutil.which('pdftoppm')):
        return ''
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(['pdftoppm', '-r', '300', '-gray', '-png', '-l', str(pages), str(path),
                            str(Path(tmp) / 'p')], capture_output=True, timeout=180)
        except (OSError, subprocess.TimeoutExpired):
            return ''
        return '\f'.join(_ocr_image(p, langs) for p in sorted(Path(tmp).glob('p*.png')))


def image_text(path, ocr=True, ocr_langs='hun+eng+deu'):
    if ocr and ocr_available():
        text = _ocr_image(path, ocr_langs)
        if meaningful(text):
            return text, 'ocr'
    return '', 'none'


def extract_text(path, kind, cfg):
    ocr_cfg = cfg.get('ocr', {})
    if kind == 'pdf':
        return pdf_text(path, cfg.get('pdf_max_pages', 10), ocr_cfg.get('enabled', True),
                        ocr_cfg.get('languages', 'hun+eng+deu'))
    if kind == 'image':
        return image_text(path, ocr_cfg.get('enabled', True), ocr_cfg.get('languages', 'hun+eng+deu'))
    return '', 'none'
