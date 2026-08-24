import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import tempfile
import os
from reportlab.lib.units import cm


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
# ONGLET 0 : À PROPOS
# =============================================================

with tab0:

    st.header("ℹ️ À propos du projet")

    st.markdown("""
Ce projet est né d’un besoin personnel.

👉 Il a été conçu pour ma fiancée, institutrice en maternelle,  
afin de lui permettre de créer facilement des supports ludiques et pédagogiques utilisés dans l'apprentissage du lexique.

🎯 Objectif :
- Faciliter l’apprentissage du lexique chez les jeunes enfants
- Transformer des images en jeux éducatifs (dominos, “J’ai… qui a ?”)
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
        "Générateur de dominos - Fond blanc + PDF"
    )

    uploaded_files = st.file_uploader(
        "Importe tes images",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        key="domino_files"
    )

    # ---------------------------------------------------------
    # CHOIX DE LA POLICE
    # ---------------------------------------------------------

    cursive = st.checkbox(
        "✍️ Police cursive",
        value=False,
        key="domino_cursive"
    )

    if cursive:
        st.caption(
            "Police utilisée : Borel"
        )
    else:
        st.caption(
            "Police utilisée : police par défaut"
        )


    # =========================================================
    # CHEMIN DE LA POLICE BOREL
    # =========================================================

    borel_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Borel.ttf"
    )


    # =========================================================
    # FONCTION POUR CHOISIR LA POLICE
    # =========================================================

    def get_domino_font():

        # -----------------------------------------------------
        # POLICE BOREL
        # -----------------------------------------------------

        if cursive:

            if not os.path.exists(borel_path):

                st.error(
                    "❌ La police Borel est introuvable.\n\n"
                    "Ajoute le fichier `Borel.ttf` "
                    "dans le même dossier que ton fichier Python "
                    "et dans ton dépôt Git."
                )

                st.stop()

            return ImageFont.truetype(borel_path)

        # -----------------------------------------------------
        # POLICE PAR DÉFAUT
        # -----------------------------------------------------

        # Sous Windows, Arial est généralement disponible.
        arial_path = "C:/Windows/Fonts/arial.ttf"

        if os.path.exists(arial_path):

            return ImageFont.truetype(arial_path)

        # Fallback pour Streamlit Cloud / Linux
        # DejaVu Sans est généralement disponible.
        try:

            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                
            )

        except:

            # Dernier recours : police PIL par défaut
            return ImageFont.load_default()


    # =========================================================
    # CRÉATION D'UN DOMINO
    # =========================================================

    def create_domino(
        img1,
        img2,
        name1,
        name2,
        size=(400, 700)
    ):

        """
        Crée un domino avec :

        - image 1
        - nom de l'image 1
        - image 2
        - nom de l'image 2
        """

        image_width = size[0]

        image_height = 280

        text_height = 70

        # -----------------------------------------------------
        # FOND BLANC
        # -----------------------------------------------------

        domino = Image.new(
            "RGB",
            size,
            "white"
        )

        draw = ImageDraw.Draw(domino)

        # -----------------------------------------------------
        # POLICE
        # -----------------------------------------------------

        font = get_domino_font()

        # -----------------------------------------------------
        # FONCTION POUR PLACER UNE IMAGE
        # -----------------------------------------------------

        def paste_with_white_background(
            base,
            img,
            position,
            img_size
        ):

            img = img.copy()

            # Conserver les proportions
            img.thumbnail(img_size)

            # Centrer l'image
            x = (
                position[0]
                + (img_size[0] - img.width) // 2
            )

            y = (
                position[1]
                + (img_size[1] - img.height) // 2
            )

            # Gestion de la transparence
            if img.mode in ("RGBA", "LA") or (
                img.mode == "P"
                and "transparency" in img.info
            ):

                alpha = img.convert(
                    "RGBA"
                ).split()[-1]

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


        # -----------------------------------------------------
        # NETTOYAGE DES NOMS
        # -----------------------------------------------------

        name1 = name1.rsplit(
            ".",
            1
        )[0]

        name2 = name2.rsplit(
            ".",
            1
        )[0]


        # -----------------------------------------------------
        # PREMIÈRE IMAGE
        # -----------------------------------------------------

        paste_with_white_background(
            domino,
            img1,
            (0, 0),
            (
                image_width,
                image_height
            )
        )


        # -----------------------------------------------------
        # NOM DE LA PREMIÈRE IMAGE
        # -----------------------------------------------------

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


        # -----------------------------------------------------
        # DEUXIÈME IMAGE
        # -----------------------------------------------------

        second_y = (
            image_height
            + text_height
        )

        paste_with_white_background(
            domino,
            img2,
            (0, second_y),
            (
                image_width,
                image_height
            )
        )


        # -----------------------------------------------------
        # NOM DE LA DEUXIÈME IMAGE
        # -----------------------------------------------------

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


        # -----------------------------------------------------
        # LIGNE CENTRALE EN PETITS POINTS
        # -----------------------------------------------------

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


        # -----------------------------------------------------
        # BORDURE
        # -----------------------------------------------------

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


    # =========================================================
    # GÉNÉRATION DES DOMINOS
    # =========================================================

    if uploaded_files and len(uploaded_files) >= 2:

        # -----------------------------------------------------
        # IMPORT DES IMAGES + NOMS
        # -----------------------------------------------------

        images = [
            (
                Image.open(f).convert("RGBA"),
                f.name
            )
            for f in uploaded_files
        ]


        # -----------------------------------------------------
        # MÉLANGE ALÉATOIRE
        # -----------------------------------------------------

        random.shuffle(images)


        # -----------------------------------------------------
        # CRÉATION DES COUPLES
        # -----------------------------------------------------

        dominos = []

        n = len(images)

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


        # -----------------------------------------------------
        # CRÉATION DE CHAQUE PAGE
        # -----------------------------------------------------

        for domino_pair in dominos:

            img1, img2, name1, name2 = domino_pair

            domino_img = create_domino(
                img1,
                img2,
                name1,
                name2
            )

            img_reader = ImageReader(
                domino_img
            )

            img_w, img_h = domino_img.size


            # -------------------------------------------------
            # DIMENSIONNEMENT DANS LA PAGE A4
            # -------------------------------------------------

            scale = min(
                width / img_w * 0.8,
                height / img_h * 0.8
            )

            new_w = img_w * scale

            new_h = img_h * scale


            # Centrage
            x = (
                width - new_w
            ) / 2

            y = (
                height - new_h
            ) / 2


            # -------------------------------------------------
            # DESSIN DU DOMINO
            # -------------------------------------------------

            c.drawImage(
                img_reader,
                x,
                y,
                width=new_w,
                height=new_h
            )

            c.showPage()


        # -----------------------------------------------------
        # FINALISATION PDF
        # -----------------------------------------------------

        c.save()

        pdf_buffer.seek(0)


        # =====================================================
        # BOUTON PDF
        # =====================================================

        st.download_button(
            label="📄 Télécharger tous les dominos en PDF",
            data=pdf_buffer,
            file_name="dominos.pdf",
            mime="application/pdf"
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
        ) in enumerate(dominos):

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
        "« J’ai… qui a ? » (images)"
    )


    uploaded_files = st.file_uploader(
        "Importer les images (PNG / JPG) – "
        "l’ordre définit le jeu",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="jai_files"
    )


    if uploaded_files and len(uploaded_files) >= 1:

        images = [
            Image.open(f).convert("RGB")
            for f in uploaded_files
        ]

        st.success(
            f"{len(images)} images importées"
        )


        if st.button(
            "📄 Générer et télécharger le PDF"
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


            card_margin = 1.5 * cm

            card_width = (
                page_width
                - 2 * card_margin
            )

            card_height = (
                page_height
                - 2 * card_margin
            )

            corner_radius = 25

            total_cards = len(images) + 1


            for i in range(total_cards):

                c.setLineWidth(3)

                c.roundRect(
                    card_margin,
                    card_margin,
                    card_width,
                    card_height,
                    corner_radius
                )


                center_y = (
                    page_height / 2
                )


                # =================================================
                # PREMIÈRE CARTE
                # =================================================

                if i == 0:

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


                    c.setFont(
                        "Helvetica-Bold",
                        40
                    )

                    c.drawCentredString(
                        page_width / 2,
                        center_y - 1 * cm,
                        "Qui a ?"
                    )


                    first_img_path = (
                        tempfile
                        .NamedTemporaryFile(
                            delete=False,
                            suffix=".jpg"
                        )
                        .name
                    )


                    images[0].save(
                        first_img_path
                    )


                    c.drawImage(
                        first_img_path,
                        card_margin + 2 * cm,
                        card_margin + 2 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    os.remove(
                        first_img_path
                    )


                # =================================================
                # CARTES INTERMÉDIAIRES
                # =================================================

                elif i < total_cards - 1:

                    img_have = images[i - 1]

                    img_who = images[i]


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
                        center_y + 1 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    c.setFont(
                        "Helvetica-Bold",
                        40
                    )


                    c.drawCentredString(
                        page_width / 2,
                        center_y - 1 * cm,
                        "Qui a ?"
                    )


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
                        card_margin + 2 * cm,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    os.remove(
                        have_path
                    )

                    os.remove(
                        who_path
                    )


                # =================================================
                # DERNIÈRE CARTE
                # =================================================

                else:

                    img_last = images[-1]


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
                        center_y,
                        card_width - 4 * cm,
                        card_height / 3,
                        preserveAspectRatio=True
                    )


                    c.setFont(
                        "Helvetica-Bold",
                        35
                    )


                    c.drawCentredString(
                        page_width / 2,
                        card_margin + 2.5 * cm,
                        "… c’est la dernière carte !"
                    )


                    os.remove(
                        last_path
                    )


                c.showPage()


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
                    mime="application/pdf"
                )


    else:

        st.info(
            "👉 Importez au moins 1 image "
            "pour générer le jeu."
        )
