import requests
from difflib import get_close_matches

def fetch_ensembl_id(gene_name):
    """
    Fetch the Ensembl ID (ENSGAL identifier) for a given gene name.
    """
    base_url = "https://rest.ensembl.org"
    endpoint = f"/xrefs/symbol/gallus_gallus/{gene_name}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Check if exact matches are found
        if data:
            return data[0]['id']
        else:
            print(f"No exact match found for gene name: {gene_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Ensembl API: {e}")
        return None

def search_with_fuzzy_matching(gene_name):
    """
    Search for approximate matches using the Ensembl API and fuzzy matching.
    """
    base_url = "https://rest.ensembl.org"
    endpoint = "/xrefs/symbol/gallus_gallus"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extract available gene names
        gene_names = [item['display_id'] for item in data]

        # Find closest matches to the input gene name
        closest_matches = get_close_matches(gene_name, gene_names, n=1, cutoff=0.6)

        if closest_matches:
            closest_gene = closest_matches[0]
            print(f"Closest match found: {closest_gene}")
            return fetch_ensembl_id(closest_gene)
        else:
            print(f"No close matches found for gene name: {gene_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Ensembl API: {e}")
        return None

if __name__ == "__main__":
    input_gene_name = input("Enter a gene name: ").strip()

    # First, try exact match
    ensembl_id = fetch_ensembl_id(input_gene_name)

    # If no exact match, use fuzzy matching
    if not ensembl_id:
        print("Trying fuzzy matching...")
        ensembl_id = search_with_fuzzy_matching(input_gene_name)

    if ensembl_id:
        print(f"Ensembl ID for {input_gene_name}: {ensembl_id}")
    else:
        print(f"Unable to find an Ensembl ID for {input_gene_name}.")
