from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from textwrap import wrap
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


def _ensure_cjk_font():
    """Register a CJK font so Chinese text doesn't render as tofu blocks."""
    try:
        pdfmetrics.getFont("STSong-Light")
    except Exception:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        except Exception:
            # As a last resort we still proceed with Helvetica, but it may show squares
            pass


def draw_branded_page(c: canvas.Canvas, title: str = "", footer: str = "", color_hex: str = "#0B3B5A"):
    width, height = A4
    # Header band
    c.setFillColor(colors.HexColor(color_hex))
    c.rect(0, height-18*mm, width, 18*mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    # Header font: title通常是英文，仍用Helvetica-Bold；若含中文，下面也再绘制一遍
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, height-11*mm, title[:120])
    try:
        _ensure_cjk_font()
        c.setFont("STSong-Light", 12)
        c.drawString(20*mm, height-11*mm, title[:120])
    except Exception:
        pass
    # Footer line
    c.setStrokeColor(colors.HexColor("#E5E7EB"))
    c.line(15*mm, 15*mm, width-15*mm, 15*mm)
    c.setFillColor(colors.HexColor("#6B7280"))
    try:
        _ensure_cjk_font(); c.setFont("STSong-Light", 9)
    except Exception:
        c.setFont("Helvetica", 9)
    c.drawRightString(width-15*mm, 10*mm, footer[:140])


def render_plain_text_to_pdf(text: str, title: str, footer: str, color_hex: str = "#0B3B5A") -> bytes:
    import io
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 20*mm, 25*mm
    y = height - 25*mm
    line_height = 5.2*mm
    max_chars = 95

    draw_branded_page(c, title=title, footer=footer, color_hex=color_hex)
    # Body font: use CJK
    try:
        _ensure_cjk_font(); c.setFont("STSong-Light", 10)
    except Exception:
        c.setFont("Helvetica", 10)

    for paragraph in text.split('\n'):
        if not paragraph:
            y -= line_height
            if y < y_margin:
                c.showPage(); draw_branded_page(c, title=title, footer=footer, color_hex=color_hex);
                try:
                    _ensure_cjk_font(); c.setFont("STSong-Light", 10)
                except Exception:
                    c.setFont("Helvetica", 10)
                y = height - 25*mm
            continue
        for line in wrap(paragraph, max_chars):
            c.setFillColor(colors.black)
            c.drawString(x_margin, y, line)
            y -= line_height
            if y < y_margin:
                c.showPage(); draw_branded_page(c, title=title, footer=footer, color_hex=color_hex);
                try:
                    _ensure_cjk_font(); c.setFont("STSong-Light", 10)
                except Exception:
                    c.setFont("Helvetica", 10)
                y = height - 25*mm
    c.save()
    return buffer.getvalue()

