import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


# =============================================================
# CONFIGURATION
# =============================================================

st.set_page_config(
    page_title="Générateur de dominos",
    layout="centered"
)

st.title("Générateur de dominos - Fond blanc + PDF")


# =============================================================
# IMPORT DES IMAGES
# =============================================================

uploaded_files = st.file_uploader(
    "Importe tes images",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg"]
)


# =============================================================
# CRÉATION D'UN DOMINO
# =============================================================

def create_domino(img1, img2, name1, name2, size=(400, 700)):
    """
    Crée un domino avec :
    - une première image
    - le nom de la première image
    - une deuxième image
    - le nom de la deuxième image
    """

    image_width = size[0]
    image_height = 280
    text_height = 70

    # Fond blanc
    domino = Image.new("RGB", size, "white")

    draw = ImageDraw.Draw(domino)

    # ---------------------------------------------------------
    # POLICE DES NOMS
    # ---------------------------------------------------------

    font = ImageFont.truetype("arial.ttf", 30)

    # ---------------------------------------------------------
    # FONCTION POUR PLACER UNE IMAGE
    # ---------------------------------------------------------

    def paste_with_white_background(base, img, position, img_size):

        img = img.copy()

        # Conserver les proportions de l'image
        img.thumbnail(img_size)

        # Centrer l'image
        x = position[0] + (img_size[0] - img.width) // 2
        y = position[1] + (img_size[1] - img.height) // 2

        # Gestion de la transparence
        if img.mode in ("RGBA", "LA") or (
            img.mode == "P"
            and "transparency" in img.info
        ):

            alpha = img.convert("RGBA").split()[-1]

            bg = Image.new(
                "RGBA",
                img.size,
                (255, 255, 255, 255)
            )

            bg.paste(
                img,
                mask=alpha
            )

            base.paste(
                bg.convert("RGB"),
                (x, y)
            )

        else:

            base.paste(
                img.convert("RGB"),
                (x, y)
            )

    # ---------------------------------------------------------
    # NETTOYAGE DES NOMS
    # ---------------------------------------------------------

    # Retire l'extension .jpg / .png / .jpeg
    name1 = name1.rsplit(".", 1)[0]
    name2 = name2.rsplit(".", 1)[0]

    # ---------------------------------------------------------
    # PREMIÈRE IMAGE
    # ---------------------------------------------------------

    paste_with_white_background(
        domino,
        img1,
        (0, 0),
        (image_width, image_height)
    )

    # Nom de la première image
    draw.text(
        (
            image_width // 2,
            image_height + text_height // 2
        ),
        name1,
        fill="black",
        font=font,
        anchor="mm"
    )

    # ---------------------------------------------------------
    # DEUXIÈME IMAGE
    # ---------------------------------------------------------

    second_y = image_height + text_height

    paste_with_white_background(
        domino,
        img2,
        (0, second_y),
        (image_width, image_height)
    )

    # Nom de la deuxième image
    draw.text(
        (
            image_width // 2,
            second_y + image_height + text_height // 2
        ),
        name2,
        fill="black",
        font=font,
        anchor="mm"
    )

    # ---------------------------------------------------------
    # LIGNE CENTRALE
    # ---------------------------------------------------------

    draw.line(
        (
            0,
            second_y,
            image_width,
            second_y
        ),
        fill="black",
        width=4
    )

    # ---------------------------------------------------------
    # BORDURE DU DOMINO
    # ---------------------------------------------------------

    draw.rectangle(
        (
            0,
            0,
            image_width - 1,
            size[1] - 1
        ),
        outline="black",
        width=4
    )

    return domino


# =============================================================
# GÉNÉRATION DES DOMINOS
# =============================================================

if uploaded_files and len(uploaded_files) >= 2:

    # On conserve l'image ET le nom du fichier
    images = [
        (
            Image.open(f).convert("RGBA"),
            f.name
        )
        for f in uploaded_files
    ]

    # Mélange aléatoire
    random.shuffle(images)

    dominos = []

    n = len(images)

    # ---------------------------------------------------------
    # CRÉATION DES COUPLES
    # ---------------------------------------------------------

    for i in range(n):

        img1, name1 = images[i]

        # Boucle circulaire :
        # la dernière image est associée à la première
        img2, name2 = images[(i + 1) % n]

        dominos.append(
            (
                img1,
                img2,
                name1,
                name2
            )
        )

    # =========================================================
    # CRÉATION DU PDF
    # =========================================================

    pdf_buffer = io.BytesIO()

    c = canvas.Canvas(
        pdf_buffer,
        pagesize=A4
    )

    width, height = A4

    for domino_pair in dominos:

        img1, img2, name1, name2 = domino_pair

        # Création du domino
        domino_img = create_domino(
            img1,
            img2,
            name1,
            name2
        )

        # Conversion pour ReportLab
        img_reader = ImageReader(domino_img)

        img_w, img_h = domino_img.size

        # Taille du domino dans la page A4
        scale = min(
            width / img_w * 0.8,
            height / img_h * 0.8
        )

        new_w = img_w * scale
        new_h = img_h * scale

        # Centrage dans la page
        x = (width - new_w) / 2
        y = (height - new_h) / 2

        c.drawImage(
            img_reader,
            x,
            y,
            width=new_w,
            height=new_h
        )

        # Nouvelle page
        c.showPage()

    # Finalisation du PDF
    c.save()

    pdf_buffer.seek(0)

    # =========================================================
    # BOUTON DE TÉLÉCHARGEMENT DU PDF
    # =========================================================

    st.download_button(
        label="Télécharger tous les dominos en PDF",
        data=pdf_buffer,
        file_name="dominos.pdf",
        mime="application/pdf"
    )

    # =========================================================
    # APERÇU DES DOMINOS
    # =========================================================

    st.subheader(
        f"{len(dominos)} dominos générés"
    )

    for i, (img1, img2, name1, name2) in enumerate(dominos):

        domino = create_domino(
            img1,
            img2,
            name1,
            name2
        )

        st.image(
            domino,
            caption=f"Domino {i + 1}"
        )

        st.divider()
