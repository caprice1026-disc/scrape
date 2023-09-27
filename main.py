import os
import csv
import json
import datetime
import requests
from time import sleep
from googleapiclient.discovery import build
import openai

# GoogleとOpenAIのAPI設定
GOOGLE_API_KEY = "your_google_api_key_here"
CUSTOM_SEARCH_ENGINE_ID = "your_custom_search_engine_id_here"
openai.api_key = os.environ.get("OPENAI_API_KEY")

# データ保存用ディレクトリ
DATA_DIR = 'data'

def makeDir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def getSearchResponse(keyword):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    response = service.cse().list(
        q=keyword,
        cx=CUSTOM_SEARCH_ENGINE_ID,
        lr='lang_ja',
        num=10
    ).execute()
    return response['items']

# CSVファイルを開く
with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Keyword", "Title", "URL"])

    # GPT-3.5 Turboによる検索ワード生成
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are an excellent search assistant. Generate as many relevant search keywords as possible for the input word and return them in list format."},
            {"role": "user", "content": "python"},
        ],
        temperature=0,
        max_tokens=500,
    )

    # 出力された検索ワードをリスト形式で取得
    search_keywords = completion.choices[0].message['content'].split(", ")

    # 各検索ワードでGoogle検索を行う
    for keyword in search_keywords:
        print(f"Searching for: {keyword}")

        # Google検索
        search_results = getSearchResponse(keyword)

        # 検索結果をCSVに保存とウェブサイトの内容取得
        for result in search_results:
            title = result['title']
            url = result['link']

            # クラウドフレアで保護されているか確認
            try:
                response = requests.head(url)
                if response.headers.get('Server') == 'cloudflare':
                    print(f"Skipping {url} as it is protected by Cloudflare.")
                    continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

            # ウェブサイトの内容を取得
            try:
                response = requests.get(url)
                website_content = response.text
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

            # CSVに保存
            csvwriter.writerow([keyword, title, url])
            print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Website Content: {website_content[:100]}...")  # 最初の100文字だけ表示

            # サーバーに負荷をかけないように少し待つ
            sleep(2)
