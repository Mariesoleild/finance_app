import streamlit as st
import pandas as pd
import plotly.express as px

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
    
    /* Fond global crème doux */
    .stApp {
        background: linear-gradient(160deg, #FAF7F2 0%, #F3EDE4 50%, #EEF2EE 100%);
    }
    
    /* Ajustement de l'espacement principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Barre latérale — sauge très pâle */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F0EDE6 0%, #E8E3D8 100%);
        border-right: 1px solid #D5CDBE;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: #4A5043;
    }
    
    /* Cartes indicateurs (Metrics) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #FDFBF7 100%);
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 2px 12px rgba(138, 131, 116, 0.08), 0 1px 3px rgba(138, 131, 116, 0.06);
        border: 1px solid #E6DFD3;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(138, 131, 116, 0.12), 0 3px 8px rgba(138, 131, 116, 0.08);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3D405B;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        font-weight: 600;
        color: #7C8172;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Boutons — sauge doux */
    .stButton>button {
        background: linear-gradient(135deg, #A3B18A 0%, #8FA578 100%);
        color: #FDFBF7;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1.2rem;
        border: none;
        box-shadow: 0 4px 10px rgba(143, 165, 120, 0.25);
        transition: all 0.3s ease;
        letter-spacing: 0.02em;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #8FA578 0%, #7A9466 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(143, 165, 120, 0.35);
        color: #FDFBF7;
    }
    
    /* Titres — bleu-gris profond */
    h1, h2, h3 {
        color: #3D405B;
    }
    h1 {
        font-weight: 700;
    }
    
    /* Tableaux modernes */
    [data-testid="stDataFrame"] {
        box-shadow: 0 2px 10px rgba(138, 131, 116, 0.08);
        border-radius: 12px;
        overflow: hidden;
    }

    /* Dividers plus doux */
    hr {
        border-color: #DDD6C8 !important;
        opacity: 0.6;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: #FDFBF7;
        border-radius: 12px;
        border: 1px solid #E6DFD3;
    }

    /* Progress bar — sauge */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #A3B18A, #457B9D) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #7C8172;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #3D405B;
        font-weight: 700;
        border-bottom-color: #A3B18A !important;
    }
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

if 'depenses_list' not in st.session_state:
    st.session_state.depenses_list = pd.DataFrame(columns=["Date", "Catégorie", "Description", "Montant"])
if 'categories_list' not in st.session_state:
    st.session_state.categories_list = ["Nourriture", "Transport", "Loyer", "Loisirs", "Santé", "Vêtements", "Factures", "Autre"]
if 'monthly_targets' not in st.session_state:
    st.session_state.monthly_targets = {}
if 'budget_historique' not in st.session_state:
    st.session_state.budget_historique = [] # Liste de dicts: [{"mois": "2026-04", "revenus": ..., ...}]
if 'custom_fixed_categories' not in st.session_state:
    st.session_state.custom_fixed_categories = [] # Liste de dicts {"nom": "", "montant": 0.0}
if 'custom_variable_categories' not in st.session_state:
    st.session_state.custom_variable_categories = [] # Liste de dicts {"nom": "", "montant": 0.0}
if 'custom_savings_categories' not in st.session_state:
    st.session_state.custom_savings_categories = [] # Liste de dicts {"nom": "", "montant": 0.0}
if 'taxes_annuelles' not in st.session_state:
    st.session_state.taxes_annuelles = 0.0
if 'permis_annuels' not in st.session_state:
    st.session_state.permis_annuels = 0.0
if 'entretien_annuel' not in st.session_state:
    st.session_state.entretien_annuel = 0.0
if 'autres_annuels_val' not in st.session_state:
    st.session_state.autres_annuels_val = 0.0
if 'custom_annual_categories' not in st.session_state:
    st.session_state.custom_annual_categories = [] # Liste de dicts {"nom": "", "montant": 0.0}

# Chiffres du budget mensuel
if 'revenus_mensuels' not in st.session_state: st.session_state.revenus_mensuels = 0.0
if 'loyer_mensuel' not in st.session_state: st.session_state.loyer_mensuel = 0.0
if 'telephone_internet' not in st.session_state: st.session_state.telephone_internet = 0.0
if 'transport_mensuel' not in st.session_state: st.session_state.transport_mensuel = 0.0
if 'assurances_mensuel' not in st.session_state: st.session_state.assurances_mensuel = 0.0
if 'electricite_mensuel' not in st.session_state: st.session_state.electricite_mensuel = 0.0
if 'nourriture_mensuel' not in st.session_state: st.session_state.nourriture_mensuel = 0.0
if 'loisirs_mensuel' not in st.session_state: st.session_state.loisirs_mensuel = 0.0
if 'celi_mensuel' not in st.session_state: st.session_state.celi_mensuel = 0.0
if 'celiapp_mensuel' not in st.session_state: st.session_state.celiapp_mensuel = 0.0
if 'reer_mensuel' not in st.session_state: st.session_state.reer_mensuel = 0.0

# Charger les données sauvegardées une seule fois au démarrage
if 'budget_initialise' not in st.session_state:
    charger_donnees_budget()
    st.session_state.budget_initialise = True

# --- Moteur d'Intelligence Financière ---
def obtenir_conseils_financiers(df_mois, budget_max, total_initial_dep):
    conseils = []
    if df_mois.empty:
        return ["Commencez à saisir vos dépenses pour recevoir des conseils personnalisés !"]
    
    # On utilise le total des dépenses réelles du tracker
    total_dep_reelles = df_mois["Montant"].sum()
    
    # 1. Analyse par catégorie
    df_cat = df_mois.groupby("Catégorie")["Montant"].sum().reset_index()
    top_cat = df_cat.loc[df_cat['Montant'].idxmax()]
    
    # Spécifique Restaurants / Nourriture (mentionnés par l'utilisateur)
    if any(df_cat['Catégorie'].isin(["Nourriture", "Restaurants"])):
        montant_bouffe = df_cat[df_cat['Catégorie'].isin(["Nourriture", "Restaurants"])]['Montant'].sum()
        if montant_bouffe > (total_dep_reelles * 0.3):
            conseils.append(f"🍔 **Tu dépenses beaucoup en nourriture/restaurations** ({format_currency(montant_bouffe)}). Essaye de cuisiner un peu plus cette semaine !")

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

    return conseils if conseils else ["Ta gestion est exemplaire ce mois-ci ! Rien à signaler. 👍"]

# --- Fonctions des pages ---

def afficher_tableau_de_bord():
    st.title("Tableau de Bord")
    st.markdown(
        "**Bienvenue dans votre espace de Finances Personnelles.**\n\n"
        "Gérez tout votre argent au même endroit. Ce *Tableau de Bord* vous donne un aperçu immédiat de l'évolution de votre budget mensuel. "
        "Pour aller plus loin, utilisez le menu afin de détailler vos comptes, suivre vos dépenses quotidiennes et estimer vos projets futurs.\n\n"
        "👉 **Pour démarrer :** indiquez vos revenus et la limite de votre budget dans le panneau de gauche."
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
    
    # --- Métriques ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Revenus du mois", format_currency(revenus))
    with col2:
        st.metric("Dépenses totales", format_currency(depenses), delta=format_currency(-depenses), delta_color="inverse")
    with col3:
        st.metric("Argent restant", format_currency(restant), delta=format_currency(restant), delta_color="normal")
        
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
    st.caption(f"Vos dépenses représentent **{progression:.1%}** de votre budget total de **{format_currency(budget_max)}** ce mois-ci.")
    
    if progression >= 1.0:
        st.error(f"**Attention : Dépassement de budget !** Tu as dépassé ton budget de **{format_currency(depenses - budget_max)}**.")
    elif progression >= 0.8:
        st.warning(f"**Tu as atteint 80% de ton budget !** Il te reste seulement **{format_currency(budget_max - depenses)}** pour finir le mois.")
    else:
        st.info(f"**Budget sous contrôle.** Il te reste encore **{format_currency(budget_max - depenses)}** de marge.")
        
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
    st.title("Budget")
    st.markdown("Gérez vos revenus et dépenses en détail.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entrées d'argent")
        st.session_state.revenus_mensuels = st.number_input("Revenus mensuels nets ($)", min_value=0.0, step=100.0, value=st.session_state.revenus_mensuels)
        revenus = st.session_state.revenus_mensuels
        
        st.subheader("Dépenses fixes")
        st.session_state.loyer_mensuel = st.number_input("Loyer / Hypothèque ($)", min_value=0.0, step=10.0, value=st.session_state.loyer_mensuel)
        st.session_state.telephone_internet = st.number_input("Téléphone & Internet ($)", min_value=0.0, step=5.0, value=st.session_state.telephone_internet)
        st.session_state.transport_mensuel = st.number_input("Transport (Auto, Commun) ($)", min_value=0.0, step=10.0, value=st.session_state.transport_mensuel)
        st.session_state.assurances_mensuel = st.number_input("Assurances ($)", min_value=0.0, step=10.0, value=st.session_state.assurances_mensuel)
        st.session_state.electricite_mensuel = st.number_input("Électricité ($)", min_value=0.0, step=5.0, value=st.session_state.electricite_mensuel)
        loyer = st.session_state.loyer_mensuel
        telephone = st.session_state.telephone_internet
        transport = st.session_state.transport_mensuel
        assurance = st.session_state.assurances_mensuel
        electricite = st.session_state.electricite_mensuel
        
        st.markdown("**Dépenses fixes :**")
        to_delete_fixed = -1
        sum_custom_fixed = 0
        for i, cat in enumerate(st.session_state.custom_fixed_categories):
            cf1, cf2, cf3 = st.columns([3, 3, 1])
            new_nom = cf1.text_input(f"Nom fixe {i+1}", value=cat["nom"], key=f"f_nom_{i}", label_visibility="collapsed")
            new_val = cf2.number_input(f"Montant fixe {i+1}", value=cat["montant"], key=f"f_val_{i}", label_visibility="collapsed", step=10.0)
            st.session_state.custom_fixed_categories[i]["nom"] = new_nom
            st.session_state.custom_fixed_categories[i]["montant"] = new_val
            sum_custom_fixed += new_val
            if cf3.button("", key=f"f_del_{i}"):
                to_delete_fixed = i
        
        if to_delete_fixed != -1:
            st.session_state.custom_fixed_categories.pop(to_delete_fixed)
            st.rerun()
            
        if st.button("Ajouter une dépense fixe"):
            st.session_state.custom_fixed_categories.append({"nom": "Nouvelle dépense fixe", "montant": 0.0})
            st.rerun()
            
        total_fixes = loyer + telephone + transport + assurance + electricite + sum_custom_fixed
        
    with col2:
        st.subheader("Dépenses variables")
        st.session_state.nourriture_mensuel = st.number_input("Nourriture / Épicerie ($)", min_value=0.0, step=10.0, value=st.session_state.nourriture_mensuel)
        st.session_state.loisirs_mensuel = st.number_input("Loisirs et Sorties ($)", min_value=0.0, step=10.0, value=st.session_state.loisirs_mensuel)
        nourriture = st.session_state.nourriture_mensuel
        loisirs = st.session_state.loisirs_mensuel
        
        st.markdown("**Dépenses variables :**")
        to_delete_var = -1
        sum_custom_var = 0
        for i, cat in enumerate(st.session_state.custom_variable_categories):
            cv1, cv2, cv3 = st.columns([3, 3, 1])
            new_nom = cv1.text_input(f"Nom var {i+1}", value=cat["nom"], key=f"v_nom_{i}", label_visibility="collapsed")
            new_val = cv2.number_input(f"Montant var {i+1}", value=cat["montant"], key=f"v_val_{i}", label_visibility="collapsed", step=10.0)
            st.session_state.custom_variable_categories[i]["nom"] = new_nom
            st.session_state.custom_variable_categories[i]["montant"] = new_val
            sum_custom_var += new_val
            if cv3.button("", key=f"v_del_{i}"):
                to_delete_var = i
        
        if to_delete_var != -1:
            st.session_state.custom_variable_categories.pop(to_delete_var)
            st.rerun()

        if st.button("Ajouter une dépense variable"):
            st.session_state.custom_variable_categories.append({"nom": "Nouvelle dépense variable", "montant": 0.0})
            st.rerun()
        
        total_variables = nourriture + loisirs + sum_custom_var

    # --- Section Épargne ---
    st.markdown("---")
    st.subheader("Épargne mensuelle")
    st.markdown("Planifiez vos cotisations dans vos comptes d'épargne enregistrés.")

    col_ep1, col_ep2, col_ep3, col_ep4 = st.columns(4)

    with col_ep1:
        st.session_state.celi_mensuel = st.number_input("CELI ($)", min_value=0.0, step=25.0,
                               help="Compte d'Épargne Libre d'Impôt", value=st.session_state.celi_mensuel)
        celi = st.session_state.celi_mensuel
        st.caption("**CELI** — Vos gains (intérêts, dividendes) ne sont jamais imposés. Retraits libres en tout temps. Idéal pour un fonds d'urgence ou des projets à moyen terme.")

    with col_ep2:
        st.session_state.celiapp_mensuel = st.number_input("CELIAPP ($)", min_value=0.0, step=25.0,
                                  help="Compte d'Épargne Libre d'Impôt pour l'Achat d'une Première Propriété", value=st.session_state.celiapp_mensuel)
        celiapp = st.session_state.celiapp_mensuel
        st.caption("**CELIAPP** — Cotisations déductibles d'impôt **et** retraits non imposés pour acheter votre première maison. Le meilleur des deux mondes.")

    with col_ep3:
        st.session_state.reer_mensuel = st.number_input("REER ($)", min_value=0.0, step=25.0,
                               help="Régime Enregistré d'Épargne-Retraite", value=st.session_state.reer_mensuel)
        reer = st.session_state.reer_mensuel
        st.caption("**REER** — Cotisations déductibles d'impôt aujourd'hui, imposées seulement au retrait (à la retraite, quand votre taux est plus bas). Parfait pour la planification retraite.")

    # --- Épargnes supplémentaires ---
    st.markdown("**Épargnes supplémentaires :**")
    to_delete_savings = -1
    sum_custom_savings = 0
    for i, cat in enumerate(st.session_state.custom_savings_categories):
        cs1, cs2, cs3 = st.columns([3, 3, 1])
        new_nom = cs1.text_input(f"Nom épargne {i+1}", value=cat["nom"], key=f"s_nom_{i}", label_visibility="collapsed")
        new_val = cs2.number_input(f"Montant épargne {i+1}", value=cat["montant"], key=f"s_val_{i}", label_visibility="collapsed", step=25.0)
        st.session_state.custom_savings_categories[i]["nom"] = new_nom
        st.session_state.custom_savings_categories[i]["montant"] = new_val
        sum_custom_savings += new_val
        if cs3.button("", key=f"s_del_{i}"):
            to_delete_savings = i
    
    if to_delete_savings != -1:
        st.session_state.custom_savings_categories.pop(to_delete_savings)
        st.rerun()

    if st.button("Ajouter une épargne"):
        st.session_state.custom_savings_categories.append({"nom": "Nouvelle épargne", "montant": 0.0})
        st.rerun()
    
    total_epargne = celi + celiapp + reer + sum_custom_savings
    sum_custom_annual_prevu = sum(cat["montant"] for cat in st.session_state.custom_annual_categories)
    total_annuel_prevu = st.session_state.taxes_annuelles + st.session_state.permis_annuels + st.session_state.entretien_annuel + st.session_state.autres_annuels_val + sum_custom_annual_prevu

    if total_epargne > 0:
        st.info(f"Vous prévoyez épargner **{format_currency(total_epargne)}** ce mois-ci. Bravo !")

    if total_annuel_prevu > 0:
        st.info(f"**Note informative** : Vos factures annuelles totalisent **{format_currency(total_annuel_prevu)}**. Vous pouvez gérer ces détails dans l'onglet **Factures annuelles**.")

    st.markdown("---")
    
    # --- Résumé ---
    depenses_totales = total_fixes + total_variables
    total_sorties = depenses_totales + total_epargne
    restant = revenus - total_sorties
    
    st.subheader("Résumé du budget mensuel")
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("Revenus", format_currency(revenus))
    col_res2.metric("Dépenses", format_currency(depenses_totales))
    col_res3.metric("Épargne", format_currency(total_epargne))
    col_res4.metric("Restant", format_currency(restant), delta=format_currency(restant))
    
    # Feedback instantané d'économie
    if restant > 0:
        st.info(f"Astuce : Si ce budget est respecté, il vous restera **{format_currency(restant)}** de marge après dépenses et épargne.")
    elif restant < 0:
        st.error(f"🛑 Alerte rouge : Vos dépenses et cotisations d'épargne dépassent vos revenus de **{format_currency(abs(restant))}**.")

    # --- Budget Prévu ---
    st.markdown("---")
    # --- Graphique ---
    # Construction dynamique des étiquettes et valeurs
    labels = ["Loyer", "Téléphone/Internet", "Transport", "Assurances", "Électricité", "Nourriture", "Loisirs"]
    valeurs = [loyer, telephone, transport, assurance, electricite, nourriture, loisirs]
    
    # Ajout des catégories fixes personnalisées
    for cat in st.session_state.custom_fixed_categories:
        if cat["montant"] > 0:
            labels.append(cat["nom"])
            valeurs.append(cat["montant"])
            
    # Ajout des catégories variables personnalisées
    for cat in st.session_state.custom_variable_categories:
        if cat["montant"] > 0:
            labels.append(cat["nom"])
            valeurs.append(cat["montant"])
            
    # Ajout des épargnes
    if celi > 0:
        labels.append("CELI")
        valeurs.append(celi)
    if celiapp > 0:
        labels.append("CELIAPP")
        valeurs.append(celiapp)
    if reer > 0:
        labels.append("REER")
        valeurs.append(reer)
        
    for cat in st.session_state.custom_savings_categories:
        if cat["montant"] > 0:
            labels.append(cat["nom"])
            valeurs.append(cat["montant"])
            
    # Ajout des provisions et restant
    labels.append("Argent Restant")
    valeurs.append(max(restant, 0))
    
    if revenus > 0:
        fig = px.pie(
            names=labels,
            values=valeurs,
            hole=0.4,
            color=labels,
            color_discrete_sequence=["#7BA7BC", "#C9ADA7", "#A3B18A", "#DAD7CD", "#DED3C4", "#5B8FA8"]
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    # --- Archivage du budget mensuel ---
    st.markdown("---")
    st.subheader("Archiver ce budget")
    st.markdown("Sauvegardez une copie de votre budget actuel pour le consulter plus tard dans l'historique.")
    
    from datetime import datetime
    mois_actuel = datetime.now().strftime("%Y-%m")
    
    col_arch1, col_arch2 = st.columns([2, 1])
    with col_arch1:
        mois_archive = st.text_input("Mois à archiver (format AAAA-MM)", value=mois_actuel)
    with col_arch2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Archiver ce budget"):
            archive = {
                "mois": mois_archive,
                "revenus": revenus,
                "depenses_fixes": total_fixes,
                "depenses_variables": total_variables,
                "epargne": total_epargne,
                "total_sorties": total_sorties,
                "restant": restant
            }
            # Remplacer si le mois existe déjà
            st.session_state.budget_historique = [
                h for h in st.session_state.budget_historique if h["mois"] != mois_archive
            ]
            st.session_state.budget_historique.append(archive)
            st.session_state.budget_historique.sort(key=lambda x: x["mois"])
            sauvegarder_donnees_budget()
            st.info(f"Budget archivé pour **{mois_archive}** !")


def afficher_prevoyance_annuelle():
    st.title("Factures")
    st.markdown("Identifiez vos dépenses importantes qui surviennent une fois par an pour mieux les anticiper.")
    
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
        ca1, ca2, ca3 = st.columns([3, 3, 1])
        new_nom = ca1.text_input(f"Nom annuel {i+1}", value=cat["nom"], key=f"a_nom_{i}", label_visibility="collapsed")
        new_val = ca2.number_input(f"Montant annuel {i+1}", value=cat["montant"], key=f"a_val_{i}", label_visibility="collapsed", step=50.0)
        st.session_state.custom_annual_categories[i]["nom"] = new_nom
        st.session_state.custom_annual_categories[i]["montant"] = new_val
        sum_custom_annual += new_val
        if ca3.button("", key=f"a_del_{i}"):
            to_delete_annual = i
    
    if to_delete_annual != -1:
        st.session_state.custom_annual_categories.pop(to_delete_annual)
        st.rerun()

    if st.button("Ajouter une facture annuelle"):
        st.session_state.custom_annual_categories.append({"nom": "Nouvelle facture", "montant": 0.0})
        st.rerun()

    total_annuel = st.session_state.taxes_annuelles + st.session_state.permis_annuels + st.session_state.entretien_annuel + st.session_state.autres_annuels_val + sum_custom_annual
    
    st.markdown("---")
    st.metric("Total des dépenses annuelles", format_currency(total_annuel))
    
    st.info("""
    **Conseil** : Ces dépenses sont importantes et arrivent une fois par an. Il est prudent de garder 
    ce montant global en tête pour bien planifier vos économies et éviter les surprises au moment du paiement.
    """)

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
                st.info("Dépense ajoutée avec succès ! 🎉")
                st.rerun()

    with st.expander("⚙️ Gérer les catégories personnalisées"):
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
        
        st.subheader("🔍 Filtres rapides et Analyse")
        
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
            label="📥 Exporter l'historique (CSV)",
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

# --- Navigation ---
st.sidebar.title("Navigation")

if 'page_active' not in st.session_state:
    st.session_state.page_active = "Tableau de Bord"

pages = ["Tableau de Bord", "Budget Mensuel", "Factures annuelles", "Suivi des Dépenses", "Analyse des Dépenses", "Historique & Comparaisons"]

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
