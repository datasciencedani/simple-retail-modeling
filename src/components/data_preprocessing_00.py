from kfp.v2.dsl import (
    Output, 
    Dataset,
    component,
)

@component(
    base_image="gcr.io/deeplearning-platform-release/r-cpu.3-6:latest",
    packages_to_install=[
        "pandas",
        "numpy",
        "google-cloud-storage",
    ],
)
def data_preprocessing(
    data_path: str,
    bucket_name: str,
) -> str:
######################################### IMPORTS
#################################################
#################################################
    import pandas as pd
    import numpy as np
    from google.cloud import storage

############################################ CODE
#################################################
#################################################
    # Read the CSV file into a DataFrame, specifying the encoding
    df = pd.read_csv(data_path, encoding='latin1')
    # [1] Transform InvoiceDate to a date type:
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    # [2] Eliminate null values.
    df = df.dropna()
    # [3] Eliminate duplicate rows:
    df = df.drop_duplicates()
    # [4] Get only UK data
    df_uk = df.query("Country=='United Kingdom'").drop(['Country'], axis=1).reset_index(drop=True)
    # [5] Remove columns:
    df_uk.drop(df_uk.query('StockCode == "M" | StockCode == "POST" | StockCode == "PADS" | StockCode == "DOT"').index, axis = 0, inplace = True)
    # [6] Reset index
    df_uk = df_uk.reset_index(drop=True)
    # [7] Positive quantity:
    df_uk = df_uk.query("Quantity>0").reset_index(drop=True)
    # [8] Purchase history for each customer
    df_uk["PurchaseNumber"] = df_uk.groupby("CustomerID")["InvoiceDate"].rank(method="dense", ascending=True)

    # [9] Get latest purchase for each CustomerID
    latest_purchase_df = df_uk.groupby('CustomerID').agg({
        'PurchaseNumber': 'max'
    })
    latest_purchase_df.rename(columns={"PurchaseNumber": "CustomerLatestPurchase", "lastname": "LASTNAME"}, inplace=True)
    # Reset the index of the grouped DataFrame
    latest_purchase_df = latest_purchase_df.reset_index()

    # [10] Merge with data frame
    df_uk = pd.merge(df_uk,latest_purchase_df,on='CustomerID',how='left')

    # [11] Get total paid
    df_uk["TotalPaid"] =  df_uk["UnitPrice"] * df_uk["Quantity"]


    #[12] Group by Invoice
    grouped_df = df_uk.groupby('InvoiceNo').agg({
        'Description': lambda x: ' '.join(x),
        'TotalPaid': 'sum',
        'InvoiceDate': 'max',
        'PurchaseNumber': 'max',
        'CustomerLatestPurchase': 'max',
    })
    # Reset the index of the grouped DataFrame
    grouped_df = grouped_df.reset_index()

    # [13] Create the 'FuturePurchase' column based on the conditions
    grouped_df['FuturePurchase'] = np.where(grouped_df['PurchaseNumber'] < grouped_df['CustomerLatestPurchase'], 1, 0)

    # [14] Get data for modeling
    model_df = grouped_df[['Description', 'TotalPaid', 'InvoiceDate', 'PurchaseNumber', 'FuturePurchase']]

##################################### PASSING DATA
#################################################
#################################################
    # Upload model data to GOOGLE CLOUD STORAGE
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)

    bucket.blob('online_retail_example/data/test.csv').upload_from_string(model_df.to_csv(), 'text/csv')

    return f'gs://{bucket_name}/online_retail_example/data/test.csv'