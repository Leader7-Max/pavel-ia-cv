import streamlit as st
from google import genai
from fpdf import FPDF
import os

# Configuration de la page
st.set_page_config(page_title="Pavel IA CV", page_icon="📝", layout="centered")

# Chargement du fichier logo.svg séparé
logo_svg = ""
if os.path.exists("logo.svg"):
    with open("logo.svg", "r", encoding="utf-8") as f:
        logo_svg = f.read()

# Header complet personnalisé avec le logo SVG séparé et les styles CSS
if logo_svg:
    st.html(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
      <div style="width: 56px; height: 56px; flex-shrink: 0;">
        {logo_svg}
      </div>
      <div>
        <h1 style="margin: 0; padding: 0; font-size: 2.2rem; color: #0E6B6B; font-weight: 700;">Pavel IA CV</h1>
        <p style="margin: 0; padding: 0; color: #555; font-size: 0.95rem;">Générateur intelligent de CV & Lettres de motivation sur-mesure</p>
      </div>
    </div>
    """)
else:
    st.title("📝 Pavel IA CV")
    st.caption("Générateur intelligent de CV & Lettres de motivation sur-mesure")

# Récupération automatique de la clé API depuis Secrets ou Sidebar
api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input(
        "Clé API Gemini", 
        type="password", 
        help="Obtiens ta clé gratuite sur https://aistudio.google.com/"
    )

# Formulaire utilisateur
with st.form("user_input_form"):
    doc_type = st.radio("Type de document", ["Lettre de motivation", "CV (Résumé d'expérience)"])
    
    col1, col2 = st.columns(2)
    with col1:
        nom_prenom = st.text_input("Nom & Prénom")
        poste_vise = st.text_input("Poste visé / Intitulé du job")
    with col2:
        entreprise = st.text_input("Nom de l'entreprise (optionnel pour CV)")
        style_ton = st.selectbox(
            "Style & Ton de rédaction",
            [
                "Professionnel & Formel (Classique)",
                "Dynamique & Moderne (Impactant)",
                "Focus Reconversion / Profil Atypique",
                "Audacieux & Créatif"
            ]
        )

    parcours = st.text_area(
        "Ton parcours & Compétences clés", 
        placeholder="Ex: 3 ans en gestion de projet, maîtrise Excel, bon relationnel, autonomie..."
    )
    
    offre_emploi = st.text_area(
        "Offre d'emploi / Fiche de poste (Optionnel)", 
        placeholder="Colle ici le texte ou les exigences de l'annonce pour adapter le document aux mots-clés de l'entreprise..."
    )
    
    idees_cles = st.text_area(
        "Idées clés / Consignes particulières", 
        placeholder="Ex: Insister sur ma disponibilité immédiate, mettre en avant la maîtrise des outils informatiques..."
    )
    
    submitted = st.form_submit_button("🚀 Générer le document sur-mesure")

# Fonction d'export PDF
def generate_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    clean_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 8, txt=line)
    
    return pdf.output(dest='S').encode('latin-1')

# Traitement du formulaire
if submitted:
    if not api_key:
        st.error("Aucune clé API trouvée. Veuillez ajouter GEMINI_API_KEY dans les Secrets Streamlit ou dans la barre latérale.")
    elif not nom_prenom or not poste_vise or not parcours:
        st.warning("Veuillez remplir au moins votre nom, le poste visé et votre parcours.")
    else:
        with st.spinner("Analyse et rédaction sur-mesure en cours par l'IA..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                Tu es un expert mondial en recrutement, rédaction de CV et lettres de motivation.
                Rédige un(e) {doc_type} d'exception, optimisé(e) pour passer les filtres de recrutement (ATS).

                INFORMATIONS CANDIDAT :
                - Nom et Prénom : {nom_prenom}
                - Poste visé : {poste_vise}
                - Entreprise cible : {entreprise if entreprise else "Non spécifié"}
                - Parcours & Compétences : {parcours}
                - Ton & Style souhaité : {style_ton}
                - Consignes particulières : {idees_cles if idees_cles else "Aucune"}

                OFFRE D'EMPLOI DE RÉFÉRENCE :
                {offre_emploi if offre_emploi else "Aucune offre collée. Base-toi sur les standards du poste visé."}

                CONSIGNES STRICTES DE RÉDACTION :
                - Adopte rigoureusement le style : {style_ton}.
                - Si une offre d'emploi est fournie, réutilise ses termes et compétences clés de manière naturelle.
                - Rédige un texte clair, structuré, percutant et sans fioritures inutiles.
                - Pas de balises Markdown complexes (évite les titres #), écris un texte brut bien aéré et directement réutilisable.
                """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
                resultat = response.text

                st.success("✨ Votre document sur-mesure a été généré !")
                st.subheader("Aperçu du résultat :")
                st.text_area("Résultat", value=resultat, height=400)

                # Export PDF
                pdf_bytes = generate_pdf(resultat)
                st.download_button(
                    label="📥 Télécharger votre PDF",
                    data=pdf_bytes,
                    file_name=f"{doc_type.replace(' ', '_')}_{nom_prenom.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la génération : {e}")
