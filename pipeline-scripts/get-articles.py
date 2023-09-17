import polars as pl
from src.procedures import fetch_articles, cleaning_articles, fetch_last_data
from dotenv import dotenv_values

config = dotenv_values("./.env")

# ------------------------------****************--------------------------------------#
def main():
    """
    Main function to execute the processing pipeline.

    This function retrieves articles from Google News with specific given keywords,
    cleans the data, and appends it to an existing database of articles.
    """

    try:
        # Set keywords
        keywords = ["kebakaran hutan", "polusi udara", "kebakaran lahan"]
        articles_df = fetch_articles(keywords, 15, 2)
        articles_df = cleaning_articles(articles_df)

        # Retrieves the most recently updated data from the database
        CONNECTION_URI = config.get("CONNECTION_URI")
        query = """
            SELECT * 
            FROM articles 
            WHERE published_date > CURRENT_DATE - INTERVAL '3 day'"""
        
        
        last_data = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
        last_data = last_data.drop(["id"])  # Drop unused column to avoid conflicts when appending

        # Concatenate both dataframes, remove duplicates, and maintain order
        concat_articles = pl.concat([articles_df, last_data], how="vertical_relaxed")
        concat_articles = concat_articles.unique(keep="none", maintain_order=False) # drop duplicates row

        # Append the final dataframe into the database
        concat_articles.write_database(table_name="articles", connection=CONNECTION_URI, if_exists="append")
        # articles_df.write_database(table_name="articles", connection=CONNECTION_URI, if_exists="append")

        
        print(concat_articles)
        print(concat_articles.estimated_size("mb"))

        # print(last_data)

    except Exception as e:
        print(f"An error occurred in the main pipeline: {e}")


# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()
