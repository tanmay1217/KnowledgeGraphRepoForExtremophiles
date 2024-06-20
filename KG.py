import streamlit as st
import pandas as pd
import re
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx

# Define the file paths for your data
chemicals_file_path = 'taTask3_PressureDeepSea_Chemical_pubmed.csv'
genes_file_path = 'taTask3_PressureDeepSea_Gene_pubmed.csv'
interactions_file_path = 'TaTask10_DiseaseShortFrom_Interaction_GeneToChemical_GrpNo.csv'

# Read the chemical, gene, and interactions CSV files into dataframes
chemicals_df = pd.read_csv(chemicals_file_path)
genes_df = pd.read_csv(genes_file_path)
interactions_df = pd.read_csv(interactions_file_path)

def preprocess_sentence(sentence):
    # Remove punctuation and convert to lowercase
    sentence = re.sub(r'[^\w\s]', '', sentence).lower()
    return sentence

# Convert 'Name' column in chemicals_df and 'Gene_Name' column in genes_df to string and preprocess
chemicals_df['Name'] = chemicals_df['Name'].astype(str).apply(preprocess_sentence)
genes_df['Gene_Name'] = genes_df['Gene_Name'].astype(str).apply(preprocess_sentence)

# Preprocess sentences in the interactions dataframe
interactions_df['Sentences'] = interactions_df['Sentences'].astype(str).apply(preprocess_sentence)

# Handle NaN values
chemicals_df.fillna('', inplace=True)
genes_df.fillna('', inplace=True)
interactions_df.fillna('', inplace=True)

# Select only 300 rows to show the result in a quick manner
interactions_df_top_300 = interactions_df.head(300)

# Create a directed graph
G = nx.DiGraph()

# Add edges (connections) between chemicals and genes with interaction type as edge attribute
for _, row in interactions_df_top_300.iterrows():
    G.add_edge(row['Chemicals'], row['Gene'], interaction_type=row['interaction_type'])

# Create dictionaries to store information about chemicals and genes
chemical_info = {name: (chem_id, length, pmid) for chem_id, name, length, pmid in zip(
    chemicals_df['Chemicals_ID'], chemicals_df['Name'], chemicals_df['length'], chemicals_df['PMID']
)}
gene_info = {name: (gene_id, length, pmid) for gene_id, name, length, pmid in zip(
    genes_df['Gene_ID'], genes_df['Gene_Name'], genes_df['length'], genes_df['PMID']
)}

# Set the theme to light using Streamlit's config
st.set_page_config(
    page_title="Chemical-Gene Interaction Graph",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "An interactive graph to visualize chemical-gene interactions."
    }
)

# Apply light theme directly in the script
st.markdown(
    """
    <style>
    body {
        background-color: #FFFFFF;
        color: #000000;
    }
    .css-1d391kg, .css-18e3th9 {
        background-color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit app
st.title("Interactive Graph with Streamlit agraph")

# Define the nodes and edges for Streamlit agraph
agraph_nodes = [
    Node(id=node, label=node, color='green' if node in chemical_info else 'blue')
    for node in G.nodes()
]
agraph_edges = [
    Edge(source=edge[0], target=edge[1], label=edge[2]['interaction_type'])
    for edge in G.edges(data=True)
]

# Configure the graph
agraph_config = Config(
    width=1200,
    height=1000,
    directed=True,
    nodeHighlightBehavior=True,
    highlightColor="#F7A7A6",
    collapsible=False,
    node={'labelProperty': 'label'},
    link={'labelProperty': 'label', 'renderLabel': True},
    hierarchical=False,  # Disable hierarchical layout
    animation=True,  # Enable animation
    layout={'improvedLayout': True},  # Use improved layout
    zoom=2.0  # Adjust zoom as needed
)

# Display the graph
agraph(nodes=agraph_nodes, edges=agraph_edges, config=agraph_config)
