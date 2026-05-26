import streamlit as st 

"""
# 비지니스 모델 분석

[네이버](http://www.naver.com)  
[홍익대학교](http://hongik.ac.kr)

이것이 일반 본문 **이것이 굵은 글씨** *이것이 기울임 글씨* ~~이것이 취소선~~  
:red[빨간색 글씨]

```python
impotr streamlit as st

print("코드 블록")

"""

st.caption('캡션(작고 흐린 글씨로 표현됨):st.caption()')

with st.echo():
    # 이 블록의 코드와 결과를 출력
    name="Daeun Kim"
    st.write("Hello, Streamlit!",name)

st.latex('\int_a^b f(x)dx')   
"$$\int_a^b f(x)dx$$"

'#### :orange[이미지 : st.image()]'
st.image("./data2/파이썬.png", caption="파이썬 로고", width=500)

'#### :orange[오디오 : st.audio()]'
st.audio("./data2/음악.mp3", format="audio/mpeg", loop=True)

'#### :orange[동영상 : st.audio()]'
# 'rb' : 바이너리 모드로 파일 열기
video_file = open("./data2/흑백영상.mp4", "rb")
video_bytes = video_file.read()

st.video(video_bytes)

st.divider() # 구분선
