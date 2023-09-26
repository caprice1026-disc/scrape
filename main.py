import requests
import json
import time
import os
import csv
import openai
from bs4 import BeautifulSoup

openai.api_key = os.environ.get("OPENAI_API_KEY")

#ワードをを追加する
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "system", "content": "あなたは優秀な検索アシスタントです。入力されたワードに対して関連性のありそうな検索ワードを出来る限り出力し、リスト形式で返してください。"},
        {"role": "user", "content": "python"},
        ],
        temperature=0,
        max_tokens=500,
        )
print(completion.choices[0].message)
'''#ワードを取得する
print(completion.choices[0].message)
#ワードを保存する
ward = completion.choices[0].message
#保存したワードを使って検索する
url = "https://www.google.com/search?q=" + ward
#検索結果を取得する
r = requests.get(url)
#文章を整形する
soup = BeautifulSoup(r.text, "html.parser")
#文章を取得する
print(soup.get_text())
titles = soup.find_all("h1")
 #タグをパースしてテキストのみを出力
for title in titles:
    print(title.text)'''