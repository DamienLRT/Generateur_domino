import streamlit as st
from PIL import Image, ImageDraw
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Générateur de dominos", layout="centered")
st.title("Générateur de dominos - Fond blanc + PDF avant aperçu")

uploaded_files = st.file_uploader(
    "Importe tes images",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg"]
)

def create_domino(img1, img2, size=(300, 600)):
    """Crée un domino avec fond blanc et transparence gérée"""
    img1 = img1.resize((size[0], size[1] // 2))
    img2 = img2.resize((size[0], size[1] // 2))

    domino = Image.new("RGB", size, (255, 255, 255))  # fond blanc

    def paste_with_white_background(base, img, position):
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            alpha = img.convert('RGBA').split()[-1]
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.paste(img, mask=alpha)
            base.paste(bg.convert("RGB"), position)
        else:
            base.paste(img, position)

    paste_with_white_background(domino, img1, (0, 0))
    paste_with_white_background(domino, img2, (0, size[1] // 2))

    draw = ImageDraw.Draw(domino)
    draw.line((0, size[1] // 2, size[0], size[1] // 2), fill="black", width=4)
    draw.rectangle((0, 0, size[0]-1, size[1]-1), outline="black", width=4)

    return domino

if uploaded_files and len(uploaded_files) >= 2:
    images = [Image.open(f).convert("RGBA") for f in uploaded_files]
    random.shuffle(images)

    dominos = []
    n = len(images)

    for i in range(n):
        img1 = images[i]
        img2 = images[(i + 1) % n]  # boucle circulaire
        dominos.append((img1, img2))

    # PDF
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    for domino_pair in dominos:
        domino_img = create_domino(domino_pair[0], domino_pair[1])
        img_reader = ImageReader(domino_img)
        img_w, img_h = domino_img.size
        scale = min(width / img_w * 0.8, height / img_h * 0.8)
        new_w, new_h = img_w * scale, img_h * scale
        x = (width - new_w) / 2
        y = (height - new_h) / 2
        c.drawImage(img_reader, x, y, width=new_w, height=new_h)
        c.showPage()
    c.save()
    pdf_buffer.seek(0)

    # Bouton PDF avant aperçu
    st.download_button(
        label="Télécharger tous les dominos en PDF",
        data=pdf_buffer,
        file_name="dominos.pdf",
        mime="application/pdf"
    )

    st.subheader(f"{len(dominos)} dominos générés")
    for i, (img1, img2) in enumerate(dominos):
        domino = create_domino(img1, img2)
        st.image(domino, caption=f"Domino {i+1}")
        st.divider()
