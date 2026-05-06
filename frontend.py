import streamlit as st
from preprocessing import preprocess
import sqlite3
import pandas as pd

col1,col2 = st.columns(2)

with col1:
    transaction = st.file_uploader("Upload your transaction file",type="csv",accept_multiple_files=False)
    ticket = st.file_uploader("Upload your support_ticket file",type="csv",accept_multiple_files=False)
    interaction = st.file_uploader("Upload your interactions file",type="csv",accept_multiple_files=False)
with col2:
    customer = st.file_uploader("Upload your customer_details file",type="csv",accept_multiple_files=False)
    campaigns = st.file_uploader("Upload your campaigns file",type="csv",accept_multiple_files=False)
    review = st.file_uploader("Upload your customer_review file",type="csv",accept_multiple_files=False)


if st.button("Start Preprocessing"):
    clean_customer,clean_ticket,clean_campaign,clean_review,clean_transaction,clean_interaction = preprocess(customer,ticket,campaigns,review,transaction,interaction)
    st.success("Preprocessing completed")

    # Store dataframes in session_state
    st.session_state['processed'] = True

    st.session_state['clean_customer'] = clean_customer
    st.session_state['clean_campaign'] = clean_campaign
    st.session_state['clean_ticket'] = clean_ticket
    st.session_state['clean_review'] = clean_review
    st.session_state['clean_transaction'] = clean_transaction
    st.session_state['clean_interaction'] = clean_interaction


if(st.session_state.get('processed')):

    if(st.button("See Buisness Questions & Answers")):
        # Retrieve dataframes from session_state
        clean_customer = st.session_state["clean_customer"]
        clean_ticket = st.session_state["clean_ticket"]
        clean_campaign = st.session_state["clean_campaign"]
        clean_review = st.session_state["clean_review"]
        clean_transaction = st.session_state["clean_transaction"]
        clean_interaction = st.session_state["clean_interaction"]


        conn = sqlite3.connect("Retail_Interaction.db")

        clean_customer.to_sql("customer", conn, if_exists="replace", index=False)
        clean_ticket.to_sql("ticket", conn, if_exists="replace", index=False)
        clean_campaign.to_sql("campaign", conn, if_exists="replace", index=False)
        clean_review.to_sql("review", conn, if_exists="replace", index=False)
        clean_transaction.to_sql("transaction", conn, if_exists="replace", index=False)
        clean_interaction.to_sql("interaction", conn, if_exists="replace", index=False)

        with open("Buisness_Questions_Answer_SQL.sql","r") as file:
            sql_queries = file.read()

        queries = sql_queries.split(';')

        st.header("Buisness Questions & Answers")

        col3,col4 = st.columns(2)
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

        st.success("SQL Queries Answered")