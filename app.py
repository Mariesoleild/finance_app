import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Allocation d'Actifs", page_icon="📊", layout="centered")

# Titre de l'application
st.title("� Allocation d'Actifs selon l'Âge")
st.markdown("Découvrez la répartition recommandée de votre portefeuille basée sur votre âge.")

# Données d'allocation par âge
allocations = {
    25: {"Cash": 35, "Obligations": 0, "Immobilier": 0, "Actifs Alternatifs": 0, "Actions": 65},
    30: {"Cash": 10, "Obligations": 5, "Immobilier": 35, "Actifs Alternatifs": 0, "Actions": 50},
    35: {"Cash": 15, "Obligations": 5, "Immobilier": 30, "Actifs Alternatifs": 5, "Actions": 45},
    40: {"Cash": 15, "Obligations": 10, "Immobilier": 25, "Actifs Alternatifs": 10, "Actions": 40},
    45: {"Cash": 10, "Obligations": 10, "Immobilier": 25, "Actifs Alternatifs": 15, "Actions": 40},
    50: {"Cash": 10, "Obligations": 15, "Immobilier": 25, "Actifs Alternatifs": 20, "Actions": 30},
    55: {"Cash": 5, "Obligations": 25, "Immobilier": 20, "Actifs Alternatifs": 20, "Actions": 30},
    60: {"Cash": 5, "Obligations": 30, "Immobilier": 20, "Actifs Alternatifs": 20, "Actions": 25},
}

# Niveaux de risque par classe d'actifs
niveaux_risque = {
    "Cash": "Très Faible",
    "Obligations": "Faible",
    "Immobilier": "Moyen",
    "Actifs Alternatifs": "Moyen",
    "Actions": "Élevé"
}

# Entrée de l'âge
st.subheader("👤 Entrez votre âge")
age = st.slider("Âge", min_value=18, max_value=80, value=30)

# Déterminer la tranche d'âge appropriée
def get_age_bracket(age):
    if age < 28:
        return 25
    elif age < 33:
        return 30
    elif age < 38:
        return 35
    elif age < 43:
        return 40
    elif age < 48:
        return 45
    elif age < 53:
        return 50
    elif age < 58:
        return 55
    else:
        return 60

tranche = get_age_bracket(age)
allocation = allocations[tranche]

# Afficher la tranche d'âge
if tranche == 60:
    st.info(f"📌 Tranche d'âge : **60 ans et plus**")
else:
    st.info(f"📌 Tranche d'âge : **environ {tranche} ans**")

# Créer le graphique en camembert
st.subheader("🥧 Votre Allocation Recommandée")

# Préparer les données pour le graphique
df = pd.DataFrame({
    "Classe d'Actifs": list(allocation.keys()),
    "Pourcentage": list(allocation.values()),
    "Niveau de Risque": [niveaux_risque[k] for k in allocation.keys()]
})

# Filtrer les actifs avec 0%
df = df[df["Pourcentage"] > 0]

# Couleurs personnalisées
colors = {
    "Cash": "#2ecc71",           # Vert
    "Obligations": "#3498db",    # Bleu
    "Immobilier": "#9b59b6",     # Violet
    "Actifs Alternatifs": "#f39c12",  # Orange
    "Actions": "#e74c3c"         # Rouge
}

fig = px.pie(
    df, 
    values="Pourcentage", 
    names="Classe d'Actifs",
    color="Classe d'Actifs",
    color_discrete_map=colors,
    hole=0.4
)

fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    margin=dict(t=20, b=20, l=20, r=20)
)

st.plotly_chart(fig, use_container_width=True)

# Tableau détaillé
st.subheader("📋 Détail de l'Allocation")

# Recréer df avec toutes les données pour le tableau
df_table = pd.DataFrame({
    "Classe d'Actifs": list(allocation.keys()),
    "Pourcentage": [f"{v}%" for v in allocation.values()],
    "Niveau de Risque": [niveaux_risque[k] for k in allocation.keys()]
})

st.dataframe(df_table, use_container_width=True, hide_index=True)

# Note explicative
st.markdown("---")
st.caption("""
💡 **Note** : Ces allocations sont des recommandations générales basées sur l'âge. 
Votre situation personnelle (tolérance au risque, objectifs, situation financière) 
peut nécessiter une allocation différente. Consultez un conseiller financier pour 
des recommandations personnalisées.
""")
