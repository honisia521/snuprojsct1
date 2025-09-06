# /mount/src/snuprojsct1/pages/01_AI추천.py

# 이 줄이 코드의 맨 위에 있어야 합니다.
import streamlit as st 

# 이제 이 줄이 올바르게 작동할 겁니다.
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
...

# pages/gemini_recommender.py

import streamlit as st
import pandas as pd # 게임 목록 표시용
import google.generativeai as genai # Gemini API 사용

# Google AI Studio API Key 설정
# 실제 서비스에서는 st.secrets["GEMINI_API_KEY"] 와 같이 사용하세요.
# https://aistudio.google.com/app/apikey 에서 발급받을 수 있습니다.
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # <-- 여기에 실제 API 키를 입력해주세요!

genai.configure(api_key=GEMINI_API_KEY)

# --- 게임 데이터 (참고용으로 가져옴, 실제 API 호출에는 직접 사용되지 않을 수 있음) ---
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요."},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임."},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요."},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요."},
    "어몽 어스": {"장르": "추리", "난이도": "하", "플레이어 수": "멀티", "평점": 3.9, "설명": "우주선 안의 임포스터를 찾아내는 마피아 게임."},
    "젤다의 전설 브레스 오브 더 와일드": {"장르": "액션 어드벤처", "난이도": "중", "플레이어 수": "싱글", "평점": 4.9, "설명": "광활한 하이랄을 탐험하며 미스터리를 풀어가는 오픈월드 어드벤처."},
    "폴가이즈": {"장르": "파티", "난이도": "하", "플레이어 수": "멀티", "평점": 3.7, "설명": "엉뚱한 장애물 코스를 통과하는 캐주얼 배틀 로얄."},
    "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG."},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요."},
    "오버워치 2": {"장르": "FPS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.3, "설명": "영웅 기반의 팀 대전 FPS. 다양한 영웅과 전략으로 목표를 달성하세요."},
    "로스트아크": {"장르": "MMORPG", "난이도": "중", "플레이어 수": "멀티", "평점": 4.4, "설명": "방대한 세계관과 화려한 액션의 MMORPG.", "태그": "판타지, 핵앤슬래시, MMORPG, 스토리, 레이드, 성장"},
    "발로란트": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.2, "설명": "정교한 총격전과 요원 스킬을 활용하는 전략 FPS.", "태그": "전략 슈터, FPS, e스포츠, 무료, 멀티플레이어"},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG.", "태그": "다크 판타지, 핵앤슬래시, RPG, 파밍, 액션, 스토리"}
}
df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

# 모델 초기화
model = genai.GenerativeModel('gemini-pro') # 또는 'gemini-1.0-pro'

st.set_page_config(layout="wide", page_title="AI 기반 추천")

st.title("✨ AI 기반 게임 추천 (Powered by Gemini)")
st.markdown("""
    <style>
    .game-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        background-color: #f9f9f9;
    }
    .game-title {
        color: #007BFF; /* AI 추천을 위한 다른 색상 */
    }
    </style>
    """, unsafe_allow_html=True)
st.write("좋아하는 게임이나 원하는 게임 스타일을 알려주세요. Gemini AI가 당신을 위한 새로운 게임을 추천해 드립니다!")

# --- 사용자 입력 방식 선택 ---
recommendation_type = st.radio(
    "어떤 방식으로 추천받으시겠어요?",
    ("선호 게임 선택", "자유로운 텍스트 설명"),
    index=0
)

recommended_games_from_gemini = []

if recommendation_type == "선호 게임 선택":
    selected_game = st.selectbox(
        "좋아하는 게임을 선택해주세요:",
        ['--선택--', *sorted(df_games.index.tolist())],
        key="gemini_rec_game_select"
    )
    if selected_game != '--선택--':
        st.info(f"'{selected_game}'와(과) 비슷한 게임을 추천해 드릴게요!")
        prompt_input = f"다음 게임과 비슷한 게임 3개를 추천해 주세요: {selected_game}. 추천 게임은 게임 이름, 장르, 1~2문장의 간략한 설명 형식으로 한국어로 제시해 주세요. 그리고 설명은 흥미롭게 작성해주세요."
        if st.button("AI 추천받기 (선호 게임)", key="btn_gemini_game_rec"):
            with st.spinner("Gemini AI가 게임을 추천 중입니다..."):
                try:
                    response = model.generate_content(prompt_input)
                    recommended_games_from_gemini = response.text
                except Exception as e:
                    st.error(f"AI 추천 중 오류가 발생했습니다: {e}")
                    st.warning("API 키가 올바른지, 또는 요청 내용이 너무 길거나 부적절하지 않은지 확인해주세요.")
            if recommended_games_from_gemini:
                st.subheader("💡 Gemini AI의 추천!")
                st.markdown(recommended_games_from_gemini) # API 응답을 그대로 마크다운으로 표시

elif recommendation_type == "자유로운 텍스트 설명":
    user_description = st.text_area(
        "어떤 종류의 게임을 찾으시나요? (예: '스토리가 깊고 판타지 세계를 탐험하는 RPG', '친구들과 같이 즐길 수 있는 캐주얼한 파티 게임')",
        height=100,
        key="gemini_rec_text_input"
    )
    if st.button("AI 추천받기 (텍스트 설명)", key="btn_gemini_text_rec"):
        if user_description:
            st.info(f"'{user_description}' 설명에 맞는 게임을 찾아볼게요!")
            prompt_input = f"다음 설명을 바탕으로 게임 3개를 추천해 주세요: '{user_description}'. 추천 게임은 게임 이름, 장르, 1~2문장의 간략한 설명 형식으로 한국어로 제시해 주세요. 그리고 설명은 흥미롭게 작성해주세요."
            with st.spinner("Gemini AI가 게임을 추천 중입니다..."):
                try:
                    response = model.generate_content(prompt_input)
                    recommended_games_from_gemini = response.text
                except Exception as e:
                    st.error(f"AI 추천 중 오류가 발생했습니다: {e}")
                    st.warning("API 키가 올바른지, 또는 요청 내용이 너무 길거나 부적절하지 않은지 확인해주세요.")
            if recommended_games_from_gemini:
                st.subheader("💡 Gemini AI의 추천!")
                st.markdown(recommended_games_from_gemini) # API 응답을 그대로 마크다운으로 표시
        else:
            st.warning("게임 스타일을 설명해주세요!")

st.sidebar.markdown("---")
st.sidebar.info("Gemini AI를 활용한 더 유연한 게임 추천을 경험해보세요.")
