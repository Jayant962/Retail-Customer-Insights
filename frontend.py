import streamlit as st
from preprocessing import preprocess
import sqlite3
import pandas as pd
import streamlit.components.v1 as components

# Initialize session state keys if they don't exist
if 'processed' not in st.session_state:
    st.session_state['processed'] = False
if 'show_questions' not in st.session_state:
    st.session_state['show_questions'] = False
if 'show_dashboard' not in st.session_state:
    st.session_state['show_dashboard'] = False

col1, col2 = st.columns(2)

with col1:
    transaction = st.file_uploader("Upload your transaction file", type="csv")
    ticket = st.file_uploader("Upload your support_ticket file", type="csv")
    interaction = st.file_uploader("Upload your interactions file", type="csv")
with col2:
    customer = st.file_uploader("Upload your customer_details file", type="csv")
    campaigns = st.file_uploader("Upload your campaigns file", type="csv")
    review = st.file_uploader("Upload your customer_review file", type="csv")

# --- STEP 1: PREPROCESSING ---
if st.button("Start Preprocessing"):
    # Perform preprocessing
    clean_customer, clean_ticket, clean_campaign, clean_review, clean_transaction, clean_interaction = preprocess(
        customer, ticket, campaigns, review, transaction, interaction
    )
    
    # Store in session state
    st.session_state['clean_customer'] = clean_customer
    st.session_state['clean_campaign'] = clean_campaign
    st.session_state['clean_ticket'] = clean_ticket
    st.session_state['clean_review'] = clean_review
    st.session_state['clean_transaction'] = clean_transaction
    st.session_state['clean_interaction'] = clean_interaction
    st.session_state['processed'] = True
    st.success("Preprocessing completed")

# --- STEP 2: SQL ANALYSIS ---
if st.session_state['processed']:
    # Use button to toggle state
    if st.button("See Business Questions & Answers"):
        st.session_state['show_questions'] = True

    if st.session_state['show_questions']:
        # Establish connection
        conn = sqlite3.connect("Retail_Interaction.db")
        
        # Write to SQL (Optimized: only needs to happen once, but fine here for now)
        st.session_state['clean_customer'].to_sql("customer", conn, if_exists="replace", index=False)
        st.session_state['clean_ticket'].to_sql("ticket", conn, if_exists="replace", index=False)
        st.session_state['clean_campaign'].to_sql("campaign", conn, if_exists="replace", index=False)
        st.session_state['clean_review'].to_sql("review", conn, if_exists="replace", index=False)
        st.session_state['clean_transaction'].to_sql("transaction", conn, if_exists="replace", index=False)
        st.session_state['clean_interaction'].to_sql("interaction", conn, if_exists="replace", index=False)

        with open("Buisness_Questions_Answer_SQL.sql", "r") as file:
            queries = file.read().split(';')

        st.header("Business Questions & Answers")
        col3, col4 = st.columns(2)
        
        # Display results (Example: index 1 and 2)
        with col3:
            st.subheader("Yearly registered customers")
            st.write(pd.read_sql_query(queries[1], conn))
            st.subheader("Percentage of customers that are repeat buyers")
            st.write(pd.read_sql_query(queries[2], conn))
            st.subheader("Customer age group contributes the highest revenue")
            st.write(pd.read_sql_query(queries[3],conn))
            st.subheader("State generated the most revenue")
            st.write(pd.read_sql_query(queries[4], conn))
            st.subheader("Average revenue per customer")
            st.write(pd.read_sql_query(queries[5], conn))
            st.subheader("Viewers (interaction users) converted into buyers")
            st.write(pd.read_sql_query(queries[6],conn))
            st.subheader("Do customers with more interactions spend more")
            st.write(pd.read_sql_query(queries[7], conn))
            st.subheader("Which campaign type generates the highest average ROI")
            st.write(pd.read_sql_query(queries[8], conn))

        with col4:
            st.subheader("Which campaign type leads to the highest number of conversions")
            st.write(pd.read_sql_query(queries[9],conn))
            # st.subheader("Which target segment has the highest average conversion rate")
            # st.write(pd.read_sql_query(queries[10],conn))
            st.subheader("Which product category generates the highest total revenue")
            st.write(pd.read_sql_query(queries[11],conn))
            st.subheader("Which product category has the highest average rating")
            st.write(pd.read_sql_query(queries[12],conn))
            st.subheader("What is the average order value per product category")
            st.write(pd.read_sql_query(queries[13],conn))
            st.subheader("Which payment method is most used")
            st.write(pd.read_sql_query(queries[14],conn))
            st.subheader("Which issue category occurs most frequently")
            st.write(pd.read_sql_query(queries[15],conn))
            st.subheader("What is the average resolution time")
            st.write(pd.read_sql_query(queries[16],conn))
        
        conn.close()

# --- STEP 3: DASHBOARD ---
if st.session_state.get('show_questions'):
    if st.button('Show Dashboard'):
        st.session_state['show_dashboard'] = True

    if st.session_state['show_dashboard']:
        components.html(
            """
            <iframe title="Dashboard" width="600" height="373.5" 
            src="https://app.powerbi.com/view?r=eyJrIjoiNjNiMzcwYTUtOGVjMC00MWU3LWFiOWUtZDQ5YTkxOGFiNDYzIiwidCI6ImUxNGU3M2ViLTUyNTEtNDM4OC04ZDY3LThmOWYyZTJkNWE0NiIsImMiOjEwfQ%3D%3D" 
            frameborder="0" allowFullScreen="true"></iframe>
            """,
            height=700
        )