#!/usr/bin/env python3
"""
Mock 데이터로 전체 데이터 수집 파이프라인 테스트
(네이버 API 문제 해결까지 임시 사용)
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv
from supabase import create_client, Client
import schedule
import time

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Mock 데이터 (실제 네이버 API 대신 사용)
KEYWORDS = ["카시트", "유모차", "기저귀", "아동복"]

# 각 키워드별 Mock 데이터
MOCK_DATA = {
    "카시트": [
        {"title": "[마먀] 신생아 회전 카시트", "lprice": "250000", "mallName": "쿠팡"},
        {"title": "브라이텍스 카시트", "lprice": "189000", "mallName": "네이버 쇼핑"},
        {"title": "짱구 회전카시트", "lprice": "320000", "mallName": "당근마켓"},
    ],
    "유모차": [
        {"title": "조니걸 럭셔리 유모차", "lprice": "450000", "mallName": "쿠팡"},
        {"title": "갈루파 접이식 유모차", "lprice": "280000", "mallName": "11번가"},
        {"title": "아기뛰기 가벼운 유모차", "lprice": "199000", "mallName": "당근마켓"},
    ],
    "기저귀": [
        {"title": "팸퍼스 팬티형 기저귀 XL", "lprice": "35000", "mallName": "쿠팡"},
        {"title": "하기스 신생아 기저귀", "lprice": "28000", "mallName": "이마트"},
        {"title": "메리스 기저귀 팬티형", "lprice": "32000", "mallName": "네이버 쇼핑"},
    ],
    "아동복": [
        {"title": "[구메이] 아동 겨울 코트", "lprice": "59000", "mallName": "쿠팡"},
        {"title": "네이버 키즈 셔츠", "lprice": "39000", "mallName": "네이버 쇼핑"},
        {"title": "뽀로로 아동 점프수트", "lprice": "25000", "mallName": "당근마켓"},
    ],
}


class MockNaverCollector:
    """Mock 네이버 데이터 수집 클래스"""

    def collect_all_products(self) -> List[Dict]:
        """
        Mock 데이터로 상품 데이터 생성
        """
        all_products = []

        for keyword in KEYWORDS:
            logger.info(f"'{keyword}' 수집 중... (Mock 데이터)")
            time.sleep(0.5)  # 실제처럼 약간의 딜레이

            mock_items = MOCK_DATA.get(keyword, [])

            for item in mock_items:
                product = {
                    'keyword': keyword,
                    'title': item['title'],
                    'lprice': item['lprice'],
                    'mall_name': item['mallName'],
                    'link': f'https://shopping.naver.com/mock/{keyword}',
                    'image': f'https://example.com/image/{keyword}.jpg',
                    'collected_at': datetime.now().isoformat()
                }
                all_products.append(product)

            logger.info(f"'{keyword}' 수집 완료: {len(mock_items)}개 상품")

        logger.info(f"총 {len(all_products)}개 상품 수집 완료")
        return all_products


class SupabaseWriter:
    """Supabase 데이터베이스 쓰기 클래스"""

    def __init__(self):
        """Supabase 클라이언트 초기화"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_API_KEY')

        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase 설정이 누락되었습니다.")
            raise ValueError("SUPABASE_URL 또는 SUPABASE_API_KEY가 누락되었습니다.")

        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase 인증 완료")
        except Exception as e:
            logger.error(f"Supabase 인증 실패: {e}")
            raise

    def insert_products(self, products: List[Dict]) -> bool:
        """상품 데이터를 Supabase에 추가"""
        if not products:
            logger.warning("추가할 상품이 없습니다.")
            return False

        try:
            logger.info(f"Supabase에 {len(products)}개 상품 데이터 추가 중...")

            data_to_insert = []
            for product in products:
                data_to_insert.append({
                    'keyword': product.get('keyword', ''),
                    'title': product.get('title', ''),
                    'lprice': product.get('lprice', ''),
                    'mall_name': product.get('mall_name', ''),
                    'link': product.get('link', ''),
                    'image': product.get('image', ''),
                    'collected_at': product.get('collected_at', '')
                })

            response = self.client.table('products').insert(data_to_insert).execute()

            logger.info(f"✓ {len(products)}개 상품 데이터가 Supabase에 추가되었습니다.")
            return True

        except Exception as e:
            logger.error(f"Supabase 데이터 추가 중 오류: {e}")
            return False


def run_collection_job():
    """주기적으로 실행될 데이터 수집 작업"""
    logger.info("=" * 50)
    logger.info("데이터 수집 작업 시작 (Mock 모드)")
    logger.info("=" * 50)

    try:
        # 1. Mock 데이터 수집
        collector = MockNaverCollector()
        products = collector.collect_all_products()

        if not products:
            logger.warning("수집된 상품이 없습니다.")
            return False

        # 2. Supabase에 저장
        writer = SupabaseWriter()
        success = writer.insert_products(products)

        if success:
            logger.info("데이터 수집 작업 완료 ✓")
        else:
            logger.error("데이터 수집 작업 실패 ✗")

        return success

    except Exception as e:
        logger.error(f"데이터 수집 작업 중 오류 발생: {e}")
        return False
    finally:
        logger.info("=" * 50)


def schedule_jobs():
    """스케줄 예약 설정"""
    schedule.every().day.at("09:00").do(run_collection_job)
    logger.info("스케줄 설정: 매일 오전 9시에 실행")

    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """메인 진입점"""
    logger.info(f"Baby Ranking 데이터 수집기 시작 (Mock 모드) - {datetime.now()}")

    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            logger.info("한 번만 실행 모드")
            run_collection_job()
        elif sys.argv[1] == '--schedule':
            logger.info("스케줄 모드 시작")
            schedule_jobs()
        else:
            print(f"사용 방법: python data_collector_mock.py [--once|--schedule]")
    else:
        logger.info("기본 모드 - 한 번만 실행")
        run_collection_job()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        sys.exit(1)
