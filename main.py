import os
import csv
import datetime
from time import sleep
from random import randint
from requests import get
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI

# 環境変数を取得する関数
def get_env_var(var_name):
    var_value = os.getenv(var_name)
    if var_value is None:
        raise ValueError(f"{var_name} is not set")
    return var_value

# GPT-3のインスタンスを初期化する関数
def initialize_gpt3(api_key, model_name):
    return ChatOpenAI(api_key=api_key, model=model_name)

# GPT-3を使用して検索キーワードを生成する関数
def generate_search_keywords(gpt3_instance, input_word):
    try:
        messages = [
            {"role": "system", "content": "あなたは優秀な検索アシスタントです。入力された単語に関連する検索キーワードをできるだけ多く生成し、リスト形式で返します。"},
            {"role": "user", "content": input_word}
        ]
        completion = gpt3_instance.chat(messages)
        return completion['choices'][0]['message']['content'].split(", ")
    except Exception as e:
        print(f"An error occurred while generating keywords: {e}")
        return []

# ウェブサイトをフェッチし、パースする関数
def fetch_and_parse_website(url):
    try:
        response = get(url)
        if 'cloudflare' in response.headers.get('Server', '').lower():
            print(f"Skipping {url} as it is protected by Cloudflare")
            return ""
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
    except Exception as e:
        print(f"An error occurred while getting website content: {e}")
        return ""

# CSVファイルに書き込む関数
def write_to_csv(csv_writer, keyword, title, url, summary):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csv_writer.writerow([keyword, title, url, summary, date])

# 要約関数（未実装）
# def get_summary(content):
#     pass

# メインの関数
def main():
    GOOGLE_API_KEY = get_env_var("GOOGLE_API_KEY")
    CUSTOM_SEARCH_ENGINE_ID = get_env_var("CUSTOM_SEARCH_ENGINE_ID")
    OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")

    gpt3 = initialize_gpt3(OPENAI_API_KEY, "gpt-3.5-turbo-16k")

    search_keywords = generate_search_keywords(gpt3, "python")

    visited_urls = set()

    with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Keyword", "Title", "URL", "Summary"])

        for keyword in search_keywords[:10]:
            print(f"Searching for: {keyword}")
            search_results = []  # Replace with actual search function
            for result in search_results[:10]:
                title = result['title']
                url = result['link']
                if url in visited_urls:
                    print(f"Skipping {url} as it has already been visited")
                    continue
                visited_urls.add(url)
                website_content = fetch_and_parse_website(url)
                summary = ""  # Replace with actual summary function
                write_to_csv(csvwriter, keyword, title, url, summary)
                sleep(randint(2, 5))

if __name__ == "__main__":
    main()