import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import random
import tempfile
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =============================================================
# CONFIGURATION GÉNÉRALE
# =============================================================

st.set_page_config(
    page_title="Outils ludiques - Dominos et J'ai...",
    layout="centered"
)


# =============================================================
# ONGLET
# =============================================================

tab0, tab1, tab2 = st.tabs([
    "A propos",
    "🎲 Dominos",
    "🃏 J’ai… qui a ?"
])


# =============================================================
# COULEURS PASTEL
# =============================================================

pastel_colors = {

    "🤍 Blanc":
        (255, 255, 255),

    "🌸 Rose pastel":
        (255, 225, 235),

    "🩵 Bleu pastel":
        (220, 240, 255),

    "🌿 Vert pastel":
        (225, 245, 225),

    "🍋 Jaune pastel":
        (255, 248, 210),

    "🍑 Pêche pastel":
        (255, 230, 215),

    "💜 Lavande":
        (235, 225, 250),

    "🩷 Rose poudré":
        (245, 220, 225),
}


# =============================================================
# CHEMIN DE LA POLICE BOREL
# =============================================================

borel_path = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "Borel.ttf"
)


# =============================================================
# FONCTION : POLICE POUR PIL
# =============================================================

def get_pil_font(cursive):

    if cursive:

        if not os.path.exists(
            borel_path
        ):

            st.error(
                "❌ La police Borel est introuvable.\n\n"
                "Ajoute le fichier Borel.ttf "
                "dans le même dossier que app.py."
            )

            st.stop()

        return ImageFont.truetype(
            borel_path,
            32
        )


    # ---------------------------------------------------------
    # POLICE NORMALE
    # ---------------------------------------------------------

    arial_path = (
        "C:/Windows/Fonts/arial.ttf"
    )


    if os.path.exists(
        arial_path
    ):

        return ImageFont.truetype(
            arial_path,
            32
        )


    # ---------------------------------------------------------
    # FALLBACK LINUX / STREAMLIT CLOUD
    # ---------------------------------------------------------

    try:

        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            32
        )

    except:

        return ImageFont.load_default()


# =============================================================
# FONCTION : POLICE POUR REPORTLAB
# =============================================================

def get_reportlab_font(cursive):

    if cursive:

        if not os.path.exists(
            borel_path
        ):

            st.error(
                "❌ La police Borel.ttf est introuvable."
            )

            st.stop()


        try:

            pdfmetrics.registerFont(
                TTFont(
                    "Borel",
                    borel_path
                )
            )

        except:

            pass


        return "Borel"


    return "Helvetica"


# =============================================================
# ONGLET 0 : À PROPOS
# =============================================================

with tab0:

    st.header(
        "ℹ️ À propos du projet"
    )

    st.markdown("""
Ce projet est né d’un besoin personnel.

👉 Il a été conçu pour ma fiancée, institutrice en maternelle,  
afin de lui permettre de créer facilement des supports ludiques et pédagogiques utilisés dans l'apprentissage du lexique.

🎯 Objectif :

- Faciliter l’apprentissage du lexique chez les jeunes enfants
- Transformer des images en jeux éducatifs
- Gagner du temps dans la création de ressources personnalisées

🧠 L’idée est de rendre la création d’outils pédagogiques :

- simple
- rapide
- et entièrement personnalisable

✨ Ce projet continue d’évoluer au fil des besoins de la classe et des retours terrain.
""")


# =============================================================
# ONGLET 1 : DOMINOS
# =============================================================

with tab1:

    st.header(
        "Générateur de dominos - Fond pastel + PDF"
    )


    # =========================================================
    # IMPORT DES IMAGES
    # =========================================================

    uploaded_files = st.file_uploader(
        "Importe tes images",
        accept_multiple_files=True,
        type=[
            "png",
            "jpg",
            "jpeg"
        ],
        key="domino_files"
    )


    # =========================================================
    # POLICE
    # =========================================================

    cursive_domino = st.checkbox(
        "✍️ Police cursive",
        value=False,
        key="domino_cursive"
    )


    if cursive_domino:

        st.caption(
            "Police utilisée : Borel"
        )

    else:

        st.caption(
            "Police utilisée : police par défaut"
        )


    # =========================================================
    # FOND
    # =========================================================

    background_name_domino = st.selectbox(
        "🎨 Couleur du fond des dominos",
        list(pastel_colors.keys()),
        index=0,
        key="domino_background"
    )


    background_color_domino = (
        pastel_colors[
            background_name_domino
        ]
    )


    # =========================================================
    # CRÉATION DOMINO
    # =========================================================

    def create_domino(
        img1,
        img2,
        name1,
        name2,
        background_color,
        cursive,
        size=(400, 700)
    ):

        image_width = size[0]

        image_height = 280

        text_height = 70


        # -----------------------------------------------------
        # FOND
        # -----------------------------------------------------

        domino = Image.new(
            "RGB",
            size,
            background_color
        )


        draw = ImageDraw.Draw(
            domino
        )


        # -----------------------------------------------------
        # POLICE
        # -----------------------------------------------------

        font = get_pil_font(
            cursive
        )


        # =====================================================
        # PLACER IMAGE
        # =====================================================

        def paste_with_background(
            base,
            img,
            position,
            img_size
        ):

            img = img.copy()

            img.thumbnail(
                img_size
            )


            x = (
                position[0]
                + (
                    img_size[0]
                    - img.width
                ) // 2
            )


            y = (
                position[1]
                + (
                    img_size[1]
                    - img.height
                ) // 2
            )


            # -------------------------------------------------
            # TRANSPARENCE
            # -------------------------------------------------

            if (
                img.mode in (
                    "RGBA",
                    "LA"
                )
                or (
                    img.mode == "P"
                    and "transparency"
                    in img.info
                )
            ):

                alpha = (
                    img.convert(
                        "RGBA"
                    ).split()[-1]
                )


                bg = Image.new(
                    "RGBA",
                    img.size,
                    background_color + (
                        255,
                    )
                )


                bg.paste(
                    img,
                    mask=alpha
                )


                base.paste(
                    bg.convert(
                        "RGB"
                    ),
                    (x, y)
                )


            else:

                base.paste(
                    img.convert(
                        "RGB"
                    ),
                    (x, y)
                )


        # =====================================================
        # NOMS
        # =====================================================

        name1 = name1.rsplit(
            ".",
            1
        )[0]


        name2 = name2.rsplit(
            ".",
            1
        )[0]


        # =====================================================
        # IMAGE 1
        # =====================================================

        paste_with_background(
            domino,
            img1,
            (0, 0),
            (
                image_width,
                image_height
            )
        )


        # =====================================================
        # NOM 1
        # =====================================================

        draw.text(
            (
                image_width // 2,
                image_height
                + text_height // 2
            ),
            name1,
            fill="black",
            font=font,
            anchor="mm"
        )


        # =====================================================
        # IMAGE 2
        # =====================================================

        second_y = (
            image_height
            + text_height
        )


        paste_with_background(
            domino,
            img2,
            (0, second_y),
            (
                image_width,
                image_height
            )
        )


        # =====================================================
        # NOM 2
        # =====================================================

        draw.text(
            (
                image_width // 2,
                second_y
                + image_height
                + text_height // 2
            ),
            name2,
            fill="black",
            font=font,
            anchor="mm"
        )


        # =====================================================
        # PETITS POINTS
        # =====================================================

        dot_radius = 2.5

        gap = 14

        x = 8


        while x < image_width - 8:

            draw.ellipse(
                (
                    x - dot_radius,
                    second_y - dot_radius,
                    x + dot_radius,
                    second_y + dot_radius
                ),
                fill="black"
            )

            x += gap


        # =====================================================
        # BORDURE ARRONDIE
        # =====================================================

        draw.rounded_rectangle(
            (
                2,
                2,
                image_width - 3,
                size[1] - 3
            ),
            radius=25,
            outline="black",
            width=4
        )


        return domino


    # =========================================================
    # GÉNÉRATION DOMINOS
    # =========================================================

    if uploaded_files and len(
        uploaded_files
    ) >= 2:


        # -----------------------------------------------------
        # IMAGES + NOMS
        # -----------------------------------------------------

        images = [

            (
                Image.open(
                    f
                ).convert("RGBA"),

                f.name
            )

            for f in uploaded_files
        ]


        random.shuffle(
            images
        )


        # -----------------------------------------------------
        # COUPLES
        # -----------------------------------------------------

        dominos = []

        n = len(
            images
        )


        for i in range(n):

            img1, name1 = images[i]

            img2, name2 = images[
                (i + 1) % n
            ]


            dominos.append(
                (
                    img1,
                    img2,
                    name1,
                    name2
                )
            )


        # =====================================================
        # PDF
        # =====================================================

        pdf_buffer = io.BytesIO()


        c = canvas.Canvas(
            pdf_buffer,
            pagesize=A4
        )


        width, height = A4


        for domino_pair in dominos:

            img1, img2, name1, name2 = (
                domino_pair
            )


            domino_img = create_domino(
                img1,
                img2,
                name1,
                name2,
                background_color_domino,
                cursive_domino
            )


            img_reader = ImageReader(
                domino_img
            )


            img_w, img_h = (
                domino_img.size
            )


            scale = min(
                width / img_w * 0.8,
                height / img_h * 0.8
            )


            new_w = (
                img_w * scale
            )

            new_h = (
                img_h * scale
            )


            x = (
                width - new_w
            ) / 2


            y = (
                height - new_h
            ) / 2


            c.drawImage(
                img_reader,
                x,
                y,
                width=new_w,
                height=new_h
            )


            c.showPage()


        c.save()

        pdf_buffer.seek(0)


        # =====================================================
        # TÉLÉCHARGEMENT
        # =====================================================

        st.download_button(
            label="📄 Télécharger tous les dominos en PDF",
            data=pdf_buffer,
            file_name="dominos.pdf",
            mime="application/pdf",
            key="domino_download"
        )


        # =====================================================
        # APERÇU
        # =====================================================

        st.subheader(
            f"{len(dominos)} dominos générés"
        )


        for i, (
            img1,
            img2,
            name1,
            name2
        ) in enumerate(
            dominos
        ):


            domino = create_domino(
                img1,
                img2,
                name1,
                name2,
                background_color_domino,
                cursive_domino
            )


            st.image(
                domino,
                caption=f"Domino {i + 1}"
            )


            st.divider()


    else:

        st.info(
            "👉 Importez au moins 2 images "
            "pour générer des dominos."
        )


# =============================================================
# ONGLET 2 : J'AI... QUI A ?
# =============================================================

with tab2:

    st.header(
        "« J’ai… qui a ? »"
    )


    # =========================================================
    # POLICE
    # =========================================================

    cursive_jai = st.checkbox(
        "✍️ Police cursive",
        value=False,
        key="jai_cursive"
    )


    if cursive_jai:

        st.caption(
            "Police utilisée : Borel"
        )

    else:

        st.caption(
            "Police utilisée : police par défaut"
        )


    # =========================================================
    # FOND
    # =========================================================

    background_name_jai = st.selectbox(
        "🎨 Couleur du fond des cartes",
        list(pastel_colors.keys()),
        index=0,
        key="jai_background"
    )


    background_color_jai = (
        pastel_colors[
            background_name_jai
        ]
    )


    # =========================================================
    # POLICE REPORTLAB
    # =========================================================

    jai_pdf_font = get_reportlab_font(
        cursive_jai
    )


    # =========================================================
    # IMPORT DES IMAGES
    # =========================================================

    uploaded_files = st.file_uploader(
        "Importer les images (PNG / JPG) – "
        "l’ordre définit le jeu",
        type=[
            "png",
            "jpg",
            "jpeg"
        ],
        accept_multiple_files=True,
        key="jai_files"
    )


    # =========================================================
    # GÉNÉRATION
    # =========================================================

    if uploaded_files and len(
        uploaded_files
    ) >= 1:


        # -----------------------------------------------------
        # IMAGES + NOMS
        # -----------------------------------------------------

        images = [

            (
                Image.open(
                    f
                ).convert("RGB"),

                f.name
            )

            for f in uploaded_files
        ]


        st.success(
            f"{len(images)} images importées"
        )


        # =====================================================
        # BOUTON PDF
        # =====================================================

        if st.button(
            "📄 Générer et télécharger le PDF",
            key="jai_generate"
        ):


            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                pdf_path = tmp.name


            c = canvas.Canvas(
                pdf_path,
                pagesize=A4
            )


            page_width, page_height = A4


            # -------------------------------------------------
            # DIMENSIONS
            # -------------------------------------------------

            card_margin = (
                1.5 * cm
            )


            card_width = (
                page_width
                - 2 * card_margin
            )


            card_height = (
                page_height
                - 2 * card_margin
            )


            corner_radius = 25


            total_cards = (
                len(images) + 1
            )


            center_y = (
                page_height / 2
            )


            # =================================================
            # CARTES
            # =================================================

            for i in range(
                total_cards
            ):


                # =================================================
                # FOND PASTEL
                # =================================================

                c.setFillColorRGB(
                    background_color_jai[0] / 255,
                    background_color_jai[1] / 255,
                    background_color_jai[2] / 255
                )


                c.roundRect(
                    card_margin,
                    card_margin,
                    card_width,
                    card_height,
                    corner_radius,
                    fill=1,
                    stroke=0
                )


                # =================================================
                # BORDURE
                # =================================================

                c.setStrokeColorRGB(
                    0,
                    0,
                    0
                )


                c.setLineWidth(
                    3
                )


                c.roundRect(
                    card_margin,
                    card_margin,
                    card_width,
                    card_height,
                    corner_radius,
                    fill=0,
                    stroke=1
                )


                # =================================================
                # PREMIÈRE CARTE
                # =================================================

                if i == 0:


                    # -------------------------------------------------
                    # TITRE
                    # -------------------------------------------------

                    c.setFont(
                        "Helvetica-Bold",
                        35
                    )


                    c.drawCentredString(
                        page_width / 2,
                        page_height
                        - card_margin
                        - 2 * cm,
                        "J’ai la première carte !"
                    )


                    # -------------------------------------------------
                    # QUI A ?
                    # -------------------------------------------------

                    c.setFont(
                        "Helvetica-Bold",
                        40
                    )


                    c.drawCentredString(
                        page_width / 2,
                        center_y - 1 * cm,
                        "Qui a ?"
                    )


                    # -------------------------------------------------
                    # IMAGE
                    # -------------------------------------------------

                    img, img_name = images[0]


                    first_img_path = (
                        tempfile
                        .NamedTemporaryFile(
                            delete=False,
                            suffix=".jpg"
                        )
                        .name
                    )


                    img.save(
                        first_img_path
                    )


                    c.drawImage(
                        first_img_path,
                        card_margin + 2 * cm,
                        card_margin + 3 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    os.remove(
                        first_img_path
                    )


                    # -------------------------------------------------
                    # NOM
                    # -------------------------------------------------

                    img_name = img_name.rsplit(
                        ".",
                        1
                    )[0]


                    c.setFont(
                        jai_pdf_font,
                        22
                    )


                    c.drawCentredString(
                        page_width / 2,
                        card_margin + 2 * cm,
                        img_name
                    )


                # =================================================
                # CARTES INTERMÉDIAIRES
                # =================================================

                elif i < total_cards - 1:


                    img_have, name_have = images[
                        i - 1
                    ]


                    img_who, name_who = images[
                        i
                    ]


                    # -------------------------------------------------
                    # J'AI
                    # -------------------------------------------------

                    c.setFont(
                        "Helvetica-Bold",
                        40
                    )


                    c.drawCentredString(
                        page_width / 2,
                        page_height
                        - card_margin
                        - 1.5 * cm,
                        "J’ai"
                    )


                    # -------------------------------------------------
                    # IMAGE DU HAUT
                    # -------------------------------------------------

                    have_path = (
                        tempfile
                        .NamedTemporaryFile(
                            delete=False,
                            suffix=".jpg"
                        )
                        .name
                    )


                    img_have.save(
                        have_path
                    )


                    c.drawImage(
                        have_path,
                        card_margin + 2 * cm,
                        center_y + 1.5 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    os.remove(
                        have_path
                    )


                    # -------------------------------------------------
                    # NOM DU HAUT
                    # -------------------------------------------------

                    name_have = name_have.rsplit(
                        ".",
                        1
                    )[0]


                    c.setFont(
                        jai_pdf_font,
                        22
                    )


                    c.drawCentredString(
                        page_width / 2,
                        center_y + 0.5 * cm,
                        name_have
                    )


                    # -------------------------------------------------
                    # QUI A ?
                    # -------------------------------------------------

                    c.setFont(
                        "Helvetica-Bold",
                        40
                    )


                    c.drawCentredString(
                        page_width / 2,
                        center_y - 1.5 * cm,
                        "Qui a ?"
                    )


                    # -------------------------------------------------
                    # IMAGE DU BAS
                    # -------------------------------------------------

                    who_path = (
                        tempfile
                        .NamedTemporaryFile(
                            delete=False,
                            suffix=".jpg"
                        )
                        .name
                    )


                    img_who.save(
                        who_path
                    )


                    c.drawImage(
                        who_path,
                        card_margin + 2 * cm,
                        card_margin + 3 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    os.remove(
                        who_path
                    )


                    # -------------------------------------------------
                    # NOM DU BAS
                    # -------------------------------------------------

                    name_who = name_who.rsplit(
                        ".",
                        1
                    )[0]


                    c.setFont(
                        jai_pdf_font,
                        22
                    )


                    c.drawCentredString(
                        page_width / 2,
                        card_margin + 2 * cm,
                        name_who
                    )


                # =================================================
                # DERNIÈRE CARTE
                # =================================================

                else:


                    img_last, name_last = images[
                        -1
                    ]


                    # -------------------------------------------------
                    # J'AI
                    # -------------------------------------------------

                    c.setFont(
                        "Helvetica-Bold",
                        40
                    )


                    c.drawCentredString(
                        page_width / 2,
                        page_height
                        - card_margin
                        - 1.5 * cm,
                        "J’ai"
                    )


                    # -------------------------------------------------
                    # IMAGE
                    # -------------------------------------------------

                    last_path = (
                        tempfile
                        .NamedTemporaryFile(
                            delete=False,
                            suffix=".jpg"
                        )
                        .name
                    )


                    img_last.save(
                        last_path
                    )


                    c.drawImage(
                        last_path,
                        card_margin + 2 * cm,
                        center_y + 0.5 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    os.remove(
                        last_path
                    )


                    # -------------------------------------------------
                    # NOM
                    # -------------------------------------------------

                    name_last = name_last.rsplit(
                        ".",
                        1
                    )[0]


                    c.setFont(
                        jai_pdf_font,
                        22
                    )


                    c.drawCentredString(
                        page_width / 2,
                        center_y - 0.5 * cm,
                        name_last
                    )


                    # -------------------------------------------------
                    # TEXTE FINAL
                    # -------------------------------------------------

                    c.setFont(
                        "Helvetica-Bold",
                        35
                    )


                    c.drawCentredString(
                        page_width / 2,
                        card_margin + 2.5 * cm,
                        "… c’est la dernière carte !"
                    )


                c.showPage()


            # =====================================================
            # FINALISATION
            # =====================================================

            c.save()


            # =====================================================
            # TÉLÉCHARGEMENT
            # =====================================================

            with open(
                pdf_path,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Télécharger le PDF final",
                    f,
                    file_name="j_ai_qui_a_cartes_final.pdf",
                    mime="application/pdf",
                    key="jai_download"
                )


    else:

        st.info(
            "👉 Importez au moins 1 image "
            "pour générer le jeu."
        )
