import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

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

    # Set font size for charts
    plt.rcParams.update({'font.size': 8})

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

    # Use Plotly for the heatmap with hover functionality
    fig = px.imshow(
        tag_faction_counts,
        labels=dict(x="Tags", y="Faction", color="Number of Personas"),
        x=tag_faction_counts.columns,
        y=tag_faction_counts.index,
        color_continuous_scale="YlGnBu",
        text_auto=False
    )

    fig.update_traces(
        hovertemplate="<b>Faction: %{y}</b><br>Tag: %{x}<br>Number of Personas: %{z}<extra></extra>"
    )

    fig.update_layout(
        title="Number of Personas per Tags within each Faction",
        xaxis_title="Tags",
        yaxis_title="Faction",
        font=dict(size=8)
    )

    st.plotly_chart(fig)
else:
    st.write("Please upload an Excel file to proceed.")
