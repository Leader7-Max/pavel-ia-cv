import re
from collections import Counter

import streamlit as st
from fpdf import FPDF
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Pavel IA CV",
    page_icon="📄",
    layout="wide",
)

MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

TONES = [
    "Professionnel",
    "Dynamique",
    "Sobre",
    "Chaleureux",
    "Direct",
]

LENGTHS = {
    "Court": "court et très synthétique",
    "Standard": "standard, clair et équilibré",
    "Détaillé": "détaillé, riche mais sans répétitions inutiles",
}

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="PAVEL IA CV">
<defs>
  <linearGradient id="pavelBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#18A0A0"/>
    <stop offset="50%" stop-color="#0E6B6B"/>
    <stop offset="100%" stop-color="#075052"/>
  </linearGradient>
  <linearGradient id="pavelGold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFE8A8"/>
    <stop offset="45%" stop-color="#F2A93B"/>
    <stop offset="100%" stop-color="#C77B13"/>
  </linearGradient>
  <linearGradient id="pavelShine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="45%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="55%" stop-color="#FFFFFF" stop-opacity="0.65"/>
    <stop offset="65%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="pavelClip">
    <rect width="64" height="64" rx="16"/>
  </clipPath>
</defs>
<rect width="64" height="64" rx="16" fill="url(#pavelBg)"/>
<g clip-path="url(#pavelClip)">
  <path d="M-10 8 L28 -12 L76 36 L38 76 Z" fill="url(#pavelShine)" opacity="0.55"/>
</g>
<path d="M18 12h18l10 10v26a3 3 0 0 1-3 3H18a3 3 0 0 1-3-3V15a3 3 0 0 1 3-3z" fill="#FFFFFF"/>
<path d="M36 12v7a3 3 0 0 0 3 3h7z" fill="#B7D6D6"/>
<rect x="21" y="27" width="16" height="3" rx="1.5" fill="#0E6B6B"/>
<rect x="21" y="34" width="11" height="3" rx="1.5" fill="#9CC3C3"/>
<circle cx="44" cy="44" r="10" fill="url(#pavelGold)" stroke="#0E6B6B" stroke-width="3"/>
<path d="M39.5 44.5l3.3 3.3 6-6.6" fill="none" stroke="#12272B" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="22" cy="16" r="1.3" fill="#FFFFFF" opacity="0.9"/>
<circle cx="50" cy="14" r="1" fill="#FFE8A8" opacity="0.9"/>
<circle cx="53" cy="36" r="0.8" fill="#FFFFFF" opacity="0.7"/>
</svg>"""

st.markdown(
    """
    <style>
    :root {
        --ink: #12272B;
        --muted: #647579;
        --teal: #0E6B6B;
        --amber: #F2A93B;
        --line: #DCE3E5;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 0 0 1.6rem;
    }

    .brand svg {
        width: 58px;
        height: 58px;
        flex: none;
    }

    .brand h1 {
        font-size: 2rem;
        line-height: 1.1;
        margin: 0;
        padding: 0;
    }

    .brand p {
        margin: .25rem 0 0;
        color: var(--muted);
        font-size: 1rem;
    }

    .step-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0 0 .6rem;
    }

    .result-box {
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: #FFFFFF;
    }

    .keyword-ok {
        color: #0E6B6B;
        font-weight: 700;
    }

    .keyword-missing {
        color: #B85C00;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="brand">{LOGO_SVG}<div><h1>PAVEL IA CV</h1>'
    "<p>Un CV ou une lettre de motivation adaptés à l'offre, prêts à télécharger.</p></div></div>",
    unsafe_allow_html=True,
)


def get_secret_key() -> str:
    key = st.secrets.get("GEMINI_API_KEY", "")
    if not key:
        key = st.secrets.get("GOOGLE_API_KEY", "")
    return key


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "document"


def clean_output(text: str) -> str:
    text = text.replace("```text", "").replace("```", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def friendly_error(exc: Exception) -> str:
    message = str(exc)

    if "API key" in message or "api_key" in message:
        return "La clé API Gemini semble absente ou invalide. Vérifie tes Secrets Streamlit."

    if "quota" in message.lower():
        return "Le quota de l'API Gemini semble avoir été atteint. Réessaie plus tard ou utilise un autre modèle."

    if "429" in message:
        return "Le service Gemini est temporairement limité. Réessaie dans quelques instants."

    return f"Une erreur est survenue : {message}"


def extract_keywords(job_offer: str) -> list[str]:
    words = re.findall(
        r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9+#.-]{2,}",
        job_offer.lower(),
    )

    stopwords = {
        "avec", "pour", "dans", "vous", "nous", "les", "des", "une",
        "sur", "aux", "est", "être", "qui", "que", "son", "ses", "par",
        "poste", "offre", "profil", "recherche", "missions", "mission",
        "ainsi", "plus", "très", "avoir", "entre", "comme", "leur",
    }

    counts = Counter(
        word for word in words
        if word not in stopwords
    )

    return [word for word, _ in counts.most_common(20)]


def keyword_match(
    document: str,
    keywords: list[str],
) -> tuple[list[str], list[str]]:
    lower = document.lower()

    found = [
        word for word in keywords
        if word in lower
    ]

    missing = [
        word for word in keywords
        if word not in lower
    ]

    return found, missing


def build_prompts(
    document_type: str,
    profile: str,
    job_offer: str,
    tone: str,
    length_label: str,
) -> tuple[str, str]:

    length = LENGTHS[length_label]

    if document_type == "CV":

        system_prompt = """Tu es un expert français en recrutement et en rédaction de CV.
Tu dois produire un CV professionnel, réaliste, clair et parfaitement adapté à l'offre.
N'invente aucune expérience, aucun diplôme, aucune compétence et aucune information personnelle.
Utilise uniquement les informations fournies par le candidat.
Optimise naturellement le vocabulaire pour l'offre d'emploi."""

        user_prompt = f"""Crée un CV {length}, avec un ton {tone.lower()}.

INFORMATIONS DU CANDIDAT :
{profile}

OFFRE D'EMPLOI :
{job_offer}

STRUCTURE SOUHAITÉE :
NOM ET PRÉNOM
Intitulé professionnel

PROFIL
...

EXPÉRIENCES PROFESSIONNELLES
...

FORMATION
...

COMPÉTENCES
...

LANGUES
...

CENTRES D'INTÉRÊT
...

Ne mets pas de commentaires sur ton travail. Retourne uniquement le contenu final du CV."""

    else:

        system_prompt = """Tu es un expert français en recrutement et en lettres de motivation.
Rédige une lettre naturelle, personnalisée et professionnelle.
N'invente aucune information.
Appuie-toi uniquement sur le profil et l'offre fournis."""

        user_prompt = f"""Rédige une lettre de motivation {length}, avec un ton {tone.lower()}.

PROFIL DU CANDIDAT :
{profile}

OFFRE D'EMPLOI :
{job_offer}

La lettre doit être directement utilisable par le candidat.
Ne mets pas de commentaires sur ton travail. Retourne uniquement la lettre finale."""

    return system_prompt, user_prompt


def stream_document(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
):
    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
    )

    response = client.models.generate_content_stream(
        model=model,
        contents=user_prompt,
        config=config,
    )

    for chunk in response:
        text = getattr(chunk, "text", None)

        if text:
            yield text


# ─────────────────────────────────────────────────────────────
# Export PDF
# ─────────────────────────────────────────────────────────────

INK = (18, 39, 43)
BODY = (38, 52, 56)
TEAL = (14, 107, 107)
AMBER = (242, 169, 59)
LINE = (220, 227, 229)

PDF_REPLACEMENTS = {
    "\u2019": "'",
    "\u2018": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u2022": "-",
    "\u00a0": " ",
    "\u202f": " ",
    "\u0153": "oe",
    "\u0152": "Oe",
    "\u20ac": "EUR",
    "\u2192": "->",
}


def pdf_safe(text: str) -> str:
    for src, dst in PDF_REPLACEMENTS.items():
        text = text.replace(src, dst)

    return text.encode(
        "latin-1",
        "replace",
    ).decode("latin-1")


def is_heading(line: str) -> bool:
    core = line.rstrip(":").strip()

    letters = [
        c for c in core
        if c.isalpha()
    ]

    return (
        bool(letters)
        and core == core.upper()
        and len(core) <= 48
        and not core.startswith("-")
    )


@st.cache_data(show_spinner=False)
def build_pdf(
    text: str,
    is_cv: bool,
) -> bytes:

    pdf = FPDF(format="A4")

    pdf.set_margins(
        20,
        18,
        20,
    )

    pdf.set_auto_page_break(
        True,
        margin=18,
    )

    pdf.add_page()

    right = pdf.w - pdf.r_margin

    header_step = 0

    for raw in text.split("\n"):

        line = pdf_safe(raw).strip()

        if not line:
            pdf.ln(3)
            continue

        if is_cv and header_step == 0:

            pdf.set_font(
                "Helvetica",
                "B",
                22,
            )

            pdf.set_text_color(*INK)

            pdf.multi_cell(
                0,
                10,
                line,
                new_x="LMARGIN",
                new_y="NEXT",
            )

            header_step = 1
            continue

        if is_cv and header_step == 1:

            header_step = 2

            if not is_heading(line):

                pdf.set_font(
                    "Helvetica",
                    "",
                    12,
                )

                pdf.set_text_color(*TEAL)

                pdf.multi_cell(
                    0,
                    7,
                    line,
                    new_x="LMARGIN",
                    new_y="NEXT",
                )

                y = pdf.get_y() + 2

                pdf.set_draw_color(*AMBER
