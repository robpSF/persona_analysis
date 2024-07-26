import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit application title
st.title("Persona Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the uploaded Excel file
    persona_details_df = pd.read_excel(uploaded_file)
    
    # Extract relevant columns
    factions = persona_details_df['Faction']
    tags = persona_details_df['Tags'].str.split(',', expand=True).stack()
    tags_with_factions = persona_details_df[['Faction', 'Tags']].copy()
    tags_with_factions = tags_with_factions.set_index('Faction')['Tags'].str.split(',', expand=True).stack().reset_index(name='Tag')

    # Chart (a): Horizontal bar chart of number of personas per Faction
    st.subheader("Number of Personas per Faction")
    faction_counts = factions.value_counts()
    fig, ax = plt.subplots()
    faction_counts.plot(kind='barh', ax=ax)
    ax.set_xlabel("Number of Personas")
    ax.set_ylabel("Faction")
    ax.set_title("Number of Personas per Faction")
    st.pyplot(fig)

    # Chart (b): Horizontal bar chart of number of personas per Tags
    st.subheader("Number of Personas per Tags")
    tag_counts = tags.value_counts()
    fig, ax = plt.subplots()
    tag_counts.plot(kind='barh', ax=ax)
    ax.set_xlabel("Number of Personas")
    ax.set_ylabel("Tags")
    ax.set_title("Number of Personas per Tags")
    st.pyplot(fig)

    # Chart (c): Number of Personas per Tags within each Faction
    st.subheader("Number of Personas per Tags within each Faction")
    tag_faction_counts = tags_with_factions.groupby(['Faction', 'Tag']).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(tag_faction_counts, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
    ax.set_xlabel("Tags")
    ax.set_ylabel("Faction")
    ax.set_title("Number of Personas per Tags within each Faction")
    st.pyplot(fig)
else:
    st.write("Please upload an Excel file to proceed.")
