import os
import csv
import json
import datetime
import requests
from time import sleep
from random import randint
from googleapiclient.discovery import build
import openai
from bs4 import BeautifulSoup

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
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        response = service.cse().list(
            q=keyword,
            cx=CUSTOM_SEARCH_ENGINE_ID,
            lr='lang_ja',
            num=10
        ).execute()
        return response['items']
    except Exception as e:
        print(f"An error occurred while searching: {e}")
        return []

def getSummary(content):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "あなたは優秀な要約アシスタントです。入力された文章を適切な形で要約してください。"},
                {"role": "user", "content": content},
            ],
            temperature=0,
            max_tokens=200,
        )
        return completion.choices[0].message['content']
    except Exception as e:
        print(f"An error occurred while generating summary: {e}")
        return ""

# CSVファイルを開く
with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Keyword", "Title", "URL", "Summary"])

    # GPT-3.5 Turboによる検索ワード生成
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are an excellent search assistant. Generate as many relevant search keywords as possible for the input word and return them in list format."},
                {"role": "user", "content": "python"},
            ],
            temperature=0,
            max_tokens=500,
        )
    except Exception as e:
        print(f"An error occurred while generating keywords: {e}")
        search_keywords = []
    else:
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
                print(f"An error occurred while checking Cloudflare protection: {e}")
                continue

            # ウェブサイトの内容を取得
            try:
                response = requests.get(url)
                website_content = response.text
            except Exception as e:
                print(f"An error occurred while getting website content: {e}")
                continue
            #bs4でウェブサイトの内容を整形
            soup = BeautifulSoup(website_content, 'html.parser')
            website_content = soup.get_text()
            # 余分な改行を削除
            website_content = website_content.replace('\n', '')
            # 余分な空白を削除
            website_content = website_content.replace(' ', '')
            # 余分なタブを削除
            website_content = website_content.replace('\t', '')
            # 余分な改行を削除
            website_content = website_content.replace('\r', '')

            # ウェブサイトの内容を要約。この部分をchatGPTを使用して要約する。要約用の関数を用意しておくこと。
            summary = getSummary(website_content)

            # CSVに保存
            csvwriter.writerow([keyword, title, url, summary])
            print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Summary: {summary}")

            # サーバーに負荷をかけないように少し待つ
            sleep(randint(2, 5))  # ランダムなスリープ時間を設定