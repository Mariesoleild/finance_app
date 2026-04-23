import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

# --- Configuration de la page ---
st.set_page_config(page_title="Finances Personnelles", page_icon="", layout="wide")

# Paramètres esthétiques globaux via CSS
st.markdown("""
<style>
    /* Importer une police élégante */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    /* Fond global chaleureux (Chic & Cozy) */
    .stApp {
        background: linear-gradient(160deg, #FDFBF7 0%, #F8F4ED 50%, #F2EFE9 100%);
    }
    
    /* Barre latérale — Sable & Lin */
    [data-testid="stSidebar"] {
        background: #F2EFE9;
        border-right: 1px solid #E6DFD3;
    }
    
    /* Boutons de Navigation (Onglets de section) — Vert Plus Foncé */
    [data-testid="stSidebar"] .stButton>button {
        background: #8FA578; /* Vert sauge plus soutenu */
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 5px;
        box-shadow: 0 2px 4px rgba(143, 165, 120, 0.2);
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #7A9466; /* Encore plus foncé au survol */
        color: white;
        transform: translateX(3px);
        box-shadow: 0 4px 8px rgba(143, 165, 120, 0.3);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: #5C6275;
    }
    
    /* Cartes indicateurs (Metrics) — Chaleureuses */
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 15px rgba(138, 131, 116, 0.05);
        border: 1px solid #E6DFD3;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(138, 131, 116, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3D405B;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #9A8C73; /* Sable profond */
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Boutons — Sable Doré (Action Chaleureuse) */
    .stButton>button {
        background: linear-gradient(135deg, #D4A373 0%, #B88E62 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.55rem 1.2rem;
        border: none;
        box-shadow: 0 4px 12px rgba(212, 163, 115, 0.25);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #B88E62 0%, #A07B55 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(212, 163, 115, 0.35);
        color: white;
    }
    
    /* Titres — Gris Bleu Profond (pour le contraste) */
    h1, h2, h3 {
        color: #3D405B;
        letter-spacing: -0.01em;
    }
    
    /* Progress bar — Sable vers Sauge */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #D4A373, #A3B18A) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #9A8C73;
    }
    .stTabs [aria-selected="true"] {
        color: #3D405B;
        border-bottom-color: #D4A373 !important;
    }

    /* Onboarding Cards — Style Sable & Sauge */
    .onboarding-card {
        background: white;
        border-left: 4px solid #D4A373;
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #E6DFD3;
        color: #3D405B;
    }
    .onboarding-card h4 {
        color: #3D405B;
        margin-bottom: 6px;
    }
    .onboarding-card p {
        color: #5C6275;
    }

    /* Classes de Section Color-codées */
    .section-revenus { border-left: 3px solid #E9C46A; padding-left: 16px; margin-bottom: 25px; }
    .section-revenus h3 { color: #B08D3E !important; }
    
    .section-fixes { border-left: 3px solid #98A6BB; padding-left: 16px; margin-bottom: 25px; }
    .section-fixes h3 { color: #6C7A8F !important; }
    
    .section-variables { border-left: 3px solid #D4A373; padding-left: 16px; margin-bottom: 25px; }
    .section-variables h3 { color: #A87D52 !important; }
    
    .section-epargne { border-left: 3px solid #A3B18A; padding-left: 16px; margin-bottom: 25px; }
    .section-epargne h3 { color: #7A8D63 !important; }
</style>
</style>
""", unsafe_allow_html=True)

# --- Fonction utilitaire de formatage ---
def format_currency(value):
    """Formate un nombre en format monétaire lisible (ex: 1 800,00 $)"""
    return "{:,.2f} $".format(value).replace(",", "X").replace(".", ",").replace("X", " ")

# --- Initialisation du Session State ---
import json
import os

BUDGET_FILE = "budget_data.json"

def sauvegarder_donnees_budget():
    cles_a_sauvegarder = [
        "revenus_mensuels", "loyer_mensuel", "telephone_internet", "transport_mensuel",
        "assurances_mensuel", "electricite_mensuel", "nourriture_mensuel", "loisirs_mensuel",
        "celi_mensuel", "celiapp_mensuel", "reer_mensuel", "taxes_annuelles",
        "permis_annuels", "entretien_annuel", "autres_annuels_val",
        "custom_fixed_categories", "custom_variable_categories", 
        "custom_savings_categories", "custom_annual_categories",
        "budget_historique"
    ]
    donnees = {cle: st.session_state[cle] for cle in cles_a_sauvegarder if cle in st.session_state}
    with open(BUDGET_FILE, "w") as f:
        json.dump(donnees, f)

def charger_donnees_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            donnees = json.load(f)
            for cle, valeur in donnees.items():
                st.session_state[cle] = valeur

# --- Initialisation du Session State avec SCÉNARIO RÉALISTE (DÉMO) ---
if 'budget_initialise' not in st.session_state:
    # 1. Revenus et Budget Actuel (Avril 2026)
    st.session_state.revenus_mensuels = 4050.0
    st.session_state.loyer_mensuel = 1450.0
    st.session_state.telephone_internet = 110.0
    st.session_state.transport_mensuel = 320.0
    st.session_state.assurances_mensuel = 165.0
    st.session_state.electricite_mensuel = 78.0
    st.session_state.nourriture_mensuel = 520.0
    st.session_state.loisirs_mensuel = 260.0
    
    # Dépenses variables personnalisées
    st.session_state.custom_variable_categories = [
        {"nom": "Vêtements / Magasinage", "montant": 140.0},
        {"nom": "Santé / Pharmacie", "montant": 60.0},
        {"nom": "Café / Restaurants", "montant": 130.0}
    ]
    st.session_state.custom_fixed_categories = []
    
    # 2. Épargne
    st.session_state.celi_mensuel = 250.0
    st.session_state.celiapp_mensuel = 300.0
    st.session_state.reer_mensuel = 150.0
    st.session_state.custom_savings_categories = [
        {"nom": "Fonds d'urgence", "montant": 100.0}
    ]
    
    # 3. Prévoyance Annuelle
    st.session_state.taxes_annuelles = 0.0
    st.session_state.permis_annuels = 320.0
    st.session_state.entretien_annuel = 950.0
    st.session_state.autres_annuels_val = 0.0
    st.session_state.custom_annual_categories = [
        {"nom": "Cadeaux / Fêtes", "montant": 700.0},
        {"nom": "Vacances / Voyage", "montant": 1800.0},
        {"nom": "Renouvellements / Abonnements", "montant": 250.0},
        {"nom": "Autres frais annuels", "montant": 450.0}
    ]

    # 4. Catégories et Listes
    st.session_state.categories_list = ["Nourriture", "Transport", "Loyer", "Loisirs", "Santé", "Vêtements", "Factures", "Restaurants", "Abonnements", "Autre"]
    st.session_state.monthly_targets = {}
    
    # 5. Historique (Archives pour montrer l'évolution)
    st.session_state.budget_historique = [
        {"mois": "2026-01", "revenus": 4050.0, "depenses_fixes": 2123.0, "depenses_variables": 1350.0, "epargne": 500.0, "total_sorties": 3973.0, "restant": 77.0},
        {"mois": "2026-02", "revenus": 4050.0, "depenses_fixes": 2123.0, "depenses_variables": 920.0, "epargne": 900.0, "total_sorties": 3943.0, "restant": 107.0},
        {"mois": "2026-03", "revenus": 4050.0, "depenses_fixes": 2123.0, "depenses_variables": 1580.0, "epargne": 300.0, "total_sorties": 4003.0, "restant": 47.0},
        {"mois": "2026-04", "revenus": 4050.0, "depenses_fixes": 2123.0, "depenses_variables": 1110.0, "epargne": 800.0, "total_sorties": 4033.0, "restant": 17.0},
        {"mois": "2026-05", "revenus": 4050.0, "depenses_fixes": 2123.0, "depenses_variables": 1050.0, "epargne": 800.0, "total_sorties": 3973.0, "restant": 77.0}
    ]
    
    # 6. Suivi des Dépenses (Détail d'Avril 2026)
    demo_expenses = [
        {"Date": "2026-04-01", "Catégorie": "Loyer", "Description": "Virement Loyer", "Montant": 1450.0},
        {"Date": "2026-04-02", "Catégorie": "Nourriture", "Description": "Épicerie Metro", "Montant": 142.50},
        {"Date": "2026-04-03", "Catégorie": "Transport", "Description": "Essence Shell", "Montant": 68.0},
        {"Date": "2026-04-04", "Catégorie": "Restaurants", "Description": "Sushi soir", "Montant": 55.40},
        {"Date": "2026-04-05", "Catégorie": "Loisirs", "Description": "Cinéma & Popcorn", "Montant": 28.0},
        {"Date": "2026-04-07", "Catégorie": "Restaurants", "Description": "Café et muffin", "Montant": 12.75},
        {"Date": "2026-04-08", "Catégorie": "Factures", "Description": "Vidéotron - Tél/Web", "Montant": 110.0},
        {"Date": "2026-04-10", "Catégorie": "Nourriture", "Description": "Épicerie Costco", "Montant": 215.30},
        {"Date": "2026-04-12", "Catégorie": "Assurances", "Description": "Assurance Auto/Logis", "Montant": 165.0},
        {"Date": "2026-04-14", "Catégorie": "Santé", "Description": "Pharmacie Jean Coutu", "Montant": 42.15},
        {"Date": "2026-04-15", "Catégorie": "Factures", "Description": "Hydro-Québec", "Montant": 78.0},
        {"Date": "2026-04-16", "Catégorie": "Vêtements", "Description": "Achat Simons", "Montant": 140.0},
        {"Date": "2026-04-18", "Catégorie": "Restaurants", "Description": "Souper resto Italien", "Montant": 85.20},
        {"Date": "2026-04-19", "Catégorie": "Transport", "Description": "Stationnement Indigo", "Montant": 22.0},
        {"Date": "2026-04-20", "Catégorie": "Nourriture", "Description": "Épicerie IGA", "Montant": 95.40},
        {"Date": "2026-04-21", "Catégorie": "Abonnements", "Description": "Spotify / Netflix", "Montant": 32.50},
        {"Date": "2026-04-22", "Catégorie": "Restaurants", "Description": "Lunch rapide", "Montant": 18.25},
        {"Date": "2026-04-23", "Catégorie": "Loisirs", "Description": "Escalade / Gym", "Montant": 25.0},
        {"Date": "2026-04-25", "Catégorie": "Transport", "Description": "Bus / Passe mensuelle", "Montant": 92.0},
        {"Date": "2026-04-27", "Catégorie": "Nourriture", "Description": "Épicerie vrac", "Montant": 43.10},
        {"Date": "2026-04-28", "Catégorie": "Santé", "Description": "Dentiste (nettoyage)", "Montant": 180.0},
        {"Date": "2026-04-29", "Catégorie": "Restaurants", "Description": "Pizza livraison", "Montant": 34.50},
        {"Date": "2026-04-30", "Catégorie": "Abonnements", "Description": "iCloud / Google Drive", "Montant": 15.0}
    ]
    st.session_state.depenses_list = pd.DataFrame(demo_expenses)
    st.session_state.depenses_list['Date'] = pd.to_datetime(st.session_state.depenses_list['Date']).dt.date
    
    # Flag d'initialisation
    st.session_state.budget_initialise = True



# --- Moteur d'Intelligence Financière ---
def obtenir_conseils_financiers(df_mois, budget_max, total_initial_dep):
    conseils = []
    if df_mois.empty:
        return ["Commencez à saisir vos dépenses pour recevoir des conseils personnalisés."]
    
    # On utilise le total des dépenses réelles du tracker
    total_dep_reelles = df_mois["Montant"].sum()
    
    # 1. Analyse par catégorie
    df_cat = df_mois.groupby("Catégorie")["Montant"].sum().reset_index()
    top_cat = df_cat.loc[df_cat['Montant'].idxmax()]
    
    # Spécifique Restaurants / Nourriture (mentionnés par l'utilisateur)
    if any(df_cat['Catégorie'].isin(["Nourriture", "Restaurants"])):
        montant_bouffe = df_cat[df_cat['Catégorie'].isin(["Nourriture", "Restaurants"])]['Montant'].sum()
        if montant_bouffe > (total_dep_reelles * 0.3):
            conseils.append(f"Vous dépensez beaucoup en nourriture/restaurations ({format_currency(montant_bouffe)}). Essayez de cuisiner un peu plus cette semaine.")

    # Suggestion d'économie (Potentiel concret)
    if top_cat['Montant'] > 200 and top_cat['Catégorie'] not in ["Loyer", "Factures"]:
        potentiel = top_cat['Montant'] * 0.15
        conseils.append(f"**Opportunité** : En réduisant tes dépenses en **{top_cat['Catégorie']}** de seulement 15%, tu économiserais **{format_currency(potentiel)}** par mois.")

    # Alerte de vitesse de dépense
    import datetime
    aujourdhui = datetime.date.today()
    jours_dans_mois = 30 # Approximation
    jours_ecoules = aujourdhui.day
    
    if budget_max > 0:
        ratio_temps = jours_ecoules / jours_dans_mois
        ratio_budget = total_dep_reelles / budget_max
        
        if ratio_budget > ratio_temps + 0.15:
            conseils.append(f"**Attention dépassement imminent** : Tu as déjà utilisé {ratio_budget:.0%} de ton budget alors qu'on est qu'au jour {jours_ecoules} du mois.")

    return conseils if conseils else ["Votre gestion est exemplaire ce mois-ci. Aucun dépassement à signaler."]

# --- Fonctions des pages ---

def afficher_tableau_de_bord():
    st.title("Tableau de Bord")
    st.markdown(
        "**Bienvenue dans votre espace de finances personnelles.**\n\n"
        "Suivez en un coup d’œil vos revenus, vos dépenses et l’argent qu’il vous reste ce mois-ci. Utilisez le menu pour gérer votre budget, enregistrer vos dépenses et analyser vos habitudes financières.\n\n"
        "Commencez par entrer vos revenus et votre budget mensuel dans le panneau de gauche."
    )
    
    # Section des entrées de données dans la Sidebar
    import datetime
    aujourdhui = datetime.date.today()
    mois_actuel = aujourdhui.strftime("%Y-%m")
    
    st.sidebar.subheader("Période visualisée")
    selected_month = st.sidebar.selectbox("Choisir le mois", 
                                        options=sorted(list(set([mois_actuel] + [d.strftime("%Y-%m") for d in pd.to_datetime(st.session_state.depenses_list['Date'])] if not st.session_state.depenses_list.empty else [mois_actuel])), reverse=True))

    # Utiliser les données du budget mensuel pour revenus et budget max
    revenus = st.session_state.revenus_mensuels
    budget_max = revenus  # Le budget max est basé sur les revenus configurés dans Budget Mensuel
    
    # Filtrer les dépenses pour le mois sélectionné
    df_all = st.session_state.depenses_list.copy()
    if not df_all.empty:
        df_all['Date'] = pd.to_datetime(df_all['Date'])
        df_mois = df_all[df_all['Date'].dt.strftime('%Y-%m') == selected_month]
        depenses = df_mois["Montant"].sum()
    else:
        df_mois = pd.DataFrame()
        depenses = 0
    
    # --- Calculs ---
    restant = revenus - depenses
    if budget_max > 0:
        progression = min(depenses / budget_max, 1.0)
    else:
        progression = 0.0 if depenses == 0 else 1.0
    
    # --- État vide (Aucune donnée) ---
    is_empty = (revenus == 0 and depenses == 0)
    if is_empty:
        st.markdown("""
        <div class="onboarding-card">
            <h4>Aucune donnée financière</h4>
            <p>Ajoutez vos revenus et votre budget mensuel dans la section dédiée pour voir votre tableau de bord s'actualiser automatiquement.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Variables d'affichage conditionnel ---
    aff_revenus = "-" if is_empty else format_currency(revenus)
    aff_depenses = "-" if is_empty else format_currency(depenses)
    aff_restant = "-" if is_empty else format_currency(restant)
    del_depenses = None if is_empty else format_currency(-depenses)
    del_restant = None if is_empty else format_currency(restant)

    # --- Métriques ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Revenus du mois", aff_revenus)
    with col2:
        st.metric("Dépenses totales", aff_depenses, delta=del_depenses, delta_color="inverse")
    with col3:
        st.metric("Argent restant", aff_restant, delta=del_restant, delta_color="normal")
        
    st.markdown("---")

    # --- Résumé Comparatif (Nouveauté) ---
    if not st.session_state.depenses_list.empty:
        df_all = st.session_state.depenses_list.copy()
        df_all['Date'] = pd.to_datetime(df_all['Date'])
        df_all['Mois'] = df_all['Date'].dt.strftime('%Y-%m')
        df_mensuel = df_all.groupby('Mois')['Montant'].sum().reset_index()
        
        # Calcul de la moyenne
        moyenne_globale = df_mensuel['Montant'].mean()
        
        # Comparaison avec le mois précédent
        mois_tries = sorted(df_mensuel['Mois'].unique(), reverse=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.metric("Ta Moyenne Mensuelle", format_currency(moyenne_globale), 
                      help="Moyenne de toutes vos dépenses enregistrées par mois.")
        
        if len(mois_tries) >= 2:
            current_idx = mois_tries.index(selected_month) if selected_month in mois_tries else 0
            if current_idx < len(mois_tries) - 1:
                prev_month = mois_tries[current_idx + 1]
                val_prev = df_mensuel[df_mensuel['Mois'] == prev_month]['Montant'].values[0]
                diff = depenses - val_prev
                pct = (diff / val_prev * 100) if val_prev != 0 else 0
                with col_c2:
                    st.metric(f"Vs Mois Précédent ({prev_month})", format_currency(depenses), 
                              delta=f"{format_currency(diff)} ({pct:.1f}%)", delta_color="inverse")
        
        st.markdown("---")
    
    # --- Progression du budget ---
    st.subheader("Progression du budget")
    st.progress(progression)
    
    if budget_max == 0:
        st.markdown("""
        <div class="onboarding-card">
            <p><strong>Objectif mensuel</strong> — Entrez un budget pour activer le suivi de votre progression et visualiser vos marges de manœuvre.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption(f"Vos dépenses représentent **{progression:.1%}** de votre budget total de **{format_currency(budget_max)}** ce mois-ci.")
        if depenses == 0:
            st.info("Aucune dépense enregistrée pour le moment. Vous avez encore tout votre budget disponible.")
        elif progression < 0.8:
            st.info("Budget sous contrôle. Vous gérez bien vos dépenses ce mois-ci.")
        elif progression < 1.0:
            st.warning("Attention, vous approchez de votre limite budgétaire.")
        else:
            st.error("Budget dépassé. Il serait utile de réduire certaines dépenses.")
        
    st.markdown("---")
    
    # --- Graphiques d'Analyse ---
    st.subheader("Aperçu Graphique")
    
    # Vérifier si nous avons des données de dépenses détaillées
    has_data = 'depenses_list' in st.session_state and not st.session_state.depenses_list.empty
    
    if has_data:
        df = st.session_state.depenses_list.copy()
        
        col_g1, col_g2 = st.columns(2)
        
        # 1. Camembert : Répartition des dépenses
        with col_g1:
            st.markdown("##### Répartition des dépenses")
            df_cat = df.groupby("Catégorie")["Montant"].sum().reset_index()
            fig_pie = px.pie(
                df_cat, values="Montant", names="Catégorie", hole=0.4,
                color_discrete_sequence=["#7BA7BC", "#C9ADA7", "#A3B18A", "#DAD7CD", "#DED3C4", "#5B8FA8"]
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # 2. Barre : Budget vs Dépenses
        with col_g2:
            st.markdown("##### Budget vs Dépenses")
            total_dep_reelles = df["Montant"].sum()
            
            # Utiliser la dépense du sidebar si aucune dépense n'est enregistrée, sinon le total réel
            # Pour l'affichage on va utiliser ce qui est le plus grand entre les dépenses estimées (sidebar) et réelles
            dep_a_afficher = max(depenses, total_dep_reelles)
            
            fig_bar = px.bar(
                x=["Budget Max", "Dépenses"],
                y=[budget_max, dep_a_afficher],
                color=["Budget Max", "Dépenses"],
                color_discrete_map={"Budget Max": "#457B9D", "Dépenses": "#C9ADA7"}
            )
            fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, xaxis_title="", yaxis_title="Montant ($)")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # 3. Ligne : Évolution des dépenses
        st.markdown("##### Évolution des dépenses (Quotidien)")
        df_time = df.groupby("Date")["Montant"].sum().reset_index().sort_values("Date")
        fig_line = px.line(df_time, x="Date", y="Montant", markers=True)
        fig_line.update_traces(line_color="#A3B18A", line_width=3, marker_size=8)
        fig_line.update_layout(margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Date", yaxis_title="Dépenses ($)")
        st.plotly_chart(fig_line, use_container_width=True)

    else:
        if is_empty:
            st.markdown("""
            <div class="onboarding-card">
                <h4>Centre d'analyse</h4>
                <p>Les visualisations graphiques et les rapports détaillés s'afficheront ici dès que vos premières données seront saisies.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Continuez à ajouter des dépenses dans l'onglet 'Suivi des Dépenses' pour voir votre répartition par catégorie et graphique d'évolution.")
            
            # Graphiques de base si pas de données de suivi détaillées encore
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                st.markdown("##### Dépenses vs Restant")
                labels = ["Dépenses", "Argent restant"]
                valeurs = [depenses, max(restant, 0)]
                if revenus > 0:
                    fig = px.pie(names=labels, values=valeurs, hole=0.4, color=labels, color_discrete_map={"Dépenses": "#C9ADA7", "Argent restant": "#A3B18A"})
                    fig.update_traces(textinfo='percent+label')
                    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("Entrez des revenus pour voir le graphique.")
                    
            with col_f2:
                st.markdown("##### Budget vs Dépenses")
                fig_bar = px.bar(
                    x=["Budget Max", "Dépenses"],
                    y=[budget_max, depenses],
                    color=["Budget Max", "Dépenses"],
                    color_discrete_map={"Budget Max": "#457B9D", "Dépenses": "#C9ADA7"}
                )
                fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, xaxis_title="", yaxis_title="Montant ($)")
                st.plotly_chart(fig_bar, use_container_width=True)

def afficher_budget_mensuel():
    st.title("Budget Mensuel")
    st.markdown("Gérez vos revenus et vos dépenses prévues pour établir une base financière solide.")
    st.markdown("---")
    
    col_main1, col_main2 = st.columns(2)
    
    with col_main1:
        st.markdown('<div class="section-revenus">', unsafe_allow_html=True)
        st.subheader("Revenus")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.session_state.revenus_mensuels = st.number_input("Revenus mensuels nets ($)", min_value=0.0, step=100.0, value=st.session_state.revenus_mensuels)
        revenus = st.session_state.revenus_mensuels
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-fixes">', unsafe_allow_html=True)
        st.subheader("Dépenses fixes")
        
        def input_court(label, key_state, step=10.0):
            c1, _ = st.columns([2, 1])
            with c1:
                st.session_state[key_state] = st.number_input(label, min_value=0.0, step=step, value=st.session_state[key_state])
            return st.session_state[key_state]

        loyer = input_court("Loyer / Hypothèque ($)", "loyer_mensuel")
        telephone = input_court("Téléphone & Internet ($)", "telephone_internet", 5.0)
        transport = input_court("Transport (Auto, Commun) ($)", "transport_mensuel")
        assurance = input_court("Assurances ($)", "assurances_mensuel")
        electricite = input_court("Électricité ($)", "electricite_mensuel", 5.0)
        
        st.markdown("**Dépenses fixes personnalisées :**")
        to_delete_fixed = -1
        sum_custom_fixed = 0
        for i, cat in enumerate(st.session_state.custom_fixed_categories):
            cf1, cf2, cf3 = st.columns([3, 2, 1])
            new_nom = cf1.text_input(f"Nom fixe {i+1}", value=cat["nom"], key=f"f_nom_{i}", label_visibility="collapsed")
            new_val = cf2.number_input(f"Montant fixe {i+1}", value=cat["montant"], key=f"f_val_{i}", label_visibility="collapsed", step=10.0)
            st.session_state.custom_fixed_categories[i]["nom"] = new_nom
            st.session_state.custom_fixed_categories[i]["montant"] = new_val
            sum_custom_fixed += new_val
            if cf3.button("Supprimer", key=f"f_del_{i}"):
                to_delete_fixed = i
        
        if to_delete_fixed != -1:
            st.session_state.custom_fixed_categories.pop(to_delete_fixed)
            st.rerun()
            
        if st.button("Ajouter une dépense fixe", key="add_fixed"):
            st.session_state.custom_fixed_categories.append({"nom": "Nouvelle dépense fixe", "montant": 0.0})
            st.rerun()
            
        total_fixes = loyer + telephone + transport + assurance + electricite + sum_custom_fixed
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_main2:
        st.markdown('<div class="section-variables">', unsafe_allow_html=True)
        st.subheader("Dépenses variables")
        nourriture = input_court("Nourriture / Épicerie ($)", "nourriture_mensuel")
        loisirs = input_court("Loisirs et Sorties ($)", "loisirs_mensuel")
        
        st.markdown("**Dépenses variables personnalisées :**")
        to_delete_var = -1
        sum_custom_var = 0
        for i, cat in enumerate(st.session_state.custom_variable_categories):
            cv1, cv2, cv3 = st.columns([3, 2, 1])
            new_nom = cv1.text_input(f"Nom var {i+1}", value=cat["nom"], key=f"v_nom_{i}", label_visibility="collapsed")
            new_val = cv2.number_input(f"Montant var {i+1}", value=cat["montant"], key=f"v_val_{i}", label_visibility="collapsed", step=10.0)
            st.session_state.custom_variable_categories[i]["nom"] = new_nom
            st.session_state.custom_variable_categories[i]["montant"] = new_val
            sum_custom_var += new_val
            if cv3.button("Supprimer", key=f"v_del_{i}"):
                to_delete_var = i
        
        if to_delete_var != -1:
            st.session_state.custom_variable_categories.pop(to_delete_var)
            st.rerun()

        if st.button("Ajouter une dépense variable", key="add_var"):
            st.session_state.custom_variable_categories.append({"nom": "Nouvelle dépense variable", "montant": 0.0})
            st.rerun()
        
        total_variables = nourriture + loisirs + sum_custom_var
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Section Épargne ---
    st.markdown("---")
    st.markdown('<div class="section-epargne">', unsafe_allow_html=True)
    st.subheader("Épargne")
    
    with st.container():
        col_ep1, col_ep2, col_ep3 = st.columns(3)
        with col_ep1:
            st.session_state.celi_mensuel = st.number_input("CELI ($)", min_value=0.0, step=25.0, value=st.session_state.celi_mensuel)
            st.caption("Compte d'Épargne Libre d'Impôt : Vos gains et retraits ne sont jamais imposables, idéal pour vos fonds d'urgence ou projets futurs.")
            celi = st.session_state.celi_mensuel
        with col_ep2:
            st.session_state.celiapp_mensuel = st.number_input("CELIAPP ($)", min_value=0.0, step=25.0, value=st.session_state.celiapp_mensuel)
            st.caption("Achat d'une première propriété : Profitez de déductions fiscales sur vos cotisations et d'un retrait non imposable pour votre mise de fonds.")
            celiapp = st.session_state.celiapp_mensuel
        with col_ep3:
            st.session_state.reer_mensuel = st.number_input("REER ($)", min_value=0.0, step=25.0, value=st.session_state.reer_mensuel)
            st.caption("Régime d'Épargne-Retraite : Réduisez votre impôt annuel tout en accumulant un capital pour votre retraite à l'abri de l'impôt.")
            reer = st.session_state.reer_mensuel

    # --- Épargnes supplémentaires ---
    if st.session_state.custom_savings_categories:
        st.markdown("**Autres projets d'épargne :**")
        to_delete_savings = -1
        sum_custom_savings = 0
        for i, cat in enumerate(st.session_state.custom_savings_categories):
            cs1, cs2, cs3 = st.columns([3, 2, 1])
            new_nom = cs1.text_input(f"Nom épargne {i+1}", value=cat["nom"], key=f"s_nom_{i}", label_visibility="collapsed")
            new_val = cs2.number_input(f"Montant épargne {i+1}", value=cat["montant"], key=f"s_val_{i}", label_visibility="collapsed", step=25.0)
            st.session_state.custom_savings_categories[i]["nom"] = new_nom
            st.session_state.custom_savings_categories[i]["montant"] = new_val
            sum_custom_savings += new_val
            if cs3.button("Supprimer", key=f"s_del_{i}"):
                to_delete_savings = i
        
        if to_delete_savings != -1:
            st.session_state.custom_savings_categories.pop(to_delete_savings)
            st.rerun()

    if st.button("Ajouter un projet d'épargne"):
        st.session_state.custom_savings_categories.append({"nom": "Nouvelle épargne", "montant": 0.0})
        st.rerun()
    
    total_epargne = celi + celiapp + reer + (sum_custom_savings if 'sum_custom_savings' in locals() else 0)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Résumé ---
    depenses_totales = total_fixes + total_variables
    total_sorties = depenses_totales + total_epargne
    restant = revenus - total_sorties
    
    st.subheader("Résumé du budget")
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("Revenus", format_currency(revenus))
    col_res2.metric("Dépenses", format_currency(depenses_totales))
    col_res3.metric("Épargne", format_currency(total_epargne))
    
    # Couleur dynamique pour le restant
    color_restant = "normal" if restant >= 0 else "inverse"
    col_res4.metric("Restant", format_currency(restant), delta=format_currency(restant), delta_color=color_restant)
    
    if restant < 0:
        st.error(f"**Attention** : Vos dépenses et épargne dépassent vos revenus de {format_currency(abs(restant))}.")
    elif restant > 0:
        st.success(f"**Bravo** : Il vous reste {format_currency(restant)} de marge de manœuvre.")

    st.markdown("---")

    # --- Graphique ---
    labels = ["Loyer", "Tél/Internet", "Transport", "Assurances", "Électricité", "Nourriture", "Loisirs"]
    valeurs = [loyer, telephone, transport, assurance, electricite, nourriture, loisirs]
    
    for cat in st.session_state.custom_fixed_categories:
        if cat["montant"] > 0:
            labels.append(cat["nom"]); valeurs.append(cat["montant"])
    for cat in st.session_state.custom_variable_categories:
        if cat["montant"] > 0:
            labels.append(cat["nom"]); valeurs.append(cat["montant"])
    if celi > 0: labels.append("CELI"); valeurs.append(celi)
    if celiapp > 0: labels.append("CELIAPP"); valeurs.append(celiapp)
    if reer > 0: labels.append("REER"); valeurs.append(reer)
    for cat in st.session_state.custom_savings_categories:
        if cat["montant"] > 0:
            labels.append(cat["nom"]); valeurs.append(cat["montant"])
    
    labels.append("Argent Restant"); valeurs.append(max(restant, 0))
    
    if revenus > 0:
        fig = px.pie(names=labels, values=valeurs, hole=0.4, color_discrete_sequence=px.colors.qualitative.Antique)
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    # --- Archivage ---
    with st.expander("Archiver ce budget"):
        st.markdown("Sauvegardez ce budget pour le consulter dans votre historique.")
        from datetime import datetime
        mois_actuel = datetime.now().strftime("%Y-%m")
        col_arch1, col_arch2 = st.columns([2, 1])
        with col_arch1:
            mois_archive = st.text_input("Mois à archiver (AAAA-MM)", value=mois_actuel)
        with col_arch2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sauvegarder l'archive"):
                archive = {"mois": mois_archive, "revenus": revenus, "depenses_fixes": total_fixes, "depenses_variables": total_variables, "epargne": total_epargne, "total_sorties": total_sorties, "restant": restant}
                st.session_state.budget_historique = [h for h in st.session_state.budget_historique if h["mois"] != mois_archive]
                st.session_state.budget_historique.append(archive)
                st.session_state.budget_historique.sort(key=lambda x: x["mois"])
                sauvegarder_donnees_budget()
                st.info(f"Budget de {mois_archive} archivé !")


def afficher_prevoyance_annuelle():
    st.title("Factures annuelles")
    st.markdown("Anticipez vos grosses dépenses ponctuelles pour équilibrer votre budget mensuel.")
    st.markdown("---")
    
    col_ann1, col_ann2 = st.columns(2)
    
    with col_ann1:
        st.session_state.taxes_annuelles = st.number_input("Taxes municipales/scolaires ($/an)", 
                                                        min_value=0.0, value=st.session_state.taxes_annuelles, step=50.0)
        st.session_state.permis_annuels = st.number_input("Permis & Immatriculation ($/an)", 
                                                        min_value=0.0, value=st.session_state.permis_annuels, step=10.0)
        
    with col_ann2:
        st.session_state.entretien_annuel = st.number_input("Entretien (Auto, Maison) ($/an)", 
                                                         min_value=0.0, value=st.session_state.entretien_annuel, step=50.0)
        st.session_state.autres_annuels_val = st.number_input("Autres frais annuels ($/an)", 
                                                           min_value=0.0, value=st.session_state.autres_annuels_val, step=50.0)

    st.markdown("**Autres factures annuelles :**")
    to_delete_annual = -1
    sum_custom_annual = 0
    for i, cat in enumerate(st.session_state.custom_annual_categories):
        ca1, ca2, ca3 = st.columns([3, 2, 1])
        new_nom = ca1.text_input(f"Nom annuel {i+1}", value=cat["nom"], key=f"a_nom_{i}", label_visibility="collapsed")
        new_val = ca2.number_input(f"Montant annuel {i+1}", value=cat["montant"], key=f"a_val_{i}", label_visibility="collapsed", step=50.0)
        st.session_state.custom_annual_categories[i]["nom"] = new_nom
        st.session_state.custom_annual_categories[i]["montant"] = new_val
        sum_custom_annual += new_val
        if ca3.button("Supprimer", key=f"a_del_{i}"):
            to_delete_annual = i
    
    if to_delete_annual != -1:
        st.session_state.custom_annual_categories.pop(to_delete_annual)
        st.rerun()

    if st.button("Ajouter une facture annuelle"):
        st.session_state.custom_annual_categories.append({"nom": "Nouvelle facture", "montant": 0.0})
        st.rerun()

    total_annuel = st.session_state.taxes_annuelles + st.session_state.permis_annuels + st.session_state.entretien_annuel + st.session_state.autres_annuels_val + sum_custom_annual
    montant_mensuel = total_annuel / 12 if total_annuel > 0 else 0
    
    st.markdown("---")
    st.subheader("Résumé pour la planification")
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Total annuel", format_currency(total_annuel))
    col_res2.metric("Équivalent mensuel", format_currency(montant_mensuel))
    
    if montant_mensuel > 0:
        st.info(f"Pour couvrir ces dépenses sereinement, vous devriez prévoir de mettre de côté environ {format_currency(montant_mensuel)} chaque mois.")
    else:
        st.info("Ajoutez des montants ci-dessus pour planifier vos dépenses annuelles.")

def afficher_suivi_depenses():
    st.title("Dépenses")
    st.markdown("Saisissez, modifiez et suivez vos dépenses au jour le jour.")
    
    # Initialize session state for expenses and categories
    if 'depenses_list' not in st.session_state:
        st.session_state.depenses_list = pd.DataFrame(columns=["Date", "Catégorie", "Description", "Montant"])
    if 'categories_list' not in st.session_state:
        st.session_state.categories_list = ["Nourriture", "Transport", "Loyer", "Loisirs", "Santé", "Vêtements", "Factures", "Autre"]
        
    # --- Formulaire ---
    with st.expander("Ajouter une nouvelle dépense", expanded=True):
        with st.form("ajout_depense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                import datetime
                date_depense = st.date_input("Date", datetime.date.today())
                categorie = st.selectbox("Catégorie", st.session_state.categories_list)
                
            with col2:
                montant = st.number_input("Montant ($)", min_value=0.01, step=1.0, format="%.2f")
                description = st.text_input("Description (Optionnelle)")
                
            submit = st.form_submit_button("Ajouter la dépense")
            
            if submit:
                # Add to dataframe
                nouvelle_depense = pd.DataFrame({
                    "Date": [pd.to_datetime(date_depense).date()],
                    "Catégorie": [categorie],
                    "Description": [description],
                    "Montant": [montant]
                })
                # Using pd.concat instead of append
                st.session_state.depenses_list = pd.concat([st.session_state.depenses_list, nouvelle_depense], ignore_index=True)
                st.info("Dépense ajoutée avec succès.")
                st.rerun()

    with st.expander("Gérer les catégories personnalisées"):
        nouvelle_cat = st.text_input("Ajouter une nouvelle catégorie")
        if st.button("Ajouter") and nouvelle_cat:
            if nouvelle_cat not in st.session_state.categories_list:
                st.session_state.categories_list.append(nouvelle_cat)
                st.info(f"Catégorie '{nouvelle_cat}' ajoutée aux options.")
                st.rerun()
            else:
                st.error("Cette catégorie existe déjà.")

    st.markdown("---")
    
    # Show expenses and graph if there are any
    if not st.session_state.depenses_list.empty:
        st.subheader("Historique des dépenses (Éditable)")
        st.info("**Astuce** : Vous pouvez modifier ou supprimer (bouton avec la corbeille) des lignes directement dans ce tableau !")
        
        # Le DataFrame éditable
        edited_df = st.data_editor(
            st.session_state.depenses_list,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", required=True),
                "Catégorie": st.column_config.SelectboxColumn("Catégorie", options=st.session_state.categories_list, required=True),
                "Montant": st.column_config.NumberColumn("Montant ($)", format="%.2f $", min_value=0.01, required=True),
                "Description": st.column_config.TextColumn("Description")
            },
            hide_index=True,
            key="editeur_depenses"
        )
        
        # Si des modifications sont apportées, on les sauvegarde
        if not edited_df.equals(st.session_state.depenses_list):
            st.session_state.depenses_list = edited_df
            st.rerun()
            
        st.markdown("---")
        
        st.subheader("Filtres rapides et Analyse")
        
        # Création des filtres
        filtre_cat = st.multiselect("Filtrer par catégories", options=st.session_state.categories_list, default=[])
        
        # Application du filtre
        df_filtre = st.session_state.depenses_list.copy()
        if filtre_cat:
            df_filtre = df_filtre[df_filtre["Catégorie"].isin(filtre_cat)]
        
        # Afficher les métriques
        total_depenses = df_filtre["Montant"].sum()
        st.metric("Total des dépenses (selon les filtres)", format_currency(total_depenses))
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        
        if not df_filtre.empty:
            with col_g1:
                # Group by category for the graph
                df_group = df_filtre.groupby("Catégorie")["Montant"].sum().reset_index()
                fig = px.pie(
                    df_group, 
                    values="Montant", 
                    names="Catégorie", 
                    hole=0.4,
                    title="Dépenses filtrées par catégorie"
                )
                fig.update_traces(textinfo='percent+label')
                fig.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)
                
            with col_g2:
                # Bar chart over time
                df_time = df_filtre.groupby("Date")["Montant"].sum().reset_index()
                fig_bar = px.bar(
                    df_time, 
                    x="Date", 
                    y="Montant",
                    title="Dépenses filtrées par jour",
                    text_auto='.2s'
                )
                fig_bar.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Vos filtres excluent toutes les données actuelles.")
            
        st.markdown("---")
        # Bouton pour réinitialiser
        if st.button("Effacer l'entièreté des données (Irréversible)"):
            st.session_state.depenses_list = pd.DataFrame(columns=["Date", "Catégorie", "Description", "Montant"])
            st.rerun()

    else:
        st.info("Aucune dépense enregistrée pour le moment. Utilisez le formulaire ci-dessus pour en ajouter une.")

def afficher_analyse_depenses():
    st.title("Analyse")
    st.markdown("Comprenez où part votre argent et analysez vos habitudes.")
    
    if 'depenses_list' not in st.session_state or st.session_state.depenses_list.empty:
        st.info("Vous n'avez pas encore enregistré de dépenses. Allez dans l'onglet 'Suivi des Dépenses' pour commencer.")
        return
        
    df = st.session_state.depenses_list.copy()
    
    # 0. Export CSV
    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Exporter l'historique (CSV)",
            data=csv,
            file_name='mes_depenses.csv',
            mime='text/csv',
        )
    
    # 1. Comparaison mois précédent
    st.subheader("📅 Comparaison au mois précédent")
    
    col1, col2 = st.columns(2)
    mois_actuel_total = df["Montant"].sum()
    
    with col1:
        st.metric("Total des dépenses ce mois-ci", format_currency(mois_actuel_total))
    with col2:
        mois_precedent = st.number_input("Entrez le total de vos dépenses du mois précédent ($)", min_value=0.0, value=0.0, step=50.0)
        
    if mois_precedent > 0:
        difference = mois_actuel_total - mois_precedent
        pourcentage = (difference / mois_precedent) * 100
        
        if difference > 0:
            st.error(f"Vos dépenses ont augmenté de **{format_currency(difference)}** (+{pourcentage:.1f}%) par rapport au mois dernier.")
        elif difference < 0:
            st.info(f"Vos dépenses ont diminué de **{format_currency(abs(difference))}** ({pourcentage:.1f}%) par rapport au mois dernier. Bravo !")
        else:
            st.info("Vos dépenses sont exactement les mêmes que le mois dernier.")
            
    st.markdown("---")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        # 2. Top 5 des dépenses
        st.subheader("🏆 Top 5 de vos dépenses")
        top_5 = df.nlargest(5, "Montant")[["Catégorie", "Description", "Montant"]]
        
        st.dataframe(
            top_5, 
            use_container_width=True,
            column_config={
                "Montant": st.column_config.NumberColumn("Montant ($)", format="%.2f $")
            },
            hide_index=True
        )

    with col_a2:
        # 3. Pourcentage par catégorie (Tableau)
        st.subheader("🔢 Pourcentages par Catégorie")
        df_cat = df.groupby("Catégorie")["Montant"].sum().reset_index()
        df_cat["Pourcentage"] = (df_cat["Montant"] / df_cat["Montant"].sum()) * 100
        df_cat = df_cat.sort_values(by="Montant", ascending=False)
        
        df_display = df_cat.copy()
        df_display["Pourcentage"] = df_display["Pourcentage"].map("{:.1f}%".format)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "Montant": st.column_config.NumberColumn("Total", format="%.2f $"),
                "Pourcentage": st.column_config.TextColumn("Part (%)")
            },
            hide_index=True
        )
        
    st.markdown("---")
    
    # 4. Graphique détaillé par catégorie
    st.subheader("🥧 Répartition Visuelle")
    fig = px.pie(
        df_cat, 
        values="Montant", 
        names="Catégorie", 
        hole=0.4,
        color_discrete_sequence=["#A3B18A", "#457B9D", "#C9ADA7", "#DAD7CD", "#B5C4B1", "#9ABBC7", "#D4C5BD", "#E8E3D8"]
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Évolution du Budget Restant & Comparaison Globale")
    
    budget_cible = st.number_input("Entrez votre budget de dépenses global (pour analyse) :", min_value=0.0, value=0.0, step=100.0)
    
    col_c1, col_c2 = st.columns(2)
    
    total_depense = df["Montant"].sum()
    
    with col_c1:
        # Graphique Budget vs Dépensé
        df_comparatif = pd.DataFrame({
            "Catégorie": ["Budget Cible", "Dépenses Cumu."],
            "Montant": [budget_cible, total_depense]
        })
        fig_comp = px.bar(
            df_comparatif, 
            x="Catégorie", 
            y="Montant", 
            color="Catégorie",
            title="Budget Fixé vs Dépensé à ce jour",
            color_discrete_map={"Budget Cible": "#457B9D", "Dépenses Cumu.": "#C9ADA7" if total_depense > budget_cible else "#DAD7CD"},
            text_auto=True
        )
        if budget_cible > 0:
            fig_comp.add_hline(y=budget_cible, line_dash="dash", line_color="#A3B18A", annotation_text="Limite")
        fig_comp.update_layout(showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_comp, use_container_width=True)
        
    with col_c2:
        # Évolution du capital restant chronologique
        df_chrono = df.groupby("Date")["Montant"].sum().reset_index()
        df_chrono["Date"] = pd.to_datetime(df_chrono["Date"])
        df_chrono = df_chrono.sort_values(by="Date")
        
        df_chrono["Dépenses_Cumulées"] = df_chrono["Montant"].cumsum()
        df_chrono["Capital_Restant"] = budget_cible - df_chrono["Dépenses_Cumulées"]
        
        fig_evol = px.line(
            df_chrono, 
            x="Date", 
            y="Capital_Restant",
            markers=True,
            title="Évolution du Budget Restant au jour le jour"
        )
        fig_evol.add_hline(y=0, line_dash="solid", line_color="#C9ADA7", annotation_text="Déficit 0$")
        fig_evol.update_traces(line_color="#457B9D", line_width=3, marker_size=8, marker_color="#5B8FA8")
        fig_evol.update_layout(margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_evol, use_container_width=True)



def afficher_historique():
    st.title("Historique")
    st.markdown("Analysez l'évolution de vos finances sur le long terme.")
    
    onglet_budget, onglet_depenses = st.tabs(["Historique des Budgets", "Historique des Dépenses"])
    
    with onglet_budget:
        if not st.session_state.budget_historique:
            st.info("Archivez votre premier budget depuis l'onglet **Budget Mensuel** pour voir l'historique apparaître ici.")
        else:
            historique = st.session_state.budget_historique
            
            # Tableau récapitulatif
            st.subheader("Récapitulatif des budgets archivés")
            df_hist = pd.DataFrame(historique)
            df_display = df_hist.copy()
            for col_name in ["revenus", "depenses_fixes", "depenses_variables", "epargne", "total_sorties", "restant"]:
                if col_name in df_display.columns:
                    df_display[col_name] = df_display[col_name].apply(format_currency)
            
            df_display = df_display.rename(columns={
                "mois": "Mois",
                "revenus": "Revenus",
                "depenses_fixes": "Dép. Fixes",
                "depenses_variables": "Dép. Variables",
                "epargne": "Épargne",
                "total_sorties": "Total Sorties",
                "restant": "Restant"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Graphique d'évolution
            st.subheader("Évolution dans le temps")
            df_graph = pd.DataFrame(historique)
            
            fig_evol = px.bar(
                df_graph,
                x="mois",
                y=["depenses_fixes", "depenses_variables", "epargne"],
                title="Répartition du budget par mois",
                labels={"value": "Montant ($)", "variable": "Catégorie", "mois": "Mois"},
                barmode="stack",
                color_discrete_map={
                    "depenses_fixes": "#457B9D",
                    "depenses_variables": "#C9ADA7",
                    "epargne": "#A3B18A"
                }
            )
            fig_evol.update_layout(
                margin=dict(t=30, b=10, l=10, r=10),
                legend_title_text="Catégorie",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3
                )
            )
            # Renommer les légendes
            newnames = {"depenses_fixes": "Dépenses Fixes", "depenses_variables": "Dépenses Variables", "epargne": "Épargne"}
            fig_evol.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))
            
            # Ajouter une ligne pour les revenus
            fig_evol.add_scatter(
                x=df_graph["mois"],
                y=df_graph["revenus"],
                mode="lines+markers",
                name="Revenus",
                line=dict(color="#DAD7CD", width=3),
                marker=dict(size=8)
            )
            st.plotly_chart(fig_evol, use_container_width=True)
            
            # Supprimer un mois archivé
            st.markdown("---")
            st.subheader("Gérer les archives")
            mois_disponibles = [h["mois"] for h in historique]
            mois_a_supprimer = st.selectbox("Sélectionner un mois à supprimer", mois_disponibles)
            if st.button("Supprimer cette archive"):
                st.session_state.budget_historique = [
                    h for h in st.session_state.budget_historique if h["mois"] != mois_a_supprimer
                ]
                sauvegarder_donnees_budget()
                st.info(f"Archive de {mois_a_supprimer} supprimée.")
                st.rerun()
    
    with onglet_depenses:
        if st.session_state.depenses_list.empty:
            st.info("Ajoutez des dépenses dans le **Suivi des Dépenses** pour voir l'historique apparaître.")
            return
            
        df = st.session_state.depenses_list.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df['Mois'] = df['Date'].dt.strftime('%Y-%m')
        
        # Groupement par mois
        df_mensuel = df.groupby('Mois')['Montant'].sum().reset_index().sort_values('Mois')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Évolution Mensuelle")
            fig_hist = px.bar(df_mensuel, x="Mois", y="Montant", 
                             title="Total des dépenses par mois",
                             color_discrete_sequence=["#457B9D"])
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col2:
            st.subheader("Statistiques Clés")
            moyenne = df_mensuel['Montant'].mean()
            max_mois = df_mensuel.loc[df_mensuel['Montant'].idxmax()]
            
            st.metric("Moyenne Mensuelle", format_currency(moyenne))
            st.metric("Mois le plus dépensier", max_mois['Mois'], delta=format_currency(max_mois['Montant']), delta_color="inverse")

        st.markdown("---")
        
        # Comparaison spécifique
        st.subheader("Comparaison Directe")
        tous_les_mois = df_mensuel['Mois'].tolist()
        if len(tous_les_mois) >= 2:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                m1 = st.selectbox("Mois A", tous_les_mois, index=len(tous_les_mois)-1)
            with col_m2:
                m2 = st.selectbox("Mois B", tous_les_mois, index=len(tous_les_mois)-2)
                
            val1 = df_mensuel[df_mensuel['Mois'] == m1]['Montant'].values[0]
            val2 = df_mensuel[df_mensuel['Mois'] == m2]['Montant'].values[0]
            
            diff = val1 - val2
            pct = (diff / val2 * 100) if val2 != 0 else 0
            
            col_res_c1, col_res_c2 = st.columns(2)
            col_res_c1.metric(f"Total {m1}", format_currency(val1))
            col_res_c2.metric(f"Différence vs {m2}", format_currency(diff), delta=f"{pct:.1f}%", delta_color="inverse")
        else:
            st.info("Il faut au moins deux mois de données pour activer la comparaison directe.")

def afficher_assistant_ia():
    # --- Style CSS Conversationnel ---
    st.markdown("""
    <style>
        .ia-container {
            background-color: #FAF7F2;
            padding: 20px;
            border-radius: 20px;
            border: 1px solid #E6DFD3;
        }
        .ia-bubble {
            background-color: white;
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #D4A373;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            color: #3D405B;
        }
        .ia-bubble-accent {
            background-color: #F8F4ED;
            border-left: 5px solid #A3B18A;
        }
        .score-circle {
            background: white;
            border: 8px solid #A3B18A;
            border-radius: 50%;
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: 800;
            color: #3D405B;
            margin: 0 auto 10px auto;
            box-shadow: 0 10px 20px rgba(163, 177, 138, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Assistant Intelligence Financière")
    st.write("Bonjour. J'ai analysé votre budget du mois. Voici mes observations personnalisées.")
    st.markdown("---")
    
    if st.session_state.depenses_list.empty:
        st.info("Bonjour. Pour commencer l'analyse, veuillez enregistrer vos premières dépenses dans le module de suivi.")
        return

    # --- CALCULS DE BASE ---
    df = st.session_state.depenses_list.copy()
    revenus = st.session_state.revenus_mensuels
    budget_max = revenus if revenus > 0 else 3000.0 # Fallback
    
    import datetime
    aujourdhui = datetime.date.today()
    mois_actuel = aujourdhui.strftime("%Y-%m")
    df['Date'] = pd.to_datetime(df['Date'])
    df_mois = df[df['Date'].dt.strftime('%Y-%m') == mois_actuel].copy()
    
    total_dep_mois = df_mois["Montant"].sum() if not df_mois.empty else 0
    pct_usage = (total_dep_mois / budget_max) * 100
    argent_restant = budget_max - total_dep_mois
    
    # Calcul de l'épargne réelle configurée
    epargne_mensuelle = st.session_state.celi_mensuel + st.session_state.celiapp_mensuel + st.session_state.reer_mensuel
    pct_epargne = (epargne_mensuelle / budget_max * 100) if budget_max > 0 else 0
    
    # Projection
    jour_actuel = aujourdhui.day
    projection = (total_dep_mois / jour_actuel * 30) if jour_actuel > 0 else total_dep_mois

    # --- CALCUL DU SCORE FINANCIER ---
    score = 100
    if pct_usage > 100: score -= 35
    elif pct_usage > 85: score -= 15
    if argent_restant < 0: score -= 15
    if pct_epargne < 10: score -= 15
    if pct_epargne >= 20: score += 5
    score = max(0, min(100, score))
    
    if score >= 80: score_label = "Très bon contrôle"; color_score = "#A3B18A"
    elif score >= 60: score_label = "Situation correcte"; color_score = "#D4A373"
    elif score >= 40: score_label = "A surveiller"; color_score = "#E9C46A"
    else: score_label = "Attention"; color_score = "#E76F51"

    # --- AFFICHAGE ---
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.markdown(f'<div class="score-circle" style="border-color: {color_score}">{score}</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>SCORE : {score_label}</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Action recommandée")
        if pct_usage > 80:
            st.warning("Action suggérée : réduire les dépenses variables de 50$ cette semaine pour sécuriser le mois.")
        elif pct_epargne < 15:
            st.info("Action suggérée : transférer 75$ supplémentaires vers votre épargne pour atteindre vos objectifs.")
        else:
            st.success("Action suggérée : maintenir votre rigueur actuelle. Vous êtes sur une excellente trajectoire.")

    with col_right:
        # Message 1: Top Catégorie
        if not df_mois.empty:
            top_cat = df_mois.groupby("Catégorie")["Montant"].sum().idxmax()
            st.markdown(f'<div class="ia-bubble">Votre plus grande catégorie de dépense ce mois-ci est <b>{top_cat}</b>. Est-ce un poste que vous pourriez optimiser ?</div>', unsafe_allow_html=True)
        
        # Message 2: Budget %
        st.markdown(f'<div class="ia-bubble ia-bubble-accent">Votre budget est utilisé à <b>{pct_usage:.0f}%</b>. Il vous reste une marge de {format_currency(argent_restant)}.</div>', unsafe_allow_html=True)
        
        # Message 3: Épargne
        st.markdown(f'<div class="ia-bubble">Votre épargne représente <b>{pct_epargne:.1f}%</b> de vos revenus. L\'objectif idéal recommandé est souvent de 20%.</div>', unsafe_allow_html=True)
        
        # Message 4: Projection
        st.markdown(f'<div class="ia-bubble ia-bubble-accent">Si votre rythme actuel continue, vos dépenses pourraient atteindre environ <b>{format_currency(projection)}</b> d\'ici la fin du mois.</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # --- MODULE INTERACTIF ---
    st.subheader("Besoin d'un éclairage spécifique ?")
    choix = st.selectbox("Choisissez une analyse", ["Résumé rapide", "Conseil épargne", "Conseil dépenses", "Prévision fin de mois"])
    
    if choix == "Résumé rapide":
        st.write(f"En résumé : Votre santé financière est notée à {score}/100 ce mois-ci. Votre gestion est proactive et vos principaux postes de coûts sont identifiés.")
    elif choix == "Conseil épargne":
        st.write(f"Pour booster votre épargne ({pct_epargne:.1f}% actuellement), essayez d'automatiser vos virements dès la réception de votre salaire. Même 20$ de plus par mois font une différence sur un an.")
    elif choix == "Conseil dépenses":
        st.write("Analysez vos dépenses fixes. Il y a souvent des abonnements oubliés ou des contrats d'assurances qui peuvent être renégociés pour libérer du budget.")
    elif choix == "Prévision fin de mois":
        status_forecast = "inférieur à vos revenus" if projection < revenus else "supérieur à vos revenus"
        st.write(f"D'après les tendances, votre total de fin de mois sera {status_forecast}. Planifiez en conséquence pour éviter tout découvert.")



# --- Navigation ---
st.sidebar.title("Navigation")

if 'page_active' not in st.session_state:
    st.session_state.page_active = "Tableau de Bord"

pages = ["Tableau de Bord", "Budget Mensuel", "Factures annuelles", "Suivi des Dépenses", "Analyse des Dépenses", "Historique & Comparaisons", "Assistant IA"]

for page in pages:
    if st.sidebar.button(page, key=f"nav_{page}", use_container_width=True):
        st.session_state.page_active = page

menu = st.session_state.page_active

st.sidebar.markdown("---")
if st.sidebar.button("Enregistrer définitivement", use_container_width=True):
    sauvegarder_donnees_budget()
    st.sidebar.success("Sauvegardé !")

if menu == "Tableau de Bord":
    afficher_tableau_de_bord()
elif menu == "Budget Mensuel":
    afficher_budget_mensuel()
elif menu == "Factures annuelles":
    afficher_prevoyance_annuelle()
elif menu == "Suivi des Dépenses":
    afficher_suivi_depenses()
elif menu == "Analyse des Dépenses":
    afficher_analyse_depenses()
elif menu == "Historique & Comparaisons":
    afficher_historique()
elif menu == "Assistant IA":
    afficher_assistant_ia()
