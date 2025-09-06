import streamlit as st
import pandas as pd
from openai import OpenAI

# --- OpenAI 클라이언트 초기화 ---
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. Streamlit Secrets를 확인하세요.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- 샘플 게임 데이터 ---
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요."},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임."},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요."},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요."},
    "어몽 어스": {"장르": "추리", "난이도": "하", "플레이어 수": "멀티", "평점": 3.9, "설명": "우주선 안의 임포스터를 찾아내는 마피아 게임."},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요."},
    "로스트아크": {"장르": "MMORPG", "난이도": "중", "플레이어 수": "멀티", "평점": 4.4, "설명": "방대한 세계관과 화려한 액션의 MMORPG."},
    "발로란트": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.2, "설명": "정교한 총격전과 요원 스킬을 활용하는 전략 FPS."},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG."}
}
df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

st.set_page_config(layout="wide", page_title="AI 기반 게임 추천 (OpenAI)")

st.title("🎮 AI 기반 게임 추천 (OpenAI)")
st.write("좋아하는 게임이나 원하는 스타일을 입력하면 OpenAI가 추천해드립니다!")

# --- 사용자 입력 방식 선택 ---
recommendation_type = st.radio(
    "추천 방식 선택:",
    ("선호 게임 선택", "자유로운 텍스트 설명"),
    index=0
)

recommended_games = ""

# --- 캐시된 추천 함수 ---
@st.cache_data(show_spinner=False)
def get_recommendation(prompt_text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 유능한 게임 큐레이터야."},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

# --- 추천 처리 ---
if recommendation_type == "선호 게임 선택":
    selected_game = st.selectbox(
        "좋아하는 게임을 선택하세요:",
        ['--선택--', *sorted(df_games.index.tolist())],
        key="game_select"
    )
    if selected_game != '--선택--':
        st.info(f"'{selected_game}'와 비슷한 게임을 추천해드릴게요!")
        if st.button("AI 추천받기 (선호 게임)"):
            prompt = f"'{selected_game}'와 비슷한 게임 3개를 추천해줘. 이름, 장르, 1~2문장 설명을 한국어로."
            with st.spinner("추천 중..."):
                recommended_games = get_recommendation(prompt)
            st.subheader("💡 OpenAI 추천 결과")
            st.markdown(recommended_games)

elif recommendation_type == "자유로운 텍스트 설명":
    user_desc = st.text_area(
        "원하는 게임 스타일을 설명해주세요:",
        height=100,
        key="text_input"
    )
    if st.button("AI 추천받기 (텍스트 설명)"):
        if user_desc.strip():
            st.info(f"'{user_desc}' 스타일에 맞는 게임을 추천합니다!")
            prompt = f"'{user_desc}' 스타일의 게임 3개를 추천해줘. 이름, 장르, 1~2문장 설명을 한국어로."
            with st.spinner("추천 중..."):
                recommended_games = get_recommendation(prompt)
            st.subheader("💡 OpenAI 추천 결과")
            st.markdown(recommended_games)
        else:
            st.warning("게임 스타일을 입력해주세요!")
