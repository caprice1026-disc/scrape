import os
import csv
import datetime
import requests
from time import sleep
from random import randint
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from langchain.llms import ChatOpenAI  # ChatOpenAIをインポート

# API設定
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.environ.get("CUSTOM_SEARCH_ENGINE_ID")
openai_api_key = os.environ.get("OPENAI_API_KEY")

# データ保存用ディレクトリ
DATA_DIR = 'data'

# ディレクトリ作成関数
def makeDir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

# Google検索関数
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

# 要約関数
def getSummary(content):
    try:
        model = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo-16k")  # ChatOpenAIのインスタンスを作成
        messages = [
            {"role": "system", "content": "あなたは優秀な要約アシスタントです。入力された文章を適切な形で要約してください。"},
            {"role": "user", "content": content}
        ]
        completion = model.chat(messages, temperature=0, max_tokens=200)
        return completion['message']['content']
    except Exception as e:
        print(f"An error occurred while generating summary: {e}")
        return ""

# CSVファイルを開く
with open('search_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Keyword", "Title", "URL", "Summary"])

    # 検索ワード生成
    try:
        model = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo-16k")  # ChatOpenAIのインスタンスを作成
        messages = [
            {"role": "system", "content": "You are an excellent search assistant. Generate as many relevant search keywords as possible for the input word and return them in list format."},
            {"role": "user", "content": "python"}
        ]
        completion = model.chat(messages, temperature=0, max_tokens=500)
        search_keywords = completion['message']['content'].split(", ")
    except Exception as e:
        print(f"An error occurred while generating keywords: {e}")
        search_keywords = []

    # 検索と結果の保存
    for keyword in search_keywords:
        print(f"Searching for: {keyword}")
        search_results = getSearchResponse(keyword)
        for result in search_results:
            title = result['title']
            url = result['link']
            try:
                response = requests.get(url)
                website_content = response.text
            except Exception as e:
                print(f"An error occurred while getting website content: {e}")
                continue
            soup = BeautifulSoup(website_content, 'html.parser')
            website_content = soup.get_text().replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
            summary = getSummary(website_content)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csvwriter.writerow([keyword, title, url, summary, date])
            print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Summary: {summary}")
            sleep(randint(2, 5))
