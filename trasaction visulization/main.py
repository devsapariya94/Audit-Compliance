import streamlit as st
from pymongo import MongoClient
import pandas as pd
from streamlit_d3graph import d3graph
import networkx as nx
import matplotlib.colors as mcolors

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['bank_database']
collection = db['transactions']

@st.cache_data
def init_graph(account_ids):
    # Query MongoDB for transactions related to the given account_ids
    transactions = collection.find({
        '$or': [
            {'sender_id': {'$in': account_ids}},
            {'receiver_id': {'$in': account_ids}}
        ]
    })

    # Convert MongoDB cursor to a list of dictionaries
    transactions_list = list(transactions)
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions_list)

    # Create a NetworkX directed graph
    G = nx.DiGraph()

    # Add nodes and directed edges to the graph
    for _, row in df.iterrows():
        G.add_edge(str(row['sender_id']), str(row['receiver_id']), weight=float(row['amount']), label=row['mode'])

    # Create adjacency matrix
    adjmat = nx.to_pandas_adjacency(G)

    return adjmat, df, G

@st.cache_data
def create_graph_data(_adjmat, _G):
    # Prepare node properties
    node_colors = [mcolors.to_hex(mcolors.to_rgba('blue', _G.degree(node) / max(dict(_G.degree()).values()))) for node in _G.nodes()]
    node_sizes = [10 for _ in _G.nodes()]
    node_opacities = [0.5 for _ in _G.nodes()]


    # Prepare edge properties
    edge_weights = [float(_G[u][v]['weight']) for u, v in _G.edges()]
    edge_colors = ['green' if _G[u][v]['label'] == 'Credit' else 'red' for u, v in _G.edges()]

    return node_colors, node_sizes, edge_weights, edge_colors, node_opacities

# Streamlit App
def main():
    st.title('Transaction Visualization')

    # Input for Account Numbers
    account_numbers = st.text_input('Enter account number(s) separated by comma (e.g., 5,9):')

    if account_numbers:
        # Convert input to list of integers
        account_ids = list(map(int, account_numbers.split(',')))

        if account_ids:
            # Initialize graph data
            adjmat, df, G = init_graph(account_ids)
            node_colors, node_sizes, edge_weights, edge_colors, node_opacities = create_graph_data(adjmat, G)

            # Create and display the graph
            st.subheader("Transaction Network Visualization")
            d3 = d3graph()
            d3.graph(adjmat)
            d3.set_node_properties(color=node_colors, size=node_sizes, opacity=node_opacities)
            d3.set_edge_properties(edge_distance=100, directed=True, marker_end='arrow', marker_color=edge_colors)
            d3.show()

            # Display transaction details
            st.subheader("Transaction Details")
            st.dataframe(df)
        else:
            st.write("Please enter valid account numbers.")

if __name__ == "__main__":
    main()
