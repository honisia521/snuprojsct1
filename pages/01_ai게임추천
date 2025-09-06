# pages/gemini_recommender.py

import streamlit as st
import pandas as pd
import google.generativeai as genai
import time # 로딩 애니메이션을 위해 추가

# --- 1. Google AI Studio API Key 설정 ---
# 제공해주신 API 키가 여기에 바로 적용됩니다.
GEMINI_API_KEY = "AIzaSyDXCnqOT3WchGYEwV7DVx4MR-IVG0dzs9U"

# API 키가 설정되었는지 확인 (이 부분은 이제 항상 통과됩니다)
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    st.error("⚠️ Gemini API 키를 설정해주세요! `pages/gemini_recommender.py` 파일에서 'YOUR_GEMINI_API_KEY'를 실제 키로 변경해야 합니다.")
    st.stop() # API 키가 없으면 앱 실행을 중단합니다.

genai.configure(api_key=GEMINI_API_KEY)

# --- 2. 게임 데이터 (예시) ---
# 실제 서비스에서는 데이터베이스나 파일에서 로드할 수 있습니다.
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요.", "태그": "MOBA, 전략, 팀플레이, 경쟁"},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임.", "태그": "배틀로얄, 슈터, 생존, 멀티플레이어"},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요.", "태그": "샌드박스, 건축, 탐험, 창의성"},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요.", "태그": "RTS, 전략, SF, e스포츠"},
    "어몽 어스": {"장르": "추리", "난이도": "하", "플레이어 수": "멀티", "평점": 3.9, "설명": "우주선 안의 임포스터를 찾아내는 마피아 게임.", "태그": "마피아, 추리, 파티, 협동"},
    "젤다의 전설 브레스 오브 더 와일드": {"장르": "액션 어드벤처", "난이도": "중", "플레이어 수": "싱글", "평점": 4.9, "설명": "광활한 하이랄을 탐험하며 미스터리를 풀어가는 오픈월드 어드벤처.", "태그": "오픈월드, 어드벤처, 액션, 탐험, 스토리"},
    "폴가이즈": {"장르": "파티", "난이도": "하", "플레이어 수": "멀티", "평점": 3.7, "설명": "엉뚱한 장애물 코스를 통과하는 캐주얼 배틀 로얄.", "태그": "파티, 캐주얼, 배틀로얄, 레이싱"},
    "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG.", "태그": "RPG, 오픈월드, SF, 액션, 스토리"},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요.", "태그": "액션RPG, 다크판타지, 고난이도, 탐험, 스토리"},
    "오버워치 2": {"장르": "FPS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.3, "설명": "영웅 기반의 팀 대전 FPS. 다양한 영웅과 전략으로 목표를 달성하세요.", "태그": "FPS, 팀대전, 영웅슈터, 경쟁, e스포츠"},
    "로스트아크": {"장르": "MMORPG", "난이도": "중", "플레이어 수": "멀티", "평점": 4.4, "설명": "방대한 세계관과 화려한 액션의 MMORPG.", "태그": "판타지, 핵앤슬래시, MMORPG, 스토리, 레이드, 성장"},
    "발로란트": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.2, "설명": "정교한 총격전과 요원 스킬을 활용하는 전략 FPS.", "태그": "전략 슈터, FPS, e스포츠, 무료, 멀티플레이어"},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG.", "태그": "다크 판타지, 핵앤슬래시, RPG, 파밍, 액션, 스토리"},
    "페르소나 5 로열": {"장르": "JRPG", "난이도": "하", "플레이어 수": "싱글", "평점": 4.9, "설명": "낮에는 고등학생, 밤에는 괴도로 활동하며 정의를 실현하는 스타일리쉬 RPG.", "태그": "JRPG, 스토리, 턴제, 시뮬레이션, 학원생활"},
    "원신": {"장르": "오픈월드 액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.6, "설명": "광활한 티바트 대륙을 탐험하며 원소 마법을 사용하는 오픈월드 액션 RPG.", "태그": "오픈월드, 액션RPG, 판타지, 가챠, 탐험"}
}
df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

# --- 3. Gemini 모델 초기화 ---
# 'gemini-pro'는 가장 안정적인 텍스트 생성 모델입니다.
model = genai.GenerativeModel('gemini-pro')

# --- 4. Streamlit 페이지 설정 ---
st.set_page_config(layout="wide", page_title="AI 기반 게임 추천")

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
        color: #007BFF; /* 추천 게임 제목 색상 */
        font-size: 1.2em;
        font-weight: bold;
    }
    .st-emotion-cache-nahz7x { /* Streamlit main content padding */
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
st.write("좋아하는 게임이나 원하는 게임 스타일을 알려주세요. Gemini AI가 당신을 위한 새로운 게임을 추천해 드립니다!")

# --- 5. 사용자 입력 방식 선택 ---
recommendation_type = st.radio(
    "어떤 방식으로 추천받으시겠어요?",
    ("선호 게임 선택", "자유로운 텍스트 설명"),
    index=0,
    key="rec_type_radio"
)

# 추천 결과를 저장할 변수 초기화
recommended_games_from_gemini = ""

if recommendation_type == "선호 게임 선택":
    selected_game = st.selectbox(
        "좋아하는 게임을 선택해주세요:",
        ['--선택--', *sorted(df_games.index.tolist())], # 게임 목록을 알파벳순으로 정렬
        key="gemini_rec_game_select"
    )
    if selected_game != '--선택--':
        st.info(f"'{selected_game}'와(과) 비슷한 게임을 추천해 드릴게요!")
        # 프롬프트 구성: 선택한 게임의 상세 정보를 포함하여 더 정확한 추천 유도
        game_info = games.get(selected_game, {})
        prompt_details = f"장르: {game_info.get('장르', '정보 없음')}, 난이도: {game_info.get('난이도', '정보 없음')}, 설명: {game_info.get('설명', '정보 없음')}, 태그: {game_info.get('태그', '정보 없음')}"

        prompt_input = f"""
        다음 게임 정보와 비슷한 특징을 가진 게임 3개를 추천해 주세요.
        ---
        기존 게임: {selected_game}
        게임 정보: {prompt_details}
        ---
        
        추천 게임은 다음 형식으로 한국어로 제시해 주세요:
        각 추천 게임은 '- [게임 이름] (장르): 1~2문장의 간략하고 흥미로운 설명' 형식으로 작성해 주세요.
        예시:
        - [사이버펑크 2077] (RPG): 미래 도시 나이트 시티에서 자유롭게 탐험하며, 사이버펑크 세계관에 푹 빠져볼 수 있는 거대한 오픈월드 RPG입니다.
        - [엘든 링] (액션 RPG): 광활한 필드와 강력한 보스들이 기다리는 다크 판타지 액션 RPG의 정수입니다.
        - [원신] (오픈월드 액션 RPG): 아름다운 티바트 대륙을 탐험하며 원소 마법을 활용한 역동적인 전투를 즐겨보세요.
        """
        
        if st.button("AI 추천받기 (선호 게임)", key="btn_gemini_game_rec"):
            with st.spinner("✨ Gemini AI가 당신을 위한 게임을 찾고 있습니다..."):
                try:
                    # Gemini API 호출
                    response = model.generate_content(prompt_input)
                    recommended_games_from_gemini = response.text
                except Exception as e:
                    st.error(f"AI 추천 중 오류가 발생했습니다: {e}")
                    if "403 Permission denied" in str(e) or "API key not valid" in str(e):
                        st.warning("🚨 API 키가 올바르지 않거나 권한이 없습니다. 키를 다시 확인해주세요.")
                    else:
                        st.warning("🌐 네트워크 문제 또는 요청 내용이 너무 길거나 부적절하지 않은지 확인해주세요.")
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
            prompt_input = f"""
            다음 설명을 바탕으로 게임 3개를 추천해 주세요: '{user_description}'
            
            추천 게임은 다음 형식으로 한국어로 제시해 주세요:
            각 추천 게임은 '- [게임 이름] (장르): 1~2문장의 간략하고 흥미로운 설명' 형식으로 작성해 주세요.
            예시:
            - [사이버펑크 2077] (RPG): 미래 도시 나이트 시티에서 자유롭게 탐험하며, 사이버펑크 세계관에 푹 빠져볼 수 있는 거대한 오픈월드 RPG입니다.
            - [엘든 링] (액션 RPG): 광활한 필드와 강력한 보스들이 기다리는 다크 판타지 액션 RPG의 정수입니다.
            - [원신] (오픈월드 액션 RPG): 아름다운 티바트 대륙을 탐험하며 원소 마법을 활용한 역동적인 전투를 즐겨보세요.
            """
            with st.spinner("✨ Gemini AI가 당신을 위한 게임을 찾고 있습니다..."):
                try:
                    # Gemini API 호출
                    response = model.generate_content(prompt_input)
                    recommended_games_from_gemini = response.text
                except Exception as e:
                    st.error(f"AI 추천 중 오류가 발생했습니다: {e}")
                    if "403 Permission denied" in str(e) or "API key not valid" in str(e):
                        st.warning("🚨 API 키가 올바르지 않거나 권한이 없습니다. 키를 다시 확인해주세요.")
                    else:
                        st.warning("🌐 네트워크 문제 또는 요청 내용이 너무 길거나 부적절하지 않은지 확인해주세요.")
            if recommended_games_from_gemini:
                st.subheader("💡 Gemini AI의 추천!")
                st.markdown(recommended_games_from_gemini) # API 응답을 그대로 마크다운으로 표시
        else:
            st.warning("어떤 종류의 게임을 찾으시는지 설명해주세요!")

st.sidebar.markdown("---")
st.sidebar.info("Gemini AI를 활용한 더 유연한 게임 추천을 경험해보세요.")
st.sidebar.markdown("Made with ❤️ by Your Name") # 여기에 당신의 이름을 넣으세요!
