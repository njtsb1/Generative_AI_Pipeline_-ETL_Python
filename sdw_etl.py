#!/usr/bin/env python3
# sdw_etl.py
import os
import time
import json
import csv
import requests
import pandas as pd
from typing import List, Dict, Optional

# Optional: pip install openai
try:
    import openai
except Exception:
    openai = None

# Configuration
sdw2023_api_url = 'https://sdw-2023-prd.up.railway.app'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # never hardcode the key
CSV_PATH = 'SDW2023.csv'
OUTPUT_JSON = 'output.json'
OUTPUT_CSV = 'output.csv'
REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_SLEEP = 0.35  # pause between requests

# ---------- Extract ----------
def extract_user_ids(path: str) -> List[int]:
    df = pd.read_csv(path)
    if 'UserID' not in df.columns:
        raise ValueError("CSV must contain column 'UserID'")
    return df['UserID'].tolist()

def get_user(user_id: int) -> Optional[Dict]:
    try:
        response = requests.get(f'{sdw2023_api_url}/users/{user_id}', timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'GET /users/{user_id} -> status {response.status_code}')
            return None
    except requests.RequestException as e:
        print(f'Error GET /users/{user_id}: {e}')
        return None

# ---------- Transform (OpenAI) ----------
def init_openai():
    if openai is None:
        raise RuntimeError("OpenAI library not installed. Run: pip install openai")
    if not OPENAI_API_KEY:
        raise RuntimeError("Set the OPENAI_API_KEY environment variable")
    openai.api_key = OPENAI_API_KEY

def generate_ai_news(user: Dict, max_chars: int = 100) -> str:
    fallback = f"{user.get('name','Customer')}, investing today protects and multiplies your financial future."
    if openai is None or not OPENAI_API_KEY:
        return fallback[:max_chars]

    prompt_user = f"Create a short message (max {max_chars} characters) for {user['name']} about the importance of investing, friendly and direct tone."
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a banking marketing specialist."},
                {"role": "user", "content": prompt_user}
            ],
            max_tokens=120,
            temperature=0.7
        )
        text = completion.choices[0].message.content.strip()
        return text[:max_chars]
    except Exception as e:
        print(f"OpenAI error for user {user.get('id')}: {e}")
        return fallback[:max_chars]

# ---------- Load ----------
def update_user(user: Dict) -> bool:
    try:
        response = requests.put(f"{sdw2023_api_url}/users/{user['id']}", json=user, timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f'Error PUT /users/{user["id"]}: {e}')
        return False

def save_local(users: List[Dict], json_path=OUTPUT_JSON, csv_path=OUTPUT_CSV):
    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    # Save CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'news_descriptions'])
        for u in users:
            name = u.get('name', '')
            news_desc = '; '.join([n.get('description', '') for n in u.get('news', [])])
            writer.writerow([u.get('id'), name, news_desc])

# ---------- Pipeline ----------
def run_pipeline():
    # 1) Extract
    print('Extracting user IDs from CSV...')
    user_ids = extract_user_ids(CSV_PATH)

    users = []
    for uid in user_ids:
        user = get_user(uid)
        if user:
            users.append(user)
        time.sleep(RATE_LIMIT_SLEEP)

    # 2) Transform
    try:
        init_openai()
        print('OpenAI initialized.')
    except Exception as e:
        print(f'OpenAI not available: {e}')

    for user in users:
        news_text = generate_ai_news(user)
        user.setdefault('news', [])
        user['news'].append({
            "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
            "description": news_text
        })
        print(f"Generated for {user['name']}: {news_text}")
        time.sleep(RATE_LIMIT_SLEEP)

    # 3) Load
    all_ok = True
    for user in users:
        success = update_user(user)
        print(f"User {user['name']} updated? {success}!")
        if not success:
            all_ok = False
        time.sleep(RATE_LIMIT_SLEEP)

    if not all_ok:
        print('Some updates failed — saving locally.')
        save_local(users)
    else:
        print('Pipeline finished. All API updates returned success.')

if __name__ == '__main__':
    run_pipeline()
