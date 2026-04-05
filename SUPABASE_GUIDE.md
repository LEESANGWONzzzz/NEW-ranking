# 🍼 Baby Ranking - 데이터 수집기 (Supabase 버전)

네이버 쇼핑 API를 활용하여 육아용품 데이터를 자동으로 수집하고 Supabase에 저장하는 Python 스크립트입니다.

## 📋 필수 사항

- Python 3.8 이상
- Supabase 무료 계정
- 네이버 쇼핑 API 키 (이미 설정됨)

## 🚀 빠른 시작

### 1️⃣ 패키지 설치

```bash
pip install -r requirements.txt
```

### 2️⃣ Supabase 프로젝트 생성

1. [Supabase 웹사이트](https://supabase.com) 접속
2. Sign Up으로 계정 생성 (GitHub로도 가능)
3. **Create New Project** 클릭
4. 프로젝트 이름 설정 (예: `baby-ranking`)
5. 데이터베이스 비밀번호 설정
6. Region 선택 (추천: `ap-northeast-1` - 도쿄, 한국과 가까움)
7. **Create New Project** 클릭 (약 2-5분 소요)

### 3️⃣ Supabase 테이블 생성

1. Supabase 대시보드에서 **SQL Editor** 선택
2. `supabase_setup.sql` 파일의 모든 SQL 복사
3. Supabase SQL Editor에 붙여넣기
4. **RUN** 버튼 클릭으로 테이블 생성

### 4️⃣ 환경 설정

#### Supabase URL과 API Key 확인

1. Supabase 대시보드 좌측 메뉴 **Settings** 선택
2. **API** 클릭
3. 다음 2가지 정보 복사:
   - **Project URL** (예: `https://your-project.supabase.co`)
   - **anon public** API Key

#### .env 파일 설정

```bash
cp .env.example .env
```

`.env` 파일 수정:
```
# 네이버 쇼핑 API (이미 설정됨)
NAVER_CLIENT_ID=tQ09if6POQZyFZ_X2AZs
NAVER_CLIENT_SECRET=iFfee_7v8b

# Supabase 설정 (실제 URL과 Key 입력)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-anon-key
```

### 5️⃣ 실행

#### 한 번만 실행
```bash
python data_collector.py --once
```

#### 매일 오전 9시 자동 실행 (백그라운드 실행)
```bash
python data_collector.py --schedule
```

## 📊 데이터 확인

### Supabase에서 직접 확인

1. Supabase 대시보드 → **Table Editor**
2. `products` 테이블 선택
3. 수집된 데이터 확인

### CSV로 내보내기

Supabase Table Editor의 **Export** 버튼으로 CSV 다운로드 가능

### SQL 쿼리로 조회

Supabase SQL Editor에서:
```sql
-- 모든 상품 조회
SELECT * FROM products;

-- 최근 수집 데이터만 조회
SELECT * FROM products
WHERE collected_at > NOW() - INTERVAL '1 day'
ORDER BY collected_at DESC;

-- 키워드별 상품 수 조회
SELECT keyword, COUNT(*) as count
FROM products
GROUP BY keyword;

-- 특정 키워드의 최저가 상품
SELECT keyword, title, lprice, mall_name
FROM products
WHERE keyword = '카시트'
ORDER BY CAST(lprice AS INTEGER) ASC;
```

## 📁 파일 구조

```
baby-ranking/
├── data_collector.py          # 메인 수집 스크립트
├── requirements.txt           # Python 의존성
├── .env                      # 환경변수 (git 무시)
├── .env.example              # 환경변수 예시
├── supabase_setup.sql        # Supabase 테이블 생성 SQL
├── data_collector.log        # 실행 로그 (자동 생성)
└── README.md                 # 이 파일
```

## 🔍 로그 확인

```bash
# 실시간 로그 확인
tail -f data_collector.log

# 마지막 100줄 보기
tail -100 data_collector.log
```

## 📊 수집 데이터 필드

| 필드명 | 설명 | 예시 |
|--------|------|-----|
| keyword | 검색 키워드 | 카시트 |
| title | 상품명 | [마먀] 신생아 회전 카시트 |
| lprice | 최저가 | 250000 |
| mall_name | 판매 쇼핑몰 | 쿠팡 |
| link | 상품 링크 | https://shopping.naver.com/... |
| image | 이미지 URL | https://shopping-phinf.pstatic.net/... |
| collected_at | 수집 일시 | 2024-04-05T10:30:45 |

## 🛠️ 문제 해결

### "SUPABASE_URL 또는 SUPABASE_API_KEY가 누락되었습니다"
- `.env` 파일 확인
- Supabase Project URL과 API Key 올바르게 입력했는지 확인

### "table 'products' does not exist"
- `supabase_setup.sql` 파일을 Supabase SQL Editor에서 실행했는지 확인
- 테이블이 `products`로 정확하게 생성되었는지 확인

### API 호출 오류
- 네이버 API Key 확인
- 네트워크 연결 확인
- Rate limit 확인 (초당 10회 제한)

## 🔐 보안

⚠️ **주의**: `.env` 파일은 절대 GitHub에 커밋하지 마세요!
- `.gitignore` 파일에 `.env` 포함되어 있습니다
- 민감한 정보(API Key)는 환경변수로 관리합니다

## 📈 성능

- **수집 시간**: 약 4-5초 (4개 키워드 × 100개 상품)
- **저장 시간**: 약 1-2초
- **전체 실행**: 약 6-8초

## 🔄 스케줄

기본 설정: **매일 오전 9시 (09:00)**

변경하려면 `data_collector.py`의 `schedule_jobs()` 함수 수정:
```python
# 매일 오전 8시로 변경
schedule.every().day.at("08:00").do(run_collection_job)

# 매 6시간마다 실행
schedule.every(6).hours.do(run_collection_job)

# 매주 월요일 9시
schedule.every().monday.at("09:00").do(run_collection_job)
```

## 📞 지원

- Supabase 공식 문서: https://supabase.com/docs
- 네이버 개발자 센터: https://developers.naver.com

---

**Made with 💚 for Baby Ranking**
