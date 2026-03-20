import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Finances Personnelles", page_icon="💰", layout="wide")

# Paramètres esthétiques globaux via CSS
st.markdown("""
<style>
    /* Importer une police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fond global plus doux */
    .stApp {
        background-color: #f4f7f6;
    }
    
    /* Ajustement de l'espacement principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Style de la barre latérale */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1e4e8;
    }
    
    /* Style des cartes pour les indicateurs (Metrics) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 800;
        color: #2c3e50;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #7f8c8d;
    }

    /* Boutons stylisés */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 4px 6px rgba(52, 152, 219, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(52, 152, 219, 0.3);
    }
    
    /* Titres avec une couleur plus riche */
    h1, h2, h3 {
        color: #1a202c;
    }
    
    /* Tableaux modernes */
    [data-testid="stDataFrame"] {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- Fonction utilitaire de formatage ---
def format_currency(value):
    """Formate un nombre en format monétaire lisible (ex: 1 800,00 $)"""
    return "{:,.2f} $".format(value).replace(",", "X").replace(".", ",").replace("X", " ")

# --- Fonctions des pages ---

def afficher_tableau_de_bord():
    st.title("📊 Tableau de Bord")
    st.markdown("Vue globale de votre santé financière du mois.")
    
    # Section des entrées de données (Sidebar ou Expander)
    st.sidebar.header("⚙️ Paramètres du mois")
    revenus = st.sidebar.number_input("Revenus du mois ($)", min_value=0, value=5000, step=100)
    budget_max = st.sidebar.number_input("Budget max. dépenses ($)", min_value=1, value=4000, step=100)
    depenses = st.sidebar.number_input("Dépenses totales ($)", min_value=0, value=3200, step=100)
    
    # --- Calculs ---
    restant = revenus - depenses
    progression = min(depenses / budget_max, 1.0) # Cap à 100% pour la barre
    
    # --- Métriques ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Revenus du mois", format_currency(revenus))
    with col2:
        st.metric("Dépenses totales", format_currency(depenses), delta=format_currency(-depenses), delta_color="inverse")
    with col3:
        st.metric("Argent restant", format_currency(restant), delta=format_currency(restant), delta_color="normal")
        
    st.markdown("---")
    
    # --- Progression du budget ---
    st.subheader("🎯 Progression du budget")
    st.progress(progression)
    st.caption(f"Vos dépenses représentent **{progression:.1%}** de votre budget total de **{format_currency(budget_max)}** ce mois-ci.")
    
    if progression >= 1.0:
        st.error(f"🚨 Vous avez dépassé votre budget de **{format_currency(depenses - budget_max)}** ! Revoyez vos dépenses urgemment.")
    elif progression >= 0.8:
        st.warning(f"⚠️ Attention, vous avez consommé plus de 80% de votre budget (Reste : **{format_currency(budget_max - depenses)}**).")
    else:
        st.success(f"✅ Vos dépenses sont bien maîtrisées ! Vous avez encore une marge de **{format_currency(budget_max - depenses)}**.")
        
    st.markdown("---")
    
    # --- Graphique Rapide ---
    st.subheader("📈 Aperçu Graphique")
    
    # Préparation des données pour le graphique
    labels = ["Dépenses", "Argent restant"]
    valeurs = [depenses, max(restant, 0)] # On ne montre pas de restant négatif sur le pie chart
    
    if revenus > 0:
        fig = px.pie(
            names=labels, 
            values=valeurs, 
            hole=0.4,
            color=labels,
            color_discrete_map={"Dépenses": "#e74c3c", "Argent restant": "#2ecc71"}
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Veuillez entrer des revenus pour voir le graphique.")

def afficher_budget_mensuel():
    st.title("💸 Budget Mensuel")
    st.markdown("Gérez vos revenus et dépenses en détail.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Entrées d'argent")
        revenus = st.number_input("Revenus mensuels nets ($)", min_value=0.0, value=5000.0, step=100.0)
        
        st.subheader("Dépenses fixes")
        loyer = st.number_input("Loyer / Hypothèque ($)", min_value=0.0, value=1200.0, step=10.0)
        telephone = st.number_input("Téléphone & Internet ($)", min_value=0.0, value=100.0, step=5.0)
        transport = st.number_input("Transport (Auto, Commun) ($)", min_value=0.0, value=300.0, step=10.0)
        
        total_fixes = loyer + telephone + transport
        
    with col2:
        st.subheader("Dépenses variables")
        nourriture = st.number_input("Nourriture / Épicerie ($)", min_value=0.0, value=500.0, step=10.0)
        loisirs = st.number_input("Loisirs et Sorties ($)", min_value=0.0, value=200.0, step=10.0)
        
        total_variables = nourriture + loisirs

    st.markdown("---")
    
    # --- Résumé ---
    depenses_totales = total_fixes + total_variables
    restant = revenus - depenses_totales
    
    st.subheader("📊 Résumé du budget")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Revenus", format_currency(revenus))
    col_res2.metric("Dépenses Totales", format_currency(depenses_totales), delta=format_currency(-depenses_totales), delta_color="inverse")
    col_res3.metric("Argent Restant", format_currency(restant), delta=format_currency(restant), delta_color="normal")
    
    # Feedback instantané d'économie
    if restant > 0:
        st.info(f"💡 Astuce : Si ce budget est respecté, vous pourriez économiser **{format_currency(restant)}** ce mois-ci.")
    elif restant < 0:
        st.error(f"🛑 Alerte rouge : Vos dépenses fixes et variables combinées dépassent déjà vos revenus de **{format_currency(abs(restant))}**.")

    # --- Budget Prévu ---
    st.markdown("---")
    st.subheader("🎯 Comparaison budget prévu")
    budget_prevu = st.number_input("Quel est votre budget total autorisé pour ce mois ? ($)", min_value=0.0, value=2500.0, step=100.0)
    
    difference = budget_prevu - depenses_totales
    
    if difference >= 0:
        st.success(f"✅ Félicitations ! Vous êtes en dessous de votre budget de **{format_currency(difference)}**.")
    else:
        st.warning(f"⚠️ Vous avez dépassé budget de **{format_currency(abs(difference))}**.")
    
    # --- Graphique ---
    labels = ["Dépenses Fixes", "Dépenses Variables", "Argent Restant (Épargne)"]
    valeurs = [total_fixes, total_variables, max(restant, 0)]
    
    if revenus > 0:
        fig = px.pie(
            names=labels,
            values=valeurs,
            hole=0.4,
            color=labels,
            color_discrete_map={
                "Dépenses Fixes": "#e67e22", 
                "Dépenses Variables": "#e74c3c", 
                "Argent Restant (Épargne)": "#2ecc71"
            }
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

def afficher_suivi_depenses():
    st.title("🛒 Suivi des Dépenses")
    st.markdown("Saisissez, modifiez et suivez vos dépenses au jour le jour.")
    
    # Initialize session state for expenses and categories
    if 'depenses_list' not in st.session_state:
        st.session_state.depenses_list = pd.DataFrame(columns=["Date", "Catégorie", "Description", "Montant"])
    if 'categories_list' not in st.session_state:
        st.session_state.categories_list = ["Nourriture", "Transport", "Loyer", "Loisirs", "Santé", "Vêtements", "Factures", "Autre"]
        
    # --- Formulaire ---
    with st.expander("➕ Ajouter une nouvelle dépense", expanded=True):
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
                st.success("Dépense ajoutée avec succès ! 🎉")
                st.rerun()

    with st.expander("⚙️ Gérer les catégories personnalisées"):
        nouvelle_cat = st.text_input("Ajouter une nouvelle catégorie")
        if st.button("Ajouter") and nouvelle_cat:
            if nouvelle_cat not in st.session_state.categories_list:
                st.session_state.categories_list.append(nouvelle_cat)
                st.success(f"Catégorie '{nouvelle_cat}' ajoutée aux options.")
                st.rerun()
            else:
                st.error("Cette catégorie existe déjà.")

    st.markdown("---")
    
    # Show expenses and graph if there are any
    if not st.session_state.depenses_list.empty:
        st.subheader("📜 Historique des dépenses (Éditable)")
        st.info("💡 **Astuce** : Vous pouvez modifier ou supprimer (bouton avec la corbeille) des lignes directement dans ce tableau !")
        
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
        if st.button("🗑️ Effacer l'entièreté des données (Irréversible)"):
            st.session_state.depenses_list = pd.DataFrame(columns=["Date", "Catégorie", "Description", "Montant"])
            st.rerun()

    else:
        st.info("Aucune dépense enregistrée pour le moment. Utilisez le formulaire ci-dessus pour en ajouter une.")

def afficher_analyse_depenses():
    st.title("📊 Analyse des Dépenses")
    st.markdown("Comprenez où part votre argent et analysez vos habitudes.")
    
    if 'depenses_list' not in st.session_state or st.session_state.depenses_list.empty:
        st.info("⚠️ Vous n'avez pas encore enregistré de dépenses. Allez dans l'onglet 'Suivi des Dépenses' pour commencer.")
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
            st.error(f"📈 Vos dépenses ont augmenté de **{format_currency(difference)}** (+{pourcentage:.1f}%) par rapport au mois dernier.")
        elif difference < 0:
            st.success(f"📉 Vos dépenses ont diminué de **{format_currency(abs(difference))}** ({pourcentage:.1f}%) par rapport au mois dernier. Bravo !")
        else:
            st.info("⚖️ Vos dépenses sont exactement les mêmes que le mois dernier.")
            
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
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📉 Évolution du Budget Restant & Comparaison Globale")
    
    budget_cible = st.number_input("Entrez votre budget de dépenses global (pour analyse) :", min_value=0.0, value=2500.0, step=100.0)
    
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
            color_discrete_map={"Budget Cible": "#3498db", "Dépenses Cumu.": "#e74c3c" if total_depense > budget_cible else "#f39c12"},
            text_auto=True
        )
        if budget_cible > 0:
            fig_comp.add_hline(y=budget_cible, line_dash="dash", line_color="green", annotation_text="Limite")
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
        fig_evol.add_hline(y=0, line_dash="solid", line_color="#e74c3c", annotation_text="Déficit 0$")
        fig_evol.update_traces(line_color="#2ecc71", line_width=3, marker_size=8, marker_color="#27ae60")
        fig_evol.update_layout(margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_evol, use_container_width=True)


def afficher_simulateurs():
    st.title("🔮 Simulateurs & Projections")
    st.markdown("Projetez votre avenir financier et optimisez vos investissements.")
    
    onglet1, onglet2 = st.tabs(["📈 Épargne & Intérêts", "📦 Modèle de Portefeuille"])
    
    with onglet1:
        st.subheader("Simulateur d'Intérêts Composés")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            capital_initial = st.number_input("Capital Initial ($)", min_value=0.0, value=1000.0, step=100.0)
        with col_s2:
            versement_mensuel = st.number_input("Versement Mensuel ($)", min_value=0.0, value=200.0, step=10.0)
        with col_s3:
            taux_annuel = st.number_input("Taux d'Intérêt Annuel (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
            
        annees = st.slider("Durée de projection (Années)", min_value=1, max_value=40, value=10)
        
        mois = annees * 12
        taux_mensuel = (taux_annuel / 100) / 12
        capital_courant = capital_initial
        capital_investi = capital_initial
        donnees_projection = [{"Année": 0, "Capital Investi": capital_investi, "Intérêts Générés": 0.0, "Total": capital_courant}]
        
        for m in range(1, mois + 1):
            interets_mois = capital_courant * taux_mensuel
            capital_courant += interets_mois + versement_mensuel
            capital_investi += versement_mensuel
            
            if m % 12 == 0:
                donnees_projection.append({
                    "Année": m // 12,
                    "Capital Investi": capital_investi,
                    "Intérêts Générés": capital_courant - capital_investi,
                    "Total": capital_courant
                })
                
        import pandas as pd
        df_proj = pd.DataFrame(donnees_projection)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Montant Final Estimé", format_currency(capital_courant))
        col_r2.metric("Total Investi", format_currency(capital_investi))
        col_r3.metric("Intérêts Gagnés", format_currency(capital_courant - capital_investi), delta="Profit")
        
        import plotly.express as px
        fig_proj = px.bar(
            df_proj, 
            x="Année", 
            y=["Capital Investi", "Intérêts Générés"],
            title="Croissance de votre épargne dans le temps",
            labels={"value": "Montant Cumulé ($)", "variable": "Composante"},
            barmode="stack",
            color_discrete_map={"Capital Investi": "#3498db", "Intérêts Générés": "#2ecc71"}
        )
        fig_proj.update_layout(margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_proj, use_container_width=True)

    with onglet2:
        st.subheader("Allocation d'Actifs Idéale")
        st.markdown("Découvrez la répartition recommandée pour votre portefeuille.")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            montant_k = st.number_input("Montant total à investir ($)", min_value=0.0, value=10000.0, step=1000.0)
        with col_p2:
            age = st.slider("Âge pour le modèle", min_value=18, max_value=80, value=30)
            
        allocations = {
            25: {"Cash": 5, "Obligations": 5, "Immobilier": 10, "Actions": 80},
            30: {"Cash": 5, "Obligations": 10, "Immobilier": 15, "Actions": 70},
            35: {"Cash": 5, "Obligations": 15, "Immobilier": 20, "Actions": 60},
            40: {"Cash": 10, "Obligations": 20, "Immobilier": 20, "Actions": 50},
            45: {"Cash": 10, "Obligations": 25, "Immobilier": 25, "Actions": 40},
            50: {"Cash": 10, "Obligations": 30, "Immobilier": 25, "Actions": 35},
            55: {"Cash": 10, "Obligations": 35, "Immobilier": 25, "Actions": 30},
            60: {"Cash": 15, "Obligations": 40, "Immobilier": 25, "Actions": 20},
        }
        
        # Calculate appropriate tranche
        tranche = 60 if age >= 60 else max([k for k in allocations.keys() if k <= age]) if age >= 25 else 25
        allocation = allocations[tranche]

        st.info(f"📌 Profil basé sur la tranche d'âge : **{tranche} ans et plus**")

        df_alloc = pd.DataFrame({
            "Classe d'Actifs": list(allocation.keys()),
            "Pourcentage": list(allocation.values()),
            "Montant Cible": [(v/100.0)*montant_k for v in allocation.values()]
        })
        
        df_alloc = df_alloc[df_alloc["Pourcentage"] > 0]

        colors = {"Cash": "#2ecc71", "Obligations": "#3498db", "Immobilier": "#9b59b6", "Actions": "#e74c3c"}
        
        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            fig_alloc = px.pie(
                df_alloc, 
                values="Pourcentage", 
                names="Classe d'Actifs",
                color="Classe d'Actifs",
                color_discrete_map=colors,
                hole=0.4
            )
            fig_alloc.update_traces(textposition='inside', textinfo='percent+label')
            fig_alloc.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_alloc, use_container_width=True)

        with col_g2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            df_table = df_alloc.copy()
            df_table["Pourcentage (%)"] = df_table["Pourcentage"].map("{:.1f}%".format)
            df_table["Cible Monétaire"] = df_table["Montant Cible"].apply(format_currency)
            st.dataframe(df_table[["Classe d'Actifs", "Pourcentage (%)", "Cible Monétaire"]], hide_index=True, use_container_width=True)

        st.caption("💡 **Note** : Ces allocations sont des recommandations générales. Consultez un conseiller pour un plan personnalisé.")

# --- Navigation ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Aller à :",
    ("Tableau de Bord", "Budget Mensuel", "Suivi des Dépenses", "Analyse des Dépenses", "Simulateurs & Projections")
)

if menu == "Tableau de Bord":
    afficher_tableau_de_bord()
elif menu == "Budget Mensuel":
    afficher_budget_mensuel()
elif menu == "Suivi des Dépenses":
    afficher_suivi_depenses()
elif menu == "Analyse des Dépenses":
    afficher_analyse_depenses()
elif menu == "Simulateurs & Projections":
    afficher_simulateurs()
