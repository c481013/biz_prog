import sqlite3
import os
import io
import base64
from PIL import Image

DB_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hongik_records.db')

def init_db():
    """SQLite 데이터베이스 테이블을 초기화합니다."""
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,          -- '식당' 또는 '카페'
            name TEXT NOT NULL,              -- 상호명
            menu TEXT NOT NULL,              -- 추천 메뉴명
            price INTEGER NOT NULL,          -- 가격
            description TEXT NOT NULL,       -- 특징 및 한줄평
            rating INTEGER NOT NULL,         -- 별점 (1~5)
            image_base64 TEXT,               -- 압축된 이미지 Base64 스트링
            nickname TEXT,                   -- 작성자 닉네임 (선택)
            password TEXT,                   -- 삭제용 비밀번호 (추가)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 기존 데이터베이스에 password 컬럼이 없는 경우 동적 추가
    try:
        cursor.execute("SELECT password FROM recommendations LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE recommendations ADD COLUMN password TEXT DEFAULT '1234'")
        
    conn.commit()
    conn.close()

def compress_and_encode_image(uploaded_file):
    """
    업로드된 이미지를 600px 너비로 리사이징하고, 
    JPEG 70% 화질로 압축한 뒤 Base64 문자열로 변환합니다.
    """
    if uploaded_file is None:
        return None
    
    try:
        # Streamlit의 UploadedFile을 PIL 이미지로 변환
        img = Image.open(uploaded_file)
        
        # RGBA 이미지는 JPEG로 저장할 수 없으므로 RGB로 변환
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGB')
        else:
            img = img.convert('RGB')
            
        # 최대 가로 길이를 600px로 제한하여 리사이징 (비율 유지)
        max_width = 600
        if img.width > max_width:
            w_percent = (max_width / float(img.width))
            h_size = int((float(img.height) * float(w_percent)))
            img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
            
        # 바이트 스트림에 JPEG 형식으로 저장 (압축률 70%)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        
        # Base64로 인코딩하여 반환
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str
    except Exception as e:
        print(f"이미지 압축 중 오류 발생: {e}")
        return None

def add_recommendation(category, name, menu, price, description, rating, image_file=None, nickname="홍대생", password="1234"):
    """새로운 추천 맛집/카페 정보를 데이터베이스에 추가합니다."""
    init_db()
    
    # 이미지 압축 및 인코딩
    image_base64 = compress_and_encode_image(image_file) if image_file else None
    
    # 기본값 지정
    if not nickname or nickname.strip() == "":
        nickname = "홍대생"
    if not password or password.strip() == "":
        password = "1234"
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recommendations (category, name, menu, price, description, rating, image_base64, nickname, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category, name, menu, price, description, rating, image_base64, nickname, password))
    
    conn.commit()
    conn.close()

def delete_recommendation(item_id):
    """아이디가 일치하는 게시글을 삭제합니다."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendations WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_recommendations(category_filter=None, search_query=None, sort_by="최신순"):
    """
    저장된 추천 목록을 필터링 및 정렬하여 가져옵니다.
    """
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 컬럼명으로 데이터 접근 가능하게 설정
    cursor = conn.cursor()
    
    query = "SELECT * FROM recommendations WHERE 1=1"
    params = []
    
    # 카테고리 필터 ('식당', '카페')
    if category_filter and category_filter in ('식당', '카페'):
        query += " AND category = ?"
        params.append(category_filter)
        
    # 검색어 필터 (상호명 검색으로 한정)
    if search_query:
        query += " AND name LIKE ?"
        like_query = f"%{search_query}%"
        params.append(like_query)
        
    # 정렬 방식 적용
    if sort_by == "최신순":
        query += " ORDER BY created_at DESC"
    elif sort_by == "별점 높은순":
        query += " ORDER BY rating DESC, created_at DESC"
    elif sort_by == "별점 낮은순":
        query += " ORDER BY rating ASC, created_at DESC"
    elif sort_by == "가격 낮은순":
        query += " ORDER BY price ASC, created_at DESC"
    elif sort_by == "가격 높은순":
        query += " ORDER BY price DESC, created_at DESC"
    else:
        query += " ORDER BY created_at DESC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # sqlite3.Row 객체 리스트를 dict 리스트로 변환 (패스워드 안전 폴백 제공)
    results = []
    for row in rows:
        d = dict(row)
        if 'password' not in d or d['password'] is None:
            d['password'] = '1234'
        results.append(d)
    conn.close()
    return results
    


def get_statistics():
    """홈 화면 대시보드용 통계 데이터를 반환합니다."""
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 전체 개수, 평균 별점, 평균 가격
    cursor.execute('''
        SELECT 
            COUNT(*), 
            AVG(rating), 
            AVG(price) 
        FROM recommendations
    ''')
    total_count, avg_rating, avg_price = cursor.fetchone()
    
    # 식당 개수
    cursor.execute("SELECT COUNT(*) FROM recommendations WHERE category = '식당'")
    restaurant_count = cursor.fetchone()[0]
    
    # 카페 개수
    cursor.execute("SELECT COUNT(*) FROM recommendations WHERE category = '카페'")
    cafe_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_count": total_count or 0,
        "restaurant_count": restaurant_count or 0,
        "cafe_count": cafe_count or 0,
        "avg_rating": round(avg_rating or 0.0, 1),
        "avg_price": int(avg_price or 0)
    }
