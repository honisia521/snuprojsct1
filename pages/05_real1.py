import requests
import json
import streamlit as st
from googletrans import Translator
import os

# --- 1. secrets.toml에서 API 열쇠 가져오기 ---
if os.getenv("STREAMLIT_CLOUD"):
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
else:
    client_id = st.secrets["twitch"]["client_id"]
    client_secret = st.secrets["twitch"]["client_secret"]


# --- 2. 임시 열쇠(Access Token)를 받는 함수 (한 시간 동안 캐싱) ---
@st.cache_data(ttl=3600)
def get_access_token():
    twitch_token_url = "https://id.twitch.tv/oauth2/token"
    token_params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    try:
        token_response = requests.post(twitch_token_url, params=token_params)
        token_response.raise_for_status()
        return token_response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Access Token을 가져오는 데 실패했습니다. 키를 확인해주세요: {e}")
        return None

# --- 3. 사용자 입력 한글을 영어로 번역하는 함수 ---
def translate_to_english(text):
    if not text:
        return ""
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest='en').text
        return translated_text
    except Exception as e:
        st.warning(f"번역 오류: {e}")
        return text

# --- 4. Streamlit 앱 UI 구성 ---
st.set_page_config(layout="wide", page_title="궁극의 게임 추천기")
st.title("🎮 궁극의 게임 추천기")
st.write("Twitch IGDB API를 활용하여 게임 정보를 검색하고 추천해 드립니다.")
st.markdown("""
    <style>
    .game-card { border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); background-color: #f9f9f9; }
    .game-title { color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# 메인 콘텐츠 영역과 사이드바 분리 (왼쪽 사이드바)
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.header("🎯 추천 필터 및 방식")
    st.markdown("---")
    recommendation_mode = st.radio(
        "어떤 방식으로 추천받으시겠어요?",
        ("필터로 게임 탐색", "이 게임과 비슷한 게임 찾기"),
        index=0
    )
    st.markdown("---")

    if recommendation_mode == "필터로 게임 탐색":
        st.subheader("🔍 API 게임 필터링")
        st.warning("🚨 한글 검색 시 번역 오류로 인해 정확한 결과가 나오지 않을 수 있습니다.")
        
        user_query = st.text_input("게임 이름을 입력하세요:", placeholder="예: GTA V 또는 스타듀 밸리")

        # 필터링을 위한 드롭다운 및 슬라이더
        GENRES = ["Action", "Adventure", "Role-playing (RPG)", "Strategy", "Simulation", "Sports", "Puzzle", "Shooter", "Fighting", "Racing", "Arcade"]
        selected_genres = st.multiselect("장르를 선택하세요:", GENRES)

        GAME_MODES = ["Single player", "Multiplayer", "Co-operative", "Massively Multiplayer Online (MMO)"]
        selected_modes = st.multiselect("플레이어 모드를 선택하세요:", GAME_MODES)

        min_rating = st.slider("최소 평점을 선택하세요 (100점 만점):", 0, 100, 75)

        # IGDB API 요청
        access_token = get_access_token()
        if access_token:
            if user_query or selected_genres or selected_modes or min_rating > 0:
                english_query = translate_to_english(user_query)
                st.write(f"**'{user_query}'**를 영어로 번역: **'{english_query}'**")

                igdb_url = "https://api.igdb.com/v4/games"
                headers = {
                    "Client-ID": client_id,
                    "Authorization": f"Bearer {access_token}"
                }
                
                filters = []
                if user_query:
                    filters.append(f'search "{english_query}"')
                if selected_genres:
                    genre_filter = " | ".join([f'genres.name = "{g}"' for g in selected_genres])
                    filters.append(f'where ({genre_filter})')
                if selected_modes:
                    mode_filter = " | ".join([f'game_modes.name = "{m}"' for m in selected_modes])
                    filters.append(f'where ({mode_filter})')
                if min_rating > 0:
                    filters.append(f'where rating > {min_rating}')

                query_body = f'fields name, genres.name, summary, rating, cover.url, game_modes.name; {" & ".join(filters)}; limit 10;'

                try:
                    igdb_response = requests.post(igdb_url, headers=headers, data=query_body)
                    igdb_response.raise_for_status()
                    games = igdb_response.json()
                except requests.exceptions.RequestException as e:
                    st.error(f"API 요청 오류: {e}")
                    games = []

            else:
                games = []

    elif recommendation_mode == "이 게임과 비슷한 게임 찾기":
        st.subheader("💖 선호 게임 기반 추천")
        st.info("이 기능은 데이터셋 기반의 추천이 필요합니다. API를 활용한 추천 기능을 직접 개발하거나 기존 데이터를 사용해 구현할 수 있습니다.")
        games = []

with col_main:
    st.header(f"✨ {recommendation_mode} 결과")
    
    # 결과 표시
    if 'games' in locals() and games:
        for game in games:
            st.markdown(f'<div class="game-card">', unsafe_allow_html=True)
            st.markdown(f'<h3 class="game-title">{game.get("name", "이름 없음")}</h3>', unsafe_allow_html=True)
            
            genres = game.get('genres')
            if genres:
                genre_names = [genre.get('name') for genre in genres]
                st.write(f"**장르:** {', '.join(genre_names)}")
            
            modes = game.get('game_modes')
            if modes:
                mode_names = [mode.get('name') for mode in modes]
                st.write(f"**플레이어 모드:** {', '.join(mode_names)}")
            
            st.write(f"**줄거리:** {game.get('summary', '줄거리 정보가 없습니다.')}")
            
            rating = game.get('rating')
            if rating:
                stars = int(round(rating / 20))
                st.write(f"**평점:** {'⭐' * stars} ({rating:.1f}/100점)")
            st.markdown(f'</div>', unsafe_allow_html=True)
    elif recommendation_mode == "필터로 게임 탐색":
        st.info("선택한 조건에 맞는 게임이 없거나, 검색을 시작하지 않았습니다.")

st.sidebar.markdown("---")
st.sidebar.info("이 추천기는 여러분의 게임 탐색을 돕기 위해 만들어졌습니다.")
