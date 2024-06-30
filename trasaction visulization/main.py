import streamlit as st
from pymongo import MongoClient
import streamlit.components.v1 as components

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['bank_database']
collection = db['transactions']

# Streamlit App
def main():
    st.title('Transaction Visualization')

    # Input for Account Numbers
    account_numbers = st.text_input('Enter account number(s) separated by comma (e.g., 5,9):')

    if account_numbers:
        # Convert input to list of integers
        account_ids = list(map(int, account_numbers.split(',')))

        # Query MongoDB for transactions related to the given account_ids
        transactions = collection.find({
            '$or': [
                {'sender_id': {'$in': account_ids}},
                {'receiver_id': {'$in': account_ids}}
            ]
        })

        # Convert MongoDB cursor to a list of dictionaries
        transactions_list = list(transactions)

        if transactions_list:
            # Display transaction data
            st.write('Transaction Data:')
            st.write(transactions_list)

            # Prepare data for visualization (example: sum amounts by transaction_id)
            data = aggregate_data(transactions_list)

            # Generate dynamic D3.js script
            d3_script = generate_d3_script(data)

            # Display D3.js graph using streamlit-d3
            st.write('Visualization using streamlit-d3:')
            components.html(d3_script, width=900, height=500)
        else:
            st.write('No transactions found for the given account numbers.')

def aggregate_data(transactions_list):
    # Example aggregation: Sum amounts by transaction_id
    aggregated_data = {}
    for transaction in transactions_list:
        transaction_id = transaction['transaction_id']
        amount = transaction['amount']
        if transaction_id in aggregated_data:
            aggregated_data[transaction_id] += amount
        else:
            aggregated_data[transaction_id] = amount
    # Convert to list of dictionaries for D3.js
    data = [{'transaction_id': key, 'amount': value} for key, value in aggregated_data.items()]
    return data

def generate_d3_script(data):
    # Generate D3.js script dynamically based on data
    d3_script = """
    // Your D3.js code for visualization
    const data = """ + str(data) + """;

    // Example D3.js code (bar chart)
    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select("#d3-container")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // D3.js chart implementation here (e.g., bar chart)
    const x = d3.scaleBand()
                .domain(data.map(d => d.transaction_id))
                .range([0, width])
                .padding(0.1);

    const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.amount)])
                .range([height, 0]);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.transaction_id))
        .attr("width", x.bandwidth())
        .attr("y", d => y(d.amount))
        .attr("height", d => height - y(d.amount));
    """

    return d3_script

if __name__ == "__main__":
    main()
