from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import streamlit as st
import psycopg2
import pandas as pd
import json  # TODO
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests, sys
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
# # Assuming session_key is stored in a global variable
# def logout():
#     global session_key
#     session_key = None
#     # Send a request to Django to clear the session
#     response = requests.get('http://127.0.0.1:8000/logout/')
#     if response.status_code == 200:
#         st.success("You have been logged out successfully!")
#     else:
#         st.error("Error logging out. Please try again.")
#
# # Assuming you have a button to trigger logout
# if st.button("Logout"):
#     logout()

# Assume you have a function to authenticate and get the access token
# Assume you have a function to authenticate and get the access token
# def get_access_token(username, password):
#     # Make a request to your Django app to obtain the access token
#     response = requests.post('http://127.0.0.1:8000/token/', data={'username': username, 'password': password})
#     response.raise_for_status()
#     data = response.json()
#     return data.get('access_token')

# Assume you have a function to get the session key
# def get_session_key(access_token):
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#     }
#
#     response = requests.get('http://127.0.0.1:8000/avapp/session_key/', headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     return data.get('session_key')

# Initialize session_key
# session_key = None
# # Function to get access token from Django
# def get_access_token(username, password):
#     response = requests.post('http://127.0.0.1:8000/avapp/generate_token/', data={'username': username, 'password': password})
#     data = response.json()
#     return data.get('token')
#
# # Function to check authentication using the obtained token
# def check_authentication(token):
#     headers = {'Authorization': f'Token {token}'}
#     response = requests.get('http://127.0.0.1:8000/avapp/session_key/', headers=headers)
#
#     print(f"Response Status Code: {response.status_code}")
#     print(f"Response Content: {response.content}")
#
#     if response.status_code == 200:
#         data = response.json()
#         return data.get('session_key')
#     else:
#         return None
#
#
# # Streamlit UI
# st.title("Django Streamlit Authentication")
#
# # Accept user input for username and password
# username = st.text_input("Username")
# password = st.text_input("Password", type="password")
#
# if st.button("Login"):
#     access_token = get_access_token(username, password)
#     st.write(access_token)
#
#     if access_token:
#         session_key = check_authentication(access_token)
#
#         if session_key:
#             st.write(f"Session Key: {session_key}")
#         else:
#             st.write("Access Denied")
#     else:
#         st.write("Invalid Credentials")

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

    # Dictionary to map Study Name to ID
    study_name_to_id = {
        "PROD2": 2,
        "DISCO1": 3,
        "PROD1": 1,
        "POC1": 4
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
            "POC1": 4
        }
        show_data_item = st.checkbox("Show Abundance Data by Item (Species)")
        if show_data_item:
            # Streamlit app code
            st.title("Abundance Search by Items and Study")
            # selected_study_id = st.selectbox("Select Study ID", df_study['StudyName'].unique())
            # selected_study_name = st.selectbox("Select Study Name", df_study['StudyName'].unique())
            selected_study_names = st.multiselect("Select Study Names", df_study['StudyName'].unique())
            selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
            # Add content specific to Page 2
            # Get the selected_study_id based on the selected_study_name
            # selected_study_id = study_name_to_id.get(selected_study_names)

            # Search for Item by typing
            search_input = st.text_input("Search for an Item")
            filtered_items = df_items[df_items['ItemName'].str.contains(search_input, case=False)]

            # # Search for Item by typing
            # taxonomy_search_input = st.text_input("Search by Taxonomy")    # Filter items based on user input
            # # Filter items based on Taxonomy search
            # if taxonomy_search_input:
            #     # Query to get Item_idItem based on Taxonomy
            #     query_taxonomy_search = f"""
            #         SELECT "Item_idItem"
            #         FROM public."Taxons"
            #         WHERE "Taxonomy" LIKE '%{taxonomy_search_input}%'
            #     """
            #     item_ids_from_taxonomy = pd.read_sql(query_taxonomy_search, conn)['Item_idItem']
            #
            #     # Filter items based on Item_idItem from Taxonomy search
            #     filtered_items_from_taxonomy = df_items[df_items['IdItem'].isin(item_ids_from_taxonomy)]
            #
            #     # Combine the results of both searches
            #     filtered_items = pd.concat([filtered_items, filtered_items_from_taxonomy])

            # Select Study Name
            host_id_selectbox_key = f"host_id_selectbox_{selected_study_ids}"

            # Get the selected_study_id based on the selected_study_name
            # selected_study_id = study_name_to_id.get(selected_study_names)
            selected_study_ids = [study_name_to_id[name] for name in selected_study_names]
            selected_study_ids_str = ', '.join(map(str, selected_study_ids))
            if not filtered_items.empty and selected_study_ids:
                # Fetch Hosts related to the Study of interest
                query_hosts = f"""
                    SELECT h."IdHost"
                    FROM public."Host" h
                    WHERE h."Study_idStudy" IN ({selected_study_ids_str})
                """
                hosts_in_study = pd.read_sql(query_hosts, conn)

                # Fetch Samples related to the selected Hosts
                query_samples = f"""
                    SELECT "IdItem" from Public."Item" where "IdItem" in ( 
                    Select "Item_idItem" from Public."AbundanceFactTable" where "Sample_idSample" in ( 
                    SELECT s."IdSample"
                    FROM public."Sample" s
                    WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}))
                """
                samples_in_study = pd.read_sql(query_samples, conn)

                # Filter Item options based on available Samples
                filtered_items = filtered_items[filtered_items['IdItem'].isin(samples_in_study['IdItem'])]

                # Display count of available options
                st.write(f"Number of available options: {len(filtered_items)}")

                # Select Item from filtered options
                selected_item = st.selectbox("Select Item", filtered_items['ItemName'])

                # Fetch Abundance data for the selected Item and StudyName

                # Fetch Abundance data for the selected Item and StudyName
                query_abundance = f"""
                    SELECT af."Sample_idSample", s."SampleName",s."Host_idHost", af."Abundance"
                    FROM public."AbundanceFactTable" af
                    JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
                    JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
                    WHERE i."ItemName" = '{selected_item}' AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
                """
                df_abundance = pd.read_sql(query_abundance, conn)

                if not df_abundance.empty:

                    # Sort dataframe by abundance in descending order
                    df_abundance_sorted = df_abundance.sort_values(by='Abundance', ascending=False)

                    # Show option to select top N items or show all using radio buttons
                    options = [5, 10, "All"]
                    selected_option = st.radio("Show Abundance Data", options)

                    if selected_option == "All":
                        df_selected = df_abundance_sorted
                    else:
                        top_n = int(selected_option)
                        df_selected = df_abundance_sorted.head(top_n)

                    # Display Abundance data for selected item
                    st.write(f"## Abundance Data for Item: {selected_item}")
                    st.dataframe(df_selected)


                else:
                    st.write("No abundance data available for the selected item.")

                # Add a download button
                if not df_selected.empty:
                    csv_export = df_selected.to_csv(index=False)
                    file_name = f"abundance_data_{selected_item}_{selected_study_names}.csv"
                    st.download_button(
                        label="Download CSV",
                        data=csv_export,
                        file_name=file_name,
                        mime="text/csv"
                    )

                # Create a distribution plot for normalized abundance
                # st.dataframe(df_selected)

                # Create a distribution plot for normalized abundance
                if not df_selected.empty:
                    # Convert 'Abundance' column to numeric (if it's not already)
                    df_selected['Abundance'] = pd.to_numeric(df_selected['Abundance'], errors='coerce')

                    # Calculate normalized abundance
                    total_abundance = df_selected['Abundance'].sum()
                    normalized_abundance = df_selected['Abundance'] / total_abundance

                    plt.figure(figsize=(10, 6))
                    sns.histplot(normalized_abundance, bins=20, kde=True)
                    plt.title(f"Distribution of Normalized Abundance for {selected_item}")
                    plt.xlabel("Normalized Abundance")
                    plt.ylabel("Frequency")
                    st.pyplot(plt)

                if not df_selected.empty:
                    # Convert 'Abundance' column to numeric (if it's not already)
                    df_selected['Abundance'] = pd.to_numeric(df_selected['Abundance'], errors='coerce')

                    # Calculate normalized abundance
                    total_abundance = df_selected['Abundance'].sum()
                    df_selected['NormalizedAbundance'] = df_selected['Abundance'] / total_abundance

                    # Create an interactive bar plot using Plotly Express
                    fig = px.bar(
                        df_selected,
                        x='NormalizedAbundance',
                        color='SampleName',  # Color bars by SampleName
                        title=f"Distribution of Normalized Abundance for {selected_item}",
                        labels={'NormalizedAbundance': 'Normalized Abundance'},
                    )
                    st.plotly_chart(fig)

                # todo
                st.write(f"## Relative Abundance V2")
                # Calculate total abundance for the selected bacterium
                total_abundance_bacterium = df_selected['Abundance'].sum()

                # Calculate relative abundance
                df_selected['RelativeAbundance'] = (df_selected['Abundance'] / total_abundance_bacterium) * 100

                # Create an interactive bar plot
                fig = px.bar(
                    df_selected,
                    x='SampleName',
                    y='RelativeAbundance',
                    title=f"Relative Abundance of {selected_item}",
                    labels={'RelativeAbundance': 'Relative Abundance (%)'},
                )
                fig.update_yaxes(range=[0, 100])  # Set y-axis range to 0-100 percent

                # Show the plot
                st.plotly_chart(fig)

                # Get the Item_idItem for the selected item
                query_item_id = f"""
                    SELECT "IdItem" FROM public."Item"
                    WHERE "ItemName" = '{selected_item}'
                """
                item_id = pd.read_sql(query_item_id, conn)['IdItem'].iloc[0]
                # Fetch Taxonomy information for the selected Item
                query_taxonomy = f"""
                       SELECT DISTINCT t."Taxonomy"
                       FROM public."Taxons" t
                       JOIN public."Item" i ON t."Item_idItem" = i."IdItem"
                       WHERE i."ItemName" = '{selected_item}'
                   """
                df_taxonomy = pd.read_sql(query_taxonomy, conn)
                df_abundance_sorted = df_abundance.sort_values(by='Abundance', ascending=False)

                # Display Abundance data for selected item
                st.write(f"## Abundance Data for Item: {selected_item}")
                st.dataframe(df_selected)

                # Display Taxonomy information
                if not df_taxonomy.empty:
                    st.write(f"## Taxonomy Information for Item: {selected_item}")
                    st.dataframe(df_taxonomy)

                    # Add the number of distinct lines in Taxonomy
                    num_distinct_lines = len(df_taxonomy['Taxonomy'].unique())
                    st.write(f"Number of Distinct Taxonomy Lines: {num_distinct_lines}")

        ####### Second part red@
        show_data_Otu = st.checkbox("Show Abundance Data by Taxonomy")
        if show_data_Otu:
            # Dropdown for selecting hierarchy level
            hierarchy_level = st.selectbox("Select Hierarchy Level",
                                           ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species",
                                            "Cluster"])

            # Search input for user to type a term
            search_input = st.text_input("Search for an Entry")

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
                            # After displaying the abundance data

                        else:
                            st.write(f"No taxonomy information found for {search_term}.")
                    else:
                        st.write("Invalid hierarchy level selected.")
        # show_composition_tax = st.checkbox("show Taxonomy Compositon")
        # if show_composition_tax:


    # For example, you can add some text or visualizations here

    def main():
        st.sidebar.title("Navigation")
        selected_page = st.sidebar.radio("Select a page", ["Search By Host",
                                                           "Search By Taxa"])
        if st.sidebar.button("Logout"):
            logout()  # Call the logout function if the button is clicked
        if selected_page == "Search By Host":
            page1()
        elif selected_page == "Search By Taxa":
            page2()
        conn.close()


    # Fetch Item names for dropdown search
    query_items = "SELECT \"IdItem\", \"ItemName\" FROM public.\"Item\""
    df_items = pd.read_sql(query_items, conn)

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
    st.title("User not authenticated. Please log in.")



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

