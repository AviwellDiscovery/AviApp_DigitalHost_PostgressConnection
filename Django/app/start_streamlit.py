from bokeh.embed import components
from bokeh.models import ColumnDataSource, WheelZoomTool, PanTool
from bokeh.plotting import figure
from django.contrib.auth import authenticate
import streamlit.components.v1 as components
from mpl_toolkits.mplot3d import Axes3D
#from ete3 import NCBITaxa, TreeStyle, Tree, faces, AttrFace
from django.views.decorators.csrf import csrf_exempt
import time
import streamlit as st
import psycopg2
import pandas as pd
import json  # TODO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests, sys
import re
import os
from django.core.wsgi import get_wsgi_application
import altair as alt
import plotly.express as px
from collections import Counter
import numpy as np
from streamlit.runtime.state import SessionState
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()


def fetch_study_names_and_ids():
    query = 'SELECT "idStudy", "StudyName" FROM public."Study"'
    df = pd.read_sql(query, conn)
    return df


def get_all_data_by_hostId(selected_study_ids, conn):
    study_ids_str = ', '.join(str(id) for id in selected_study_ids)
    query = f'''
    SELECT *
    FROM public."AbundanceFactTable" AS aft
    JOIN public."Sample" AS s ON s."IdSample" = aft."Sample_idSample"
    JOIN public."Host" AS h ON h."IdHost" = s."Host_idHost" where h."IdHost" in ({study_ids_str});
    '''
    df = pd.read_sql(query, conn)
    return df


def get_all_idHost_based_on_study_id(studyid, conn):
    # Fetch data from the database
    query = f'''
              select "IdHost" from public."Host" where "Study_idStudy" = {studyid}
        '''
    hostIds = pd.read_sql(query, conn)
    hostIds = set(hostIds['IdHost'].values.tolist())

    return hostIds


def filter_data(selected_study_ids, conn):
    # Fetch data from the database
    query = '''
        SELECT s."idStudy", s."StudyName", h.*
        FROM public."Study" s
        INNER JOIN public."Host" h ON s."idStudy" = h."Study_idStudy"
    '''
    data = pd.read_sql(query, conn)
    study_ids_str = ', '.join(str(id) for id in selected_study_ids)
    # this query concern only the feature from FeatureFactTable
    query_features_options_by_study_selected = f'''
    select  "FeatureName" from public."Feature" where "IdFeature" in(select DISTINCT "Feature_idFeature"
     from public."FeatureFactTable" where "Host_idHost" in (SELECT  DISTINCT h."IdHost"
        FROM public."Study" s
        INNER JOIN public."Host" h ON s."idStudy" = h."Study_idStudy"
        WHERE s."idStudy" in ({study_ids_str})))

    '''
    Feature_options_by_study_selected = pd.read_sql(query_features_options_by_study_selected, conn)
    # st.write(Feature_options_by_study_selected)

    # Filter data based on selected study IDs
    filtered_data = data[data['idStudy'].isin(selected_study_ids)]

    # Select the host IDs corresponding to the filtered data
    host_ids = filtered_data['IdHost'].unique()

    return filtered_data, host_ids, Feature_options_by_study_selected


def feature_pen_to_select(selected_study_name, conn):
    selected_study_names_str = ", ".join(["'{}'".format(name) for name in selected_study_name])
    # Fetch data from the database
    query_features_options_by_study_selected_from_pen = f'''
        SELECT DISTINCT "FeatureName"
        FROM public."Feature"
        WHERE "IdFeature" IN (
            SELECT "Feature_IdFeature"
            FROM "Pen_has_Feature"
            WHERE "Pen_IdPen" IN (
                SELECT DISTINCT "Pen_IdPen"
                FROM public."Host_has_Pen"
                WHERE "Host_IdHost" IN (
                    SELECT "IdHost"
                    FROM public."Host"
                    WHERE "Study_idStudy" IN (
                        SELECT "idStudy"
                        FROM public."Study"
                        WHERE "StudyName" IN ({selected_study_names_str})
                    )
                )
            )
        );
        '''
    data = pd.read_sql(query_features_options_by_study_selected_from_pen, conn)
    FeatureNamePen = data["FeatureName"]

    return FeatureNamePen


def clean_abundance_value(value):
    # Use a regular expression to remove non-numeric characters
    cleaned_value = re.sub(r'[^0-9.]', '', str(value))
    return cleaned_value


def logout():
    """Logs out the user by clearing session state."""
    st.session_state.clear()  # Clear all session state variables


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        user = authenticate(
            username=st.session_state['username'],
            password=st.session_state['password']
        )

        if (user is not None):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True


if check_password():
    st.title(f"Welcome to Aviwell's Streamlit App")

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        database="devdatabase_16_11",
        user="reda",
        password="1321",
        host="localhost",
        port="5432"
    )

    # Fetch Host data
    query_host = "SELECT * FROM public.\"Host\""
    query_study = "SELECT * FROM public.\"Study\""
    query_taxons = "SELECT * FROM public.\"Taxons\""

    df_host = pd.read_sql(query_host, conn)
    df_study = pd.read_sql(query_study, conn)
    df_taxons = pd.read_sql(query_taxons, conn)
    df_merged = pd.DataFrame
    # Dictionary to map Study Name to ID
    study_name_to_id = {
        "PROD2": 2,
        "DISCO1": 3,
        "PROD1": 1,
        "POC1": 4,
        "POC2": 5,
        "Trouts": 6
    }


    def page1():
        st.title("Check Host Information")
        st.write("Output form >> //IdHost - Tag - Sex- GrowthRoom - Study_id - Weight //")

        # Streamlit app code
        st.title("Choose Your Study and Sex ")

        # Fetch Host data with filters
        # selected_study_id = st.selectbox("Select Study ID", df_study['StudyName'].unique())
        selected_study_name = st.selectbox("Select Study Name", df_study['StudyName'].unique())

        # Get the selected_study_id based on the selected_study_name
        selected_study_id = study_name_to_id.get(selected_study_name)

        selected_sex = st.multiselect("Select Sex", df_host['Sex'].unique())

        # Filter Host data based on selected Study ID and Sex
        filtered_host_data = df_host[
            (df_host['Study_idStudy'] == selected_study_id) & (df_host['Sex'].isin(selected_sex))]

        # Convert 'Weight' column to dictionaries
        filtered_host_data['Weight'] = filtered_host_data['Weight'].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x)

        # Convert 'Weight' column to dictionaries
        filtered_host_data['Weight'] = filtered_host_data['Weight'].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x)

        if 'Weight' in filtered_host_data.columns and not filtered_host_data['Weight'].isnull().all():
            # Filter out rows with NaN values in 'Weight' column
            filtered_host_data = filtered_host_data.dropna(subset=['Weight'])

            # Expand 'Weight' dictionary into separate columns
            weight_data_expanded = pd.DataFrame(filtered_host_data['Weight'].tolist())

            # Reset the index of both DataFrames
            filtered_host_data = filtered_host_data.reset_index(drop=True)
            weight_data_expanded = weight_data_expanded.reset_index(drop=True)

            # Concatenate the original DataFrame with the expanded weight data
            filtered_host_data = pd.concat([filtered_host_data, weight_data_expanded], axis=1).drop(columns=['Weight'])

        # Count the number of rows in filtered_host_data
        num_rows = len(filtered_host_data)
        # Display filtered Host data
        st.write(f"## Host Data for Study: {selected_study_name} and Sex: {selected_sex}")
        st.write(f"Number of Rows: {num_rows}")
        st.dataframe(filtered_host_data, height=400)

        # Define a checkbox to toggle the section visibility
        filter_weights = st.checkbox("Filter on Weight Option")
        # Conditionally display the section based on the checkbox value
        if filter_weights:
            if selected_study_id == 3:
                # Add a sidebar with a slider for weight range
                weight_range_BirdWeight_D0 = st.slider("BirdWeight_D0", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                weight_range_BirdWeight_D9 = st.slider("BirdWeight_D9", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                weight_range_BirdWeight_D21 = st.slider("BirdWeight_D21", min_value=0.0, max_value=2.0,
                                                        value=(0.0, 2.0))
                weight_range_BirdWeight_D35 = st.slider("BirdWeight_D35", min_value=0.0, max_value=2.0,
                                                        value=(0.0, 3.0))

                # Filter based on weight ranges
                filtered_host_data_weight_range = filtered_host_data[
                    (filtered_host_data['BirdWeight_D0'] >= weight_range_BirdWeight_D0[0]) &
                    (filtered_host_data['BirdWeight_D0'] <= weight_range_BirdWeight_D0[1]) &
                    (filtered_host_data['BirdWeight_D9'] >= weight_range_BirdWeight_D9[0]) &
                    (filtered_host_data['BirdWeight_D9'] <= weight_range_BirdWeight_D9[1]) &
                    (filtered_host_data['BirdWeight_D21'] >= weight_range_BirdWeight_D21[0]) &
                    (filtered_host_data['BirdWeight_D21'] <= weight_range_BirdWeight_D21[1]) &
                    (filtered_host_data['BirdWeight_D35'] >= weight_range_BirdWeight_D35[0]) &
                    (filtered_host_data['BirdWeight_D35'] <= weight_range_BirdWeight_D35[1])
                    ]

                # Display the number of rows
                num_rows_range = len(filtered_host_data_weight_range)
                st.write(f"Number of Rows With Range Option: {num_rows_range}")

                # Display the filtered data
                st.dataframe(filtered_host_data_weight_range, height=400)

            if selected_study_id == 4:
                # Add a sidebar with a slider for weight range
                AvgBirdWeight_D0 = st.slider("AvgBirdWeight_D0", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                AvgBirdWeight_D7 = st.slider("AvgBirdWeight_D7", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                AvgBirdWeight_D14 = st.slider("AvgBirdWeight_D14", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                AvgBirdWeight_D21 = st.slider("AvgBirdWeight_D21", min_value=0.0, max_value=2.0, value=(0.0, 3.0))
                AvgBirdWeight_D28 = st.slider("AvgBirdWeight_D28", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                AvgBirdWeight_D35 = st.slider("AvgBirdWeight_D35", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                Bird_weight_D36 = st.slider("Bird_weight_D36", min_value=0.0, max_value=2.0, value=(0.0, 3.0))

                # Filter based on weight ranges
                filtered_host_data_weight_range = filtered_host_data[
                    (filtered_host_data['AvgBirdWeight_D0'] >= AvgBirdWeight_D0[0]) &
                    (filtered_host_data['AvgBirdWeight_D0'] <= AvgBirdWeight_D0[1]) &
                    (filtered_host_data['AvgBirdWeight_D7'] >= AvgBirdWeight_D7[0]) &
                    (filtered_host_data['AvgBirdWeight_D7'] <= AvgBirdWeight_D7[1]) &
                    (filtered_host_data['AvgBirdWeight_D14'] >= AvgBirdWeight_D14[0]) &
                    (filtered_host_data['AvgBirdWeight_D14'] <= AvgBirdWeight_D14[1]) &
                    (filtered_host_data['AvgBirdWeight_D21'] >= AvgBirdWeight_D21[0]) &
                    (filtered_host_data['AvgBirdWeight_D21'] <= AvgBirdWeight_D21[1]) &
                    (filtered_host_data['AvgBirdWeight_D28'] >= AvgBirdWeight_D28[0]) &
                    (filtered_host_data['AvgBirdWeight_D28'] <= AvgBirdWeight_D28[1]) &
                    (filtered_host_data['AvgBirdWeight_D35'] >= AvgBirdWeight_D35[0]) &
                    (filtered_host_data['AvgBirdWeight_D35'] <= AvgBirdWeight_D35[1]) &
                    (filtered_host_data['Bird_weight_D36'] >= Bird_weight_D36[0]) &
                    (filtered_host_data['Bird_weight_D36'] <= Bird_weight_D36[1])
                    ]

                # Display the number of rows
                num_rows_range = len(filtered_host_data_weight_range)
                st.write(f"Number of Rows With Range Option: {num_rows_range}")

                # Display the filtered data
                st.dataframe(filtered_host_data_weight_range, height=400)

        # Option to display features of a selected Host_id
        selected_host_id_feature = st.selectbox("Select Host ID to Display Features", filtered_host_data['IdHost'])

        # Fetch related Feature data for the selected Host from the connection table
        query_features = f"SELECT f.\"FeatureName\", ff.\"Value\" FROM public.\"FeatureFactTable\" ff JOIN public.\"Feature\" f ON ff.\"Feature_idFeature\" = f.\"IdFeature\" WHERE ff.\"Host_idHost\" = {selected_host_id_feature}"
        df_features = pd.read_sql(query_features, conn)

        # Display Features for the selected Host_id
        st.write(f"## Features for Host ID {selected_host_id_feature}")
        st.dataframe(df_features)

        # # Option to display features of a selected Host_id
        # selected_host_id_feature = st.selectbox("Select Host ID to Display Features", filtered_host_data['IdHost'])
        # query_features = f"SELECT * FROM public.\"FeatureFactTable\" WHERE \"Host_idHost\" = {selected_host_id_feature}"
        # df_features = pd.read_sql(query_features, conn)
        #
        # # Display Features for the selected Host_id
        # st.write(f"## Features for Host ID {selected_host_id_feature}")
        # st.dataframe(df_features)
        #
        #

        # Display Features for the selected Host_id as a bar chart
        st.write(f"## Feature Distribution for Host ID {selected_host_id_feature}")
        plt.figure(figsize=(10, 6))
        plt.bar(df_features["FeatureName"], df_features["Value"])
        plt.xlabel("Feature Name")
        plt.ylabel("Value")
        plt.title(f"Feature Distribution for Host ID {selected_host_id_feature}")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(plt)

        # Extract weight values for the selected host
        if selected_host_id_feature and selected_study_id == 3:
            weight_fields = ["BirdWeight_D0", "BirdWeight_D9", "BirdWeight_D21", "BirdWeight_D35"]

            # Extract weight values from JSON data
            weight_data = []
            for field in weight_fields:
                weights = filtered_host_data[field].tolist()
                weight_data.append(weights)

        # Add a checkbox to enable weight visualization
        show_weight_chart = st.checkbox("Show Weight Visualization")

        # ... (previous code)

        # Visualize weight if checkbox is selected
        # if show_weight_chart:
        #     st.title("Weight Visualization")
        #
        #     # Extract weight values for the selected hosts
        #     if selected_host_id_feature:
        #         weight_fields = ["BirdWeight_D0", "BirdWeight_D9", "BirdWeight_D21", "BirdWeight_D35"]
        #
        #         # Extract weight values from DataFrame
        #         weight_data = filtered_host_data[weight_fields]
        #
        #         # Display Weight data as a heatmap
        #         st.write(f"## Weight Evolution Heatmap")
        #         plt.figure(figsize=(10, 6))
        #         plt.imshow(weight_data, cmap='viridis', aspect='auto')
        #         plt.colorbar()
        #         plt.xlabel("Time")
        #         plt.ylabel("Host ID")
        #         plt.title(f"Weight Evolution Heatmap")
        #         plt.xticks(range(len(weight_fields)), weight_fields, rotation=45, ha="right")
        #         plt.yticks(range(len(weight_data)), weight_data.index)
        #         st.pyplot(plt)

        # Visualize weight if checkbox is selected
        if show_weight_chart:
            st.title("Weight Visualization")

            # Extract weight values for the selected hosts
            if selected_host_id_feature:
                weight_fields = ["BirdWeight_D0", "BirdWeight_D9", "BirdWeight_D21", "BirdWeight_D35"]
                weight_fields_study4 = ["AvgBirdWeight_D0", "AvgBirdWeight_D7", "AvgBirdWeight_D21",
                                        "AvgBirdWeight_D28",
                                        "AvgBirdWeight_D35", "Bird_weight_D36"]

                # Determine which weight fields to use based on selected study ID
                if selected_study_id == 3:
                    weight_fields = weight_fields
                elif selected_study_id == 4:
                    weight_fields = weight_fields_study4

                # Extract weight values from DataFrame
                weight_data = filtered_host_data.set_index("IdHost")[weight_fields]

                # Select multiple host IDs for comparison
                selected_host_ids = st.multiselect("Select Host IDs", weight_data.index)

                # Filter weight data for selected host IDs
                selected_weight_data = weight_data.loc[selected_host_ids]

                # Display Weight data as a line plot
                st.write(f"## Weight Evolution for Selected Host IDs")
                plt.figure(figsize=(10, 6))
                for idx, row in selected_weight_data.iterrows():
                    plt.plot(weight_fields, row, marker='o', label=f"Host ID {idx}")
                plt.xlabel("Time")
                plt.ylabel("Weight")
                plt.title(f"Weight Evolution for Selected Host IDs")
                plt.legend()
                plt.xticks(rotation=0, ha="center")
                st.pyplot(plt)

        # For example, you can add some text or visualizations here


    def split_taxonomy(taxonomy_string):
        taxonomy_list = taxonomy_string.split(";")
        return {
            'domain': taxonomy_list[0],
            'phylum': taxonomy_list[1],
            'class': taxonomy_list[2],
            'order': taxonomy_list[3],
            'family': taxonomy_list[4],
            'genus': taxonomy_list[5],
            'species': taxonomy_list[6]
        }


    def page2():
        # Dictionary to map Study Name to ID
        study_name_to_id = {
            "PROD2": 2,
            "DISCO1": 3,
            "PROD1": 1,
            "POC1": 4,
            "POC2": 5,
            "Trouts": 6
        }
        # Fetch Item names for dropdown search
        query_items = "SELECT \"IdItem\", \"ItemName\" FROM public.\"Item\""
        df_items = pd.read_sql(query_items, conn)
        #### First section  ####
        ######################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#########################
        # show_data_item = st.checkbox("Show Abundance Data by Species (OTU)  #1")
        # if show_data_item:
        #     # Streamlit app code
        #     st.title("Abundance Search by Taxa and Study")
        #     # selected_study_id = st.selectbox("Select Study ID", df_study['StudyName'].unique())
        #     # selected_study_name = st.selectbox("Select Study Name", df_study['StudyName'].unique())
        #     selected_study_names = st.multiselect("Select Study Names", df_study['StudyName'].unique())
        #     selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
        #     # Add content specific to Page 2
        #     # Get the selected_study_id based on the selected_study_name
        #     # selected_study_id = study_name_to_id.get(selected_study_names)
        #
        #     # Search for Item by typing
        #     search_input = st.text_input("Search for OTU")
        #     filtered_items = df_items[df_items['ItemName'].str.contains(search_input, case=False)]
        #
        #     # # Search for Item by typing
        #     # taxonomy_search_input = st.text_input("Search by Taxonomy")    # Filter items based on user input
        #     # # Filter items based on Taxonomy search
        #     # if taxonomy_search_input:
        #     #     # Query to get Item_idItem based on Taxonomy
        #     #     query_taxonomy_search = f"""
        #     #         SELECT "Item_idItem"
        #     #         FROM public."Taxons"
        #     #         WHERE "Taxonomy" LIKE '%{taxonomy_search_input}%'
        #     #     """
        #     #     item_ids_from_taxonomy = pd.read_sql(query_taxonomy_search, conn)['Item_idItem']
        #     #
        #     #     # Filter items based on Item_idItem from Taxonomy search
        #     #     filtered_items_from_taxonomy = df_items[df_items['IdItem'].isin(item_ids_from_taxonomy)]
        #     #
        #     #     # Combine the results of both searches
        #     #     filtered_items = pd.concat([filtered_items, filtered_items_from_taxonomy])
        #
        #     # Select Study Name
        #     host_id_selectbox_key = f"host_id_selectbox_{selected_study_ids}"
        #
        #     # Get the selected_study_id based on the selected_study_name
        #     # selected_study_id = study_name_to_id.get(selected_study_names)
        #     selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
        #     selected_study_ids_str = ', '.join(map(str, selected_study_ids))
        #     if not filtered_items.empty and selected_study_ids:
        #         # Fetch Hosts related to the Study of interest
        #         query_hosts = f"""
        #             SELECT h."IdHost"
        #             FROM public."Host" h
        #             WHERE h."Study_idStudy" IN ({selected_study_ids_str})
        #         """
        #         hosts_in_study = pd.read_sql(query_hosts, conn)
        #
        #         # Fetch Samples related to the selected Hosts
        #         query_samples = f"""
        #             SELECT "IdItem" from Public."Item" where "IdItem" in (
        #             Select "Item_idItem" from Public."AbundanceFactTable" where "Sample_idSample" in (
        #             SELECT s."IdSample"
        #             FROM public."Sample" s
        #             WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}))
        #         """
        #         samples_in_study = pd.read_sql(query_samples, conn)
        #
        #         # Filter Item options based on available Samples
        #         filtered_items = filtered_items[filtered_items['IdItem'].isin(samples_in_study['IdItem'])]
        #
        #         # Display count of available options
        #         st.write(f"Number of available options: {len(filtered_items)}")
        #
        #         # Select Item from filtered options
        #         selected_item = st.selectbox("Select Item", filtered_items['ItemName'])
        #
        #         # Fetch Abundance data for the selected Item and StudyName
        #
        #         # Fetch Abundance data for the selected Item and StudyName
        #         query_abundance = f"""
        #             SELECT af."Sample_idSample", s."SampleName",s."Host_idHost", af."Abundance"
        #             FROM public."AbundanceFactTable" af
        #             JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
        #             JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
        #             WHERE i."ItemName" = '{selected_item}' AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
        #         """
        #         df_abundance = pd.read_sql(query_abundance, conn)
        #
        #         if not df_abundance.empty:
        #
        #             # Sort dataframe by abundance in descending order
        #             df_abundance_sorted = df_abundance.sort_values(by='Abundance', ascending=False)
        #
        #             # Show option to select top N items or show all using radio buttons
        #             options = [5, 10, 20, "All"]
        #             selected_option = st.radio("Show Abundance Data", options)
        #
        #             if selected_option == "All":
        #                 df_selected = df_abundance_sorted
        #             else:
        #                 top_n = int(selected_option)
        #                 df_selected = df_abundance_sorted.head(top_n)
        #
        #             # Display Abundance data for selected item
        #             st.write(f"## Abundance Data for OTU: {selected_item}")
        #             st.dataframe(df_selected)
        #
        #
        #         else:
        #             st.write("No abundance data available for the selected Otu.")
        #
        #         # Add a download button
        #         if not df_selected.empty:
        #             csv_export = df_selected.to_csv(index=False)
        #             file_name = f"abundance_data_{selected_item}_{selected_study_names}.csv"
        #             st.download_button(
        #                 label="Download data on csv",
        #                 data=csv_export,
        #                 file_name=file_name,
        #                 mime="text/csv"
        #             )
        #
        #         # Create a distribution plot for normalized abundance
        #         # st.dataframe(df_selected)
        #         # Create a distribution plot for normalized abundance
        #         if not df_selected.empty:
        #             # Convert 'Abundance' column to numeric (if it's not already)
        #             df_selected['Abundance'] = pd.to_numeric(df_selected['Abundance'], errors='coerce')
        #
        #             # Calculate normalized abundance
        #             total_abundance = df_selected['Abundance'].sum()
        #             normalized_abundance = df_selected['Abundance'] / total_abundance
        #
        #             plt.figure(figsize=(10, 6))
        #             sns.histplot(normalized_abundance, bins=20, kde=True)
        #             plt.title(f"Distribution of Normalized Abundance for {selected_item}")
        #             plt.xlabel("Normalized Abundance")
        #             plt.ylabel("Frequency")
        #             st.pyplot(plt)
        #
        #         if not df_selected.empty:
        #             # Convert 'Abundance' column to numeric (if it's not already)
        #             df_selected['Abundance'] = pd.to_numeric(df_selected['Abundance'], errors='coerce')
        #
        #             # Calculate normalized abundance
        #             total_abundance = df_selected['Abundance'].sum()
        #             df_selected['NormalizedAbundance'] = df_selected['Abundance'] / total_abundance
        #
        #             # Create an interactive bar plot using Plotly Express
        #             fig = px.bar(
        #                 df_selected,
        #                 x='NormalizedAbundance',
        #                 color='SampleName',  # Color bars by SampleName
        #                 title=f"Distribution of Normalized Abundance for {selected_item}",
        #                 labels={'NormalizedAbundance': 'Normalized Abundance'},
        #             )
        #             st.plotly_chart(fig)
        #
        #         # todo
        #         st.write(f"## Relative Abundance V2")
        #         # Calculate total abundance for the selected bacterium
        #         total_abundance_bacterium = df_selected['Abundance'].sum()
        #
        #         # Calculate relative abundance
        #         df_selected['RelativeAbundance'] = (df_selected['Abundance'] / total_abundance_bacterium) * 100
        #
        #         # Create an interactive bar plot
        #         fig = px.bar(
        #             df_selected,
        #             x='SampleName',
        #             y='RelativeAbundance',
        #             title=f"Relative Abundance of {selected_item}",
        #             labels={'RelativeAbundance': 'Relative Abundance (%)'},
        #         )
        #         fig.update_yaxes(range=[0, 100])  # Set y-axis range to 0-100 percent
        #
        #         # Show the plot
        #         st.plotly_chart(fig)
        #
        #         # Get the Item_idItem for the selected item
        #         query_item_id = f"""
        #             SELECT "IdItem" FROM public."Item"
        #             WHERE "ItemName" = '{selected_item}'
        #         """
        #         item_id = pd.read_sql(query_item_id, conn)['IdItem'].iloc[0]
        #         # Fetch Taxonomy information for the selected Item
        #         query_taxonomy = f"""
        #                SELECT DISTINCT t."Taxonomy"
        #                FROM public."Taxons" t
        #                JOIN public."Item" i ON t."Item_idItem" = i."IdItem"
        #                WHERE i."ItemName" = '{selected_item}'
        #            """
        #         df_taxonomy = pd.read_sql(query_taxonomy, conn)
        #         df_abundance_sorted = df_abundance.sort_values(by='Abundance', ascending=False)
        #
        #         # Display Abundance data for selected item
        #         st.write(f"## Abundance Data for Item: {selected_item}")
        #         st.dataframe(df_selected)
        #
        #         # Display Taxonomy information
        #         if not df_taxonomy.empty:
        #             st.write(f"## Taxonomy Information for Item: {selected_item}")
        #             st.dataframe(df_taxonomy)
        #
        #             # Add the number of distinct lines in Taxonomy
        #             num_distinct_lines = len(df_taxonomy['Taxonomy'].unique())
        #             st.write(f"Number of Distinct Taxonomy Lines: {num_distinct_lines}")

        # todo
        # Second section
        # ######################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#########################
        # show_data_Otu = st.checkbox("Show Abundance Data for Species Whith In Samples:  #2'")
        # #
        # if show_data_Otu:
        #     # Dropdown for selecting hierarchy level
        #     hierarchy_level = st.selectbox("Select Hierarchy Level",
        #                                    ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species",
        #                                     "Strain"])
        #
        #     # Search input for user to type a term
        #     search_input = st.text_input("Type the Entry for search")
        #
        #     # Search button
        #     search_button = st.button("Search ")
        #     if search_button:
        #         # Execute search when button is clicked
        #         search_term = search_input.strip()
        #
        #         #######
        #         if search_button:
        #             # Execute search when the button is clicked
        #             search_term = search_input.strip()
        #
        #             if search_term:
        #                 # Split taxonomy string by semicolon
        #                 df_taxonomy = pd.read_sql("SELECT  \"Item_idItem\",\"Taxonomy\" FROM public.\"Taxons\"", conn)
        #                 df_taxonomy["Taxonomy"] = df_taxonomy["Taxonomy"].str.split(";")
        #
        #                 # Map the user's selection to the corresponding position in the split Taxonomy list
        #                 position = {
        #                     "Domain": 0,
        #                     "Phylum": 1,
        #                     "Class": 2,
        #                     "Order": 3,
        #                     "Family": 4,
        #                     "Genus": 5,
        #                     "Species": 6,
        #                     "Strain": 7
        #                 }.get(hierarchy_level)
        #
        #                 if position is not None:
        #                     # Filter Taxonomy based on the search term (contains)
        #                     df_filtered_taxonomy = df_taxonomy[
        #                         df_taxonomy["Taxonomy"].str[position].str.contains(search_term, case=False, na=False)]
        #
        #                     count = len(df_filtered_taxonomy)
        #                     if not df_filtered_taxonomy.empty:
        #                         # Display Taxonomy information
        #                         st.write(f"## Taxonomy Information for {search_term}")
        #                         st.dataframe(df_filtered_taxonomy)
        #                         st.write(f"Number of Lines: {count}")
        #
        #                         # Get Item_idItem for the selected entry
        #                         item_ids = df_filtered_taxonomy["Item_idItem"].tolist()
        #
        #                         # Fetch abundance data from AbundanceFactTable for all samples, including SampleName
        #                         query_abundance_all_samples = f"""
        #                             SELECT A."Abundance", S."SampleName"
        #                             FROM public."AbundanceFactTable" A
        #                             INNER JOIN public."Sample" S ON A."Sample_idSample" = S."IdSample"
        #                             WHERE A."Item_idItem" IN ({', '.join(map(str, item_ids))})
        #                         """
        #                         df_abundance_all_samples = pd.read_sql(query_abundance_all_samples, conn)
        #
        #                         if not df_abundance_all_samples.empty:
        #                             # Display Abundance data across all samples
        #                             st.write(f"## Abundance Data Across All Samples for {search_term}")
        #
        #                             # Create a bar chart using Altair
        #                             chart = alt.Chart(df_abundance_all_samples).mark_bar().encode(
        #                                 x=alt.X('SampleName:N', title='Sample Name', axis=alt.Axis(labelAngle=45)),
        #                                 # Rotate x-axis labels
        #                                 y='Abundance:Q',
        #                                 tooltip=['SampleName:N', alt.Tooltip('Abundance:Q', title='Abundance')]
        #                             ).properties(
        #                                 width=600,
        #                                 height=400
        #                             )
        #
        #                             st.altair_chart(chart, use_container_width=True)
        #
        #                             # Aggregating data by taking the mean for each sample
        #                             df_aggregated = df_abundance_all_samples.groupby('SampleName').mean().reset_index()
        #
        #                             # Sort the DataFrame by abundance in descending order
        #                             df_sorted = df_aggregated.sort_values(by='Abundance', ascending=False)
        #
        #                             # Select the top N samples (e.g., top 50)
        #                             top_n = 50
        #                             df_top_n = df_sorted.head(top_n)
        #
        #                             # Creating a bar chart with a fixed y-axis scale for the top N samples
        #                             chart = alt.Chart(df_top_n).mark_bar().encode(
        #                                 x=alt.X('SampleName:N', title='Sample Name', axis=alt.Axis(labelAngle=45)),
        #                                 y=alt.Y('Abundance:Q', title='Mean Abundance'),
        #                                 tooltip=['SampleName:N', alt.Tooltip('Abundance:Q', title='Mean Abundance')],
        #                                 color=alt.condition(
        #                                     alt.datum.Abundance > 0,
        #                                     alt.value('steelblue'),
        #                                     alt.value('lightgray')
        #                                 )
        #                             ).properties(
        #                                 width=800,
        #                                 height=400
        #                             ).interactive()
        #
        #                             st.altair_chart(chart, use_container_width=True)
        #
        #                         else:
        #                             st.write(f"No abundance data found for {search_term} across all samples.")
        #                     else:
        #                         st.write(f"No taxonomy information found for {search_term}.")
        #                 else:
        #                     st.write("Invalid hierarchy level selected.")
        #             else:
        #                 st.write("Please enter a search term.")

        ######################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#########################

        # Checkbox with styled title and adjusted spacing

        show_data_item = st.checkbox("Show Absolute & Relative Abundance/Sample by Multi selection on (OTU) ")
        # Collect data for all selected items
        if show_data_item:
            # Streamlit app code
            st.title('_Abundance Search by Taxa and Study_')
            # selected_study_id = st.selectbox("Select Study ID", df_study['StudyName'].unique())
            # selected_study_name = st.selectbox("Select Study Name", df_study['StudyName'].unique())
            selected_study_names = st.multiselect("Select Study Names", df_study['StudyName'].unique())
            selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
            # Add content specific to Page 2
            # Get the selected_study_id based on the selected_study_name
            # selected_study_id = study_name_to_id.get(selected_study_names)

            # Search for Item by typing
            # search_input = st.text_input("Search for OTU")
            search_input = st.text_input("Search for OTU (comma-separated)")
            search_terms = [term.strip() for term in search_input.split(',') if term.strip()]  # Split terms by comma

            # filtered_items = df_items[df_items['ItemName'].str.contains(search_input, case=False)]
            filtered_items = df_items[df_items['ItemName'].str.contains('|'.join(search_terms), case=False)]

            # Select Study Name
            host_id_selectbox_key = f"host_id_selectbox_{selected_study_ids}"

            # Get the selected_study_id based on the selected_study_name
            # selected_study_id = study_name_to_id.get(selected_study_names)
            selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
            selected_study_ids_str = ', '.join(map(str, selected_study_ids))
            if not filtered_items.empty and selected_study_ids:
                query_abundance_all = f"""
                    SELECT s."SampleName", i."ItemName", af."Sample_idSample", af."Item_idItem", af."Abundance"
                    FROM public."AbundanceFactTable" af
                    JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                    JOIN public."Item" i ON af."Item_idItem" = i."IdItem"

                """
                df_abundance_all = pd.read_sql(query_abundance_all, conn)

                # Fetch Hosts related to the Study of interest
                if selected_study_ids_str:
                    query_hosts = f"""
                                SELECT h."IdHost"
                                FROM public."Host" h
                                WHERE h."Study_idStudy" IN ({selected_study_ids_str})
                            """
                    hosts_in_study = pd.read_sql(query_hosts, conn)

                # Fetch Samples related to the selected Hosts
                # Make the link with the related host to the study of interest so we got only sample related to selected studies
                query_items = f"""
                            SELECT "IdItem" from Public."Item" where "IdItem" in ( 
                            Select "Item_idItem" from Public."AbundanceFactTable" where "Sample_idSample" in ( 
                            SELECT s."IdSample"
                            FROM public."Sample" s
                            WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}))
                        """
                item_in_study = pd.read_sql(query_items, conn)

                # Filter Item options based on available Samples
                filtered_items = filtered_items[filtered_items['IdItem'].isin(item_in_study['IdItem'])]

                # Display count of available options
                st.write(f"Number of available options: {len(filtered_items)}")

                # Select Item from filtered options
                # selected_item = st.selectbox("Select Item", filtered_items['ItemName'])
                selected_items = st.multiselect("Select Items", filtered_items['ItemName'])

                # Check if at least two items are selected
                if len(selected_items) < 2:
                    st.warning("Please select at least two items.")
                    st.stop()

                # Convert the list of selected items to a tuple for use in the SQL query
                selected_items_tuple = tuple(selected_items)

                # Fetch Abundance data for the selected Item and StudyName

                # Fetch Abundance data for the selected Item and StudyName
                # if selected_items:
                #     # Convert the list of selected items to a tuple for use in the SQL query
                #     selected_items_tuple = tuple(selected_items)
                #
                #     # Fetch Abundance data for the selected Item and StudyName
                #     query_abundance = f"""
                #         SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                #         FROM public."AbundanceFactTable" af
                #         JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                #         JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                #         WHERE i."ItemName" IN {selected_items_tuple} AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                #     """
                # else:
                #     # If no items are selected, construct a query without the IN clause
                #     query_abundance = f"""
                #         SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                #         FROM public."AbundanceFactTable" af
                #         JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                #         WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                #     """
                #
                # df_abundance = pd.read_sql(query_abundance, conn)
                # iterate throught the selected  items
                # Check if any items are selected before constructing the SQL query
                if selected_items:
                    for selected_item in selected_items:
                        # Convert the selected item to a tuple for use in the SQL query
                        selected_item_tuple = (selected_item,)

                        if selected_items:
                            # Convert the list of selected items to a tuple for use in the SQL query
                            selected_items_tuple = tuple(selected_items)

                            # Fetch Abundance data for the selected Item and StudyName
                            query_abundance = f"""
                                SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                                FROM public."AbundanceFactTable" af
                                JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                                JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                                WHERE i."ItemName" = '{selected_item}' AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                            """
                        else:
                            # If no items are selected, construct a query without the IN clause
                            query_abundance = f"""
                                SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                                FROM public."AbundanceFactTable" af
                                JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                                WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                            """
                        # Execute the query
                        df_abundance = pd.read_sql(query_abundance, conn)

                        # Sort the DataFrame in descending order by the 'Abundance' column
                        df_abundance = df_abundance.sort_values(by="Abundance", ascending=False)

                        # Display the dataframe with a title for each item
                        st.divider()
                        st.write(f"Table of abundnce for {selected_item}")
                        st.dataframe(df_abundance[["SampleName", "Abundance"]], hide_index=True)

                        # Display the count for each item
                        count = df_abundance.shape[0]
                        st.write(f"Count for {selected_item}: {count}")

                        # Allow the user to choose the number of most abundant values to visualize
                        num_most_abundant = st.slider(f"Select number of most abundant values for {selected_item}",
                                                      min_value=1, max_value=50, value=5)

                        # Sort the dataframe by abundance and select the top N values
                        df_top_abundance = df_abundance.sort_values(by="Abundance", ascending=False).head(
                            num_most_abundant)

                        # Create a bar chart
                        plt.figure(figsize=(10, 6))
                        plt.bar(df_top_abundance["SampleName"], df_top_abundance["Abundance"])
                        plt.xlabel("SampleName")
                        plt.ylabel("Abundance")
                        plt.title(f"Top {num_most_abundant} Abundances for {selected_item}")
                        plt.xticks(rotation=45, ha="right")

                        # Show the chart within the Streamlit app
                        st.pyplot(plt)

                else:
                    # Handle the case where no items are selected
                    st.warning("Please select at least one item.")

                # Collect data for all selected items
                all_data = []

                for selected_item in selected_items:
                    # Convert the selected item to a tuple for use in the SQL query
                    selected_item_tuple = (selected_item,)

                    # Your adapted SQL query
                    # Check if any items are selected before constructing the SQL query
                    if selected_items:
                        # Convert the list of selected items to a tuple for use in the SQL query
                        selected_items_tuple = tuple(selected_items)

                        # Fetch Abundance data for the selected Item and StudyName
                        query_abundance = f"""
                            SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                            FROM public."AbundanceFactTable" af
                            JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                            JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                            WHERE i."ItemName" IN {selected_items_tuple} AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                        """
                    else:
                        # If no items are selected, construct a query without the IN clause
                        query_abundance = f"""
                            SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                            FROM public."AbundanceFactTable" af
                            JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                            WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                        """
                    # Execute the query
                    df_abundance = pd.read_sql(query_abundance, conn)

                    # Sort the DataFrame in descending order by the 'Abundance' column
                    df_abundance = df_abundance.sort_values(by="Abundance", ascending=False)

                    # Append the data for the current item to the list
                    all_data.append((selected_item, df_abundance[["SampleName", "Abundance"]]))
                #
                if selected_items:
                    # Convert the list of selected items to a tuple for use in the SQL query
                    selected_items_tuple = tuple(selected_items)

                    # Fetch Abundance data for the selected Item and StudyName
                    query_abundance_a = f"""
                        SELECT i."ItemName", af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                        FROM public."AbundanceFactTable" af
                        JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                        JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                        WHERE i."ItemName" IN {selected_items_tuple} AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                    """
                else:
                    # If no items are selected, construct a query without the IN clause
                    query_abundance_a = f"""
                        SELECT i."ItemName", af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance"
                        FROM public."AbundanceFactTable" af
                        JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                        JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                        WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                    """

                # Execute the query
                df_abundance = pd.read_sql(query_abundance_a, conn)

                # Check if the DataFrame is empty
                if df_abundance.empty:
                    st.warning("No data found.")
                    st.stop()

                df_abundance = df_abundance.sort_values(by="Abundance", ascending=False)
                df_abundance = df_abundance.drop_duplicates(
                    subset=["ItemName", "Sample_idSample", "Host_idHost", "Abundance"])
                # Display the DataFrame
                df_to_work = df_abundance[["ItemName", "SampleName", "Abundance"]]
                # st.write("New DataFrame")
                # st.write(f"Number of lines{len(df_to_work)}")
                #
                # st.write(df_to_work)

                # Count the occurrences of each SampleName
                sample_name_counts = df_to_work['SampleName'].value_counts()

                # Filter the DataFrame to include only the rows where SampleName appears at least two times
                df_filtered_at_least_two_items = df_to_work[
                    df_to_work['SampleName'].isin(sample_name_counts.index[sample_name_counts >= 2])]
                df_filtered_at_least_two_items = df_filtered_at_least_two_items.sort_values(by='SampleName')
                # st.write(f"Number of lines{len(df_filtered_at_least_two_items)}")
                # st.write(df_filtered_at_least_two_items)
                # Fancy separation line
                st.markdown(
                    """
                    <style>
                        .separator {
                            width: 100%;
                            height: 3px;
                            background: linear-gradient(to right, #3498db, #2ecc71, #3498db);
                            margin: 20px 0;
                        }
                    </style>
                    <div class="separator"></div>
                    """,
                    unsafe_allow_html=True
                )
                # chart mixed absolute abundance
                # Assuming df_filtered_at_least_two_items is already filtered to include only samples with at least two occurrences
                st.markdown(f"##  Mixed Chart for \"{', '.join(map(str, selected_items))}\"")
                num_most_abundant = st.slider("Select number of most abundant values", min_value=1, max_value=50,
                                              value=5)

                # Select the top N values for each selected item
                df_top_abundance = df_filtered_at_least_two_items.groupby('ItemName').apply(
                    lambda x: x.nlargest(num_most_abundant, 'Abundance')).reset_index(drop=True)

                # Create a mixed chart with bars for each selected item
                plt.figure(figsize=(10, 6))
                # Assuming you have a list of selected items named selected_items
                for selected_item in selected_items:
                    # Filter data for the current selected item
                    df_selected_item = df_top_abundance[df_top_abundance['ItemName'] == selected_item]

                    # Create a bar chart for the selected item
                    plt.bar(df_selected_item["SampleName"], df_selected_item["Abundance"], label=selected_item)

                plt.xlabel("SampleName")
                plt.ylabel("Abundance")
                plt.title(f"Top {num_most_abundant} Abundances for Selected Items")
                plt.xticks(rotation=45, ha="right")
                plt.legend()

                # Show the chart within the Streamlit app
                st.pyplot(plt)
                st.write("Items Sharing at least into two Samples:")

                count = len(df_filtered_at_least_two_items)
                st.write(f"Number of Lines: {count}")
                st.write(df_filtered_at_least_two_items, hide_index=True)
                # Add a download button to download the grouped DataFrame as a CSV file
                csv_data = df_filtered_at_least_two_items.to_csv(index=False, encoding='utf-8')
                st.download_button(label="Download this DataFrame as CSV", data=csv_data,
                                   file_name='grouped_data_Item_sharing_at_least_one-SampleName.csv',
                                   mime='text/csv')

                # Display the dataframes for all selected items
                # for selected_item, df_item in all_data:
                #     # st.write(f"Table of abundance for {selected_item}")
                #     # st.dataframe(df_item)

                # New gtraph showing  By same sample
                # Filter items to include only those with at least one common SampleName
                selected_items_data = []
                # Get the Abundance for Selected Item sharing at least one sample Name
                # if all_data:
                #     all_data_df = pd.concat([df_item.assign(Item=selected_item) for selected_item, df_item in all_data],
                #                         ignore_index=True)
                #     all_data_df_sorted = all_data_df.sort_values(by='Abundance', ascending=False)
                # else:
                #     # Handle the case when all_data is empty
                #     st.warning("No data found in all_data.")
                #     st.stop()
                if all_data:
                    all_data_df = pd.concat([df_item.assign(Item=selected_item) for selected_item, df_item in all_data],
                                            ignore_index=True)
                    # Count the occurrences of each SampleName
                    sample_name_counts = all_data_df['SampleName'].value_counts()

                    # Filter rows where SampleName appears two or more times
                    all_data_df_filtered = all_data_df[
                        all_data_df['SampleName'].isin(sample_name_counts.index[sample_name_counts >= 2])]

                    all_data_df_sorted = all_data_df_filtered.sort_values(by='Abundance', ascending=False)
                else:
                    # Handle the case when all_data is empty
                    st.warning("No data found in all_data.")
                    # You can choose to stop the execution or continue with a default behavior
                    # st.stop()
                    # Continue with default behavior
                    all_data_df_sorted = pd.DataFrame(columns=["SampleName", "Abundance", "Item"])

                # Allow the user to choose the number of most abundant values to visualize
                st.divider()

                # Assuming `all_data_df` is your DataFrame with columns SampleName, Abundance, and Item
                # Count the occurrences of each SampleName
                sample_name_counts = all_data_df['SampleName'].value_counts()

                # Filter the DataFrame to include only rows where SampleName appears two or more times
                # st.write(all_data_df)
                # st.write(len(all_data_df))
                # st.write(df_filtered_at_least_two_items)
                # st.write(len(df_filtered_at_least_two_items))
                # st.write(len(df_to_work))
                # st.write(df_to_work)

                # df_to_work
                df_filtered_at_least_two_items.rename(columns={'ItemName': 'Item'}, inplace=True)

                filtered_df = all_data_df[
                    all_data_df['SampleName'].isin(sample_name_counts[sample_name_counts >= 2].index)]
                filtered_df = filtered_df.drop_duplicates(
                    subset=["SampleName", "Abundance", "Item"])
                # Print the count of each SampleName
                # st.write("SampleName Counts:")
                # for sample_name, count in sample_name_counts.items():
                #    st.write(f"{sample_name}: {count}")

                # Print the filtered DataFrame
                # st.write("\nFiltered DataFrame:")
                # st.write(filtered_df.head(num_most_abundant))  # Display only the top N rows for brevity
                # Fancy separation line
                st.markdown(
                    """
                    <style>
                        .separator {
                            width: 100%;
                            height: 3px;
                            background: linear-gradient(to right, #3498db, #2ecc71, #3498db);
                            margin: 20px 0;
                        }
                    </style>
                    <div class="separator"></div>
                    """,
                    unsafe_allow_html=True
                )

                # Your Streamlit app code after the separation

                # Small title
                st.markdown(
                    "<h3 style='text-align:center; color:#3498db;'>Absolute Abundance for Each Item through the Samples</h3>",
                    unsafe_allow_html=True)

                # New graph
                # Allow the user to choose the number of top N SampleNames based on total abundance
                num_top_sample_names = st.slider("Select number of top N SampleNames", min_value=1,
                                                 max_value=len(df_filtered_at_least_two_items['SampleName'].unique()),
                                                 value=5)

                # Calculate the total abundance for each SampleName
                total_abundance_per_sample = df_filtered_at_least_two_items.groupby('SampleName')[
                    'Abundance'].sum().reset_index()

                # Get the top N SampleNames based on total abundance
                top_sample_names = total_abundance_per_sample.nlargest(num_top_sample_names, 'Abundance')['SampleName']

                # Filter the DataFrame to include only the top N SampleNames
                filtered_df_top = df_filtered_at_least_two_items[
                    df_filtered_at_least_two_items['SampleName'].isin(top_sample_names)]

                # Create a grouped bar plot using Seaborn
                plt.figure(figsize=(12, 8))
                sns.barplot(data=filtered_df_top, x='SampleName', y='Abundance', hue='Item', palette='husl', dodge=True)

                # Customize the plot
                plt.xlabel("SampleName")
                plt.ylabel("Abundance")
                plt.title(f"Top {num_top_sample_names} SampleNames by Total Abundance, Abundances by Item")
                plt.xticks(rotation=45, ha="right")
                plt.legend(title='Item')

                # Show the chart within the Streamlit app
                st.pyplot(plt)

                # Create a DataFrame where you group by 'SampleName' and 'Item' to get the abundance for each combination
                grouped_df = filtered_df_top.groupby(['SampleName', 'Item'])['Abundance'].sum().reset_index()

                # Display the grouped DataFrame
                st.write("Grouped abundance for each Item By Sample Name")
                # Display the count of rows in the DataFrame
                st.write(f"Number of rows: {len(grouped_df)}")
                st.dataframe(grouped_df)
                # Add a download button to download the grouped DataFrame as a CSV file
                csv_data = grouped_df.to_csv(index=False, encoding='utf-8')
                st.download_button(label="Download this DataFrame as CSV", data=csv_data,
                                   file_name='grouped_data_Item_Abundance_through-SampleName.csv',
                                   mime='text/csv')

                # Relative abUNDANCE
                st.markdown(
                    """
                    <style>
                        .separator {
                            width: 100%;
                            height: 3px;
                            background: linear-gradient(to right, #3498db, #2ecc71, #3498db);
                            margin: 20px 0;
                        }
                    </style>
                    <div class="separator"></div>
                    """,
                    unsafe_allow_html=True
                )

                # Your Streamlit app code after the separation

                # Small title
                st.markdown(
                    "<h3 style='text-align:center; color:#3498db;'>Relative Abundance for Each Item through the Samples</h3>",
                    unsafe_allow_html=True)

                # Assuming df_abundance_all is your DataFrame
                df_abundance_all['total_abundance_through_sampleName'] = df_abundance_all.groupby('SampleName')[
                    'Abundance'].transform('sum')

                # Display the dataframe with the new column
                # st.write(df_abundance_all)
                # Create a new column for relative abundance
                df_abundance_all['relative_abundance'] = df_abundance_all['Abundance'] / df_abundance_all[
                    'total_abundance_through_sampleName']

                # Filter df_abundance_all based on selected_items_tuple
                filtered_df = df_abundance_all[df_abundance_all['ItemName'].isin(selected_items_tuple)]

                # Select specific columns to display
                selected_columns = ['SampleName', 'ItemName', 'Abundance', 'total_abundance_through_sampleName',
                                    'relative_abundance']

                # Assuming filtered_df is your DataFrame with 'ItemName', 'SampleName', and 'relative_abundance' columns

                # Assuming filtered_df is your DataFrame with 'ItemName', 'SampleName', and 'relative_abundance' columns

                max_relative_a = filtered_df['relative_abundance'].max()
                min_relative_a = filtered_df['relative_abundance'].max() / 1.5

                # Allow the user to choose the lower and upper bounds for relative abundance range
                lower_bound = st.slider("Select lower bound for relative abundance", key="lower_bound_slider",
                                        min_value=0.0, max_value=1.0, value=min_relative_a, step=0.01)
                upper_bound = st.slider("Select upper bound for relative abundance", key="upper_bound_slider",
                                        min_value=0.0, max_value=1.0, value=max_relative_a, step=0.01)

                # Filter the DataFrame to include only items within the specified relative abundance range
                filtered_df_within_range = filtered_df[
                    (filtered_df['relative_abundance'] >= lower_bound) & (
                            filtered_df['relative_abundance'] <= upper_bound)]

                # Sort the DataFrame by 'relative_abundance' in descending order
                filtered_df_within_range = filtered_df_within_range.sort_values(by='relative_abundance',
                                                                                ascending=False)

                # Create a grouped bar plot using Seaborn
                plt.figure(figsize=(12, 8))
                sns.barplot(data=filtered_df_within_range, x='SampleName', y='relative_abundance', hue='ItemName',
                            palette='husl', dodge=True)

                # Customize the plot
                plt.xlabel("SampleName")
                plt.ylabel("Relative Abundance")
                plt.title(f"Relative Abundance by Sample - Items between {lower_bound} and {upper_bound}")
                plt.xticks(rotation=45, ha="right")
                plt.legend(title='ItemName')

                # Show the chart within the Streamlit app
                st.pyplot(plt)

                # Create a strip plot using Seaborn
                plt.figure(figsize=(12, 8))
                sns.stripplot(data=filtered_df, x='ItemName', y='relative_abundance', palette='husl', jitter=True)

                # Customize the plot
                plt.xlabel("ItemName")
                plt.ylabel("Relative Abundance")
                plt.title(f"Strip Plot of Relative Abundance by Item")
                plt.xticks(rotation=45, ha="right")

                # Show the chart within the Streamlit app
                st.pyplot(plt)
                # Display the count of rows in the DataFrame
                st.write(f"Number of rows: {len(filtered_df)}")
                # Display the DataFrame with selected columns
                st.dataframe(filtered_df[selected_columns], hide_index=True)
                # Add a download button to download the grouped DataFrame as a CSV file
                csv_data = grouped_df.to_csv(index=False, encoding='utf-8')
                st.download_button(label="Download this DataFrame as CSV", data=csv_data,
                                   file_name='Relative_Abundance_of_Item_through-Sample.csv',
                                   mime='text/csv')
                st.divider()
                st.markdown(
                    """
                    <style>
                        .separator {
                            width: 100%;
                            height: 3px;
                            background: linear-gradient(to right, #3498db, #2ecc71, #3498db);
                            margin: 20px 0;
                        }
                    </style>
                    <div class="separator"></div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    "<h3 style='text-align:center; color:#3498db;'>Sunburst Plot</h3>",
                    unsafe_allow_html=True)

                fig = px.sunburst(filtered_df, path=['ItemName', 'SampleName'], values='relative_abundance')

                # Customize the plot
                # fig.update_layout(title=f"Sunburst Plot of Relative Abundance by Item and Sample")
                fig.update_layout(
                    title={
                        'text': "Sunburst Plot of Relative Abundance by Item and Sample",
                        'font': {'size': 20}
                    }
                )
                # Show the chart within the Streamlit app
                st.plotly_chart(fig)
                ###

                # Assuming filtered_df is your DataFrame with 'ItemName', 'SampleName', and 'relative_abundance' columns
                # Calculate the maximum value of 'relative_abundance' in the DataFrame
                max_relative_abundance = filtered_df['relative_abundance'].max()
                min_relative_abundance = filtered_df['relative_abundance'].min()

                # Allow the user to choose the threshold for relative abundance
                threshold_slider = st.slider("Select the threshold for relative abundance", key="threshold_slider",
                                             min_value=min_relative_abundance,
                                             max_value=max_relative_abundance, value=0.5, step=0.01)

                # Filter the DataFrame to include only items above the threshold
                filtered_df_above_threshold = filtered_df[filtered_df['relative_abundance'] > threshold_slider]

                # Check if the filtered DataFrame is not empty
                if not filtered_df_above_threshold.empty:
                    # Create a Sunburst plot using Plotly Express
                    fig = px.sunburst(filtered_df_above_threshold, path=['ItemName', 'SampleName'],
                                      values='relative_abundance')

                    # Customize the plot

                    fig.update_layout(
                        title={
                            'text': f"Sunburst Plot of Relative Abundance by Item and Sample above {threshold_slider}",
                            'font': {'size': 20}
                        }
                    )
                    # Show the chart within the Streamlit app
                    st.plotly_chart(fig)
                else:
                    # Display a message if no data is found above the threshold
                    st.warning(f"No data found above the threshold {threshold_slider}")

                ##"
                # Assuming df_abundance_all is your DataFrame with 'SampleName', 'ItemName', and 'Abundance' columns

                # Get unique SampleNames from the DataFrame
                all_sample_names = df_abundance_all['SampleName'].unique()

                # Allow the user to choose the SampleName from the existing options
                selected_sample_input = st.selectbox("Select SampleName", all_sample_names)

                # Debugging: Print the selected SampleName
                st.write(f"Selected SampleName: {selected_sample_input}")

                # Filter the DataFrame for the selected SampleName
                selected_sample_data = df_abundance_all[df_abundance_all['SampleName'] == selected_sample_input]

                # Check if the filtered DataFrame is not empty
                if not selected_sample_data.empty:
                    # Calculate total abundance for each Item in the selected SampleName
                    total_abundance_per_item = selected_sample_data.groupby('ItemName')['Abundance'].sum().reset_index()

                    # Calculate relative abundance for each Item
                    total_abundance_per_item['RelativeAbundance'] = total_abundance_per_item['Abundance'] / \
                                                                    total_abundance_per_item['Abundance'].sum()

                    # Sort the DataFrame by 'RelativeAbundance' in descending order
                    total_abundance_per_item = total_abundance_per_item.sort_values(by='RelativeAbundance',
                                                                                    ascending=False)

                    # Create a stacked bar chart using Plotly Express
                    fig = px.bar(total_abundance_per_item, x='ItemName', y='RelativeAbundance',
                                 title=f"Relative Abundance Composition for {selected_sample_input}",
                                 labels={'RelativeAbundance': 'Relative Abundance'},
                                 color='ItemName')

                    # Customize the plot
                    fig.update_layout(barmode='stack')

                    # Show the chart within the Streamlit app
                    st.plotly_chart(fig)
                else:
                    # Display a message if no data is found for the selected SampleName
                    st.warning(f"No data found for the selected SampleName: {selected_sample_input}")

                #
                st.write(selected_items_tuple)
                # Filter the DataFrame for the selected items
                # Assuming 'SampleName', 'ItemName', and 'RelativeAbundance' are columns in your DataFrame
                # Replace 'your_dataframe' with the actual variable name of your DataFrame
                # st.write(filtered_df_above_threshold)
                threshold_slider = st.slider("Select the threshold for relative abundance", key="threshold_slider_3d",
                                             min_value=min_relative_abundance,
                                             max_value=max_relative_abundance, value=0.5, step=0.001)

                # Filter the DataFrame to include only items above the threshold
                filtered_df_above_threshold = filtered_df[filtered_df['relative_abundance'] > threshold_slider]

                # Check if the filtered DataFrame is not empty
                if not filtered_df_above_threshold.empty:
                    # Customize the plot

                    # Assuming 'SampleName', 'ItemName', and 'relative_abundance' are columns in your DataFrame
                    fig = px.scatter_3d(filtered_df_above_threshold, x='SampleName', y='ItemName',
                                        z='relative_abundance',
                                        color='relative_abundance', size='relative_abundance',
                                        labels={'relative_abundance': 'relative_abundance'},
                                        color_continuous_scale='Viridis',  # Change 'Viridis' to the desired color scale
                                        )

                    # Customize the layout as needed
                    fig.update_layout(
                        scene=dict(zaxis=dict(range=[0, filtered_df_above_threshold['relative_abundance'].max()])),
                        title='3D Scatter Plot of Sample Relative Abundance by Item',
                        margin=dict(l=0, r=0, b=0, t=40))  # Adjust margins as needed

                    # Show the chart within the Streamlit app
                    st.plotly_chart(fig)
                else:
                    # Display a message if no data is found above the threshold
                    st.warning(f"No data found above the threshold {threshold_slider}")

        # if not df_abundance.empty:
        #
        #     # Sort dataframe by abundance in descending order
        #     df_abundance_sorted = df_abundance.sort_values(by='Abundance', ascending=False)
        #
        #     # Show option to select top N items or show all using radio buttons
        #     options = [5, 10, 20, "All"]
        #     selected_option = st.radio("Show Abundance Data", options)
        #
        #     if selected_option == "All":
        #         df_selected = df_abundance_sorted
        #     else:
        #         top_n = int(selected_option)
        #         df_selected = df_abundance_sorted.head(top_n)
        #
        #     # Display Abundance data for selected item
        #     st.write(f"## Abundance Data for OTU: {selected_items_tuple}")
        #     st.dataframe(df_selected)
        #
        #
        # else:
        #     st.write("No abundance data available for the selected Otu.")

        # Add a download button
        # if not df_selected.empty:
        #     csv_export = df_selected.to_csv(index=False)
        #     file_name = f"abundance_data_{selected_items_tuple}_{selected_study_names}.csv"
        #     st.download_button(
        #         label="Download data on csv",
        #         data=csv_export,
        #         file_name=file_name,
        #         mime="text/csv"
        #     )

        # # Create a distribution plot for normalized abundance
        # # st.dataframe(df_selected)
        # # Create a distribution plot for normalized abundance
        # if not df_selected.empty:
        #     # Convert 'Abundance' column to numeric (if it's not already)
        #     df_selected['Abundance'] = pd.to_numeric(df_selected['Abundance'], errors='coerce')
        #
        #     # Calculate normalized abundance
        #     total_abundance = df_selected['Abundance'].sum()
        #     normalized_abundance = df_selected['Abundance'] / total_abundance
        #
        #     plt.figure(figsize=(10, 6))
        #     sns.histplot(normalized_abundance, bins=20, kde=True)
        #     plt.title(f"Distribution of Normalized Abundance for {selected_items_tuple}")
        #     plt.xlabel("Normalized Abundance")
        #     plt.ylabel("Frequency")
        #     st.pyplot(plt)
        #
        # if not df_selected.empty:
        #     # Convert 'Abundance' column to numeric (if it's not already)
        #     df_selected['Abundance'] = pd.to_numeric(df_selected['Abundance'], errors='coerce')
        #
        #     # Calculate normalized abundance
        #     total_abundance = df_selected['Abundance'].sum()
        #     df_selected['NormalizedAbundance'] = df_selected['Abundance'] / total_abundance
        #
        #     # Create an interactive bar plot using Plotly Express
        #     fig = px.bar(
        #         df_selected,
        #         x='NormalizedAbundance',
        #         color='SampleName',  # Color bars by SampleName
        #         title=f"Distribution of Normalized Abundance for {selected_items_tuple}",
        #         labels={'NormalizedAbundance': 'Normalized Abundance'},
        #     )
        #     st.plotly_chart(fig)
        #
        # # todo
        # st.write(f"## Relative Abundance V2")
        # # Calculate total abundance for the selected bacterium
        # total_abundance_bacterium = df_selected['Abundance'].sum()
        #
        # # Calculate relative abundance
        # df_selected['RelativeAbundance'] = (df_selected['Abundance'] / total_abundance_bacterium) * 100
        #
        # # Create an interactive bar plot
        # fig = px.bar(
        #     df_selected,
        #     x='SampleName',
        #     y='RelativeAbundance',
        #     title=f"Relative Abundance of {selected_items_tuple}",
        #     labels={'RelativeAbundance': 'Relative Abundance (%)'},
        # )
        # fig.update_yaxes(range=[0, 100])  # Set y-axis range to 0-100 percent
        #
        # # Show the plot
        # st.plotly_chart(fig)
        #
        # # Get the Item_idItem for the selected item
        # query_item_id = f"""
        #             SELECT "IdItem" FROM public."Item"
        #             WHERE "ItemName" IN '{selected_items_tuple}'
        #         """
        # item_id = pd.read_sql(query_item_id, conn)['IdItem'].iloc[0]
        # # Fetch Taxonomy information for the selected Item
        # query_taxonomy = f"""
        #                SELECT DISTINCT t."Taxonomy"
        #                FROM public."Taxons" t
        #                JOIN public."Item" i ON t."Item_idItem" = i."IdItem"
        #                WHERE i."ItemName" IN '{selected_items_tuple}'
        #            """
        # df_taxonomy = pd.read_sql(query_taxonomy, conn)
        # df_abundance_sorted = df_abundance.sort_values(by='Abundance', ascending=False)
        #
        # # Display Abundance data for selected item
        # st.write(f"## Abundance Data for Item: {selected_items_tuple}")
        # st.dataframe(df_selected)
        #
        # # Display Taxonomy information
        # if not df_taxonomy.empty:
        #     st.write(f"## Taxonomy Information for Item: {selected_items_tuple}")
        #     st.dataframe(df_taxonomy)
        #
        #     # Add the number of distinct lines in Taxonomy
        #     num_distinct_lines = len(df_taxonomy['Taxonomy'].unique())
        #     st.write(f"Number of Distinct Taxonomy Lines: {num_distinct_lines}")
        #

        ####
        # select all otu to see the prevalence
        show_data_item_prevalence = st.checkbox("Show Prevalence based on the OTU ")

        # Collect data for all selected items
        if show_data_item_prevalence:
            st.title('_Prevalence values_')
            selected_study_names = st.multiselect("Select Study Names", df_study['StudyName'].unique())
            selected_study_ids = [study_name_to_id[name] for name in selected_study_names]

            # Fetch Hosts related to the Study of interest
            if selected_study_ids:
                query_hosts = f"""
                    SELECT h."IdHost"
                    FROM public."Host" h
                    WHERE h."Study_idStudy" IN ({', '.join(map(str, selected_study_ids))})
                """
                hosts_in_study = pd.read_sql(query_hosts, conn)

                # Fetch Samples related to the selected Hosts
                query_items = f"""
                    SELECT "IdItem" from Public."Item" where "IdItem" in ( 
                    Select "Item_idItem" from Public."AbundanceFactTable" where "Sample_idSample" in ( 
                    SELECT s."IdSample"
                    FROM public."Sample" s
                    WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}))
                """
                item_in_study = pd.read_sql(query_items, conn)

                # Filter Item options based on available Samples
                filtered_items = df_items[df_items['IdItem'].isin(item_in_study['IdItem'])]

                # Display count of available options
                st.write(f"Number of available options: {len(filtered_items)}")

                # Select Item from filtered options
                selected_items = st.multiselect("Select Items", filtered_items['ItemName'])

                # Fetch Abundance data for the selected Item and StudyName
                query_abundance_all = f"""
                    SELECT s."SampleName", i."ItemName", af."Sample_idSample", af."Item_idItem", af."Abundance"
                    FROM public."AbundanceFactTable" af
                    JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                    JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                """
                df_abundance_all = pd.read_sql(query_abundance_all, conn)

                # Get the unique OTUs (Items) from the DataFrame
                unique_otus = df_abundance_all['ItemName'].unique()
                all_sample_names = df_abundance_all['SampleName'].unique()

                # Create a list to store prevalence information
                prevalence_data = []

                # Iterate through each OTU and calculate its prevalence
                st.write("Start OTU Prevalence:")

                exclude_otu_word = st.text_input("Exclude OTUs containing some part of this word")

                # Filter OTUs based on the word provided
                if exclude_otu_word:
                    # Use the str.contains condition to filter OTUs containing some part of the word
                    df_abundance_all = df_abundance_all[
                        ~df_abundance_all['ItemName'].str.contains(exclude_otu_word, case=False)]

                for otu in unique_otus:
                    # Check if the OTU is present in each sample
                    otu_presence = df_abundance_all[df_abundance_all['ItemName'] == otu]['SampleName'].unique()

                    # Calculate prevalence as the proportion of samples with the OTU
                    prevalence = len(otu_presence) / len(all_sample_names)

                    # Only include OTUs with prevalence greater than 0
                    if prevalence > 0:
                        # Append the OTU and its prevalence to the list
                        prevalence_data.append({'OTU': otu, 'Prevalence': prevalence})

                # Create a DataFrame from the list
                prevalence_df = pd.DataFrame(prevalence_data)

                # Display the DataFrame with OTU prevalence
                st.write("OTU Prevalence:")
                st.dataframe(prevalence_df)

                # Add a line to display the count of lines in the DataFrame
                st.write(f"Total lines in DataFrame: {len(prevalence_df)}")

                prevalence_df_sorted = prevalence_df.sort_values(by='Prevalence', ascending=False)
                # Select only the top 20 OTUs
                prevalence_df = prevalence_df_sorted.head(20)

                # Bar Chart
                plt.figure(figsize=(12, 6))
                sns.barplot(x='OTU', y='Prevalence', data=prevalence_df)
                plt.title('Prevalence of OTUs')
                plt.xticks(rotation=45, ha='right')
                st.pyplot()  # Use st.pyplot() instead of plt.show()
                plt.clf()  # Clear the Matplotlib figure

                # Pie Chart (if applicable, suitable for a small number of OTUs)
                plt.figure(figsize=(8, 8))
                plt.pie(prevalence_df['Prevalence'], labels=prevalence_df['OTU'], autopct='%1.1f%%', startangle=90)
                plt.title('Distribution of OTU Prevalence')
                st.pyplot()  # Use st.pyplot() instead of plt.show()
                plt.clf()  # Clear the Matplotlib figure

                # Heatmap
                plt.figure(figsize=(12, 8))
                heatmap_data = prevalence_df.pivot_table(index='OTU', values='Prevalence', aggfunc='mean')
                sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True)
                plt.title('OTU Prevalence Heatmap')
                st.pyplot()  # Use st.pyplot() instead of plt.show()
                plt.clf()  # Clear the Matplotlib figure

                # Box Plot
                plt.figure(figsize=(12, 6))
                sns.boxplot(x='OTU', y='Prevalence', data=prevalence_df)
                plt.title('Distribution of OTU Prevalence')
                plt.xticks(rotation=45, ha='right')
                st.pyplot()  # Use st.pyplot() instead of plt.show()
                plt.clf()  # Clear the Matplotlib figure

                st.write(f"End of section")

        # 13/12/2023 section
        ######################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#########################
        show_data_Otu = st.checkbox("Show Abundance based on the Taxonomy : #2")
        if show_data_Otu:
            # Params
            position = None
            count_taxonomy = None
            selected_item_ids = None

            # Fetch Hosts related to the Study of interest
            selected_study_names = st.multiselect("Select Study Names", df_study['StudyName'].unique())
            selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
            selected_study_ids_str = ', '.join(map(str, selected_study_ids))

            if selected_study_ids_str:
                query_hosts = f"""
                                            SELECT h."IdHost"
                                            FROM public."Host" h
                                            WHERE h."Study_idStudy" IN ({selected_study_ids_str})
                                    """
                hosts_in_study = pd.read_sql(query_hosts, conn)

            # Queries ....
            df_taxonomy = pd.read_sql("SELECT  \"Item_idItem\",\"Taxonomy\" FROM public.\"Taxons\"", conn)

            # Dropdown for selecting taxonomy level
            hierarchy_level = st.selectbox("Select Taxonomy Level",
                                           ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species",
                                            "Cluster"])

            search_input = st.text_input("Search for Entry (comma-separated)")
            search_terms = [term.strip() for term in search_input.split(',') if term.strip()]  # Split terms by comma
            # Search input for the user to type a term
            # Multiselect example

            # Search button

            # Execute search when the button is clicked
            # search_term = search_input.strip()

            if search_terms:
                # Split taxonomy string by semicolon
                df_taxonomy["Taxonomy"] = df_taxonomy["Taxonomy"].str.split(";")

                # Map the user's selection to the corresponding position in the split Taxonomy list
                position = {
                    "Domain": 0,
                    "Phylum": 1,
                    "Class": 2,
                    "Order": 3,
                    "Family": 4,
                    "Genus": 5,
                    "Species": 6,
                    "Cluster": 7
                }.get(hierarchy_level)

                if position is not None:
                    # Filter Taxonomy based on search term (contains)
                    df_filtered_taxonomy = df_taxonomy[
                        df_taxonomy["Taxonomy"].str[position].str.contains('|'.join(search_terms), case=False,
                                                                           na=False)]

                    # df_filtered_taxonomy = df_taxonomy[
                    #     df_taxonomy["Taxonomy"].str[position].str.contains(search_term, case=False, na=False)]
                else:
                    st.stop()
                    st.write("Invalid hierarchy level selected.")

                if not df_filtered_taxonomy.empty:
                    count_taxonomy = len(df_filtered_taxonomy)
                    # Display Taxonomy information

                # Get unique values from the selected taxonomy level
                taxonomy_options = df_filtered_taxonomy["Taxonomy"].apply(
                    lambda x: x[position] if len(x) > position else "").unique()
                count_options_in_the_selected_Taxonomic_hierarchy_level = len(taxonomy_options)
                if count_taxonomy:
                    st.write(f"The count of Taxonomy found: {count_taxonomy}")
                st.write(
                    f"Number of options available for {hierarchy_level} level : {count_options_in_the_selected_Taxonomic_hierarchy_level}")

                selected_options = st.multiselect("Select Options", taxonomy_options)

                if selected_options:
                    st.write(f"Th selected Options are: {selected_options}")
                    df_filtered_taxonomy_from_options = df_taxonomy[
                        df_taxonomy["Taxonomy"].str[position].str.contains('|'.join(selected_options), case=False,
                                                                           na=False)]
                    # Create tuples of (Item_idItem, Taxonomy) for selected options
                    # selected_item_tuples = [(row["Item_idItem"], row["Taxonomy"]) for index, row in
                    #                         df_filtered_taxonomy_from_options.iterrows()]

                    selected_item_ids = df_filtered_taxonomy_from_options["Item_idItem"].tolist()
                    # st.write(f"Count Lines {len(df_filtered_taxonomy)}")
                    # st.write(df_filtered_taxonomy)
                    # Display the selected options
                    # st.write(f"Count Lines {len(df_filtered_taxonomy_from_options)}")
                    # st.write(df_filtered_taxonomy_from_options)
                    # st.write(selected_item_ids)

                st.write(
                    f"********** Options1: Relative/Abs abundance based on the item selected from the Taxonomy ********")
                # if selected_item_ids and hosts_in_study:
                if selected_item_ids is not None and hosts_in_study is not None and not df_filtered_taxonomy_from_options.empty:
                    # Convert the list of selected items to a tuple for use in the SQL query
                    # Display the selected options and corresponding Item_idItem values
                    selected_items_tuple = tuple(selected_options)
                    # st.write(hosts_in_study)

                    # Fetch Abundance data for the selected Item and StudyName
                    query_abundance_taxonomy = f"""
                                               SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance",  i."IdItem", i."ItemName"
                                               FROM public."AbundanceFactTable" af
                                               JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                                               JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                                               WHERE i."IdItem"  IN {tuple(selected_item_ids)} AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                                           """
                    # st.write(f""" SELECT af."Sample_idSample", s."SampleName", s."Host_idHost", af."Abundance",
                    # i."IdItem", i."ItemName" FROM public."AbundanceFactTable" af JOIN public."Sample" s ON
                    # af."Sample_idSample" = s."IdSample" JOIN public."Item" i ON af."Item_idItem" = i."IdItem" WHERE
                    # i."IdItem" IN {tuple(selected_item_ids)} AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                    #                        """)
                    # Execute the query
                    df_abundance = pd.read_sql(query_abundance_taxonomy, conn)
                    # st.write(f"Count of lines of merged df_abundance: {len(df_abundance)}")
                    # st.write(df_abundance)
                    # Check if the DataFrame is empty
                    if df_abundance.empty:
                        st.warning("No data found try to check the studies included.")
                        st.stop()

                    else:

                        # Merge dataframes based on the specified columns
                        merged_df = pd.merge(df_abundance, df_filtered_taxonomy_from_options, left_on="IdItem",
                                             right_on="Item_idItem", how="left")

                        # Drop the redundant column (Item_idItem) if needed
                        merged_df = merged_df.drop("Item_idItem", axis=1)

                        # Display the merged dataframe
                        # st.write(f"Count of lines of merged df: {len(merged_df)}")
                        # st.write(merged_df)
                        # do as the first option

                        merged_df = merged_df.sort_values(by="Abundance", ascending=False)
                        merged_df = merged_df.drop_duplicates(
                            subset=["ItemName", "Sample_idSample", "Host_idHost", "Abundance"])
                        # Display the DataFrame
                        df_to_work = merged_df[["ItemName", "SampleName", "Abundance", "Taxonomy"]]
                        # st.write("New DataFrame")
                        # st.write(f"Number of lines{len(df_to_work)}")
                        #
                        # st.write(df_to_work)

                        # Fancy separation line
                        st.markdown(
                            """
                            <style>
                                .separator {
                                    width: 100%;
                                    height: 3px;
                                    background: linear-gradient(to right, #3498db, #2ecc71, #3498db);
                                    margin: 20px 0;
                                }
                            </style>
                            <div class="separator"></div>
                            """,
                            unsafe_allow_html=True
                        )
                        # chart mixed absolute abundance
                        # Assuming df_filtered_at_least_two_items is already filtered to include only samples with at least two occurrences
                        #     #  TODO  based on the selected_item_ids bring the actual name of the ItemName
                        #
                        # Assuming 'IdItem' is the correct column name in df_abundance
                        filtered_items_ids_df = df_abundance[df_abundance['IdItem'].isin(selected_item_ids)]

                        # Extracting ItemName from the filtered DataFrame
                        selected_items_name = filtered_items_ids_df['ItemName'].tolist()

                        # Getting unique ItemName values
                        selected_items_name = filtered_items_ids_df['ItemName'].tolist()

                        unique_selected_item_names = list(set(selected_items_name))
                        # Create the taxonomy fields for the dataframe
                        # Split 'Taxonomy' column using semicolon as a separator

                        # Create column names dynamically based on the number of levels
                        column_names = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Cluster']

                        # # Rename columns
                        # merged_df['count_elements'] = merged_df['Taxonomy'].str.split().apply(len)

                        # # Check if 'Cluster' column is present in the original DataFrame
                        # has_cluster_column = 'Cluster' in df_split_taxonomy.columns
                        #
                        # # If 'Cluster' column is not present, add it with None values
                        # if not has_cluster_column:
                        #     df_split_taxonomy['Cluster'] = None
                        #
                        # # Concatenate the original DataFrame with the split values DataFrame
                        # df_taxonomy = pd.concat([df_taxonomy, df_split_taxonomy], axis=1)
                        merged_df['count_elements'] = merged_df['Taxonomy'].apply(len)
                        # Display the updated DataFrame

                        # st.write(f'Type of taxonomy_list: {type(merged_df["Taxonomy"])}')
                        ranks = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Cluster']

                        # Function to create the 'ranks' fields based on count_elements
                        def create_ranks(row):
                            ranks = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Cluster']
                            if row['count_elements'] == 7:
                                # If count_elements is 7, fill the fields with content split from Taxonomy
                                ranks_values = row['Taxonomy']
                                # Add None for Cluster if needed
                                ranks_values.extend([None] * (8 - len(ranks_values)))
                            elif row['count_elements'] == 8:
                                # If count_elements is 8, fill all the fields with content split from Taxonomy
                                ranks_values = row['Taxonomy']
                            else:
                                # Handle other cases if needed
                                ranks_values = [None] * 8

                            return pd.Series(ranks_values, index=ranks)

                        # Apply the custom function to create 'ranks' fields for merged_df
                        merged_df[ranks] = merged_df.apply(create_ranks, axis=1)

                        # Display the updated DataFrame
                        print(merged_df)
                        # Display the updated DataFrame
                        st.write(f"Count Lines {len(merged_df)}")

                        st.write(merged_df)
                        st.table(pd.DataFrame({"Column Names": list(merged_df.columns)}))
                        # Krona plot ete3 Ncbi lib

                    # Choose the order of taxonomy for sunburst plot
                    taxonomy_order = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Cluster']

                    # """""""""""""""""""""""""""""""###############################################################
                    # Choose the order of taxonomy for presentation
                    # Allow the user to choose a specific taxonomic order
                    st.title("Select the Most Abundant Samples for Taxonomic Composition Analysis")

                    selected_order = st.selectbox('Select Taxonomic Order', [None] + taxonomy_order,
                                                  key='taxonomic_options1_order')

                    if selected_order:

                        # Allow the user to choose the number of top samples
                        top_samples_count = st.slider('Choose the number of top samples', min_value=1,
                                                      max_value=30, value=5)

                        # Sort samples based on abundance and select the top samples
                        top_samples_df = merged_df.nlargest(top_samples_count, 'Abundance')

                        # Create an empty DataFrame to store the composition data
                        composition_df = pd.DataFrame(columns=[selected_order, 'SampleName', 'RelativeAbundance'])
                        # For each sample, calculate the taxonomic composition for the selected order
                        for sample in top_samples_df['SampleName']:
                            sample_df = merged_df[merged_df['SampleName'] == sample]
                            total_abundance = sample_df['Abundance'].sum()

                            # Group by the selected taxonomic order and calculate the sum of abundance for each
                            # group
                            grouped_df = sample_df.groupby(selected_order)['Abundance'].sum().reset_index()

                            # Normalize abundance values to get relative abundance
                            grouped_df['RelativeAbundance'] = grouped_df['Abundance'] / total_abundance

                            # Add the sample name to the DataFrame
                            grouped_df['SampleName'] = sample

                            # Append the results to the composition DataFrame
                            composition_df = pd.concat(
                                [composition_df, grouped_df[['SampleName', selected_order, 'RelativeAbundance']]])

                        # Create a grouped bar chart for the taxonomic composition
                        fig = px.bar(
                            composition_df,
                            x='SampleName',
                            y='RelativeAbundance',
                            color=selected_order,
                            title=f'Taxonomic Composition based on {selected_order} across Samples',
                            labels={'RelativeAbundance': 'Relative Abundance'},
                        )

                        # Display the bar chart
                        st.plotly_chart(fig)
                        #
                        # # Same options but user provide the own samples
                        # Allow the user to input the name of the sample or samples
                        # User selects sample names
                        # Assuming calculate_relative_abundance and display_grouped_bar_chart functions are defined as before...

                    else:
                        st.warning("Please select a taxonomic order.")

                        # Sunbrust
                    # Streamlit app
                    st.title("Select the Most Abundant Samples for Taxonomic Composition Analysis")

                    # Select Taxonomic Order
                    selected_order = st.selectbox('Select Taxonomic Order', taxonomy_order)

                    # Choose the number of top samples
                    top_samples_count = st.slider('Choose the number of top samples ', min_value=1, max_value=30,
                                                  value=5)

                    # Sort samples based on abundance and select the top samples
                    top_samples_df = merged_df.nlargest(top_samples_count, 'Abundance')

                    # Create an empty DataFrame to store the composition data
                    composition_df = pd.DataFrame(columns=[selected_order, 'SampleName', 'Abundance'])

                    if selected_order:
                        # For each sample, calculate the taxonomic composition for the selected order
                        for sample in top_samples_df['SampleName']:
                            sample_df = merged_df[merged_df['SampleName'] == sample]
                            total_abundance = sample_df['Abundance'].sum()

                            # Group by the selected taxonomic order and calculate the sum of abundance for each group
                            grouped_df = sample_df.groupby(selected_order)['Abundance'].sum().reset_index()

                            # Add the sample name to the DataFrame
                            grouped_df['SampleName'] = sample

                            # Append the results to the composition DataFrame
                            composition_df = pd.concat(
                                [composition_df, grouped_df[['SampleName', selected_order, 'Abundance']]])

                        # Create a sunburst plot for the taxonomic composition
                        fig3 = px.sunburst(
                            composition_df,
                            path=[selected_order, 'SampleName'],
                            values='Abundance',
                            title=f'Taxonomic Composition based on {selected_order} across Samples',
                            labels={'Abundance': 'Abundance'},
                        )

                        # Display the sunburst plot
                        st.plotly_chart(fig3)

                        ######

                    # ---------------------------------
                    # Select Taxonomic Order

                    st.title("Select the Sample Abundant  for Taxonomic Composition Analysis")

                    try:
                        selected_order_input = st.selectbox('Select Taxonomic Order', [None] + taxonomy_order,
                                                            key='selected_order_input1')

                        top_sample_names = merged_df.groupby('SampleName')['Abundance'].sum().sort_values(
                            ascending=False).index[:1000]
                        # Select Sample Names
                        selected_sample_names_input = tuple(
                            st.multiselect("Select Sample Names", top_sample_names))

                        # Check if at least one sample is selected
                        if not selected_sample_names_input:
                            st.warning("Please select at least one sample.")
                        else:
                            # Attempt to perform analysis
                            st.write(selected_order_input)
                            st.write(selected_sample_names_input)

                            dfs_to_concat = []

                            # Check if the selected taxonomic order exists in the dataframe
                            for sample_name in selected_sample_names_input:
                                sample_df = merged_df[merged_df['SampleName'] == sample_name]
                                total_abundance = sample_df['Abundance'].sum()

                                # Group by the selected taxonomic order and calculate the sum of abundance for each group
                                grouped_df = sample_df.groupby(selected_order_input)['Abundance'].sum().reset_index()

                                # Normalize abundance values to get relative abundance
                                grouped_df['RelativeAbundance'] = grouped_df['Abundance'] / total_abundance

                                # Add the sample name to the DataFrame
                                grouped_df['SampleName'] = sample_name

                                # Append the results to the list
                                dfs_to_concat.append(
                                    grouped_df[['SampleName', selected_order_input, 'RelativeAbundance']])

                            # Concatenate the DataFrames
                            composition_multi_df = pd.concat(dfs_to_concat)

                            # Create a grouped bar chart for the taxonomic composition with a continuous color scale
                            fig1 = px.bar(
                                composition_multi_df,
                                x='SampleName',
                                y='RelativeAbundance',
                                color=selected_order_input,
                                title=f'Taxonomic Composition based on {selected_order_input} for Selected Samples',
                                labels={'RelativeAbundance': 'Relative Abundance'},
                                color_continuous_scale='Viridis',
                            )

                            # Display the bar chart
                            st.plotly_chart(fig1)

                    except Exception as e:
                        # Log the exception to the console and display the full stack trace in Streamlit
                        st.exception(e)

                    # st.markdown("## Section :")
                    # st.title("Select Samples for Taxonomic Composition Analysis")
                    #
                    # selected_order_input = st.selectbox('Select Taxonomic Order', [None] + taxonomy_order,
                    #                                     key='selected_order_input')
                    #
                    # # Select Sample Names
                    # selected_sample_names_input = st.multiselect("Select Sample Names",
                    #                                              merged_df['SampleName'].unique())
                    #
                    # # Use st.debug for interactive debugging
                    #
                    # if not selected_order_input:
                    #     st.warning("Please select a taxonomic order.")
                    # elif not selected_sample_names_input:
                    #     st.warning("Please select at least one sample.")
                    # else:
                    #     # Use st.debug for interactive debugging
                    #     st.debug()
                    #
                    #     st.write("************************************")
                    #     dfs_to_concat = []
                    #
                    #     # Check if the selected taxonomic order exists in the dataframe
                    #
                    #     for sample_name in selected_sample_names_input:
                    #         sample_df = merged_df[merged_df['SampleName'] == sample_name]
                    #         total_abundance = sample_df['Abundance'].sum()
                    #
                    #         # Group by the selected taxonomic order and calculate the sum of abundance for each group
                    #         grouped_df = sample_df.groupby(selected_order_input)['Abundance'].sum().reset_index()
                    #
                    #         # Normalize abundance values to get relative abundance
                    #         grouped_df['RelativeAbundance'] = grouped_df['Abundance'] / total_abundance
                    #
                    #         # Add the sample name to the DataFrame
                    #         grouped_df['SampleName'] = sample_name
                    #
                    #         # Append the results to the list
                    #         dfs_to_concat.append(
                    #             grouped_df[['SampleName', selected_order_input, 'RelativeAbundance']])
                    #
                    #     # Concatenate the DataFrames
                    #     composition_multi_df = pd.concat(dfs_to_concat)
                    #
                    #     # Create a grouped bar chart for the taxonomic composition with a continuous color scale
                    #     fig1 = px.bar(
                    #         composition_multi_df,
                    #         x='SampleName',
                    #         y='RelativeAbundance',
                    #         color=selected_order_input,
                    #         title=f'Taxonomic Composition based on {selected_order_input} for Selected Samples',
                    #         labels={'RelativeAbundance': 'Relative Abundance'},
                    #         color_continuous_scale='Viridis',
                    #     )
                    #
                    #     # Display the bar chart
                    #     st.plotly_chart(fig1)

                    # def calculate_relative_abundance(sample_df, selected_order):
                    #     total_abundance = sample_df['Abundance'].sum()
                    #     grouped_df = sample_df.groupby(selected_order)['Abundance'].sum().reset_index()
                    #     grouped_df['RelativeAbundance'] = grouped_df['Abundance'] / total_abundance
                    #     return grouped_df
                    #
                    # def display_grouped_bar_chart(composition_df, selected_order, title_suffix):
                    #     fig = px.bar(
                    #         composition_df,
                    #         x='SampleName',
                    #         y='RelativeAbundance',
                    #         color=selected_order,
                    #         title=f'Taxonomic Composition based on {selected_order} {title_suffix}',
                    #         labels={'RelativeAbundance': 'Relative Abundance'},
                    #         color_continuous_scale='Viridis',
                    #     )
                    #     st.plotly_chart(fig)
                    #
                    # @st.cache  # Cache the result of this function
                    # def process_selected_samples(selected_order_input, selected_sample_names_input, merged_df):
                    #     dfs_to_concat = []
                    #
                    #     for sample_name in selected_sample_names_input:
                    #         sample_df = merged_df[merged_df['SampleName'] == sample_name]
                    #         grouped_df = calculate_relative_abundance(sample_df, selected_order_input)
                    #         grouped_df['SampleName'] = sample_name
                    #         dfs_to_concat.append(
                    #             grouped_df[['SampleName', selected_order_input, 'RelativeAbundance']])
                    #
                    #     composition_df = pd.concat(dfs_to_concat)
                    #     display_grouped_bar_chart(composition_df, selected_order_input, "for Selected Samples")
                    #
                    #
                    # # Section 1: Analyzing top samples
                    # selected_order = st.selectbox('Select Taxonomic Order', taxonomy_order)
                    # top_samples_count = st.slider('Choose the number of top samples', min_value=1, max_value=30,
                    #                               value=5)
                    # top_samples_df = merged_df.nlargest(top_samples_count, 'Abundance')
                    # composition_df = pd.DataFrame(columns=[selected_order, 'SampleName', 'RelativeAbundance'])

                    # if selected_order:
                    #     for sample_name in top_samples_df['SampleName']:
                    #         sample_df = merged_df[merged_df['SampleName'] == sample_name]
                    #         grouped_df = calculate_relative_abundance(sample_df, selected_order)
                    #         grouped_df['SampleName'] = sample_name
                    #         composition_df = pd.concat(
                    #             [composition_df, grouped_df[['SampleName', selected_order, 'RelativeAbundance']]])
                    #
                    #     display_grouped_bar_chart(composition_df, selected_order, "across Samples")
                    #
                    # Section 2: Analyzing user-provided samples
                    # selected_order_input = st.selectbox('Select Taxonomic Order ', taxonomy_order)
                    # selected_sample_names_input = ''
                    # # Only proceed if a taxonomic order is selected
                    # if selected_order_input:
                    #     selected_sample_names_input = st.multiselect("Select Sample Names",
                    #                                                  merged_df['SampleName'].unique())
                    #
                    #     if selected_sample_names_input:
                    #         # Call the cached function
                    #         process_selected_samples(selected_order_input, selected_sample_names_input, merged_df)
                    #         dfs_to_concat = []
                    #
                    #         for sample_name in selected_sample_names_input:
                    #             sample_df = merged_df[merged_df['SampleName'] == sample_name]
                    #             grouped_df = calculate_relative_abundance(sample_df, selected_order_input)
                    #             grouped_df['SampleName'] = sample_name
                    #             dfs_to_concat.append(
                    #                 grouped_df[['SampleName', selected_order_input, 'RelativeAbundance']])
                    #
                    #         composition_df = pd.concat(dfs_to_concat)
                    #         display_grouped_bar_chart(composition_df, selected_order_input, "for Selected Samples")


            else:
                st.warning("Please select a Study and Taxonomy values.")
                #
                # # Relative abundance
                # # Multi selection on sample based on the most abundant
                #
                # selected_samples = st.multiselect('Select Samples', merged_df['SampleName'].unique())
                #
                # query_abundance_all = f"""
                #                     SELECT s."SampleName", i."ItemName", af."Sample_idSample", af."Item_idItem", af."Abundance"
                #                     FROM public."AbundanceFactTable" af
                #                     JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                #                     JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                #
                #                 """
                # df_abundance_all = pd.read_sql(query_abundance_all, conn)
                #
                # # Assuming df_abundance_all is your DataFrame
                # df_abundance_all['total_abundance_through_sampleName'] = df_abundance_all.groupby('SampleName')[
                #     'Abundance'].transform('sum')
                #
                # # Create a new column for relative abundance
                # df_abundance_all['relative_abundance'] = df_abundance_all['Abundance'] / df_abundance_all[
                #     'total_abundance_through_sampleName']
                #
                # st.write(df_abundance_all)
                # # Filter df_abundance_all based on selected_items_tuple
                # selected_sample_name_tuple = tuple(selected_samples)
                # st.write(selected_sample_name_tuple)
                #
                # filtered_df = df_abundance_all[df_abundance_all['SampleName'].isin(selected_sample_name_tuple)]
                #
                # # Select specific columns to display
                # selected_columns = ['SampleName', 'ItemName', 'Abundance', 'total_abundance_through_sampleName',
                #                     'relative_abundance']
                # st.write(filtered_df)
                # st.write(merged_df)

        # todo
        # Second section
        ######################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#########################
        show_data_Otu = st.checkbox("Show Abundance Data by Taxonomy : #2")
        if show_data_Otu:
            # Dropdown for selecting hierarchy level
            hierarchy_level = st.selectbox("Select Hierarchy Level",
                                           ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species",
                                            "Cluster"])

            # Search input for user to type a term
            search_input = st.text_input("Search for an Entry")

            # Search button
            search_button = st.button("Search ")

            if search_button:
                # Execute search when button is clicked
                search_term = search_input.strip()

                if search_term:
                    # Split taxonomy string by semicolon
                    df_taxonomy = pd.read_sql("SELECT  \"Item_idItem\",\"Taxonomy\" FROM public.\"Taxons\"", conn)
                    df_taxonomy["Taxonomy"] = df_taxonomy["Taxonomy"].str.split(";")

                    # Map the user's selection to the corresponding position in the split Taxonomy list
                    position = {
                        "Domain": 0,
                        "Phylum": 1,
                        "Class": 2,
                        "Order": 3,
                        "Family": 4,
                        "Genus": 5,
                        "Species": 6,
                        "Cluster": 7
                    }.get(hierarchy_level)

                    if position is not None:
                        # Filter Taxonomy based on search term (contains)
                        df_filtered_taxonomy = df_taxonomy[
                            df_taxonomy["Taxonomy"].str[position].str.contains(search_term, case=False, na=False)]

                        count = len(df_filtered_taxonomy)
                        if not df_filtered_taxonomy.empty:
                            # Display Taxonomy information
                            st.write(f"## Taxonomy Information for {search_term}")
                            st.dataframe(df_filtered_taxonomy)
                            st.write(f"Number of Lines: {count}")

                            # Get Item_idItem for the selected entry
                            item_ids = df_filtered_taxonomy["Item_idItem"].tolist()

                            # Fetch abundance data from AbundanceFactTable
                            query_abundance = f"""
                                                    SELECT *
                                                    FROM public."AbundanceFactTable"
                                                    WHERE "Item_idItem" IN ({', '.join(map(str, item_ids))})
                                                """
                            df_abundance = pd.read_sql(query_abundance, conn)

                            if not df_abundance.empty:
                                # Display Abundance data
                                st.write(f"## Abundance Data for {search_term}")
                                st.dataframe(df_abundance)

                                # Retrieve the Study_idStudy associated with each Sample_idSample
                                query_study = f"""
                                    SELECT s."IdSample", h."Study_idStudy"
                                    FROM public."Sample" s
                                    JOIN public."Host" h ON s."Host_idHost" = h."IdHost"
                                    WHERE s."IdSample" IN ({', '.join(map(str, df_abundance['Sample_idSample'].tolist()))})
                                     """
                                df_study_1 = pd.read_sql(query_study, conn)

                                # Group abundance data by Study_idStudy
                                grouped_abundance = df_abundance.groupby(df_study_1['Study_idStudy'])

                                # Display abundance data for each study
                                study_results = []

                                for study_id, group in grouped_abundance:
                                    item_ids = group["Item_idItem"].tolist()

                                    # Step 1: Retrieve Taxonomy for each Item_idItem
                                    df_taxonomies = df_taxonomy[df_taxonomy["Item_idItem"].isin(item_ids)][
                                        ["Item_idItem", "Taxonomy"]]

                                    # Step 2: Replace Item_idItem with ItemName from the Item table
                                    query_item_names = f"""
                                        SELECT "IdItem", "ItemName"
                                        FROM public."Item"
                                        WHERE "IdItem" IN ({', '.join(map(str, item_ids))})
                                    """
                                    df_item_names = pd.read_sql(query_item_names, conn)

                                    # Assuming 'Item_idItem' is the original column name
                                    group = group.rename(columns={'Item_idItem': 'IdItem'})

                                    # Merge abundance data with ItemName information (using inner join)
                                    merged_data = pd.merge(group, df_item_names, left_on="IdItem", right_on="IdItem",
                                                           how="inner")

                                    # Step 3: Retrieve Abundance for each Item
                                    query_abundance = f"""
                                        SELECT "Item_idItem", "Abundance"
                                        FROM public."AbundanceFactTable"
                                        WHERE "Item_idItem" IN ({', '.join(map(str, item_ids))})
                                    """
                                    df_abundance = pd.read_sql(query_abundance, conn)

                                    # Merge abundance data with taxonomy information
                                    merged_data = pd.merge(merged_data, df_taxonomies, left_on="IdItem",
                                                           right_on="Item_idItem", how="inner")
                                    merged_data = pd.merge(merged_data, df_abundance, left_on="IdItem",
                                                           right_on="Item_idItem", how="inner")

                                    # Rename columns to remove duplicates
                                    merged_data = merged_data.rename(columns={"Abundance_y": "Abundance"})

                                    # Drop the extra column
                                    merged_data = merged_data.drop(
                                        columns=["Abundance_x", "Item_idItem_y", "IdItem", "Sample_idSample"])

                                    # Add Study ID as a column
                                    merged_data["Study_ID"] = study_id

                                    # Append to the list of study results
                                    study_results.append(merged_data)

                                # Concatenate the list of study results into one dataframe
                                if study_results:
                                    final_study_results = pd.concat(study_results, ignore_index=True)

                                    # Reset the index to have a sequential index
                                    final_study_results.reset_index(drop=True, inplace=True)

                                    # Display the final study results as a table
                                    st.write(f"## Combined Data for All Studies")
                                    st.dataframe(final_study_results)
                                else:
                                    st.write("No data available for the selected studies.")

                        else:
                            st.write(f"No taxonomy information found for {search_term}.")
                    else:
                        st.write("Invalid hierarchy level selected.")

        # todo
        # Third section Show_composition_Tax
        ######################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#########################
        # sHOW Composition taxonomy
        show_composition_tax = st.checkbox("show_composition_tax #3")
        if show_composition_tax:
            # Dropdown for selecting hierarchy level
            hierarchy_level = st.selectbox("Select Hierarchy Level ",
                                           ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species",
                                            "Cluster"])

            # Search input for user to type a term
            search_input = st.text_input("Search for an Entry ")

            # Search button
            search_button = st.button("Search")

            if search_button:
                # Execute search when button is clicked
                search_term = search_input.strip()

                if search_term:
                    # Split taxonomy string by semicolon
                    df_taxonomy = pd.read_sql("SELECT  \"Item_idItem\",\"Taxonomy\" FROM public.\"Taxons\"", conn)
                    df_taxonomy["Taxonomy"] = df_taxonomy["Taxonomy"].str.split(";")

                    # Map the user's selection to the corresponding position in the split Taxonomy list
                    position = {
                        "Domain": 0, "Phylum": 1, "Class": 2, "Order": 3, "Family": 4, "Genus": 5, "Species": 6,
                        "Cluster": 7
                    }.get(hierarchy_level)

                    if position is not None:
                        # Filter Taxonomy based on search term (contains)
                        df_filtered_taxonomy = df_taxonomy[
                            df_taxonomy["Taxonomy"].str[position].str.contains(search_term, case=False, na=False)]

                        count = len(df_filtered_taxonomy)

                        if not df_filtered_taxonomy.empty:
                            # Display Taxonomy information
                            st.write(f"## Taxonomy Information for {search_term}")
                            st.dataframe(df_filtered_taxonomy)
                            st.write(f"Number of Lines: {count}")

                            # Get Item_idItem for the selected entry
                            item_ids = df_filtered_taxonomy["Item_idItem"].tolist()

                            # Fetch abundance data from AbundanceFactTable
                            query_abundance = f"""
                                                            SELECT af.*, s."SampleName", h."Study_idStudy"
                                                            FROM public."AbundanceFactTable" af
                                                            JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                                                            JOIN public."Host" h ON s."Host_idHost" = h."IdHost"
                                                            WHERE af."Item_idItem" IN ({', '.join(map(str, item_ids))})
                                                        """
                            df_abundance = pd.read_sql(query_abundance, conn)

                            if not df_abundance.empty:
                                # Display Abundance data
                                st.write(f"## Abundance Data for {search_term}")
                                st.dataframe(df_abundance)

                                # Retrieve ItemName for each Item_idItem
                                query_item_names = f"""
                                                                SELECT "IdItem", "ItemName"
                                                                FROM public."Item"
                                                                WHERE "IdItem" IN ({', '.join(map(str, item_ids))})
                                                            """
                                df_item_names = pd.read_sql(query_item_names, conn)

                                # Merge abundance data with taxonomy and item information
                                merged_data = pd.merge(df_abundance, df_taxonomy, left_on="Item_idItem",
                                                       right_on="Item_idItem", how="inner")
                                merged_data = pd.merge(merged_data, df_item_names, left_on="Item_idItem",
                                                       right_on="IdItem", how="inner")
                                merged_data = merged_data[
                                    ["ItemName", "SampleName", "Abundance", "Taxonomy", "Study_idStudy"]]

                                # Display the final combined data as a table
                                st.write(f"## Combined Data for All Studies")
                                st.dataframe(merged_data)

                                # Create new columns for each taxonomy level
                                tax_levels = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species',
                                              'Cluster']

                                for level in tax_levels:
                                    merged_data[level] = merged_data['Taxonomy'].apply(
                                        lambda x: x[tax_levels.index(level)] if len(x) > tax_levels.index(
                                            level) else None
                                    )

                                # Let the user choose a taxonomy level with a unique key
                                selected_tax_level = st.selectbox(f"Select Taxonomy Level",
                                                                  ['Domain', 'Phylum', 'Class', 'Order', 'Family',
                                                                   'Genus', 'Species', 'Cluster'],
                                                                  key="select_tax_level")

                                # Iterate through each unique study
                                for study_name in df_study['StudyName'].unique():
                                    selected_study_id = study_name_to_id.get(study_name)

                                    # Filter merged_data based on selected Study ID
                                    filtered_merged_data = merged_data[
                                        merged_data['Study_idStudy'] == selected_study_id]

                                    # Get the total number of lines and unique sample names
                                    total_lines = len(filtered_merged_data)
                                    unique_samples = len(filtered_merged_data['SampleName'].unique())

                                    st.write(
                                        f"Data for Study: {study_name} (Total Lines: {total_lines}, Unique Samples: {unique_samples})")
                                    st.dataframe(filtered_merged_data)

                                    # Group the data by the selected taxonomy level and calculate the sum of abundances for each sample
                                    grouped_data = filtered_merged_data.groupby([selected_tax_level, 'SampleName'])[
                                        'Abundance'].sum().reset_index()

                                    # Create a bar plot
                                    plt.figure(figsize=(10, 6))
                                    for sample in grouped_data['SampleName'].unique():
                                        sample_data = grouped_data[grouped_data['SampleName'] == sample]
                                        plt.bar(sample_data[selected_tax_level], sample_data['Abundance'], label=sample)

                                    plt.xlabel(selected_tax_level)
                                    plt.ylabel('Abundance')
                                    plt.title(f'Taxonomic Composition')
                                    st.pyplot(plt)
                            else:
                                st.write("No abundance data available for the selected studies.")
                        else:
                            st.write(f"No taxonomy information found for {search_term}.")
                    else:
                        st.write("Invalid hierarchy level selected.")


    # For example, you can add some text or visualizations here
    # Function to create a styled sidebar section
    def styled_sidebar_section(title, overview, options, explanation):
        st.sidebar.markdown(f"### {title}:", unsafe_allow_html=True)
        st.sidebar.text(overview)
        st.sidebar.text("### Options Available:")
        st.sidebar.text(options)
        st.sidebar.text("### Explanation:")
        st.sidebar.text(explanation)


    def main():

        # filtered_data_weight_range_bw_POC2 = None  # Assign an initial value
        filtered_data_weight_range_bw_POC2 = pd.DataFrame()
        # filtered_data_weight_range_bw_POC1 = None  # Assign an initial value
        filtered_data_weight_range_bw_POC1 = pd.DataFrame()

        filtered_data_weight_range_4bw_diso1 = None
        filtered_data_weight_range_bw_POC2_list = None
        filtered_data_weight_range_bw_POC1_list = None

        st.sidebar.title("Main Content")
        selected_page = st.sidebar.radio("Select a page",
                                         ["App Overview","Digital Host(Dev Mode)", "Advanced Filter Entry", "Search By Host", "Search By Taxa"],
                                         index=None)
        if st.sidebar.button("Logout"):
            logout()  # Call the logout function if the button is clicked

        elif selected_page == "Digital Host(Dev Mode)":
            ##################################### start queires url

            # Title of the Streamlit app
            query_params = st.query_params
            # Check if query parameters exist
            if query_params:
                # Extract studies
                studies = query_params.get('studies', '').split('|')
                features = {}

                # Extract features and ranges for each study
                for study in studies:
                    study_features = query_params.get(f"{study}_features", '').split('|')
                    features[study] = {}
                    for feature in study_features:
                        if ":" in feature:
                            feature_name, range_values = feature.split(":")
                            min_value, max_value = map(float, range_values.split("-"))
                            features[study][feature_name] = (min_value, max_value)
                        else:
                            features[study][feature] = None

                # Display the parsed data in a cleaner format
                st.subheader("Parsed Query Data")
                st.write("**Studies:**")
                for study in studies:
                    st.write(f"- {study}")
                    if study in features:
                        st.write("  **Features with Ranges:**")
                        for feature_name, range_values in features[study].items():
                            if range_values is not None:
                                st.write(f"    - {feature_name}: Min = {range_values[0]},  Max = {range_values[1]}")
                            else:
                                st.write(f"    - {feature_name}: No range provided")

                 # Fetch unique study names and their IDs
                study_names_and_ids = fetch_study_names_and_ids()
                # Get corresponding study IDs based on selected study names
                selected_study_ids = study_names_and_ids.loc[
                    study_names_and_ids['StudyName'].isin(studies), 'idStudy'].tolist()

                # Display the selected study IDs
                st.write("Study Names and IDs:", study_names_and_ids)
                st.write(f"Selected Study IDs: {selected_study_ids}")
                # 2do


                # else:
                #     # Default app behavior when no query parameters are present
                #     st.header("Normal App Access")
                #     st.write("This is the default app view.")
                #     st.write("No query parameters were provided in the URL.")
            ##################################### end queires url

        elif selected_page == "Advanced Filter Entry":
            st.sidebar.title("You selected: Test All Filter")
            st.write("### All Filter Section:")
            st.write("You will be able to filter on all features with all content of that.")
            st.write("\n---\n")  # Larger section separation
            # Sidebar filter - Step 1: Select Study Names
            st.sidebar.subheader("Step 1: Select Study Names")
            # Explanation of options
            # Create an expander for the explanation
            with st.sidebar.expander("Explanation"):
                st.write("""
                    - Option 1: Prod2 - xxxxxxxxxxxxxxxx
                    - Option 2: Disco1 - xxxxxxxxxxxxxxxx
                    - Option 3: Poc1 - xxxxxxxxxxxxxxxx
                    - Option 4: Prod1 - xxxxxxxx
                    - Option 5: Poc2 - xxxxxxxxxxx 
                    - Option 6: Trouts - xxxxxxxxxxx
                """)

            # Fetch unique study names and their IDs
            study_names_and_ids = fetch_study_names_and_ids()

            # Multiselect dropdown for study names
            selected_study_names = st.sidebar.multiselect("Select Study Names", study_names_and_ids['StudyName'])

            # Proceed to Step 2 if at least one study name is selected
            if selected_study_names:
                # Display selected study names
                st.write("Selected Study Names:", ", ".join(selected_study_names))
                # Sidebar filter - Step 2: Apply Filters and Display Data
                # Get corresponding study IDs based on selected study names
                selected_study_ids = study_names_and_ids.loc[
                    study_names_and_ids['StudyName'].isin(selected_study_names), 'idStudy'].tolist()

                # Filter data based on selected study IDs
                filtered_data, host_ids, Feature_options_by_study_selected = filter_data(selected_study_ids, conn)
                if host_ids is not None:
                    len_host_ids = len(set(host_ids))
                else:
                    # Handle the case when common_host_ids is None
                    len_host_ids = 0  # Display the common host IDs and the count using Streamlit
                st.write("filtered_data")
                st.write("Number of Host ids founded ", len_host_ids)
                st.write(filtered_data)
                st.write("Filterable Hosts Feature Set", Feature_options_by_study_selected)
                # FeaturePen
                feature_options_to_select = feature_pen_to_select(selected_study_names, conn)
                st.write("Filterable Pen Feature Set", feature_options_to_select)

                # Dictionary to store the types of each feature
                feature_types = {
                    "indWeight": "range",
                    "liverWeight": "range",
                    "liverClass": "text",
                    "inoculation": "text",
                    "Size": "range",
                    "Age": "range",
                    "Weight": "range",
                    "Feed_consumed_D0_D42": "range",
                    "Feed_consumed_D0_D7": "range",
                    "Feed_consumed_D0_D14": "range",
                    "Feed_consumed_D0_D21": "range",
                    "Feed_consumed_D0_D28": "range",
                    "Feed_consumed_D0_D35": "range",
                    "Study_Day": "text",
                    "FCR_D0_7": "range",
                    "FCR_D0_14": "range",
                    "FCR_D0_21": "range",
                    "FCR_D0_28": "range",
                    "FCR_D0_35": "range",
                    "FCR_D0_42": "range",
                    "Block": "text",

                    # Pen feature  5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22
                    "Mortality_removal_D9": "range",
                    "Mortality_removal_D9_D14": "range",
                    "Mortality_removal_D14_D21": "range",
                    "Mortality_removal_D21_D28": "range",
                    "Mortality_removal_D28_D35": "range",
                    "Feed_Consumed_D9": "range",
                    "Feed_Consumed_D9_D14": "range",
                    "Feed_Consumed_D14_D21": "range",
                    "Feed_Consumed_D21_D28": "range",
                    "Feed_Consumed_D28_D35": "range",
                    "Adj_Feed_Gain_D0_D9": "range",
                    "Adj_Feed_Gain_D0_D14": "range",
                    "Adj_Feed_Gain_D0_D21": "range",
                    "Adj_Feed_Gain_D0_D28": "range",
                    "Adj_Feed_Gain_D0_D35": "range",
                    "Adj_Feed_Gain_D14_D21": "range",
                    "Adj_Feed_Gain_D14_D28": "range",
                    "Adj_Feed_Gain_D14_D35": "range",
                    # Add other features here
                }
                # Fetch unique liverClass values from your dataset
                sql_query_liver_class = """
                SELECT DISTINCT "Value"
                FROM public."FeatureFactTable"
                WHERE "Feature_idFeature" = 3
                """
                df_liver_classes = pd.read_sql_query(sql_query_liver_class, conn)
                unique_liver_classes = df_liver_classes['Value'].unique().tolist()
                #
                sql_query_inoculation = """
                               SELECT DISTINCT "Value"
                               FROM public."FeatureFactTable"
                               WHERE "Feature_idFeature" = 4
                               """
                df_inoculation = pd.read_sql_query(sql_query_inoculation, conn)
                unique_inoculation = df_inoculation['Value'].unique().tolist()
                #
                sql_query_studydate = """
                select DISTINCT "Value" from public.
                "FeatureFactTable" where "Feature_idFeature" = 29
                """
                df_study_date = pd.read_sql_query(sql_query_studydate, conn)
                unique_study_date = df_study_date['Value'].unique().tolist()
                #
                sql_query_liverClass = """
                               SELECT DISTINCT "Value"
                               FROM public."FeatureFactTable"
                               WHERE "Feature_idFeature" = 3
                               """
                df_liverClass = pd.read_sql_query(sql_query_liverClass, conn)
                unique_liverClass = df_liverClass['Value'].unique().tolist()

                # Sidebar filter - Step 2: Host Features Filters
                st.sidebar.write("\n---\n")  # Section separation
                st.sidebar.subheader("Step 2: Host & Pen Features Filters")

                # Fetch unique features from the Feature table
                feature_names = ["indWeight", "liverWeight", "liverClass", "inoculation", "Size", "Age", "Weight",
                                 "Feed_consumed_D0_D42", "Feed_consumed_D0_D7",
                                 "Feed_consumed_D0_D14", "Feed_consumed_D0_D21", "Feed_consumed_D0_D28",
                                 "Feed_consumed_D0_D35", "Study_Day", "FCR_D0_7", "FCR_D0_14",
                                 "FCR_D0_21", "FCR_D0_28", "FCR_D0_35", "FCR_D0_42", "Block", "Adj_Feed_Gain_D0_D9",
                                 "Adj_Feed_Gain_D0_D14", "Adj_Feed_Gain_D0_D21",
                                 "Adj_Feed_Gain_D0_D28", "Adj_Feed_Gain_D0_D35", "Adj_Feed_Gain_D14_D21",
                                 "Adj_Feed_Gain_D14_D28", "Adj_Feed_Gain_D14_D35",
                                 # features from pen
                                 "Mortality_removal_D9", "Mortality_removal_D9_D14", "Mortality_removal_D14_D21",
                                 "Mortality_removal_D21_D28", "Mortality_removal_D28_D35",
                                 "Feed_Consumed_D9", "Feed_Consumed_D9_D14", "Feed_Consumed_D14_D21",
                                 "Feed_Consumed_D21_D28",
                                 "Feed_Consumed_D28_D35", "Adj_Feed_Gain_D0_D9", "Adj_Feed_Gain_D0_D14",
                                 "Adj_Feed_Gain_D0_D21", "Adj_Feed_Gain_D0_D28", "Adj_Feed_Gain_D0_D35",
                                 "Adj_Feed_Gain_D14_D21",
                                 "Adj_Feed_Gain_D14_D28", "Adj_Feed_Gain_D14_D35",
                                 ]
                # TODO fEATURE IN PENHASFEATURE AND FEATUREfACTtABLE
                # 20 Adj_Feed_Gain_D14_D21
                # 17    Adj_Feed_Gain_D0_D21
                # 22    Adj_Feed_Gain_D14_D35
                # 16    Adj_Feed_Gain_D0_D14
                # 15    Adj_Feed_Gain_D0_D9
                # 18    Adj_Feed_Gain_D0_D28
                pen_feature_list = ["Mortality_removal_D9", "Mortality_removal_D9_D14", "Mortality_removal_D14_D21",
                                    "Mortality_removal_D21_D28", "Mortality_removal_D28_D35",
                                    "Feed_Consumed_D9", "Feed_Consumed_D9_D14", "Feed_Consumed_D14_D21",
                                    "Feed_Consumed_D21_D28",
                                    "Feed_Consumed_D28_D35", "Adj_Feed_Gain_D0_D35", "Adj_Feed_Gain_D14_D28"]
                # Multiselect dropdown for feature selection
                # Make Features names based of the dispo                 Feature_options_by_study_selected     feature_options_to_select
                # Convert both lists to sets to ensure uniqueness

                # Combine the sets and convert to a list, excluding the first element if needed
                #
                # feature_names_union = feature_names_union[1:]  # Exclude the first element if needed
                # Convert both columns to lists
                # # Combine both lists and convert to set to remove duplicates, then back to list
                # todo fix that selection list
                combined_df = pd.concat([feature_options_to_select, Feature_options_by_study_selected],
                                        ignore_index=True)
                combined_feature_names = combined_df['FeatureName'].unique().tolist()
                # Alternatively, you can use the filter() function
                combined_feature_names = list(filter(pd.notna, combined_feature_names))
                # check and print the combined features
                # st.write("Combined feature names ", combined_feature_names )

                # Section ~ filter on weight for DISCO1 (3), POC1 (4), POC2 (5)

                # # Convert 'Weight' column to dictionaries
                # filtered_data['Weight'] = filtered_data['Weight'].apply(
                #     lambda x: json.loads(x) if isinstance(x, str) else x)

                # Convert 'Weight' column to dictionaries
                filtered_data['Weight'] = filtered_data['Weight'].apply(
                    lambda x: json.loads(x) if isinstance(x, str) else x)

                if 'Weight' in filtered_data.columns and not filtered_data['Weight'].isnull().all():
                    # Filter out rows with NaN values in 'Weight' column
                    filtered_data = filtered_data.dropna(subset=['Weight'])

                    # Expand 'Weight' dictionary into separate columns
                    weight_data_expanded = pd.DataFrame(filtered_data['Weight'].tolist())

                    # Reset the index of both DataFrames
                    filtered_data = filtered_data.reset_index(drop=True)
                    weight_data_expanded = weight_data_expanded.reset_index(drop=True)

                    # Concatenate the original DataFrame with the expanded weight data
                    filtered_data = pd.concat([filtered_data, weight_data_expanded], axis=1).drop(columns=['Weight'])
                # Make a copy of filtered_data
                filtered_data_weight_range_7bw_poc2 = filtered_data.copy()
                filtered_data_weight_range_4bw = filtered_data.copy()
                filtered_data_weight_range_7bw_poc1 = filtered_data.copy()

                # Sidebar options
                # Check if any study id contains 3, 4, or 5 dico1 poc1 poc2
                if any("3" in str(id) or "4" in str(id) or "5" in str(id) for id in selected_study_ids):
                    filter_weights = st.sidebar.checkbox("Activate Filtering by Weights \n"
                                                         "(Available only For Poc1,Poc2 & Disco1)")
                    # st.write(selected_study_ids) #dEBUG print study ids
                else:
                    filter_weights = None
                # Initialize empty DataFrame
                if filter_weights:
                    if 3 in selected_study_ids:
                        # Add a sidebar with a slider for weight range
                        weight_range_BirdWeight_D0 = st.slider("BirdWeight_D0", min_value=0.0, max_value=2.0,
                                                               value=(0.0, 2.0))
                        weight_range_BirdWeight_D9 = st.slider("BirdWeight_D9", min_value=0.0, max_value=2.0,
                                                               value=(0.0, 2.0))
                        weight_range_BirdWeight_D21 = st.slider("BirdWeight_D21", min_value=0.0, max_value=2.0,
                                                                value=(0.0, 2.0))
                        weight_range_BirdWeight_D35 = st.slider("BirdWeight_D35", min_value=0.0, max_value=2.0,
                                                                value=(0.0, 3.0))

                        # Filter based on weight ranges
                        filtered_data_weight_range_4bw_diso1 = filtered_data_weight_range_4bw[
                            (filtered_data['BirdWeight_D0'] >= weight_range_BirdWeight_D0[0]) &
                            (filtered_data['BirdWeight_D0'] <= weight_range_BirdWeight_D0[1]) &
                            (filtered_data['BirdWeight_D9'] >= weight_range_BirdWeight_D9[0]) &
                            (filtered_data['BirdWeight_D9'] <= weight_range_BirdWeight_D9[1]) &
                            (filtered_data['BirdWeight_D21'] >= weight_range_BirdWeight_D21[0]) &
                            (filtered_data['BirdWeight_D21'] <= weight_range_BirdWeight_D21[1]) &
                            (filtered_data['BirdWeight_D35'] >= weight_range_BirdWeight_D35[0]) &
                            (filtered_data['BirdWeight_D35'] <= weight_range_BirdWeight_D35[1])
                            ]

                        # Display the number of rows
                        num_rows_range = len(filtered_data_weight_range_4bw_diso1)
                        st.write(f"Number of Rows With Range Option: {num_rows_range}")

                        # Display the filtered data
                        st.dataframe(filtered_data_weight_range_4bw_diso1, height=400)
                    # fix in wich project yout filtering to not mix poc1 and poc2 TODO
                    if 5 in selected_study_ids:
                        # Add a sidebar with a slider for weight range
                        AvgBW_D7 = st.slider("AvgBW_D7", min_value=0.0, max_value=2.0, value=(0.0, 2.0))
                        AvgBW_D14 = st.slider("AvgBW_D14", min_value=0.0, max_value=2.0,
                                              value=(0.0, 2.0))
                        AvgBW_D21 = st.slider("AvgBW_D21", min_value=0.0, max_value=2.0,
                                              value=(0.0, 3.0))
                        AvgBW_D28 = st.slider("AvgBW_D28", min_value=0.0, max_value=2.0,
                                              value=(0.0, 2.0))
                        AvgBW_D35 = st.slider("AvgBW_D35", min_value=0.0, max_value=2.0,
                                              value=(0.0, 2.0))
                        AvgBW_D42 = st.slider("AvgBW_D42", min_value=0.0, max_value=2.0, value=(0.0, 3.0))
                        IndBW_D14 = st.slider("IndBW_D14", min_value=0.0, max_value=2.0, value=(0.0, 3.0))
                        IndBW_D28 = st.slider("IndBW_D28", min_value=0.0, max_value=2.0, value=(0.0, 3.0))
                        IndBW_D42 = st.slider("IndBW_D42", min_value=0.0, max_value=2.0, value=(0.0, 3.0))

                        # Filter based on weight ranges
                        filtered_data_weight_range_bw_POC2 = filtered_data_weight_range_7bw_poc2[
                            (filtered_data['AvgBW_D7'] >= AvgBW_D7[0]) &
                            (filtered_data['AvgBW_D7'] <= AvgBW_D7[1]) &
                            (filtered_data['AvgBW_D14'] >= AvgBW_D14[0]) &
                            (filtered_data['AvgBW_D14'] <= AvgBW_D14[1]) &
                            (filtered_data['AvgBW_D21'] >= AvgBW_D21[0]) &
                            (filtered_data['AvgBW_D21'] <= AvgBW_D21[1]) &
                            (filtered_data['AvgBW_D28'] >= AvgBW_D28[0]) &
                            (filtered_data['AvgBW_D28'] <= AvgBW_D28[1]) &
                            (filtered_data['AvgBW_D35'] >= AvgBW_D35[0]) &
                            (filtered_data['AvgBW_D35'] <= AvgBW_D35[1]) &
                            (filtered_data['AvgBW_D42'] >= AvgBW_D42[0]) &
                            (filtered_data['AvgBW_D42'] <= AvgBW_D42[1]) &
                            (filtered_data['IndBW_D14'] >= IndBW_D14[0]) &
                            (filtered_data['IndBW_D14'] <= IndBW_D14[1]) &
                            (filtered_data['IndBW_D28'] >= IndBW_D28[0]) &
                            (filtered_data['IndBW_D28'] <= IndBW_D28[1]) &
                            (filtered_data['IndBW_D42'] >= IndBW_D42[0]) &
                            (filtered_data['IndBW_D42'] <= IndBW_D42[1])

                            ]
                        # Display the number of rows
                        num_rows_range = len(filtered_data_weight_range_bw_POC2)
                        st.write(f"Number of Rows With Range Option: {num_rows_range}")
                        # Display the filtered data
                        st.dataframe(filtered_data_weight_range_bw_POC2, height=400)

                    if 4 in selected_study_ids:
                        # Add a sidebar with a slider for weight range
                        AvgBirdWeight_D0 = st.slider("AvgBirdWeight_D0", min_value=0.0, max_value=2.0,
                                                     value=(0.0, 2.0))
                        AvgBirdWeight_D7 = st.slider("AvgBirdWeight_D7", min_value=0.0, max_value=2.0,
                                                     value=(0.0, 2.0))
                        AvgBirdWeight_D14 = st.slider("AvgBirdWeight_D14", min_value=0.0, max_value=2.0,
                                                      value=(0.0, 2.0))
                        AvgBirdWeight_D21 = st.slider("AvgBirdWeight_D21", min_value=0.0, max_value=2.0,
                                                      value=(0.0, 3.0))
                        AvgBirdWeight_D28 = st.slider("AvgBirdWeight_D28", min_value=0.0, max_value=2.0,
                                                      value=(0.0, 2.0))
                        AvgBirdWeight_D35 = st.slider("AvgBirdWeight_D35", min_value=0.0, max_value=2.0,
                                                      value=(0.0, 2.0))
                        Bird_weight_D36 = st.slider("Bird_weight_D36", min_value=0.0, max_value=2.0,
                                                    value=(0.0, 3.0))

                        # Filter based on weight ranges
                        filtered_data_weight_range_bw_POC1 = filtered_data_weight_range_7bw_poc1[
                            (filtered_data['AvgBirdWeight_D0'] >= AvgBirdWeight_D0[0]) &
                            (filtered_data['AvgBirdWeight_D0'] <= AvgBirdWeight_D0[1]) &
                            (filtered_data['AvgBirdWeight_D7'] >= AvgBirdWeight_D7[0]) &
                            (filtered_data['AvgBirdWeight_D7'] <= AvgBirdWeight_D7[1]) &
                            (filtered_data['AvgBirdWeight_D14'] >= AvgBirdWeight_D14[0]) &
                            (filtered_data['AvgBirdWeight_D14'] <= AvgBirdWeight_D14[1]) &
                            (filtered_data['AvgBirdWeight_D21'] >= AvgBirdWeight_D21[0]) &
                            (filtered_data['AvgBirdWeight_D21'] <= AvgBirdWeight_D21[1]) &
                            (filtered_data['AvgBirdWeight_D28'] >= AvgBirdWeight_D28[0]) &
                            (filtered_data['AvgBirdWeight_D28'] <= AvgBirdWeight_D28[1]) &
                            (filtered_data['AvgBirdWeight_D35'] >= AvgBirdWeight_D35[0]) &
                            (filtered_data['AvgBirdWeight_D35'] <= AvgBirdWeight_D35[1]) &
                            (filtered_data['Bird_weight_D36'] >= Bird_weight_D36[0]) &
                            (filtered_data['Bird_weight_D36'] <= Bird_weight_D36[1])
                            ]
                        # Display the number of rows
                        num_rows_range = len(filtered_data_weight_range_bw_POC1)
                        st.write(f"Number of Rows With Range Option: {num_rows_range}")
                        # Display the filtered data
                        st.dataframe(filtered_data_weight_range_bw_POC1, height=400)
                        st.write("--Results for filtering by weights----")

                # End section weight filter
                #
                selected_features = st.sidebar.multiselect("Select Features to Filter", combined_feature_names)
                selected_feature_values = {}
                if selected_features:
                    for feature_name in selected_features:
                        if feature_name == "liverClass":
                            # Dropdown for liverClass selection
                            selected_values = st.sidebar.multiselect("Select liverClass", unique_liver_classes)
                            if selected_values:  # Check if any values are selected
                                selected_feature_values[feature_name] = selected_values
                            else:
                                st.sidebar.warning("Please select at least one liverClass")
                        elif feature_name == "inoculation":
                            # Dropdown for inoculation selection
                            selected_values = st.sidebar.multiselect("Select inoculation", unique_inoculation)
                            if selected_values:  # Check if any values are selected
                                selected_feature_values[feature_name] = selected_values
                            else:
                                st.sidebar.warning("Please select at least one inoculation")
                        elif feature_name == "Study_Day":
                            # Dropdown for Study_Day selection
                            selected_values = st.sidebar.multiselect("Select Study_Day", unique_study_date)
                            if selected_values:  # Check if any values are selected
                                selected_feature_values[feature_name] = selected_values
                            else:
                                st.sidebar.warning("Please select at least one Study_Day")

                        elif feature_types.get(feature_name) == "range":
                            min_val = st.sidebar.text_input(f"Enter minimum value for {feature_name}")
                            max_val = st.sidebar.text_input(f"Enter maximum value for {feature_name}")
                            if min_val and max_val:  # Check if both minimum and maximum values are provided
                                selected_feature_values[feature_name] = (min_val, max_val)
                            else:
                                st.sidebar.warning(f"Please enter both minimum and maximum values for {feature_name}")
                        else:
                            value = st.sidebar.text_input(f"Enter value for {feature_name}")
                            if value:  # Check if a value is provided
                                selected_feature_values[feature_name] = value
                            else:
                                st.sidebar.warning(f"Please enter a value for {feature_name}")
                else:
                    st.write(f"Please select a feature on the side bar.")
                # Initialize an empty set to store the resulting host IDs
                host_ids = set()

                # Initialize dictionaries to store host IDs for each condition
                host_ids_conditions = {}

                # Iterate through selected features and their values
                if selected_feature_values:
                    formatted_selected_study_ids = ', '.join(map(str, selected_study_ids))
                    for feature_name, feature_value in selected_feature_values.items():
                        # Initialize an empty set to store host IDs for the current condition
                        host_ids_condition = set()

                        # If the feature is a range type
                        if feature_name in pen_feature_list:
                            if feature_types.get(feature_name) == "range":
                                min_val, max_val = feature_value
                                if min_val and max_val:
                                    # Construct the query for the current condition
                                    query_condition = f"""
                                                               SELECT DISTINCT "Host_IdHost" as "Host_idHost"
                                                               from public."Host_has_Pen" hhp JOIN public."Host" h ON h."IdHost" = hhp."Host_IdHost" WHERE h."Study_idStudy"  in ({formatted_selected_study_ids})
                                                               AND "Pen_IdPen" in (select "Pen_IdPen" from public."Pen_has_Feature" where "Feature_IdFeature"=(SELECT "IdFeature" FROM public."Feature" WHERE "FeatureName" = '{feature_name}')
                                                               AND CAST(REPLACE("Value", ',', '.') AS NUMERIC) BETWEEN {min_val} AND {max_val})
                                                           """

                            else:
                                # Check if feature_value is a list
                                if isinstance(feature_value, list):
                                    st.write("List")
                                    # Construct the query for multiple feature values
                                    values_str = ", ".join([f"'{val}'" for val in feature_value])
                                    query_condition = f"""
                                                                                             SELECT DISTINCT fft."Host_idHost"
                                                                    FROM public."FeatureFactTable" fft
                                                                    JOIN public."Feature" f ON fft."Feature_idFeature" = f."IdFeature"
                                                                    JOIN public."Host" h ON fft."Host_idHost" = h."IdHost"
                                                                    WHERE fft."Feature_idFeature" = (SELECT "IdFeature" FROM public."Feature" WHERE "FeatureName" = '{feature_name}')
                                                                    AND fft."Value" in ({values_str}) AND h."Study_idStudy"  in ({formatted_selected_study_ids})
                                                            """
                                else:
                                    # Construct the query for the current condition

                                    feature_value = feature_value[0]
                                    query_condition = f"""
                                                               SELECT DISTINCT "Host_IdHost"  as Host_idHost"
                                                                from public."Host_has_Pen" hhp JOIN public."Host" h ON h."IdHost" = hhp."Host_IdHost" WHERE h."Study_idStudy"  in ({formatted_selected_study_ids})
                                                                AND "Pen_IdPen" in (select "Pen_IdPen" from public."Pen_has_Feature"
                                                                where "Feature_IdFeature"=(SELECT "IdFeature" FROM public."Feature" WHERE "FeatureName"= '{feature_name}')
                                                               AND fft."Value" = '{feature_value}')
                                                           """

                                # Execute the query for the current condition using Pandas
                            df_condition = pd.read_sql_query(query_condition, conn)
                            # Store the host IDs for the current condition
                            host_ids_condition.update(df_condition["Host_idHost"])
                            # Store the host IDs in the dictionary
                            host_ids_conditions[feature_name] = host_ids_condition
                        else:
                            if feature_types.get(feature_name) == "range":
                                min_val, max_val = feature_value
                                if min_val and max_val:
                                    # Construct the query for the current condition
                                    query_condition = f"""
                                        SELECT DISTINCT fft."Host_idHost"
                                        FROM public."FeatureFactTable" fft
                                        JOIN public."Feature" f ON fft."Feature_idFeature" = f."IdFeature"
                                        JOIN public."Host" h ON fft."Host_idHost" = h."IdHost"
                                        WHERE fft."Feature_idFeature" = (SELECT "IdFeature" FROM public."Feature" WHERE "FeatureName" = '{feature_name}')
                                        AND h."Study_idStudy"  in ({formatted_selected_study_ids})
                                        AND CAST(REPLACE(fft."Value", ',', '.') AS NUMERIC) BETWEEN {min_val} AND {max_val} 
                                    """

                            else:
                                if isinstance(feature_value, list):
                                    st.write("List")
                                    # Construct the query for multiple feature values
                                    values_str = ", ".join([f"'{val}'" for val in feature_value])
                                    query_condition = f"""
                                                                 SELECT DISTINCT fft."Host_idHost"
                                        FROM public."FeatureFactTable" fft
                                        JOIN public."Feature" f ON fft."Feature_idFeature" = f."IdFeature"
                                        JOIN public."Host" h ON fft."Host_idHost" = h."IdHost"
                                        WHERE fft."Feature_idFeature" = (SELECT "IdFeature" FROM public."Feature" WHERE "FeatureName" = '{feature_name}')
                                        AND fft."Value" in ({values_str}) AND h."Study_idStudy"  in ({formatted_selected_study_ids})
                                                                
                                                            """
                                else:
                                    # Construct the query for the current condition
                                    feature_value = feature_value[0]
                                    query_condition = f"""
                                        SELECT DISTINCT fft."Host_idHost"
                                        FROM public."FeatureFactTable" fft
                                        JOIN public."Feature" f ON fft."Feature_idFeature" = f."IdFeature"
                                        JOIN public."Host" h ON fft."Host_idHost" = h."IdHost"
                                        WHERE fft."Feature_idFeature" = (SELECT "IdFeature" FROM public."Feature" WHERE "FeatureName" = '{feature_name}')
                                        AND fft."Value" = '{feature_value}' AND h."Study_idStudy"  in ({formatted_selected_study_ids})
                                    """

                            # Execute the query for the current condition using Pandas
                            # Test query condition
                            # st.write(query_condition)
                            df_condition = pd.read_sql_query(query_condition, conn)
                            # Store the host IDs for the current condition
                            host_ids_condition.update(df_condition["Host_idHost"])
                            # Store the host IDs in the dictionary
                            host_ids_conditions[feature_name] = host_ids_condition

                # Initialize the common host IDs with the host IDs from the first condition
                # Check if host_ids_conditions is not empty before trying to get the next item
                if host_ids_conditions:
                    # Get the next item from host_ids_conditions
                    common_host_ids = host_ids_conditions[next(iter(host_ids_conditions))]
                else:
                    # Handle the case when host_ids_conditions is empty
                    # For example, you can assign a default value to common_host_ids
                    common_host_ids = None  # or any other appropriate default value

                # Find the intersection of host IDs for all conditions
                if host_ids_conditions:
                    for host_ids_condition in host_ids_conditions.values():
                        common_host_ids = common_host_ids.intersection(host_ids_condition)

                # TODO CHECK THE FEATURE COMMING FROM pEN NOT FEATURE FACT TABLE
                # Count the number of common host IDs
                # Check if common_host_ids is not None before getting its length
                if common_host_ids:
                    st.write("Common Host IDs (based only one features pen/host without weight filtering):", len(common_host_ids))
                    # st.write("Common Host IDs Set:", len(set(common_host_ids)))   #debug common hots Ids
                else:
                    st.write("No Common Host IDs")
                # if disco1 poc1 or poc2 is selected and filtred with weight  do this section
                if common_host_ids:
                    if selected_study_ids is not None:
                        if 3 in selected_study_ids:
                            all_disco1_idHost_list = get_all_idHost_based_on_study_id(3, conn)
                            if 'filtered_data_weight_range_4bw_diso1' in locals() and filtered_data_weight_range_4bw_diso1 is not None and not filtered_data_weight_range_4bw_diso1.empty:
                                filtered_data_weight_range_4bw_list = set(
                                    filtered_data_weight_range_4bw_diso1['IdHost'].tolist())

                                # Remove elements from common_host_ids that are in all_disco1_idHost_list
                                common_host_ids = [id for id in common_host_ids if id not in all_disco1_idHost_list]
                            else:
                                filtered_data_weight_range_4bw_list = None
                            if filtered_data_weight_range_4bw_list is not None:
                                common_host_ids.extend(filtered_data_weight_range_4bw_list)

                    # if selected_study_ids is not None:
                    #     if 4 in selected_study_ids:
                    #         all_poc1_idHost_list = get_all_idHost_based_on_study_id(4, conn)
                    #
                    #         if filtered_data_weight_range_bw_POC1.empty:
                    #             filtered_data_weight_range_bw_POC1_list = set(filtered_data_weight_range_bw_POC1['IdHost'].tolist())
                    #
                    #             # Remove elements from common_host_ids that are in all_poc1_idHost_list
                    #             common_host_ids = [id for id in common_host_ids if id not in all_poc1_idHost_list]
                    #             # Add elements from filtered_data_weight_range_bw_POC1 to common_host_ids
                    #         else:
                    #             filtered_data_weight_range_bw_POC1_list = None
                    #         if filtered_data_weight_range_bw_POC1_list is not None:
                    #             common_host_ids.extend(filtered_data_weight_range_bw_POC1_list)
                    if selected_study_ids is not None:
                        if 4 in selected_study_ids:
                            all_poc1_idHost_list = get_all_idHost_based_on_study_id(4, conn)
                            if 'filtered_data_weight_range_bw_POC1' in locals() and filtered_data_weight_range_bw_POC1 is not None and not filtered_data_weight_range_bw_POC1.empty:

                                filtered_data_weight_range_bw_POC1_list = set(
                                    filtered_data_weight_range_bw_POC1['IdHost'].tolist())

                                # st.write("Filtered DataFrame list:",
                                #          filtered_data_weight_range_bw_POC1_list)  # Debugging statement

                                # Remove elements from common_host_ids that are in all_poc1_idHost_list
                                common_host_ids = [id for id in common_host_ids if id not in all_poc1_idHost_list]
                                # Add elements from filtered_data_weight_range_bw_POC1 to common_host_ids
                                common_host_ids.extend(filtered_data_weight_range_bw_POC1_list)

                                # st.write("Common Host IDs after extension:", common_host_ids)  # Debugging statement
                            else:
                                filtered_data_weight_range_bw_POC1_list = None

                            # st.write("Filtered Data List:",
                            #          filtered_data_weight_range_bw_POC1_list)  # Debugging statement

                    if selected_study_ids is not None:
                        if 5 in selected_study_ids:
                            all_poc2_idHost_list = get_all_idHost_based_on_study_id(5, conn)
                            if 'filtered_data_weight_range_bw_POC2' in locals() and filtered_data_weight_range_bw_POC2 is not None and not filtered_data_weight_range_bw_POC2.empty:
                                filtered_data_weight_range_bw_POC2_list = set(
                                    filtered_data_weight_range_bw_POC2['IdHost'].tolist())
                                # st.write(len(all_poc2_idHost_list))
                                # st.write(all_poc2_idHost_list)
                                # st.write("filtered_data_weight_range_bw_POC2", filtered_data_weight_range_bw_POC2_list)
                                # Remove elements from common_host_ids that are in all_poc2_idHost_list
                                common_host_ids = [id for id in common_host_ids if id not in all_poc2_idHost_list]
                                # st.write("len after deleting all ", len(common_host_ids))
                            else:
                                filtered_data_weight_range_bw_POC2_list = None
                        # Add elements from filtered_data_weight_range_bw_POC2 to common_host_ids
                        if filtered_data_weight_range_bw_POC2_list is not None:
                            common_host_ids.extend(filtered_data_weight_range_bw_POC2_list)

                        # st.write("len after adding the ones ",len(common_host_ids))

                # st.write("idHost_filtred_based_on_weight", idHost_filtred_based_on_weight)

                # filtered_data_weight_range_4bw  filtered_data_weight_range_7bw  common_host_ids
                # idHost_list_4bw = set()
                # idHost_list_7bw = set()

                # if 3 in selected_study_ids:
                #     idHost_list_4bw = set(filtered_data_weight_range_4bw['IdHost'].tolist())
                #     st.write("IdHost Set 4BW:", idHost_list_4bw)
                #
                # if 4 in selected_study_ids:
                #     idHost_list_7bw = set(filtered_data_weight_range_bw_POC1['IdHost'].tolist())
                #     st.write("IdHost Set 7BW Poc1:", idHost_list_7bw)
                #
                # if 5 in selected_study_ids:
                #     idHost_list_7bw = set(filtered_data_weight_range_bw_POC2['IdHost'].tolist())
                #     st.write("IdHost Set 7BW Poc2:", idHost_list_7bw)
                #
                if common_host_ids:
                    st.sidebar.write("\n---\n")  # Section separation
                    st.sidebar.subheader(
                        f"Step 3: You have {len(common_host_ids)} individual hosts that correspond to your "
                        f"filtering.")
                    st.write("FINAL Common Host IDs:", len(common_host_ids))
                    # Iterate through the list and display each element
                    # Create an empty list to store the host IDs
                    host_ids_list_final = []

                    # Iterate through the common_host_ids list and append each element to the host_ids_list
                    for id in common_host_ids:
                        host_ids_list_final.append(id)

                    # Display the host_ids_list
                    # st.write(host_ids_list_final)
                    st.write("\n---\n")  # Larger section separation

                    # Step 4: Choose action
                    st.sidebar.write("\n---\n")  # Section separation
                    st.sidebar.subheader(
                        f"Step 4: Choose an action")
                    action = st.sidebar.selectbox("", ["Fetch all information", "Visualization", "Explomics (Soon)"], index=None)
                    df_vizualisation = get_all_data_by_hostId(host_ids_list_final, conn)

                    if action == "Fetch all information":
                        with st.spinner("Please wait, we're fetching all selected information..."):
                            df = get_all_data_by_hostId(host_ids_list_final, conn)
                            st.success("Data preparation completed!")

                        st.write("The matrix contains", len(df), "lines of information.")
                        st.write(
                            "Below is the dataframe that will serve as input for all graphs and previous visualizations:")
                        st.write(df)
                        # Add a download button to download the grouped DataFrame as a CSV file
                        csv_data = df.to_csv(index=False, encoding='utf-8')
                        st.download_button(label="Download this DataFrame as CSV", data=csv_data,
                                           file_name='Filtred-matrix.csv',
                                           mime='text/csv')

                        # Add code to fetch all information concerning the common hosts
                        # For example:
                        # all_information = fetch_all_information(common_host_ids)
                        # st.write(all_information)
                        pass
                    elif action == "Visualization":
                        st.title('Visualization Selector')

                        # Allow users to select features from the DataFrame
                        selected_features = st.multiselect("Select features:", df_vizualisation.columns)

                        # Filter DataFrame based on selected features
                        filtered_df = df_vizualisation[selected_features]

                        # Convert filtered DataFrame to JSON format
                        json_data = filtered_df.to_json(orient="records")

                        # Display RawGraphs in an iframe
                        if st.button("Visualize with RawGraphs"):
                            # Create a JSON file to pass data to RawGraphs
                            with open("data.json", "w") as json_file:
                                json.dump(json.loads(json_data), json_file)

                            # URL to RawGraphs with the file path to the JSON data
                            rawgraphs_url = "https://app.rawgraphs.io/?data=/data.json"

                            # Embed RawGraphs in an iframe with larger height
                            iframe_code = f'<iframe src="{rawgraphs_url}" width="100%" height="1200px" style="border:none;"></iframe>'
                            st.write(iframe_code, unsafe_allow_html=True)
                            # api_call = "https://api.rawgraphs.io/v2.0-alpha/rcv1?id=" + "&".join(df_vizualisation)
                            # response = requests.get(api_call)
                            # # Display RawGraph visualization or link
                            # st.write("RawGraph Visualization:")
                            # st.write(response.text)  # Displaying API response, adjust as needed
                        pass


                else:
                    st.sidebar.write("\n---\n")  # Section separation
                    st.sidebar.subheader("Step 3: Too much restrictions in the filtering.")
                    # Additional content in the sidebar
                    st.sidebar.write("You've applied too many restrictions in the filtering process.")
                    st.sidebar.write("Consider refining your filters to get more results.")

                # (bring me all the info)
                # (Visualisation)




        # ////////////////////////////////// App Overview \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        elif selected_page == "App Overview":
            st.sidebar.title("You selected: App Overview")
            st.write("### Overview:")
            st.write("Welcome to Your App! This application allows you to explore, analyze, and visualize data.")

            # Key features section
            st.subheader("Key Features:")
            features = [
                "Search and filter data by host, taxonomy, and more.",
                "Visualize abundance and weight data.",
                "Download filtered data as CSV."
            ]
            st.markdown("\n".join([f"- {feature}" for feature in features]))

            # How to use section
            st.subheader("How to Use:")
            usage_steps = [
                "Select a page from the sidebar navigation.", "Download filtered data using the provided buttons."
                                                              "Explore data using checkboxes, sliders, and dropdowns.",
                "Download filtered data using the provided buttons."
            ]
            st.markdown("\n".join([f"**Step {i + 1}:** {step}" for i, step in enumerate(usage_steps)]))

            # Data sources section
            st.subheader("Data Sources:")
            st.write("The app uses data from Postgres Database V3.2.")

            # Support and documentation section
            st.subheader("Support:")
            st.write("If you need assistance, please refer to the documentation or contact us.")

            # Decorative separator
            components.html("<hr style='border: 1px solid #ddd;'>", height=10)
        elif selected_page == "Search By Host":
            with st.spinner("Wait, we're warming up the data for you..."):
                time.sleep(3)  # Simulate some processing time
                st.success("Data preparation completed!")
            st.sidebar.title("You selected: Search By Host")
            page1()

        elif selected_page == "Search By Taxa":
            st.sidebar.title("You selected: Search by Taxa")

            # # Additional content for searching by taxa
            st.sidebar.text("### Overview:")
            # st.sidebar.text("Searching by taxa allows you to find information related to \n"
            #                 " different taxonomic groups.")
            #
            # st.sidebar.text("### Options Available:")
            # st.sidebar.text("- **Taxonomic Rank:** Choose the specific taxonomic rank you \n"
            #                 " are interested in.")
            # st.sidebar.text("- **Taxon Name:** Enter the name of the taxon you want to search for.")
            # st.sidebar.text("- **Search Depth:** Set the depth of the taxonomic search.")
            #
            # st.sidebar.text("### Explanation:")
            # st.sidebar.text("The 'Taxonomic Rank' refers to the level of classification (e.g., genus, species).")
            # st.sidebar.text("Specify the 'Taxon Name' to find information about a particular taxon.")
            # st.sidebar.text("Adjust the 'Search Depth' to control the level of detail in the search results.")
            # #
            # Add a sidebar

            # Sidebar section for Absolute and Relative Abundance
            if st.sidebar.checkbox("Show Absolute & Relative Abundance/Sample by Multi-selection on (OTU)"):
                styled_sidebar_section(
                    "Absolute and Relative Abundance",
                    "Analyze absolute and relative abundance for each item across samples.",
                    "- **Top N SampleNames:** Choose the number of top SampleNames to visualize.\n"
                    "- **Relative Abundance Range:** Set the range for relative abundance.",
                    "Select the 'Top N SampleNames' to focus on the most abundant samples. "
                    "Adjust the 'Relative Abundance Range' to filter items based on their relative abundance."
                )

            # Sidebar section for Sunburst Plot
            elif st.sidebar.checkbox("Show Sunburst Plot"):
                styled_sidebar_section(
                    "Sunburst Plot",
                    "Visualize the relative abundance through a Sunburst Plot.",
                    "- **Threshold for Relative Abundance:** Set the threshold for relative abundance.",
                    "Adjust the 'Threshold for Relative Abundance' to focus on items above a certain abundance level."
                )

            # Sidebar section for 3D Scatter Plot
            elif st.sidebar.checkbox("Show 3D Scatter Plot"):
                styled_sidebar_section(
                    "3D Scatter Plot",
                    "Visualize relative abundance in a 3D Scatter Plot.",
                    "- **Threshold for Relative Abundance:** Set the threshold for relative abundance.",
                    "Adjust the 'Threshold for Relative Abundance' to focus on data points above a certain abundance level."
                )

            # Sidebar section for Individual Sample Analysis
            elif st.sidebar.checkbox("Show Individual Sample Analysis"):
                styled_sidebar_section(
                    "Individual Sample Analysis",
                    "Analyze relative abundance for each item in a specific sample.",
                    "- **Select SampleName:** Choose the specific SampleName for analysis.",
                    "Choose a 'SampleName' to analyze the relative abundance composition for each item in that sample."
                )

            page2()

        conn.close()


    if __name__ == '__main__':
        main()
    # Streamlit app code
    # # Search for Item by name
    # selected_item = st.selectbox("Select Item", df_items['ItemName'])
    #
    #
    # # Fetch Abundance data for the selected Item
    # query_abundance = f"""
    #     SELECT af."Sample_idSample", s."SampleName", af."Abundance"
    #     FROM public."AbundanceFactTable" af
    #     JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
    #     JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
    #     WHERE i."ItemName" = '{selected_item}'
    # """
    # df_abundance = pd.read_sql(query_abundance, conn)
    #
    # # Display Abundance data
    # st.write(f"## Abundance Data for Item: {selected_item}")
    # st.dataframe(df_abundance)

    # V2
    # Search for Item by typing
    # Streamlit app code
    # st.title("Search Items and View Abundance")
    #
    # Add the rest of your Streamlit app code...
else:
    st.title("User not authenticated.\n Please log in.")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# # Search for Item by typing
# search_input = st.text_input("Search for an Item")
# filtered_items = df_items[df_items['ItemName'].str.contains(search_input, case=False)]
#
# if not filtered_items.empty:
#     selected_item = st.selectbox("Select Item", filtered_items['ItemName'])
#
#     # Display count of available options
#     st.write(f"Number of available options: {len(filtered_items)}")
#
#     # Fetch Abundance data for the selected Item and StudyName
#     query_abundance = f"""
#         SELECT af."Sample_idSample", s."SampleName", af."Abundance"
#         FROM public."AbundanceFactTable" af
#         JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
#         JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
#         JOIN public."Host" h ON s."Host_idHost" = h."IdHost"
#         JOIN public."Study" st ON h."Study_idStudy" = st."idStudy"
#         WHERE i."ItemName" = '{selected_item}' AND st."idStudy" = '{selected_study_id}'
#     """
#     df_abundance = pd.read_sql(query_abundance, conn)
#
#     # Display Abundance data
#     st.write(f"## Abundance Data for Item: {selected_item}")
#     st.dataframe(df_abundance)
# else:
#     st.write("No items found.")


# Close the database connection when done

# # Display Host data as a table
# st.write("## Host Data")
# st.dataframe(df_host, height=400)
#
# # Allow the user to click on a row and display the selected Host details
# selected_row = st.table_add_rows_click("Click on a row to view related features", df_host)
#
# # Fetch related Feature data for the selected Host from the connection table
# if selected_row is not None:
#     selected_host_id = df_host.loc[selected_row]['IdHost']
#
#     query_related = f"""
#         SELECT f."IdFeature", f."FeatureName", ff."Value"
#         FROM public."FEATUREFactTable" ff
#         JOIN public."Feature" f ON ff."Feature_idFeature" = f."IdFeature"
#         WHERE ff."Host_idHost" = {selected_host_id}
#     """
#     df_related = pd.read_sql(query_related, conn)
#
#     # Display related Feature data
#     st.write("## Related Feature Data")
#     st.dataframe(df_related, height=300)
#     st.dataframe(df_related, height=300)