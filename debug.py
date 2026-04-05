#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

print("=" * 50)
print("환경변수 확인")
print("=" * 50)

naver_id = os.getenv('NAVER_CLIENT_ID')
naver_secret = os.getenv('NAVER_CLIENT_SECRET')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_API_KEY')

print(f"NAVER_CLIENT_ID: {naver_id}")
print(f"NAVER_CLIENT_SECRET: {naver_secret}")
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_API_KEY: {supabase_key[:20]}..." if supabase_key else "SUPABASE_API_KEY: None")

print("\n" + "=" * 50)
print("API 테스트")
print("=" * 50)

import requests

headers = {
    "X-Naver-Client-Id": naver_id,
    "X-Naver-Client-Secret": naver_secret,
}

params = {
    'query': '카시트',
    'display': 10,
    'start': 1
}

try:
    response = requests.get(
        'https://openapi.naver.com/v1/search/shop.json',
        headers=headers,
        params=params,
        timeout=10
    )

    print(f"응답 코드: {response.status_code}")
    print(f"응답 헤더: {response.headers}")

    if response.status_code == 200:
        print("✅ API 호출 성공!")
        data = response.json()
        print(f"검색 결과: {len(data.get('items', []))}개 상품")
    else:
        print(f"❌ API 호출 실패!")
        print(f"응답 내용: {response.text}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
