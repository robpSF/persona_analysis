import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from io import BytesIO
from streamlit_folium import folium_static

# Streamlit application title
st.title("Persona Analysis Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the uploaded Excel file
    persona_details_df = pd.read_excel(uploaded_file)
    
    # Extract relevant columns
    factions = persona_details_df['Faction']
    tags_with_factions = persona_details_df[['Faction', 'Tags']].copy()
    tags_with_factions = tags_with_factions.set_index('Faction')['Tags'].str.split(',', expand=True).stack().reset_index(name='Tag')

    # Faction selection
    selected_factions = st.multiselect("Select Factions", options=factions.unique(), default=factions.unique())

    # Filter data based on selected factions
    def filter_data(df, factions):
        filtered_df = df[df['Faction'].isin(factions)]
        filtered_tags_df = filtered_df[['Faction', 'Tags']].copy()
        filtered_tags_df = filtered_tags_df.set_index('Faction')['Tags'].str.split(',', expand=True).stack().reset_index(name='Tag')
        return filtered_df, filtered_tags_df

    filtered_persona_details_df, filtered_tags_with_factions = filter_data(persona_details_df, selected_factions)

    # Function to create charts
    def create_charts(filtered_tags_with_factions, factions, persona_details_df):
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
        tag_counts = filtered_tags_with_factions['Tag'].value_counts()
        fig, ax = plt.subplots()
        tag_counts.plot(kind='barh', ax=ax)
        ax.set_xlabel("Number of Personas")
        ax.set_ylabel("Tags")
        ax.set_title("Number of Personas per Tags")
        st.pyplot(fig)
        
        # Chart (c): Number of Personas per Tags within each Faction
        st.subheader("Number of Personas per Tags within each Faction")
        tag_faction_counts = filtered_tags_with_factions.groupby(['Faction', 'Tag']).size().unstack(fill_value=0)

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
        
        # Chart (d): Number of audience segments
        st.subheader("Number of Audience Segments")
        segment_counts = persona_details_df['Tags'].value_counts()
        fig, ax = plt.subplots()
        segment_counts.plot(kind='barh', ax=ax)
        ax.set_xlabel("Number of Personas")
        ax.set_ylabel("Audience Segments")
        ax.set_title("Number of Audience Segments")
        st.pyplot(fig)

        # Multi-select tag filter for heatmap
        all_tags = sorted(filtered_tags_with_factions['Tag'].unique())
        selected_tags = st.multiselect("Select Tags for Heatmap", options=all_tags, default=all_tags)

        # Chart (e): Heatmap of tag combinations
        st.subheader("Heatmap of Tag Combinations")
        tags_expanded = persona_details_df['Tags'].str.get_dummies(sep=',')
        tags_expanded = tags_expanded[selected_tags]  # Filter selected tags
        co_occurrence_matrix = tags_expanded.T.dot(tags_expanded)
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(co_occurrence_matrix, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
        ax.set_xlabel("Tags")
        ax.set_ylabel("Tags")
        ax.set_title("Heatmap of Tag Combinations")
        st.pyplot(fig)

        # Table with Name, Handle, Faction, Tags, Bio
        st.subheader("Persona Details")
        st.dataframe(persona_details_df[['Name', 'Handle', 'Faction', 'Tags', 'Bio']])

        # Map with GPS coordinates and Image column
        st.subheader("Map of Personas")

        # Filter out rows without valid GPS data
        valid_gps = persona_details_df.dropna(subset=['GPS'])
        valid_gps[['lat', 'lon']] = valid_gps['GPS'].str.split(',', expand=True).astype(float)

        # Create a Folium map
        m = folium.Map(location=[valid_gps['lat'].mean(), valid_gps['lon'].mean()], zoom_start=3)

        # Add pins to the map
        for idx, row in valid_gps.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(f"<b>{row['Name']}</b><br>{row['Handle']}<br>{row['Faction']}<br>{row['Tags']}", max_width=300),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

        # Display the map
        folium_static(m)

    # Initial chart creation
    create_charts(filtered_tags_with_factions, factions, filtered_persona_details_df)

    # Search and replace tags
    st.subheader("Search and Replace Tags")
    search_tag = st.text_input("Tag to search for")
    replace_tag = st.text_input("Tag to replace with")
    
    if st.button("Replace Tags"):
        if search_tag and replace_tag:
            # Perform the replacement
            def replace_tags(tags, search, replace):
                if pd.isna(tags):
                    return tags
                updated_tags = [replace if tag == search else tag for tag in tags.split(',')]
                unique_tags = list(dict.fromkeys(updated_tags))  # Remove duplicates while preserving order
                return ','.join(unique_tags)

            persona_details_df['Tags'] = persona_details_df['Tags'].apply(lambda x: replace_tags(x, search_tag, replace_tag))
            st.success(f"Replaced '{search_tag}' with '{replace_tag}' in tags.")
            
            # Filter data again after replacement
            filtered_persona_details_df, filtered_tags_with_factions = filter_data(persona_details_df, selected_factions)
            
            # Recreate charts with updated tags
            create_charts(filtered_tags_with_factions, factions, filtered_persona_details_df)
        else:
            st.error("Please provide both search and replace tags.")

    # Export modified DataFrame to Excel
    st.subheader("Export Modified Data")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        persona_details_df.to_excel(writer, index=False, sheet_name='Sheet1')
    buffer.seek(0)
    st.download_button(
        label="Download Excel file",
        data=buffer,
        file_name="modified_persona_details.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.write("Please upload an Excel file to proceed.")
