import numpy as np
import pandas as pd

# Importing all tables

def preprocess(customer,ticket,campaign,review,transaction,interaction):

    customer = pd.read_csv(customer)
    ticket = pd.read_csv(ticket)
    campaign = pd.read_csv(campaign)
    review = pd.read_csv(review)
    transaction = pd.read_csv(transaction)
    interaction = pd.read_csv(interaction)

    # ## Cleaning customer table


    customer.sample()

    customer.shape

    customer.isnull().sum()

    customer.duplicated().sum()

    customer.info()

    customer.drop(columns=['email','phone','zip_code','street_address'],inplace=True)

    customer['age'] = pd.to_numeric(customer['age'],errors='coerce').astype('Int64')
    customer['registration_date'] = pd.to_datetime(customer['registration_date'],errors='coerce')

    customer['full_name'] = customer['full_name'].fillna('Unknown')
    customer['gender'] = customer['gender'].fillna('Unknown')
    customer['city'] = customer['city'].fillna('Unknown')
    customer['state'] = customer['state'].fillna('Unknown')
    customer['preferred_channel'] = customer['preferred_channel'].fillna('Unknown')

    customer['age'] = customer['age'].fillna(customer['age'].median())

    customer['year'] = customer["registration_date"].dt.year

    customer['month'] = customer["registration_date"].dt.month

    customer['age_group'] = pd.cut(
        customer['age'],
        bins=[1,18, 35, 45, 60, 100],
        labels=['1-17','18-35', '36-45', '46-60', '60+'],
        right=True
    )



    # ## Cleaning support_ticket table


    ticket.sample()

    ticket.info()

    ticket.isnull().sum()

    ticket.duplicated().sum()

    ticket.shape

    ticket['submission_date'] = pd.to_datetime(ticket['submission_date'],errors='coerce')
    ticket['resolution_date'] = pd.to_datetime(ticket['resolution_date'],errors='coerce')

    ticket.drop(columns=['notes'],inplace=True)

    ticket['issue_category'] = ticket['issue_category'].fillna('Unknown')
    ticket['priority'] = ticket['priority'].fillna('Unknown')

    # If resolution_date exists → status must be resolved
    ticket.loc[
        ticket['resolution_status'].isna() & ticket['resolution_date'].notna(),
        'resolution_status'
    ] = 'resolved'

    # If resolution_date is null → status must be open
    ticket.loc[
        ticket['resolution_status'].isna() & ticket['resolution_date'].isna(),
        'resolution_status'
    ] = 'open'

    ticket.loc[
        ticket['resolution_time_hours'].isna(),
        'resolution_time_hours'
    ] = (
        (ticket['resolution_date'] - ticket['submission_date'])
        .dt.total_seconds() / 3600
    )

    avg_score = ticket['customer_satisfaction_score'].mean()
    ticket['customer_satisfaction_score'] = ticket['customer_satisfaction_score'].fillna(round(avg_score))

    ticket['ticket_year'] = ticket['submission_date'].dt.year
    ticket['ticket_month'] = ticket['submission_date'].dt.month
    ticket['ticket_day'] = ticket['submission_date'].dt.day

    ticket['resolution_speed'] = pd.cut(
        ticket['resolution_time_hours'],
        bins=[0, 24, 72, 168, float('inf')],
        labels=['within_1_day', '1_3_days', '3_7_days', 'more_than_7_days']
    )

    ticket['isResolved'] = ticket['resolution_date'].notna().astype(int)

    ticket['high_priority_flag'] = (ticket['priority'] == 'high').astype(int)
    ticket['sla_breach'] = (ticket['resolution_time_hours'] > 72).astype(int)





    # ## Proceding with review table


    review.sample()

    review.info()

    review.isnull().sum()

    review.shape

    review.duplicated().sum()

    review['transaction_date'] = pd.to_datetime(review['transaction_date'],errors='coerce')
    review['review_date'] = pd.to_datetime(review['review_date'],errors='coerce')

    review = review.merge(
        customer[['customer_id','full_name']],
        how='left',
        on='customer_id',
        suffixes=('','_cust')
    )

    review['full_name'] = review['full_name'].fillna(review['full_name_cust'])
    review['full_name'] = review['full_name'].fillna('Unknown')

    review.drop(columns=['full_name_cust'],inplace=True)

    review['product_name'] = review['product_name'].fillna(
        review['product_name'].mode()[0]
    )

    review['product_category'] = review['product_category'].fillna(
        review['product_category'].mode()[0]
    )


    review['review_year'] = review['review_date'].dt.year
    review['review_month'] = review['review_date'].dt.month
    review['days_after_transaction'] = (review['review_date'] - review['transaction_date']).dt.days

    review['sentiment'] = pd.cut(
        review['rating'],
        bins=[0,2,3,5],
        labels=['Negative','Neutral','Positive']
    )





    # ## Proceed with campaign table


    campaign.sample()

    campaign.info()

    campaign['start_date'] = pd.to_datetime(campaign['start_date'],errors='coerce')
    campaign['end_date'] = pd.to_datetime(campaign['end_date'],errors='coerce')

    campaign.isnull().sum()

    campaign.shape

    campaign['campaign_name'] = campaign['campaign_name'].fillna('Unknown')
    campaign['campaign_type'] = campaign['campaign_type'].fillna('Unknown')

    campaign['budget'] = campaign['budget'].fillna(0)
    campaign['impressions'] = campaign['impressions'].fillna(0)
    campaign['clicks'] = campaign[['clicks', 'impressions']].min(axis=1)
    campaign['conversions'] = campaign[['conversions', 'clicks']].min(axis=1)


    campaign['conversion_rate'] = (
        campaign['conversions'] / campaign['clicks']
    ).replace([float('inf'), -float('inf')], 0).fillna(0)

    campaign['roi'] = (
        campaign['conversions'] / campaign['budget']
    ).replace([float('inf'), -float('inf')], 0).fillna(0)





    campaign['campaign_duration_days'] = ( campaign['end_date'] - campaign['start_date'] ).dt.days

    campaign['start_year'] = campaign['start_date'].dt.year
    campaign['start_month'] = campaign['start_date'].dt.month

    campaign['cost_per_click'] = (
        campaign['budget'] / campaign['clicks']
    ).replace([float('inf'), -float('inf')], 0).fillna(0)

    campaign['cost_per_conversion'] = (
        campaign['budget'] / campaign['conversions']
    ).replace([float('inf'), -float('inf')], 0).fillna(0)





    # ## Proceed with transaction Table


    transaction.sample()

    transaction.info()

    transaction.isnull().sum()

    transaction.shape

    transaction['transaction_date'] = pd.to_datetime(transaction['transaction_date'],errors='coerce')

    transaction['product_name'] = transaction['product_name'].fillna(
        transaction['product_name'].mode()[0]
    )

    transaction['product_category'] = transaction['product_category'].fillna(
        transaction['product_category'].mode()[0]
    )

    transaction['quantity'] = transaction['quantity'].fillna(
        transaction.groupby('product_name')['quantity'].transform('median')
    )

    transaction['quantity'] = transaction['quantity'].fillna(
        transaction.groupby('product_category')['quantity'].transform('median')
    )

    transaction['quantity'] = transaction['quantity'].fillna(
        transaction['quantity'].median())


    transaction['price'] = transaction['price'].fillna(
        transaction.groupby('product_name')['price'].transform('median')
    )

    transaction['price'] = transaction['price'].fillna(
        transaction.groupby('product_category')['price'].transform('median')
    )

    transaction['price'] = transaction['price'].fillna(
        transaction['price'].median()
    )

    transaction['store_location'] = transaction['store_location'].fillna(
        transaction['store_location'].mode()[0]
    )

    transaction['payment_method'] = transaction['payment_method'].fillna(
        transaction['payment_method'].mode()[0])

    transaction['discount_applied'] = transaction['discount_applied'].fillna(
        transaction.groupby('product_category')['discount_applied'].transform('median')
    )
    transaction['discount_applied'] = transaction['discount_applied'].fillna(
        transaction['discount_applied'].median()
    )





    transaction['txn_year'] = transaction['transaction_date'].dt.year
    transaction['txn_month'] = transaction['transaction_date'].dt.month
    transaction['txn_weekday'] = transaction['transaction_date'].dt.day_name()

    transaction['gross_amount'] = transaction['price']*transaction['quantity']
    transaction['final_amount'] = transaction['gross_amount'] - (transaction['gross_amount']*transaction['discount_applied']/100)







    # ### Add some more features to customer table based on transaction table


    customer_spend = (
        transaction.groupby('customer_id')['final_amount']
        .sum()
        .reset_index(name='total_spent')
    )

    customer = customer.merge(customer_spend, on='customer_id', how='left')
    customer['total_spent'] = customer['total_spent'].fillna(0)

    customer['spending_category'] = pd.qcut(
        customer['total_spent'],
        q=3,
        labels=['Low','Medium','High']
    )

    customer_txn_count = (
        transaction.groupby('customer_id')['transaction_id']
        .count()
        .reset_index(name='total_transactions')
    )
    customer = customer.merge(customer_txn_count, on='customer_id', how='left')
    customer['total_transactions'] = customer['total_transactions'].fillna(0)








    # ## Proceed with Interaction table


    interaction.sample()

    interaction.shape

    interaction.isnull().sum()

    interaction.duplicated().sum()

    interaction.info()

    interaction['interaction_date'] = pd.to_datetime(interaction['interaction_date'],errors='coerce')

    interaction['channel'] = interaction['channel'].fillna(
        interaction['channel'].mode()[0]
    )
    interaction['interaction_type'] = interaction['interaction_type'].fillna(
        interaction['interaction_type'].mode()[0]
    )
    interaction['duration'] = interaction['duration'].fillna(
        interaction.groupby('interaction_type')['duration'].transform('median')
    )
    interaction['page_or_product'] = interaction['page_or_product'].fillna(
        interaction['page_or_product'].mode()[0]
    )



    interaction['int_year'] = interaction['interaction_date'].dt.year
    interaction['int_month'] = interaction['interaction_date'].dt.month
    interaction['int_weekday'] = interaction['interaction_date'].dt.day_name()
    interaction['int_time'] = interaction['interaction_date'].dt.time

    interaction['time_period'] = pd.cut(
        interaction['interaction_date'].dt.hour,
        bins=[0,6,12,18,24],
        labels=['Night','Morning','Afternoon','Evening'],
        right=False
    )

    interaction['total_usage'] = (
        interaction.groupby('customer_id')['duration']
        .transform('sum')
    )

    interaction['usage_category'] = pd.qcut(
        interaction['total_usage'],
        q=3,
        labels=['Low','Medium','High']
    )



    # ### Add some more features to customer table based on transaction table


    fav_page = (
        interaction.groupby(['customer_id','page_or_product'])
        .size()
        .reset_index(name='count')
        .sort_values(['customer_id','count'], ascending=[True, False])
        .drop_duplicates('customer_id')
        [['customer_id','page_or_product']]
    )

    customer = customer.merge(fav_page, on='customer_id', how='left')
    customer.rename(columns={'page_or_product':'favorite_page_or_product'}, inplace=True)

    customer['favorite_page_or_product'] = customer['favorite_page_or_product'].fillna('Unknown')







    # customer.to_csv('data/cleaned/customer_clean.csv', index=False)
    # ticket.to_csv('data/cleaned/ticket_clean.csv', index=False)
    # campaign.to_csv('data/cleaned/campaign_clean.csv', index=False)
    # transaction.to_csv('data/cleaned/transaction_clean.csv', index=False)
    # review.to_csv('data/cleaned/review_clean.csv', index=False)
    # interaction.to_csv('data/cleaned/interaction_clean.csv', index=False)

    return customer,ticket,campaign,review,transaction,interaction

    