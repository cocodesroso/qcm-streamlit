
import streamlit as st
import re
import xml.dom.minidom

st.set_page_config(page_title="Générateur de QCM Pronote", layout="wide")
st.title("🧪 Générateur de QCM XML - Pronote")

# Entrées utilisateur
titre_qcm = st.text_input("📌 Nom du QCM")
niveau = st.selectbox("📘 Niveau", ["5EME", "4EME", "3EME"])
texte_qcm = st.text_area("📝 Collez vos questions ici :", height=300, placeholder="Ex :\nQ: Exemple ? | A: Bonne réponse* | Mauvaise réponse")

# Fonction de parsing
def parse_questions(text):
    questions = []
    lignes = text.strip().split("\n")
    for ligne in lignes:
        if not ligne.strip():
            continue
        if not ligne.startswith("Q:"):
            st.warning(f"Ligne invalide : {ligne}")
            return []
        try:
            question_part, reponses_part = ligne.split("| A:", 1)
            question = question_part.replace("Q:", "").strip()
            reponses_raw = [r.strip() for r in reponses_part.strip().split("|")]
            reponses = []
            bonnes_reponses = []
            for r in reponses_raw:
                if r.endswith("*"):
                    propre = r[:-1].strip()
                    bonnes_reponses.append(propre)
                    reponses.append(propre)
                else:
                    reponses.append(r.strip())
            if not bonnes_reponses:
                st.warning(f"Aucune bonne réponse détectée pour :\n{question}")
                return []
            questions.append({
                "texte": question,
                "reponses": reponses,
                "bonnes_reponses": bonnes_reponses
            })
        except Exception as e:
            st.warning(f"Erreur de parsing : {e}")
            return []
    return questions

# Affichage et génération XML
if st.button("Analyser et générer le XML"):
    if not titre_qcm or not texte_qcm:
        st.error("Veuillez remplir le nom du QCM et coller vos questions.")
    else:
        questions = parse_questions(texte_qcm)
        if questions:
            st.success(f"{len(questions)} question(s) analysée(s) avec succès ✅")
            xml_content = f'<quiz>\n  <!--{titre_qcm}-->\n  <question type="category">\n    <category>\n      <text><![CDATA[<infos><name>{titre_qcm}</name><answernumbering>123</answernumbering><niveau>{niveau}</niveau><matiere>TECHNOLOGIE</matiere></infos>]]></text>\n    </category>\n  </question>'
            for i, q in enumerate(questions, start=1):
                xml_content += f'''\n  <question type="multichoice">\n    <name>\n      <text><![CDATA[Question {i}]]></text>\n    </name>\n    <questiontext format="html">\n      <text><![CDATA[<div style="font-family: Arial; font-size: 13px;"><strong>{q["texte"]}</strong></div>]]></text>\n    </questiontext>\n    <single>false</single>'''
                nb_bonnes = len(q["bonnes_reponses"])
                fraction_unit = 100 // nb_bonnes if nb_bonnes > 0 else 0
                for rep in q["reponses"]:
                    fraction = str(fraction_unit) if rep in q["bonnes_reponses"] else "0"
                    xml_content += f'''\n    <answer fraction="{fraction}" format="plain_text">\n      <text><![CDATA[{rep}]]></text>\n    </answer>'''
                xml_content += "\n  </question>"
            xml_content += "\n</quiz>"

            st.code(xml_content, language="xml")
            st.download_button("⬇️ Télécharger le XML", xml_content, file_name=f"{titre_qcm.replace(' ', '_')}.xml", mime="text/xml")
