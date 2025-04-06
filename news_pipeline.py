import requests
from bs4 import BeautifulSoup
import pandas as pd
from openai import OpenAI

# ========== CONFIG ==========
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
URL = "https://finance.yahoo.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = [""]  # così non filtra niente, prende tutto
N_ARTICLES = 10
OUTPUT_FILE = "notizie_finali.csv"
# =============================


# === 1. SCRAPING NOTIZIE ===
def scrape_news():
    print("🔍 Scraping Yahoo Finance...")
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.find_all("a", attrs={"data-ylk": True})
    
    news = []
    for article in articles:
        title = article.text.strip()
        href = article.get("href")
        if href and "/news/" in href and title:
            full_link = "https://finance.yahoo.com" + href
            news.append({"title": title, "link": full_link})
    
    return news[:N_ARTICLES]


# === 2. FILTRAGGIO CON PAROLE CHIAVE ===
def filter_news(news):
    print("🧹 Filtraggio con parole chiave...")
    return [
        n for n in news
        if any(kw.lower() in n["title"].lower() for kw in KEYWORDS)
    ]


# === 3. GPT PER SELEZIONE MIGLIORE ===
def gpt_select(news):
    print("🧠 Selezione con GPT...")

    titles = "\n".join(f"- {n['title']}" for n in news)

    prompt = f"""
Sei un esperto di finanza personale e social media.
Da questa lista di notizie, scarta quelle irrilevanti o troppo generiche.
Poi, scegli le 3 notizie più utili, interessanti o rilevanti per una pagina Instagram di divulgazione finanziaria rivolta a un pubblico giovane.
Rispondi in formato JSON con: "title" e "link".

{titles}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Errore GPT:", e)
        return None



# === 4. SALVA SU FILE ===
def save_output(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ Notizie salvate in {filename}")


# === RUN TUTTO ===
def run_pipeline():
    news = scrape_news()
    filtered = filter_news(news)

    if not filtered:
        print("😔 Nessuna notizia rilevante trovata oggi.")
        return

    selection = gpt_select(filtered)
    if selection:
        save_output(selection, OUTPUT_FILE)

if __name__ == "__main__":
    run_pipeline()
