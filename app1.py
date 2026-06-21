import streamlit as st
import base64
import database

# Streamlit 페이지 설정
st.set_page_config(
    page_title="홍대 맛집 추천.zip",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터베이스 초기화
database.init_db()

# 다이얼로그 정의 (Streamlit의 팝업 창 기능)
@st.dialog("🎉 등록 완료")
def show_registration_success_dialog(name):
    st.markdown(f"<h3 style='color: #1B3A6B; text-align: center; margin-top: 0;'>'{name}' 등록이 완료되었습니다!</h3>", unsafe_allow_html=True)
    st.write("소중한 추천 감사합니다. 등록된 글은 홈에서 바로 확인해 보실 수 있습니다!")
    if st.button("확인", use_container_width=True):
        st.rerun()

@st.dialog("🗑️ 게시글 삭제")
def show_delete_dialog(item_id, name, correct_password):
    st.markdown(f"<h3 style='color: #1B3A6B; text-align: center; margin-top: 0;'>'{name}' 삭제</h3>", unsafe_allow_html=True)
    st.write("이 추천글을 삭제하시겠습니까? 등록할 때 입력하셨던 4자리 삭제 비밀번호를 입력해 주세요.")
    
    input_pw = st.text_input("비밀번호 입력", type="password", max_chars=4, key=f"del_input_{item_id}")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("삭제하기", type="primary", use_container_width=True, key=f"del_btn_action_{item_id}"):
            if input_pw == correct_password:
                database.delete_recommendation(item_id)
                st.success("게시글이 성공적으로 삭제되었습니다!")
                st.rerun()
            else:
                st.error("비밀번호가 일치하지 않습니다!")
    with col_btn2:
        if st.button("취소", use_container_width=True, key=f"del_btn_cancel_{item_id}"):
            st.rerun()

# 커스텀 CSS 주입 (파란색/하얀색 테마)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Outfit:wght@300;400;500;700;900&display=swap');
    
    /* 전체 폰트 적용 */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
        background-color: #F0F4FA;
    }
    
    /* 헤더 스타일 */
    .header-container {
        background: linear-gradient(135deg, #1B3A6B 0%, #2B5EA7 50%, #4A90D9 100%);
        padding: 40px 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(27, 58, 107, 0.25);
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 24px;
    }
    .header-mascot {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255,255,255,0.5);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .header-text {
        text-align: left;
    }
    .header-title {
        font-size: 2.4rem;
        font-weight: 900;
        margin-bottom: 6px;
        letter-spacing: -1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* 맛집/카페 카드 스타일 */
    .food-card {
        background-color: #ffffff;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
        border: 1px solid #dce6f1;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 24px;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .food-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 35px rgba(27, 58, 107, 0.12);
        border-color: #7BAAF7;
    }
    .food-card-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-bottom: 1px solid #e8eef5;
    }
    .food-card-no-img {
        width: 100%;
        height: 200px;
        background: linear-gradient(135deg, #D6E4F7 0%, #B8D0F0 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #2B5EA7;
        font-size: 3rem;
    }
    .cafe-card-no-img {
        width: 100%;
        height: 200px;
        background: linear-gradient(135deg, #E8E0F0 0%, #D5C8E8 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #5C4B8A;
        font-size: 3rem;
    }
    .food-card-content {
        padding: 20px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .food-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .badge-restaurant {
        background-color: #DBEAFE;
        color: #1B3A6B;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #93C5FD;
    }
    .badge-cafe {
        background-color: #EDE9FE;
        color: #5C4B8A;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        border: 1px solid #C4B5FD;
    }
    .rating-stars {
        color: #FCC419;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .food-card-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1B3A6B;
        margin: 6px 0;
    }
    .food-card-menu {
        font-size: 0.95rem;
        color: #495057;
        margin-bottom: 8px;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    .food-card-price {
        font-size: 1.15rem;
        font-weight: 800;
        color: #2B5EA7;
        margin-bottom: 12px;
    }
    .food-card-desc {
        font-size: 0.9rem;
        color: #495057;
        line-height: 1.6;
        margin-bottom: 16px;
        background-color: #F0F4FA;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #7BAAF7;
        flex-grow: 1;
    }
    .cafe-card-desc {
        border-left: 4px solid #C4B5FD;
    }
    .food-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        color: #868E96;
        border-top: 1px solid #e8eef5;
        padding-top: 12px;
        margin-top: auto;
    }
    
    /* 대시보드 통계 카드 */
    .stat-box {
        background-color: white;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #dce6f1;
        transition: transform 0.2s;
    }
    .stat-box:hover {
        transform: translateY(-3px);
    }
    .stat-val {
        font-size: 2rem;
        font-weight: 900;
        color: #1B3A6B;
        margin-top: 5px;
    }
    .stat-lbl {
        font-size: 0.9rem;
        color: #868E96;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# 캐릭터 이미지를 Base64로 인코딩하여 배너에 삽입
import os
mascot_b64 = ""
mascot_path = os.path.join(os.path.dirname(__file__), '다운로드.jpg')
if os.path.exists(mascot_path):
    with open(mascot_path, 'rb') as f:
        mascot_b64 = base64.b64encode(f.read()).decode('utf-8')

# 메인 타이틀 배너
st.markdown(f"""
<div class="header-container">
    <img class="header-mascot" src="data:image/png;base64,{mascot_b64}" alt="마스코트">
    <div class="header-text">
        <div class="header-title">🍜 홍대 맛집 추천.zip</div>
        <div class="header-subtitle">🍕 홍대인들이 추천해주는 내돈내산 맛집 리스트 🍰</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정 (통계 및 검색 기능 포함)
with st.sidebar:

    st.markdown("### 🔍 전체 검색 및 정렬")
    search_query = st.text_input("검색어 입력", placeholder="상호명, 메뉴, 한줄평 키워드...")
    
    sort_by = st.selectbox(
        "정렬 기준",
        ["최신순", "별점 높은순", "별점 낮은순", "가격 낮은순", "가격 높은순"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 실시간 통계")
    stats = database.get_statistics()
    
    st.markdown(f"""
    <div class="stat-box" style="margin-bottom:15px;">
        <div class="stat-lbl">✍️ 등록된 총 리뷰 수</div>
        <div class="stat-val">{stats['total_count']}개</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-lbl">🍕 식당</div>
            <div class="stat-val" style="color: #2B5EA7;">{stats['restaurant_count']}개</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-lbl">☕ 카페</div>
            <div class="stat-val" style="color: #5C4B8A;">{stats['cafe_count']}개</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"""
    <div class="stat-box" style="margin-top:15px; margin-bottom:15px;">
        <div class="stat-lbl">⭐ 평균 만족도</div>
        <div class="stat-val" style="color: #FCC419;">{'★' * int(round(stats['avg_rating']))} ({stats['avg_rating']}/5)</div>
    </div>
    """, unsafe_allow_html=True)


# 메인 탭 구성
tab_home, tab_restaurant, tab_cafe, tab_register = st.tabs([
    "🏠 홈", 
    "🍕 식당 추천 목록", 
    "☕ 카페 추천 목록", 
    "✍️ 나의 추천 등록"
])

# --- TAB 1: 홈 & 분석 ---
with tab_home:
    st.markdown("### 🏆 홍대생들이 추천해주는 홍대 식당 & 카페")
    
    # 별점 5점 리스트 3개 노출 (검색 필터 반영)
    top_picks = database.get_recommendations(search_query=search_query, sort_by="별점 높은순")
    if top_picks:
        st.markdown("#### ⭐ 최고 추천 평점(5점) 리스트")
        top_5_stars = [item for item in top_picks if item['rating'] == 5][:3]
        if top_5_stars:
            cols_top = st.columns(len(top_5_stars))
            for idx, item in enumerate(top_5_stars):
                with cols_top[idx]:
                    img_tag = ""
                    if item['image_base64']:
                        img_tag = f'<img class="food-card-img" src="data:image/jpeg;base64,{item["image_base64"]}" alt="{item["name"]}">'
                    else:
                        cls = "food-card-no-img" if item['category'] == '식당' else "cafe-card-no-img"
                        icon = "🍕" if item['category'] == '식당' else "☕"
                        img_tag = f'<div class="{cls}">{icon}</div>'
                        
                    badge_cls = "badge-restaurant" if item['category'] == '식당' else "badge-cafe"
                    desc_border_cls = "food-card-desc" if item['category'] == '식당' else "food-card-desc cafe-card-desc"
                    
                    card_html = f"""
                    <div class="food-card">
                        {img_tag}
                        <div class="food-card-content">
                            <div class="food-card-header">
                                <span class="{badge_cls}">{item['category']}</span>
                                <span class="rating-stars">{"★" * item['rating']}</span>
                            </div>
                            <div class="food-card-title">{item['name']}</div>
                            <div class="food-card-menu">📌 추천 메뉴: {item['menu']}</div>
                            <div class="food-card-price">💸 가격: {item['price']:,}원</div>
                            <div class="{desc_border_cls}">{item['description']}</div>
                            <div class="food-card-footer">
                                <span>👤 {item['nickname']}</span>
                                <span>📅 {item['created_at'][:10]}</span>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button("🗑️ 삭제", key=f"del_btn_home_{item['id']}", use_container_width=True):
                        show_delete_dialog(item['id'], item['name'], item['password'])
        else:
            st.info("아직 5점 만점의 별점을 받은 가게가 없습니다. 직접 첫 번째 만점 맛집을 등록해 보세요!")
    else:
        st.info("아직 등록된 가게가 없습니다. 오른쪽 끝의 '✍️ 나만의 추천 등록' 탭에서 추천글을 작성해 보세요!")


# --- TAB 2: 식당 추천 목록 ---
with tab_restaurant:
    st.markdown("### 🍕 식당 추천 목록")
    restaurants = database.get_recommendations(
        category_filter="식당", 
        search_query=search_query, 
        sort_by=sort_by
    )
    
    if not restaurants:
        st.warning("조건에 맞는 맛집 추천글이 없습니다. 첫 리뷰어가 되어주세요!")
    else:
        # 3열 카드 그리드 배치
        cols = st.columns(3)
        for idx, item in enumerate(restaurants):
            with cols[idx % 3]:
                img_tag = ""
                if item['image_base64']:
                    img_tag = f'<img class="food-card-img" src="data:image/jpeg;base64,{item["image_base64"]}" alt="{item["name"]}">'
                else:
                    img_tag = f'<div class="food-card-no-img">🍕</div>'
                    
                card_html = f"""
                <div class="food-card">
                    {img_tag}
                    <div class="food-card-content">
                        <div class="food-card-header">
                            <span class="badge-restaurant">{item['category']}</span>
                            <span class="rating-stars">{"★" * item['rating']}</span>
                        </div>
                        <div class="food-card-title">{item['name']}</div>
                        <div class="food-card-menu">📌 추천 메뉴: {item['menu']}</div>
                        <div class="food-card-price">💸 가격: {item['price']:,}원</div>
                        <div class="food-card-desc">{item['description']}</div>
                        <div class="food-card-footer">
                            <span>👤 {item['nickname']}</span>
                            <span>📅 {item['created_at'][:10]}</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button("🗑️ 삭제", key=f"del_btn_res_{item['id']}", use_container_width=True):
                    show_delete_dialog(item['id'], item['name'], item['password'])

# --- TAB 3: 카페 추천 목록 ---
with tab_cafe:
    st.markdown("### ☕ 카페 추천 목록")
    cafes = database.get_recommendations(
        category_filter="카페", 
        search_query=search_query, 
        sort_by=sort_by
    )
    
    if not cafes:
        st.warning("조건에 맞는 카페 추천글이 없습니다. 첫 리뷰어가 되어주세요!")
    else:
        # 3열 카드 그리드 배치
        cols = st.columns(3)
        for idx, item in enumerate(cafes):
            with cols[idx % 3]:
                img_tag = ""
                if item['image_base64']:
                    img_tag = f'<img class="food-card-img" src="data:image/jpeg;base64,{item["image_base64"]}" alt="{item["name"]}">'
                else:
                    img_tag = f'<div class="cafe-card-no-img">☕</div>'
                    
                card_html = f"""
                <div class="food-card">
                    {img_tag}
                    <div class="food-card-content">
                        <div class="food-card-header">
                            <span class="badge-cafe">{item['category']}</span>
                            <span class="rating-stars">{"★" * item['rating']}</span>
                        </div>
                        <div class="food-card-title">{item['name']}</div>
                        <div class="food-card-menu">📌 추천 메뉴: {item['menu']}</div>
                        <div class="food-card-price">💸 가격: {item['price']:,}원</div>
                        <div class="food-card-desc cafe-card-desc">{item['description']}</div>
                        <div class="food-card-footer">
                            <span>👤 {item['nickname']}</span>
                            <span>📅 {item['created_at'][:10]}</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button("🗑️ 삭제", key=f"del_btn_cafe_{item['id']}", use_container_width=True):
                    show_delete_dialog(item['id'], item['name'], item['password'])

# --- TAB 4: 나만의 추천 등록 ---
with tab_register:
    st.markdown("### ✍️ 나만의 홍대 맛집/카페 추천하기")
    st.info("방문하셨던 맛집의 정보와 사진을 등록하여 학우들과 공유하세요! 입력한 내용은 우측에 실시간 프리뷰 카드로 표시됩니다.")
    
    col_form, col_preview = st.columns([3, 2])
    
    with col_form:
        category = st.radio(
            "카테고리", 
            ["식당", "카페"], 
            horizontal=True,
            help="식당 탭과 카페 탭 중 저장될 위치를 선택합니다."
        )
        
        name = st.text_input(
            "가게 이름", 
            placeholder="상호명을 정확히 입력해 주세요 (예: 율촌)"
        )
        
        menu = st.text_input(
            "추천 메뉴명", 
            placeholder="추천하는 베스트 메뉴를 적어주세요 (예: 닭칼국수)"
        )
        
        price = st.number_input(
            "가격 (1인분 또는 단품 기준, 원)", 
            min_value=0, 
            max_value=1000000, 
            value=8000, 
            step=500
        )
        
        rating = st.slider(
            "별점 만족도", 
            min_value=1, 
            max_value=5, 
            value=5, 
            step=1,
            help="1점: 비추천 / 3점: 평범 / 5점: 적극 추천"
        )
        
        description = st.text_area(
            "식당 특징 및 리뷰", 
            placeholder="예: 홍문관 가성비 맛집으로 정말 최고입니다! 국물이 깔끔하고 맛있어요!",
            height=150
        )
        
        image_file = st.file_uploader(
            "📷 직접 찍은 사진 첨부 (JPEG, PNG 지원)", 
            type=["jpg", "jpeg", "png"],
            help="업로드한 사진은 자동으로 가로 600px 크기로 리사이징 및 70% 최적화 압축되어 DB에 저장됩니다."
        )
        
        nickname = st.text_input(
            "작성자 닉네임 (선택)", 
            placeholder="기본값: 홍대생 (예: 와우)",
            value="홍대생"
        )
        
        password = st.text_input(
            "삭제 비밀번호 (4자리)", 
            placeholder="예: 1234",
            type="password",
            max_chars=4,
            help="이 추천글을 추후에 직접 삭제하고 싶을 때 필요한 비밀번호입니다. 꼭 기억해 두세요!"
        )
        
        # 제출 버튼
        submit_btn = st.button("🚀 맛집 정보 등록하기", use_container_width=True)
        
    with col_preview:
        st.markdown("#### 👁️ 실시간 등록 카드 미리보기")
        
        # 이미지 프리뷰 인코딩
        temp_img_base64 = None
        if image_file:
            try:
                # 업로드된 파일 내용을 임시 Base64 스트링으로 변경하여 화면에 직접 렌더링
                temp_img_base64 = base64.b64encode(image_file.getvalue()).decode('utf-8')
            except:
                pass
                
        # 카드 렌더링
        img_tag_preview = ""
        if temp_img_base64:
            img_tag_preview = f'<img class="food-card-img" src="data:image/jpeg;base64,{temp_img_base64}" alt="미리보기">'
        else:
            if category == "식당":
                img_tag_preview = f'<div class="food-card-no-img">🍕</div>'
            else:
                img_tag_preview = f'<div class="cafe-card-no-img">☕</div>'
                
        preview_name = name if name else "가게 이름이 들어갑니다"
        preview_menu = menu if menu else "대표 메뉴가 들어갑니다"
        preview_desc = description if description else "이곳에 작성된 특징 및 생생한 리뷰 한줄평이 들어갑니다."
        preview_nickname = nickname if nickname else "홍대생"
        
        badge_preview_cls = "badge-restaurant" if category == "식당" else "badge-cafe"
        desc_border_preview_cls = "food-card-desc" if category == "식당" else "food-card-desc cafe-card-desc"
        
        preview_card_html = f"""
        <div class="food-card">
            {img_tag_preview}
            <div class="food-card-content">
                <div class="food-card-header">
                    <span class="{badge_preview_cls}">{category}</span>
                    <span class="rating-stars">{"★" * rating}</span>
                </div>
                <div class="food-card-title">{preview_name}</div>
                <div class="food-card-menu">📌 추천 메뉴: {preview_menu}</div>
                <div class="food-card-price">💸 가격: {price:,}원</div>
                <div class="{desc_border_preview_cls}">{preview_desc}</div>
                <div class="food-card-footer">
                    <span>👤 {preview_nickname}</span>
                    <span>📅 2026-06-21 (오늘)</span>
                </div>
            </div>
        </div>
        """
        st.markdown(preview_card_html, unsafe_allow_html=True)
        
    # 제출 액션 처리
    if submit_btn:
        if not name.strip():
            st.error("가게 이름을 정확히 입력해주세요!")
        elif not menu.strip():
            st.error("추천 메뉴명을 입력해주세요!")
        elif not description.strip():
            st.error("식당의 특징이나 짧은 평을 입력해 주세요!")
        else:
            with st.spinner("맛집 데이터를 데이터베이스에 기록하고 있습니다..."):
                database.add_recommendation(
                    category=category,
                    name=name,
                    menu=menu,
                    price=price,
                    description=description,
                    rating=rating,
                    image_file=image_file,
                    nickname=nickname,
                    password=password
                )
            st.balloons()
            show_registration_success_dialog(name)
