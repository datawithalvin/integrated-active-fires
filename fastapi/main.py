from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from dotenv import dotenv_values
from src.procedures import fetch_last_data

app = FastAPI()

config = dotenv_values("./.env")
url = config.get("SUPABASE_URL")
key = config.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.get("/articles/{start_date}/{end_date}")
def get_articles(start_date: str, end_date: str):
    try:
        articles = supabase.table("articles") \
                            .select("title", "url", "image", "published_time") \
                            .gte("published_date", start_date) \
                            .lt("published_date", end_date) \
                            .execute()

        # Check if the response is as expected and extract data
        if hasattr(articles, "data"):
            article_data = articles.data
            if article_data is None or len(article_data) == 0:
                raise HTTPException(status_code=404, detail="No articles found for the given date range")
            return article_data
        else:
            raise HTTPException(status_code=500, detail="Unexpected response format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
