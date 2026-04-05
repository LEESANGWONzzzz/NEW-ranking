#!/usr/bin/env python3
"""
네이버 쇼핑 검색 API를 활용하여 육아용품 데이터를 수집하고
Supabase에 자동으로 적재하는 스크립트
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional

import requests
import schedule
from dotenv import load_dotenv
from supabase import create_client, Client

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

# 상수 정의
NAVER_API_URL = "https://openapi.naver.com/v1/search/shop.json"
KEYWORDS = ["카시트", "유모차", "기저귀", "아동복"]
ITEMS_PER_KEYWORD = 100
API_CALL_DELAY = 1  # API 호출 간 딜레이 (초)

class NaverShoppingCollector:
    """네이버 쇼핑 API 데이터 수집 클래스"""

    def __init__(self):
        """초기화 및 환경변수 검증"""
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')

        if not self.client_id or not self.client_secret:
            logger.error("네이버 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
            raise ValueError("NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 누락되었습니다.")

        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }

        logger.info("네이버 쇼핑 수집기 초기화 완료")

    def search_products(self, keyword: str, display: int = 100) -> List[Dict]:
        """
        네이버 쇼핑 API를 통해 상품 데이터 검색

        Args:
            keyword (str): 검색 키워드
            display (int): 조회할 결과 건수 (최대 100)

        Returns:
            List[Dict]: 정제된 상품 데이터 리스트
        """
        try:
            logger.info(f"'{keyword}' 검색 시작...")

            params = {
                'query': keyword,
                'display': min(display, 100),  # 최대 100
                'start': 1,
                'sort': 'asc'
            }

            response = requests.get(
                NAVER_API_URL,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if 'items' not in data:
                logger.warning(f"'{keyword}' 검색 결과에서 items가 없습니다.")
                return []

            products = []
            for item in data['items']:
                try:
                    product = {
                        'keyword': keyword,
                        'title': item.get('title', '').replace('<b>', '').replace('</b>', ''),
                        'lprice': item.get('lprice', 'N/A'),
                        'mallName': item.get('mallName', 'N/A'),
                        'link': item.get('link', ''),
                        'image': item.get('image', ''),
                        'collected_at': datetime.now().isoformat()
                    }
                    products.append(product)
                except Exception as e:
                    logger.warning(f"상품 데이터 파싱 오류: {e}")
                    continue

            logger.info(f"'{keyword}' 검색 완료: {len(products)}개 상품 수집")
            return products

        except requests.exceptions.Timeout:
            logger.error(f"'{keyword}' 검색 중 timeout 발생")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"'{keyword}' 검색 중 API 오류: {e}")
            return []
        except Exception as e:
            logger.error(f"'{keyword}' 검색 중 예상치 못한 오류: {e}")
            return []

    def collect_all_products(self) -> List[Dict]:
        """
        모든 키워드에 대해 상품 데이터 수집

        Returns:
            List[Dict]: 전체 상품 데이터 리스트
        """
        all_products = []

        for keyword in KEYWORDS:
            try:
                products = self.search_products(keyword, ITEMS_PER_KEYWORD)
                all_products.extend(products)

                # Rate limit 고려 - 다음 API 호출 전 대기
                time.sleep(API_CALL_DELAY)

            except Exception as e:
                logger.error(f"'{keyword}' 수집 중 오류: {e}")
                continue

        logger.info(f"총 {len(all_products)}개 상품 수집 완료")
        return all_products


class SupabaseWriter:
    """Supabase 데이터베이스 쓰기 클래스"""

    def __init__(self):
        """Supabase 클라이언트 초기화"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_API_KEY')

        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase 설정이 누락되었습니다. .env 파일을 확인하세요.")
            raise ValueError(
                "SUPABASE_URL 또는 SUPABASE_API_KEY가 누락되었습니다."
            )

        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase 인증 완료")

        except Exception as e:
            logger.error(f"Supabase 인증 실패: {e}")
            raise

    def insert_products(self, products: List[Dict]) -> bool:
        """
        상품 데이터를 Supabase 'products' 테이블에 추가

        Args:
            products (List[Dict]): 추가할 상품 데이터 리스트

        Returns:
            bool: 성공 여부
        """
        if not products:
            logger.warning("추가할 상품이 없습니다.")
            return False

        try:
            logger.info(f"Supabase에 {len(products)}개 상품 데이터 추가 중...")

            # 데이터 변환
            data_to_insert = []
            for product in products:
                data_to_insert.append({
                    'keyword': product.get('keyword', ''),
                    'title': product.get('title', ''),
                    'lprice': product.get('lprice', ''),
                    'mall_name': product.get('mallName', ''),
                    'link': product.get('link', ''),
                    'image': product.get('image', ''),
                    'collected_at': product.get('collected_at', '')
                })

            # Supabase에 데이터 삽입
            response = self.client.table('products').insert(data_to_insert).execute()

            logger.info(f"✓ {len(products)}개 상품 데이터가 Supabase에 추가되었습니다.")
            return True

        except Exception as e:
            logger.error(f"Supabase 데이터 추가 중 오류: {e}")
            return False


def run_collection_job():
    """주기적으로 실행될 데이터 수집 작업"""
    logger.info("=" * 50)
    logger.info("데이터 수집 작업 시작")
    logger.info("=" * 50)

    try:
        # 1. 네이버 데이터 수집
        collector = NaverShoppingCollector()
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
    # 매일 오전 9시에 실행
    schedule.every().day.at("09:00").do(run_collection_job)
    logger.info("스케줄 설정: 매일 오전 9시에 실행")

    # 스케줄러 실행 (무한 루프)
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 확인


def main():
    """메인 진입점"""
    logger.info(f"Baby Ranking 데이터 수집기 시작 - {datetime.now()}")

    # 커맨드라인 인자 체크
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # 한 번만 실행
            logger.info("한 번만 실행 모드")
            run_collection_job()
        elif sys.argv[1] == '--schedule':
            # 스케줄 모드
            logger.info("스케줄 모드 시작")
            schedule_jobs()
        else:
            print(f"사용 방법: python data_collector.py [--once|--schedule]")
            print("  --once    : 한 번만 실행하고 종료")
            print("  --schedule: 스케줄에 따라 주기적 실행")
    else:
        # 기본: 한 번만 실행
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
