import streamlit as st
from pymongo import MongoClient
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

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

    return df

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
            df = init_graph(account_ids)

            nodes = []
            edges = []

            # Create nodes and edges for the graph
            for account_id in account_ids:
                nodes.append(Node(id=str(account_id), label=f"Account {account_id}", size=25, shape="circular"))

            for _, row in df.iterrows():
                sender_id = str(row['sender_id'])
                receiver_id = str(row['receiver_id'])
                amount = row['amount']
                transaction_id = row['transaction_id']
                mode = row['mode']
                
                # Add nodes if they are not already added
                if not any(node.id == sender_id for node in nodes):
                    nodes.append(Node(id=sender_id, label=f"Account {sender_id}", size=25, shape="circular"))
                if not any(node.id == receiver_id for node in nodes):
                    nodes.append(Node(id=receiver_id, label=f"Account {receiver_id}", size=25, shape="circular"))

                # Add edge
                
                if not any (edge.id == transaction_id for edge in edges):
                        edges.append(Edge(source=sender_id, target=receiver_id, label=f"Transaction ID: {transaction_id}", weight=amount, id = transaction_id))

            # Config for the graph
            config = Config(width=750,
                            height=950,
                            directed=True, 
                            physics=True, 
                            hierarchical=False)

            # Display the graph
            st.subheader("Transaction Network Visualization")
            return_value = agraph(nodes=nodes, edges=edges, config=config)

            # Display transaction details
            st.subheader("Transaction Details")
            st.dataframe(df)
        else:
            st.write("Please enter valid account numbers.")

if __name__ == "__main__":
    main()
