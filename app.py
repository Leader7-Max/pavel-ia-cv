"""Pavel IA CV — générateur de CV et lettres de motivation sur-mesure."""

import re
from collections import Counter

import streamlit as st
from fpdf import FPDF
from google import genai
from google.genai import types

# ─────────────────────────────────────────────────────────────
# Configuration générale
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pavel IA CV",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

TONES = [
    "Professionnel et formel (classique)",
    "Dynamique et moderne (impactant)",
    "Reconversion / profil atypique",
    "Audacieux et créatif",
]

LENGTHS = {
    "cv": {
        "Concise": "tient sur une page, 3 puces maximum par expérience",
        "Standard": "tient sur une page, 3 à 4 puces par expérience",
        "Détaillée": "peut occuper deux pages, 4 à 6 puces par expérience",
    },
    "lettre": {
        "Concise": "200 à 250 mots",
        "Standard": "300 à 350 mots",
        "Détaillée": "400 à 450 mots",
    },
}

# ─────────────────────────────────────────────────────────────
# LOGO PAVEL IA CV — VERSION BRILLANTE
# ─────────────────────────────────────────────────────────────
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
  <path d="M-10 8 L28 -12 L76 36 L38 76 Z"
        fill="url(#pavelShine)"
        opacity="0.55"/>
</g>

<path d="M18 12h18l10 10v26a3 3 0 0 1-3 3H18a3 3 0 0 1-3-3V15a3 3 0 0 1 3-3z"
      fill="#FFFFFF"/>

<path d="M36 12v7a3 3 0 0 0 3 3h7z"
      fill="#B7D6D6"/>

<rect x="21" y="27" width="16" height="3" rx="1.5" fill="#0E6B6B"/>
<rect x="21" y="34" width="11" height="3" rx="1.5" fill="#9CC3C3"/>

<circle cx="44" cy="44" r="10"
        fill="url(#pavelGold)"
        stroke="#0E6B6B"
        stroke-width="3"/>

<path d="M39.5 44.5l3.3 3.3 6-6.6"
      fill="none"
      stroke="#12272B"
      stroke-width="2.8"
      stroke-linecap="round"
      stroke-linejoin="round"/>

<circle cx="22" cy="16" r="1.3"
        fill="#FFFFFF"
        opacity="0.9"/>

<circle cx="50" cy="14" r="1"
        fill="#FFE8A8"
        opacity="0.9"/>

<circle cx="53" cy="36" r="0.8"
        fill="#FFFFFF"
        opacity="0.7"/>
</svg>"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=DM+Sans:wght@400;500;700&display=swap');

:root {
  --ink: #12272B;
  --teal: #0E6B6B;
  --amber: #F2A93B;
  --paper: #F5F7F8;
  --line: #DCE3E5;
  --muted: #5B6B70;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--ink);
}

.stApp {
  background: var(--paper);
}

#MainMenu, footer {
  visibility: hidden;
}

header[data-testid="stHeader"] {
  background: transparent;
}

.block-container {
  max-width: 820px;
  padding-top: 2.2rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4, h5 {
  font-family: 'Bricolage Grotesque', sans-serif;
  letter-spacing: -0.01em;
  color: var(--ink);
}

/* En-tête de marque */
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

/* Formulaire */
[data-testid="stForm"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.5rem 1.5rem 1.1rem;
}

[data-testid="stForm"] h5 {
  margin: .4rem 0 .2rem;
  font-size: 1.05rem;
}

.stTextInput input,
.stTextArea textarea {
  border-radius: 10px;
}

[data-baseweb="select"] > div {
  border-radius: 10px;
}

/* Boutons */
.stFormSubmitButton button,
.stButton button,
.stDownloadButton button {
  border-radius: 10px;
  font-weight: 700;
  padding: .65rem 1rem;
}

.stFormSubmitButton button {
  width: 100%;
}

/* Barre latérale */
[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid var(--line);
}

.tip {
  color: var(--muted);
  font-size: .92rem;
  line-height: 1.5;
}

/* Résultat */
.result-meta {
  color: var(--muted);
  font-size: .92rem;
  margin: -.2rem 0 .6rem;
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────────────────────
def get_secret_key() -> str:
    """Lit la clé API dans les secrets Streamlit sans planter si absents."""
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def slugify(value: str) -> str:
    return re.sub(
        r"[^\w-]+",
        "_",
        value.strip(),
        flags=re.UNICODE,
    ).strip("_") or "document"


def clean_output(text: str) -> str:
    """Retire le Markdown résiduel pour obtenir un texte brut réutilisable."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[\*\-•]\s+", "• ", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def friendly_error(err: Exception) -> str:
    msg = str(err).lower()

    if (
        "api key" in msg
        or "api_key" in msg
        or "permission" in msg
        or "401" in msg
        or "403" in msg
    ):
        return "La clé API est refusée. Vérifiez qu'elle est correcte et active."

    if "429" in msg or "quota" in msg or "rate" in msg:
        return "La limite d'utilisation de l'API est atteinte. Réessayez dans une minute."

    if "503" in msg or "overloaded" in msg or "unavailable" in msg:
        return "Le service de rédaction est saturé. Réessayez dans quelques instants."

    return f"La génération a échoué. Détail technique : {err}"


STOPWORDS = set(
    """
    dans pour avec vous nous votre notre vos nos être sera seront cette cettes entre leurs leur
    aussi ainsi alors plus moins comme chez sous sont elle elles ils dont mais donc car
    poste offre mission missions profil candidat entreprise société travail équipe
    recherchons rejoindre rejoignez avoir faire tous toutes tout toute très bien
    """.split()
)


def extract_keywords(text: str, top: int = 20) -> list[str]:
    words = re.findall(
        r"[a-zà-ÿœ][a-zà-ÿœ'-]{4,}",
        text.lower(),
    )
    counts = Counter(
        w for w in words
        if w not in STOPWORDS
    )
    return [w for w, _ in counts.most_common(top)]


def keyword_match(offer: str, document: str):
    keywords = extract_keywords(offer)

    if not keywords:
        return None

    doc = document.lower()
    missing = [
        k for k in keywords
        if k not in doc
    ]

    return len(keywords) - len(missing), len(keywords), missing


# ─────────────────────────────────────────────────────────────
# Génération IA
# ─────────────────────────────────────────────────────────────
def build_prompts(p: dict) -> tuple[str, str]:
    is_cv = p["doc_type"].startswith("CV")
    kind = "cv" if is_cv else "lettre"
    length = LENGTHS[kind][p["length"]]

    if is_cv:
        structure = (
            "STRUCTURE DU CV (chaque titre de section en MAJUSCULES, seul sur sa ligne) :\n"
            "- Ligne 1 : nom et prénom. Ligne 2 : intitulé du poste visé.\n"
            "- PROFIL : 3 lignes maximum.\n"
            "- COMPÉTENCES CLÉS : liste courte, orientée vers l'offre.\n"
            "- EXPÉRIENCES PROFESSIONNELLES : pour chaque expérience, une ligne "
            "« Poste, Structure (période) » puis des puces commençant par un verbe d'action "
            "et, si possible, un résultat.\n"
            "- FORMATION\n"
            "- LANGUES ET ATOUTS (si pertinent)\n"
            f"Le CV {length}."
        )
    else:
        structure = (
            "STRUCTURE DE LA LETTRE :\n"
            "- Coordonnées du candidat (entre crochets si inconnues), lieu et date, "
            "destinataire.\n"
            "- Objet.\n"
            "- Formule d'appel.\n"
            "- 3 ou 4 paragraphes : accroche personnalisée, valeur ajoutée du candidat "
            "avec des exemples concrets, motivation pour l'entreprise, ouverture vers un entretien.\n"
            "- Formule de politesse et signature.\n"
            f"La lettre fait {length}."
        )

    system = (
        "Tu es un expert en recrutement et en rédaction de CV et de lettres de motivation, "
        "capable d'écrire des documents optimisés pour les logiciels de tri (ATS) tout en "
        "restant agréables à lire pour un recruteur.\n"
        "RÈGLES ABSOLUES :\n"
        "1. N'invente JAMAIS de fait : employeur, diplôme, date, chiffre ou outil absent des "
        "informations fournies. Si une information utile manque, insère un champ entre "
        "crochets, par exemple [ville] ou [chiffre à préciser].\n"
        "2. Écris en texte brut : pas de Markdown, pas de titres avec #, pas de gras. "
        "Utilise « • » pour les puces.\n"
        "3. Style clair, concret, sans formules creuses ni superlatifs inutiles.\n"
        f"4. Rédige en {p['language']}.\n"
        "5. Réponds uniquement avec le document final, sans commentaire avant ni après."
    )

    offer = (
        p["offer"]
        or "Aucune offre fournie. Base-toi sur les standards du poste visé."
    )

    prompt = f"""Rédige : {p['doc_type']}

INFORMATIONS SUR LE CANDIDAT
- Nom et prénom : {p['name']}
- Poste visé : {p['job']}
- Entreprise ciblée : {p['company'] or 'Non précisée'}
- Parcours et compétences : {p['background']}
- Ton souhaité : {p['tone']}
- Consignes particulières : {p['notes'] or 'Aucune'}

OFFRE D'EMPLOI DE RÉFÉRENCE
{offer}

{structure}

Si une offre est fournie, reprends naturellement ses mots-clés et compétences attendues, \
uniquement lorsqu'ils correspondent au parcours du candidat."""

    return system, prompt


def stream_document(
    api_key: str,
    system: str,
    prompt: str,
    temperature: float,
):
    """Génère le texte en flux continu, avec un modèle de secours si le premier échoue."""
    client = genai.Client(api_key=api_key)
    last_error = None

    for model in MODELS:
        started = False

        try:
            stream = client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                ),
            )

            for chunk in stream:
                if chunk.text:
                    started = True
                    yield chunk.text

            return

        except Exception as err:
            if started:
                raise

            last_error = err

    raise last_error


# ─────────────────────────────────────────────────────────────
# Export PDF
# ─────────────────────────────────────────────────────────────
INK = (18, 
