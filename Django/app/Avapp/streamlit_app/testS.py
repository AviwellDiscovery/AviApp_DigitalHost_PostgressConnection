import start_streamlit as st
import psycopg2
import pandas as pd
import json  # TODO
import matplotlib.pyplot as plt

# Connect to PostgreSQL database
conn = psycopg2.connect(
    database="devdb_v2.2",
    user="reda",
    password="1321",
    host="localhost",
    port="5432"
)

# Streamlit app code
st.title("Hosts and Related Features")

# Fetch Host data
query_host = "SELECT * FROM public.\"Host\""
query_study = "SELECT * FROM public.\"Study\""

df_host = pd.read_sql(query_host, conn)
df_study = pd.read_sql(query_study, conn)

# Streamlit app code
st.title("Filtered Hosts with Weight Information")

# Fetch Host data with filters
# selected_study_id = st.selectbox("Select Study ID", df_study['StudyName'].unique())
selected_study_name = st.selectbox("Select Study ID", df_study['StudyName'].unique())

# Dictionary to map Study Name to ID
study_name_to_id = {
    "PROD1": 1,
    "PROD2": 2,
    "DISCO1": 3,
    "POC1": 4
}

# Get the selected_study_id based on the selected_study_name
selected_study_id = study_name_to_id.get(selected_study_name)

selected_sex = st.multiselect("Select Sex", df_host['Sex'].unique())

# Filter Host data based on selected Study ID and Sex
filtered_host_data = df_host[(df_host['Study_idStudy'] == selected_study_id) & (df_host['Sex'].isin(selected_sex))]

# Display filtered Host data
st.write("## Filtered Host Data")
st.dataframe(filtered_host_data, height=400)

# Extract weight values for study 3
if selected_study_id == 3:
    weight_fields_study3 = ["BirdWeight_D0", "BirdWeight_D21", "BirdWeight_D35", "BirdWeight_D9"]
    for field in weight_fields_study3:
        filtered_host_data[field] = filtered_host_data['Weight'].apply(lambda x: x.get(field, None))

    # Display Weight data for study 3
    st.write("## Weight Data for Study 3")
    st.dataframe(filtered_host_data[["IdHost"] + weight_fields_study3])

# Extract weight values for study 4
if selected_study_id == 4:
    weight_fields_study4 = {
        "AvgBirdWeight_D0": "AvgBirdWeight_D0",
        "AvgBirdWeight_D7": "AvgBirdWeight_D7",
        "AvgBirdWeight_D14": "AvgBirdWeight_D14",
        "AvgBirdWeight_D21": "AvgBirdWeight_D21",
        "AvgBirdWeight_D28": "AvgBirdWeight_D28",
        "AvgBirdWeight_D35": "AvgBirdWeight_D35",
        "Bird_weight_D36": "Bird_weight_D36"
    }
    for field, target_field in weight_fields_study4.items():
        filtered_host_data[target_field] = filtered_host_data['Weight'].apply(lambda x: x.get(field, None))

    # Display Weight data for study 4
    st.write("## Weight Data for Study 4")
    st.dataframe(filtered_host_data[["IdHost"] + list(weight_fields_study4.values())])

# Option to display features of a selected Host_id
selected_host_id_feature = st.selectbox("Select Host ID to Display Features", filtered_host_data['IdHost'])

# Fetch related Feature data for the selected Host from the connection table
query_features = f"SELECT f.\"FeatureName\", ff.\"Value\" FROM public.\"FeatureFactTable\" ff JOIN public.\"Feature\" f ON ff.\"Feature_idFeature\" = f.\"IdFeature\" WHERE ff.\"Host_idHost\" = {selected_host_id_feature}"
df_features = pd.read_sql(query_features, conn)

# Display Features for the selected Host_id
st.write(f"## Features for Host ID {selected_host_id_feature}")
st.dataframe(df_features)

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

# Visualize weight if checkbox is selected
if show_weight_chart:
    st.title("Weight Visualization")

    # Extract weight values for the selected hosts
    if selected_host_id_feature:
        weight_fields = ["BirdWeight_D0", "BirdWeight_D9", "BirdWeight_D21", "BirdWeight_D35"]
        weight_fields_study4 = ["AvgBirdWeight_D0", "AvgBirdWeight_D7", "AvgBirdWeight_D21", "AvgBirdWeight_D28",
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

# Fetch Item names for dropdown search
query_items = "SELECT \"IdItem\", \"ItemName\" FROM public.\"Item\""
df_items = pd.read_sql(query_items, conn)

# Streamlit app code
st.title("Search Items and View Abundance")

# Streamlit app code
st.title("Search Items and View Abundance")

# Search for Item by typing
search_input = st.text_input("Search for an Item")
filtered_items = df_items[df_items['ItemName'].str.contains(search_input, case=False)]

# selected_study_id = st.selectbox("Select Study ID", df_study['StudyName'].unique())
selected_study_name2 = st.selectbox("Select Study ID", df_study['StudyName'].unique())

# Get the selected_study_id based on the selected_study_name
selected_study_id = study_name_to_id.get(selected_study_name2)
# Input field for IdStudy
# selected_study_id = st.text_input("Enter Study ID")

if not filtered_items.empty and selected_study_id:
    # Convert input study ID to integer
    selected_study_id = int(selected_study_id)

    # Fetch Hosts related to the Study of interest
    query_hosts = f"""
        SELECT h."IdHost"
        FROM public."Host" h
        WHERE h."Study_idStudy" = {selected_study_id}
    """
    hosts_in_study = pd.read_sql(query_hosts, conn)

    # Fetch Samples related to the selected Hosts
    query_samples = f"""
        SELECT s."IdSample"
        FROM public."Sample" s
        WHERE s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
    """
    samples_in_study = pd.read_sql(query_samples, conn)

    # Filter Item options based on available Samples
    filtered_items = filtered_items[filtered_items['IdItem'].isin(samples_in_study['IdSample'])]

    # Display count of available options
    st.write(f"Number of available options: {len(filtered_items)}")

    # Select Item from filtered options
    selected_item = st.selectbox("Select Item", filtered_items['ItemName'])

    # Fetch Abundance data for the selected Item and StudyName
    query_abundance = f"""
        SELECT af."Sample_idSample", s."SampleName", af."Abundance"
        FROM public."AbundanceFactTable" af
        JOIN public."Sample" s ON af."Sample_idSample" = s."IdSample"
        JOIN public."Item" i ON af."Item_idItem" = i."IdItem"
        WHERE i."ItemName" = '{selected_item}' AND s."Host_idHost" IN {tuple(hosts_in_study['IdHost'])}
    """
    df_abundance = pd.read_sql(query_abundance, conn)

    # Display Abundance data
    st.write(f"## Abundance Data for Item: {selected_item}")
    st.dataframe(df_abundance)
elif not selected_study_id:
    st.warning("Please enter a valid Study ID.")

# Close the database connection when done
conn.close()
