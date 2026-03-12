import feedparser
from Bio import Entrez
import pandas as pd
import numpy as np
import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup


def search_pubmed(queries):
    Entrez.email = 'email@example.com'
    results = []

    for query in queries:
        handle = Entrez.esearch(db='pubmed',
                                sort='relevance',
                                retmax='250000',
                                retmode='xml',
                                term=query)
        result = Entrez.read(handle)
        results.append(result)

    return results


def fetch_pubmed_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results


def process_pubmed_data(papers):
    data = []
    for paper in papers['PubmedArticle']:
        item = {
            'Title': paper['MedlineCitation']['Article']['ArticleTitle'],
            'Abstract': paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0] if 'Abstract' in
                                                                                              paper['MedlineCitation'][
                                                                                                  'Article'] else 'No Abstract',
            'Journal': paper['MedlineCitation']['Article']['Journal']['Title'] if 'Journal' in paper['MedlineCitation'][
                'Article'] else np.nan,
            'Language': paper['MedlineCitation']['Article']['Language'][0] if 'Language' in paper['MedlineCitation'][
                'Article'] else np.nan,
            'Year': paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'] if 'Year' in
                                                                                                         paper[
                                                                                                             'MedlineCitation'][
                                                                                                             'Article'][
                                                                                                             'Journal'][
                                                                                                             'JournalIssue'][
                                                                                                             'PubDate'] else 'No Data',
            'Month': paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month'] if 'Month' in
                                                                                                           paper[
                                                                                                               'MedlineCitation'][
                                                                                                               'Article'][
                                                                                                               'Journal'][
                                                                                                               'JournalIssue'][
                                                                                                               'PubDate'] else 'No Data',
        }

        # Ensure all values are converted to strings to avoid mixed data types
        item = {key: str(value) for key, value in item.items()}
        data.append(item)

    return data


# Define the fetch_arxiv_papers function


# Define the fetch_arxiv_papers function for web scraping
def fetch_arxiv_papers(query, category, n_papers, chunk_size):
    papers = []

    # Split the query by commas
    keywords = [kw.strip() for kw in query.split(',')]

    for keyword in keywords:
        for chunk_i in range(0, n_papers, chunk_size):
            encoded_query = urllib.parse.quote(keyword)
            feed = feedparser.parse(
                f'http://export.arxiv.org/api/query?search_query={encoded_query}+cat:{category}&start={chunk_i}&max_results={chunk_size}'
            )

            for entry in feed.entries:
                title = entry.title.replace('\n', '')
                papers.append({'Title': title, 'Summary': entry.summary, 'Link': entry.link})
        # Convert the list of dictionaries to a DataFrame
    papers_df = pd.DataFrame(papers)
    return papers_df

# def fetch_arxiv_papers(query, category, n_papers):
#     papers = []
#
#     # Split the query by commas
#     keywords = [kw.strip() for kw in query.split(',')]
#
#     for keyword in keywords:
#         # Make a request to the arXiv search page
#         url = f'https://arxiv.org/search/?query={keyword}&searchtype=all&source=header&category_{category}=on&abstracts=show&size={n_papers}'
#         response = requests.get(url)
#         soup = BeautifulSoup(response.content, 'html.parser')
#
#         # Extract paper details from the search results
#         entries = soup.find_all('li', class_='arxiv-result')
#         for entry in entries:
#             title = entry.find('p', class_='title is-5 mathjax').text.strip()
#             summary = entry.find('span', class_='abstract-full has-text-grey-dark mathjax').text.strip()
#             link = entry.find('p', class_='list-title is-inline-block').find('a')['href']
#
#             papers.append({'Title': title, 'Summary': summary, 'Link': link})
#
#     return papers



def main():
    # Streamlit app
    st.title("PubMed Web Scraping")

    # Search PubMed
    query_input = st.text_input("Enter your search queries (separated by commas):", 'FCR,CHICKEN')
    queries = [query.strip() for query in query_input.split(',')]
    
    # Ensure at least one query is entered
    if not any(queries):
        st.warning("Please enter at least one search query.")
        return

    studies_id_list = search_pubmed(queries)

    # Fetch PubMed details
    papers = fetch_pubmed_details(studies_id_list[0]['IdList'])

    # Process and display data
    if 'PubmedArticle' in papers:
        data = process_pubmed_data(papers)
        df = pd.DataFrame(data)

        # Convert month names to numeric values
        month_mapping = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                         'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

        df['Month'].replace(month_mapping, inplace=True)
        df['Month'].replace('No Data', np.nan, inplace=True)

        st.write("PubMed Data:")

        # Display the length of the DataFrame
        st.write(f"Number of Records: {len(df)}")
        st.write(df)
    else:
        st.write("No PubMed data found.")

    st.title("arXiv Papers Fetcher")

    # Set parameters
    query_input_arxiv = st.text_input('Search Query (Comma-separated)', 'interesting topic')
    n_papers = st.slider('Number of Papers', 1, 50000, 30000, step=1)
    chunk_size = st.slider('Chunk Size', 1, 100, 50, step=1)
    category = st.text_input('Category of interest', 'biology')

    # Add a "Search" button
    search_button = st.button("Search")

    # Fetch arXiv papers based on the query when the "Search" button is clicked
    if search_button:
        if category:
            papers_arxiv = fetch_arxiv_papers(query_input_arxiv, category, n_papers, chunk_size)

            # Display filtered papers
            st.write(f"Number of Papers matching '{query_input_arxiv}': {len(papers_arxiv)}")
            st.write("Filtered arXiv Papers:")
            st.write(papers_arxiv)

if __name__ == "__main__":
    main()