/**
 * app.js
 * 육아용품 랭킹 & 최저가 검색 - 동적 렌더링 로직
 * 데이터 소스: Supabase PostgreSQL
 */

// Supabase 클라이언트 초기화
const SUPABASE_URL = 'https://grocmjqqtkemqihwgorm.supabase.co';
const SUPABASE_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdyb2NtanFxdGtlbXFpaHdnb3JtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzOTA0MzgsImV4cCI6MjA5MDk2NjQzOH0.a-dQBJvQZs6ZMihjRAYn30kGAlyVBBY8TZvgcQ6nb4U';

let cachedProducts = null;

/**
 * Supabase에서 상품 데이터 가져오기
 */
async function fetchProducts() {
    if (cachedProducts) return cachedProducts;

    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/products?limit=500`, {
            headers: {
                'apikey': SUPABASE_API_KEY,
                'Authorization': `Bearer ${SUPABASE_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Supabase 형식을 app.js 호환 형식으로 변환
        cachedProducts = data.map(item => ({
            // 원본 필드
            keyword: item.keyword,
            title: item.title,
            lprice: item.lprice,
            mall_name: item.mall_name,
            link: item.link,
            image: item.image,
            collected_at: item.collected_at,

            // UI용으로 변환된 필드
            category: item.keyword,                    // 카테고리 = 검색 키워드
            name: item.title,                          // 상품명
            price: parseInt(item.lprice) || 0,         // 가격 (숫자로 변환)
            brand: item.mall_name || 'N/A',            // 브랜드 = 쇼핑몰
            rating: '⭐ 4.5',                          // 고정값 (네이버는 별점 미제공)
            score: 85 + Math.random() * 15             // 점수 (랜덤 85~100)
        }));

        return cachedProducts;
    } catch (error) {
        console.error('Supabase에서 데이터를 가져오지 못했습니다:', error);
        // 오류 시 mock-data 폴백
        try {
            const response = await fetch('mock-data.json');
            const data = await response.json();
            cachedProducts = data;
            return cachedProducts;
        } catch (fallbackError) {
            console.error('Mock 데이터도 로드 실패:', fallbackError);
            return [];
        }
    }
}

// ──────────────────────────────────────────────
// 검색 입력 이벤트
// ──────────────────────────────────────────────
document.getElementById('searchInput').addEventListener('keyup', function(e) {
    const keyword = e.target.value.trim();

    // X 버튼 표시 여부
    document.getElementById('searchClear').classList.toggle('hidden', keyword.length === 0);

    if (keyword.length > 0) {
        renderRanking(keyword);
    } else {
        // 빈 검색어 → 전체 목록 복원
        document.getElementById('rankingTitle').classList.add('hidden');
        document.getElementById('rankingDefaultHeader').classList.remove('hidden');
        renderRanking('');
    }
});

// X 버튼 클릭 → 검색어 초기화
document.getElementById('searchClear').addEventListener('click', function() {
    const input = document.getElementById('searchInput');
    input.value = '';
    input.focus();
    this.classList.add('hidden');
    document.getElementById('rankingTitle').classList.add('hidden');
    document.getElementById('rankingDefaultHeader').classList.remove('hidden');
    renderRanking('');
});

// ──────────────────────────────────────────────
// 랭킹 렌더링 함수
// ──────────────────────────────────────────────
async function renderRanking(keyword) {
    try {
        const data = await fetchProducts();

        // 1. 키워드 필터링 (빈 문자열이면 전체)
        // 2. score 내림차순 정렬
        // 3. 상위 10개 추출
        const filteredData = (keyword.length === 0 ? data : data.filter(
            item => item.category.includes(keyword) || item.name.includes(keyword)
        ))
            .slice()                            // 원본 배열 보호
            .sort((a, b) => b.score - a.score)
            .slice(0, 10);

        const listContainer  = document.getElementById('rankingList');
        const titleContainer = document.getElementById('rankingTitle');
        const keywordDisplay = document.getElementById('keywordDisplay');
        const defaultHeader  = document.getElementById('rankingDefaultHeader');

        listContainer.innerHTML = '';

        if (filteredData.length > 0) {
            if (keyword.length > 0) {
                titleContainer.classList.remove('hidden');
                defaultHeader.classList.add('hidden');
                keywordDisplay.innerText = keyword;
            }

            filteredData.forEach((item, index) => {
                const card = `
                    <div class="bg-white rounded-xl shadow-sm border border-gray-100
                                overflow-hidden hover:shadow-lg hover:-translate-y-0.5
                                transition-all duration-200">
                        <div class="p-5">
                            <div class="flex justify-between items-center mb-2">
                                <span class="bg-pink-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                                    Top ${index + 1}
                                </span>
                                <span class="text-xs text-gray-400 font-medium">${item.brand}</span>
                            </div>
                            <h3 class="text-base font-bold text-gray-900 leading-snug mb-3 line-clamp-2">
                                ${item.name}
                            </h3>
                            <div class="flex items-center gap-1 mb-4">
                                <span class="text-sm font-bold text-gray-800">${item.rating}</span>
                                <svg class="w-4 h-4 text-yellow-400 fill-current flex-shrink-0" viewBox="0 0 20 20">
                                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"/>
                                </svg>
                                <span class="text-xs text-gray-400 ml-1">점수 ${item.score}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-xl font-black text-gray-900">
                                    ${item.price.toLocaleString('ko-KR')}원
                                </span>
                                <button class="bg-gray-800 text-white text-xs font-bold
                                               px-4 py-2 rounded-lg hover:bg-black
                                               active:scale-95 transition-all duration-150">
                                    최저가 확인
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                listContainer.innerHTML += card;
            });

        } else {
            listContainer.innerHTML = `
                <p class="col-span-full text-center py-12 text-gray-400 text-sm">
                    '<span class="font-semibold text-gray-600">${keyword}</span>'에 대한 랭킹 정보가 아직 없습니다.
                </p>
            `;
        }

    } catch (error) {
        console.error('[baby-ranking] 데이터 로드 실패:', error);
        document.getElementById('rankingList').innerHTML = `
            <p class="col-span-full text-center py-12 text-red-400 text-sm">
                ⚠️ 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.
            </p>
        `;
    }
}

// ──────────────────────────────────────────────
// 초기 실행: 페이지 로드 시 전체 랭킹 표시
// ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => renderRanking(''));
