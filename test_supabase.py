#!/usr/bin/env python3
"""
Supabase 연동 테스트 - 더미 데이터로 테스트
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# 환경변수 로드
load_dotenv()

print("=" * 50)
print("Supabase 연동 테스트")
print("=" * 50)

# 더미 데이터
dummy_products = [
    {
        'keyword': '카시트',
        'title': '[테스트] 신생아 바운서 카시트',
        'lprice': '89000',
        'mall_name': '쿠팡',
        'link': 'https://example.com/1',
        'image': 'https://example.com/image1.jpg',
        'collected_at': datetime.now().isoformat()
    },
    {
        'keyword': '유모차',
        'title': '[테스트] 고급 유모차',
        'lprice': '250000',
        'mall_name': '네이버 쇼핑',
        'link': 'https://example.com/2',
        'image': 'https://example.com/image2.jpg',
        'collected_at': datetime.now().isoformat()
    },
    {
        'keyword': '기저귀',
        'title': '[테스트] 팬티형 기저귀',
        'lprice': '35000',
        'mall_name': '당근마켓',
        'link': 'https://example.com/3',
        'image': 'https://example.com/image3.jpg',
        'collected_at': datetime.now().isoformat()
    }
]

try:
    # Supabase 클라이언트 초기화
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')

    print(f"\n✓ Supabase URL 로드됨: {supabase_url}")
    print(f"✓ Supabase Key 로드됨: {supabase_key[:20]}...")

    client: Client = create_client(supabase_url, supabase_key)
    print("\n✓ Supabase 클라이언트 초기화 완료")

    # 데이터 삽입
    print(f"\n{len(dummy_products)}개 더미 데이터를 삽입 중...")
    response = client.table('products').insert(dummy_products).execute()

    print(f"\n✅ Supabase에 데이터 추가 성공!")
    print(f"추가된 행 수: {len(response.data)}")

    # 확인
    all_data = client.table('products').select('*').execute()
    print(f"\n현재 Supabase 'products' 테이블 총 행 수: {len(all_data.data)}")
    print("\n최근 3개 데이터:")
    for item in all_data.data[-3:]:
        print(f"  - {item.get('keyword')}: {item.get('title')}")

except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
