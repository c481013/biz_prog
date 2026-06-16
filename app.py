# app.py -- 지점 매출 분석 대시보드 (통합 버전)
import streamlit as st

# =========================================================================
# 1. 계산용 유틸리티 함수 통합 (기존 utils.py의 내용)
# =========================================================================

INCENTIVE_TABLE = {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "F": 0.0}


def total_sales(branch):
    """지점 총매출."""
    return branch["1분기"] + branch["2분기"] + branch["3분기"]


def average_sales(branch):
    """지점 평균."""
    return total_sales(branch) / 3


def to_grade(avg):
    """평균을 등급으로 변환."""
    if avg >= 120:
        return "A"
    elif avg >= 100:
        return "B"
    elif avg >= 80:
        return "C"
    elif avg >= 60:
        return "D"
    else:
        return "F"


def grade_to_incentive(grade):
    """등급을 성과급률로 변환."""
    return INCENTIVE_TABLE[grade]


def quarter_average(branches, quarter):
    """분기 평균."""
    if not branches:
        return 0.0
    total = 0
    for b in branches:
        total += b[quarter]
    return total / len(branches)


def quarter_top(branches, quarter):
    """분기 최고."""
    if not branches:
        return 0
    top = branches[0][quarter]
    for b in branches[1:]:
        if b[quarter] > top:
            top = b[quarter]
    return top


def grade_distribution(branches):
    """등급별 지점 수."""
    dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for b in branches:
        g = to_grade(average_sales(b))
        dist[g] += 1
    return dist


def rank_list(branches):
    """총매출 기준 정렬."""
    return sorted(branches, key=lambda x: total_sales(x), reverse=True)


def achievement_rate(branches, target=90):
    """목표 달성 비율(%)."""
    if not branches:
        return 0.0
    count = 0
    for b in branches:
        if average_sales(b) >= target:
            count += 1
    return count / len(branches) * 100


# =========================================================================
# 2. 대시보드 화면 구성 (기존 app.py의 내용)
# =========================================================================

st.set_page_config(page_title="매출 분석 대시보드", layout="wide")

# 상단 배너 이미지 (banner.png 파일을 함께 둘 것)
# ※ 최신 Streamlit 배포 서버의 규격에 맞게 use_container_width=True를 사용합니다.
st.image("banner (1).png", use_container_width=True)
st.title("지점 매출 분석 대시보드")

QUARTERS = ["1분기", "2분기", "3분기"]

# 처음 실행 시 샘플 지점 데이터를 세션에 넣어 둔다. (다시 실행돼도 유지) / 단위: 백만원
if "branches" not in st.session_state:
    st.session_state.branches = [
        {"지점": "강남점", "1분기": 150, "2분기": 130, "3분기": 140},
        {"지점": "홍대점", "1분기": 90,  "2분기": 110, "3분기": 100},
        {"지점": "판교점", "1분기": 120, "2분기": 100, "3분기": 95},
        {"지점": "부산점", "1분기": 80,  "2분기": 90,  "3분기": 85},
        {"지점": "대전점", "1분기": 50,  "2분기": 55,  "3분기": 45},
    ]

branches = st.session_state.branches

tab1, tab2, tab3, tab4 = st.tabs(["지점 입력", "지점별 실적", "분기별 통계", "순위 & 등급 분포"])

# --- Tab 1 : 지점 추가 ---
with tab1:
    st.header("지점 추가")
    name = st.text_input("지점명")
    q1 = st.number_input("1분기 매출", 0, 1000, 0)
    q2 = st.number_input("2분기 매출", 0, 1000, 0)
    q3 = st.number_input("3분기 매출", 0, 1000, 0)
    if st.button("추가"):
        branches.append({"지점": name, "1분기": q1, "2분기": q2, "3분기": q3})
        st.success(f"{name} 지점을 추가했습니다.")

# --- 상단 요약 지표 ---
col1, col2, col3 = st.columns(3)
col1.metric("지점 수", f"{len(branches)}개")

if len(branches) > 0:
    avgs = [average_sales(b) for b in branches]
    overall = sum(avgs) / len(avgs)
else:
    overall = 0.0
col2.metric("전체 평균(분기)", round(overall, 2))
col3.metric("목표 달성률", f"{achievement_rate(branches):.1f}%")

# --- Tab 2 : 지점별 실적표 ---
with tab2:
    st.header("지점별 실적표")
    table = []
    for b in branches:
        avg = average_sales(b)
        grade = to_grade(avg)
        table.append({
            "지점": b["지점"],
            "1분기": b["1분기"], "2분기": b["2분기"], "3분기": b["3분기"],
            "총매출": total_sales(b),
            "평균": round(avg, 2),
            "등급": grade,
            "성과급률": grade_to_incentive(grade),
        })
    st.table(table)

# --- Tab 3 : 분기별 통계 ---
with tab3:
    st.header("분기별 통계")
    cols = st.columns(3)
    for i in range(len(QUARTERS)):
        quarter = QUARTERS[i]
        with cols[i]:
            st.subheader(quarter)
            st.write("평균: " + str(quarter_average(branches, quarter)))
            st.write(f"최고: {quarter_top(branches, quarter)}")

    chart_data = []
    for quarter in QUARTERS:
        chart_data.append({"분기": quarter, "평균": quarter_average(branches, quarter)})
    st.bar_chart(chart_data, x="분기", y="평균", horizontal=True, height=400)

# --- Tab 4 : 순위 & 등급 분포 ---
with tab4:
    st.header("매출 순위")
    ranked = rank_list(branches)
    rank_table = []
    rank = 1
    for b in ranked:
        rank_table.append({"순위": rank, "지점": b["지점"], "총매출": total_sales(b)})
        rank = rank + 1
    st.table(rank_table)

    st.header("등급 분포")
    dist = grade_distribution(branches)
    dist_data = [{"등급": g, "지점수": dist[g]} for g in ["A", "B", "C", "D", "F"]]
    st.bar_chart(dist_data, x="등급", y="지점수", horizontal=True, height=400)
