import streamlit as st
from PIL import Image, ImageDraw
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import tempfile
import os
from reportlab.lib.units import cm

# Config générale
st.set_page_config(page_title="Outils ludiques - Dominos et J'ai...", layout="centered")

# Onglets
tab1, tab2 = st.tabs(["🎲 Dominos", "🃏 J’ai… qui a ?"])

# =========================
# Onglet 1 : Dominos
# =========================
with tab1:
    st.header("Générateur de dominos - Fond blanc + PDF avant aperçu")

    uploaded_files = st.file_uploader(
        "Importe tes images",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"]
    )

    def create_domino(img1, img2, size=(300, 600)):
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
    else:
        st.info("👉 Importez au moins 2 images pour générer des dominos.")

# =========================
# Onglet 2 : J'ai… qui a ?
# =========================
with tab2:
    st.header("« J’ai… qui a ? » (images)")

    uploaded_files = st.file_uploader(
        "Importer les images (PNG / JPG) – l’ordre définit le jeu",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="jai_files"
    )

    if uploaded_files and len(uploaded_files) >= 1:
        images = [Image.open(f).convert("RGB") for f in uploaded_files]
        st.success(f"{len(images)} images importées")

        if st.button("📄 Générer et télécharger le PDF"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf_path = tmp.name

            c = canvas.Canvas(pdf_path, pagesize=A4)
            page_width, page_height = A4

            card_margin = 1.5 * cm
            card_width = page_width - 2 * card_margin
            card_height = page_height - 2 * card_margin
            corner_radius = 25
            total_cards = len(images) + 1

            for i in range(total_cards):
                c.setLineWidth(3)
                c.roundRect(card_margin, card_margin, card_width, card_height, corner_radius)
                center_y = page_height / 2

                if i == 0:
                    c.setFont("Helvetica-Bold", 35)
                    c.drawCentredString(page_width / 2, page_height - card_margin - 2 * cm, "J’ai la première carte !")
                    c.setFont("Helvetica-Bold", 40)
                    c.drawCentredString(page_width / 2, center_y - 1 * cm, "Qui a ?")
                    first_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    images[0].save(first_img_path)
                    c.drawImage(first_img_path, card_margin + 2 * cm, card_margin + 2 * cm,
                                card_width - 4 * cm, card_height / 3, preserveAspectRatio=True)
                    os.remove(first_img_path)
                elif i < total_cards - 1:
                    img_have = images[i - 1]
                    img_who = images[i]
                    c.setFont("Helvetica-Bold", 40)
                    c.drawCentredString(page_width / 2, page_height - card_margin - 1.5 * cm, "J’ai")
                    have_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    img_have.save(have_path)
                    c.drawImage(have_path, card_margin + 2 * cm, center_y + 1 * cm,
                                card_width - 4 * cm, card_height / 3, preserveAspectRatio=True)
                    c.setFont("Helvetica-Bold", 40)
                    c.drawCentredString(page_width / 2, center_y - 1 * cm, "Qui a ?")
                    who_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    img_who.save(who_path)
                    c.drawImage(who_path, card_margin + 2 * cm, card_margin + 2 * cm,
                                card_width - 4 * cm, card_height / 3, preserveAspectRatio=True)
                    os.remove(have_path)
                    os.remove(who_path)
                else:
                    img_last = images[-1]
                    c.setFont("Helvetica-Bold", 40)
                    c.drawCentredString(page_width / 2, page_height - card_margin - 1.5 * cm, "J’ai")
                    last_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    img_last.save(last_path)
                    c.drawImage(last_path, card_margin + 2 * cm, center_y,
                                card_width - 4 * cm, card_height / 3, preserveAspectRatio=True)
                    c.setFont("Helvetica-Bold", 35)
                    c.drawCentredString(page_width / 2, card_margin + 2.5 * cm, "… c’est la dernière carte !")
                    os.remove(last_path)

                c.showPage()
            c.save()

            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Télécharger le PDF final",
                    f,
                    file_name="j_ai_qui_a_cartes_final.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("👉 Importez au moins 1 image pour générer le jeu.")
