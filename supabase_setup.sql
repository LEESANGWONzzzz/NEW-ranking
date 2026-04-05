-- Supabase 에서 실행할 SQL 스크립트
-- Supabase 대시보드 > SQL Editor에서 아래 쿼리를 복사해서 실행하세요

-- products 테이블 생성
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  keyword TEXT NOT NULL,
  title TEXT NOT NULL,
  lprice TEXT,
  mall_name TEXT,
  link TEXT,
  image TEXT,
  collected_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (검색 성능 개선)
CREATE INDEX idx_products_keyword ON products(keyword);
CREATE INDEX idx_products_collected_at ON products(collected_at);

-- RLS(Row Level Security) 비활성화 (개발 단계)
ALTER TABLE products DISABLE ROW LEVEL SECURITY;

-- COMMENT
COMMENT ON TABLE products IS '네이버 쇼핑 API에서 수집한 육아용품 상품 데이터';
COMMENT ON COLUMN products.keyword IS '검색 키워드 (카테고리)';
COMMENT ON COLUMN products.title IS '상품명';
COMMENT ON COLUMN products.lprice IS '최저가';
COMMENT ON COLUMN products.mall_name IS '모든 쇼핑몰명';
COMMENT ON COLUMN products.link IS '상품 링크';
COMMENT ON COLUMN products.image IS '상품 이미지 URL';
COMMENT ON COLUMN products.collected_at IS '데이터 수집 일시';
