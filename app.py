import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Finances Personnelles", page_icon="💰", layout="wide")

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
        st.metric("Revenus du mois", f"{revenus:,.2f} $".replace(",", " "))
    with col2:
        st.metric("Dépenses totales", f"{depenses:,.2f} $".replace(",", " "), delta=f"-{depenses} $", delta_color="inverse")
    with col3:
        st.metric("Argent restant", f"{restant:,.2f} $".replace(",", " "), delta=f"{restant} $")
        
    st.markdown("---")
    
    # --- Progression du budget ---
    st.subheader("🎯 Progression du budget")
    st.progress(progression)
    st.caption(f"Vos dépenses représentent **{progression:.1%}** de votre budget de **{budget_max} $** ce mois-ci.")
    
    if progression >= 1.0:
        st.error("⚠️ Vous avez dépassé votre budget !")
    elif progression >= 0.8:
        st.warning("⚠️ Attention, vous vous approchez de votre limite de budget.")
    else:
        st.success("✅ Vos dépenses sont bien maîtrisées !")
        
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
    col_res1.metric("Revenus", f"{revenus:,.2f} $".replace(",", " "))
    col_res2.metric("Dépenses Totales", f"{depenses_totales:,.2f} $".replace(",", " "), delta=f"-{depenses_totales} $", delta_color="inverse")
    col_res3.metric("Argent Restant", f"{restant:,.2f} $".replace(",", " "), delta=f"{restant} $")
    
    # --- Budget Prévu ---
    st.markdown("---")
    st.subheader("🎯 Comparaison budget prévu")
    budget_prevu = st.number_input("Quel était votre budget total de dépenses prévu pour ce mois ? ($)", min_value=0.0, value=2500.0, step=100.0)
    
    difference = budget_prevu - depenses_totales
    
    if difference >= 0:
        st.success(f"✅ Vous êtes en dessous de votre budget de **{difference:,.2f} $**. Bon travail !".replace(",", " "))
    else:
        st.error(f"⚠️ Vous avez dépassé votre budget de **{abs(difference):,.2f} $**.".replace(",", " "))
    
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
    st.markdown("Saisissez et suivez vos dépenses au jour le jour.")
    
    # Initialize session state for expenses if it doesn't exist
    if 'depenses_list' not in st.session_state:
        st.session_state.depenses_list = pd.DataFrame(columns=["Date", "Catégorie", "Description", "Montant"])
        
    # Form for adding an expense
    with st.expander("➕ Ajouter une nouvelle dépense", expanded=True):
        with st.form("ajout_depense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                import datetime
                date_depense = st.date_input("Date", datetime.date.today())
                categorie = st.selectbox("Catégorie", ["Nourriture", "Transport", "Loyer", "Loisirs", "Santé", "Vêtements", "Factures", "Autre"])
                
            with col2:
                montant = st.number_input("Montant ($)", min_value=0.01, step=1.0, format="%.2f")
                description = st.text_input("Description (Optionnelle)")
                
            submit = st.form_submit_button("Ajouter la dépense")
            
            if submit:
                # Add to dataframe
                nouvelle_depense = pd.DataFrame({
                    "Date": [date_depense],
                    "Catégorie": [categorie],
                    "Description": [description],
                    "Montant": [montant]
                })
                # Using pd.concat instead of append since append is deprecated
                st.session_state.depenses_list = pd.concat([st.session_state.depenses_list, nouvelle_depense], ignore_index=True)
                st.success("Dépense ajoutée avec succès ! 🎉")

    st.markdown("---")
    
    # Show expenses and graph if there are any
    if not st.session_state.depenses_list.empty:
        st.subheader("📜 Historique des dépenses")
        
        # Afficher la table triée par date
        df_affichage = st.session_state.depenses_list.sort_values(by="Date", ascending=False)
        st.dataframe(
            df_affichage, 
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Montant": st.column_config.NumberColumn("Montant ($)", format="%.2f $")
            },
            hide_index=True
        )
        
        # Afficher les métriques
        total_depenses = st.session_state.depenses_list["Montant"].sum()
        st.metric("Total cumulé des dépenses", f"{total_depenses:,.2f} $".replace(",", " "))
        
        st.markdown("---")
        
        st.subheader("📊 Graphiques d'analyse")
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # Group by category for the graph
            df_group = st.session_state.depenses_list.groupby("Catégorie")["Montant"].sum().reset_index()
            
            fig = px.pie(
                df_group, 
                values="Montant", 
                names="Catégorie", 
                hole=0.4,
                title="Dépenses par catégorie"
            )
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_g2:
            # Bar chart over time
            df_time = st.session_state.depenses_list.groupby("Date")["Montant"].sum().reset_index()
            fig_bar = px.bar(
                df_time, 
                x="Date", 
                y="Montant",
                title="Dépenses par jour",
                text_auto='.2s'
            )
            fig_bar.update_layout(margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        # Bouton pour réinitialiser
        if st.button("🗑️ Effacer toutes les dépenses"):
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
    
    # 1. Comparaison mois précédent
    st.subheader("📅 Comparaison au mois précédent")
    
    col1, col2 = st.columns(2)
    mois_actuel_total = df["Montant"].sum()
    
    with col1:
        st.metric("Total des dépenses ce mois-ci", f"{mois_actuel_total:,.2f} $".replace(",", " "))
    with col2:
        mois_precedent = st.number_input("Entrez le total de vos dépenses du mois précédent ($)", min_value=0.0, value=0.0, step=50.0)
        
    if mois_precedent > 0:
        difference = mois_actuel_total - mois_precedent
        pourcentage = (difference / mois_precedent) * 100
        
        if difference > 0:
            st.error(f"📈 Vos dépenses ont augmenté de **{difference:,.2f} $** (+{pourcentage:.1f}%) par rapport au mois dernier.".replace(",", " "))
        elif difference < 0:
            st.success(f"📉 Vos dépenses ont diminué de **{abs(difference):,.2f} $** ({pourcentage:.1f}%) par rapport au mois dernier. Bravo !".replace(",", " "))
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


def afficher_allocation_actifs():
    st.title("📊 Allocation d'Actifs selon l'Âge")
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

    niveaux_risque = {
        "Cash": "Très Faible",
        "Obligations": "Faible",
        "Immobilier": "Moyen",
        "Actifs Alternatifs": "Moyen",
        "Actions": "Élevé"
    }

    st.subheader("👤 Entrez votre âge")
    age = st.slider("Âge", min_value=18, max_value=80, value=30)

    def get_age_bracket(age):
        if age < 28: return 25
        elif age < 33: return 30
        elif age < 38: return 35
        elif age < 43: return 40
        elif age < 48: return 45
        elif age < 53: return 50
        elif age < 58: return 55
        else: return 60

    tranche = get_age_bracket(age)
    allocation = allocations[tranche]

    if tranche == 60:
        st.info(f"📌 Tranche d'âge : **60 ans et plus**")
    else:
        st.info(f"📌 Tranche d'âge : **environ {tranche} ans**")

    st.subheader("🥧 Votre Allocation Recommandée")

    df = pd.DataFrame({
        "Classe d'Actifs": list(allocation.keys()),
        "Pourcentage": list(allocation.values()),
        "Niveau de Risque": [niveaux_risque[k] for k in allocation.keys()]
    })

    df = df[df["Pourcentage"] > 0]

    colors = {
        "Cash": "#2ecc71",
        "Obligations": "#3498db",
        "Immobilier": "#9b59b6",
        "Actifs Alternatifs": "#f39c12",
        "Actions": "#e74c3c"
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

    st.plotly_chart(fig, width='stretch')

    st.subheader("📋 Détail de l'Allocation")

    df_table = pd.DataFrame({
        "Classe d'Actifs": list(allocation.keys()),
        "Pourcentage": [f"{v}%" for v in allocation.values()],
        "Niveau de Risque": [niveaux_risque[k] for k in allocation.keys()]
    })

    st.dataframe(df_table, width='stretch', hide_index=True)

    st.markdown("---")
    st.caption("""
    💡 **Note** : Ces allocations sont des recommandations générales basées sur l'âge. 
    Votre situation personnelle peut nécessiter une allocation différente. Consultez un conseiller.
    """)

# --- Navigation ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Aller à :",
    ("Tableau de Bord", "Budget Mensuel", "Suivi des Dépenses", "Analyse des Dépenses", "Allocation d'Actifs")
)

if menu == "Tableau de Bord":
    afficher_tableau_de_bord()
elif menu == "Budget Mensuel":
    afficher_budget_mensuel()
elif menu == "Suivi des Dépenses":
    afficher_suivi_depenses()
elif menu == "Analyse des Dépenses":
    afficher_analyse_depenses()
elif menu == "Allocation d'Actifs":
    afficher_allocation_actifs()
