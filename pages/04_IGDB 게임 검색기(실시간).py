import streamlit as st
import requests
import json
import os
from googletrans import Translator
import asyncio

# --- 1. secrets.toml에서 IGDB/Twitch API 열쇠 가져오기 ---
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
translator = Translator()

async def translate_korean_to_english_async(text):
    """비동기 방식으로 한국어를 영어로 번역하는 함수"""
    try:
        if any('\uac00' <= char <= '\ud7a3' for char in text):
            result = await asyncio.to_thread(translator.translate, text, dest='en')
            return result.text
    except Exception as e:
        st.warning(f"번역 중 오류가 발생했습니다: {e}")
    return text

def translate_korean_to_english(text):
    """동기 방식으로 비동기 함수를 실행하는 래퍼 함수"""
    return asyncio.run(translate_korean_to_english_async(text))

# --- 4. Streamlit 앱 UI 구성 ---
st.title("🎮 IGDB 게임 검색기")
st.markdown("궁금한 게임의 이름을 입력하거나, 옆의 필터들을 사용해 보세요.")
st.markdown("""
    <style>
    .game-card { border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); background-color: #f9f9f9; }
    .game-title { color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# 메인 콘텐츠 영역과 사이드바 분리 (왼쪽 사이드바)
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.header("🎯 게임 필터링")
    st.markdown("---")

    game_name = st.text_input("게임 이름 검색 (한글/영어)", placeholder="예: The Witcher 3 또는 The Witcher")
    st.caption("🚨 한글 검색 시 번역 오류로 인해 정확한 결과가 나오지 않을 수 있습니다.")

    # IGDB의 장르 목록 (더 다양함)
    GENRES = ["Action", "Adventure", "Role-playing (RPG)", "Strategy", "Simulation", "Sports", "Shooter", "Puzzle", "Arcade"]
    selected_genres = st.multiselect("장르를 선택하세요:", GENRES)

    # IGDB의 게임 모드 목록
    GAME_MODES = ["Single player", "Multiplayer", "Co-operative", "Massively Multiplayer Online (MMO)"]
    selected_modes = st.multiselect("플레이어 모드를 선택하세요:", GAME_MODES)

    min_rating = st.slider("최소 평점 (100점 만점)", min_value=0, max_value=100, value=75)

    st.markdown("---")
    search_button = st.button("검색 시작")

# --- 5. 검색 로직 실행 및 결과 표시 ---
with col_main:
    st.header("✨ 검색 결과")
    
    if search_button:
        access_token = get_access_token()
        if access_token:
            igdb_url = "https://api.igdb.com/v4/games"
            headers = {
                "Client-ID": client_id,
                "Authorization": f"Bearer {access_token}"
            }

            filters = []
            if game_name:
                translated_game_name = translate_korean_to_english(game_name)
                filters.append(f'search "{translated_game_name}"')
            
            if selected_genres:
                genre_filter = " | ".join([f'genres.name = "{g}"' for g in selected_genres])
                filters.append(f'where ({genre_filter})')
            
            if selected_modes:
                mode_filter = " | ".join([f'game_modes.name = "{m}"' for m in selected_modes])
                filters.append(f'where ({mode_filter})')
            
            if min_rating > 0:
                filters.append(f'where rating > {min_rating}')

            query_body = f'fields name, genres.name, summary, rating, cover.url, game_modes.name; {" & ".join(filters)}; limit 10;'

            if filters:
                try:
                    response = requests.post(igdb_url, headers=headers, data=query_body)
                    response.raise_for_status()
                    games = response.json()

                    if games:
                        st.subheader("🎲 검색 결과입니다:")
                        for game in games:
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if game.get("cover") and game["cover"].get("url"):
                                    # RAWG와 IGDB는 이미지 URL 형식이 다름.
                                    # IGDB는 '//'로 시작하므로 'https:'를 추가해야 함.
                                    image_url = f"https:{game['cover']['url']}"
                                    st.image(image_url, width=100)
                                else:
                                    st.write("이미지 없음")
                            
                            with col2:
                                st.markdown(f'<h3 class="game-title">{game["name"]}</h3>', unsafe_allow_html=True)
                                
                                genres = game.get('genres')
                                if genres:
                                    genre_names = [g.get('name') for g in genres]
                                    st.write(f"**장르:** {', '.join(genre_names)}")
                                
                                modes = game.get('game_modes')
                                if modes:
                                    mode_names = [m.get('name') for m in modes]
                                    st.write(f"**플레이어 모드:** {', '.join(mode_names)}")
                                
                                rating = game.get('rating')
                                if rating:
                                    stars = int(round(rating / 20))
                                    st.write(f"**평점:** {'⭐' * stars} ({rating:.1f}/100점)")
                                else:
                                    st.write(f"**평점:** 정보 없음")

                                st.markdown("---")
                    else:
                        st.info("선택한 조건에 맞는 게임이 없습니다. 게임명을 더 구체적으로 입력하거나, 다른 필터를 사용해보세요.")

                except requests.exceptions.RequestException as e:
                    st.error(f"API 요청 중 오류가 발생했습니다: {e}")
            else:
                st.warning("검색할 게임 이름을 입력하거나, 필터를 사용해 주세요.")
    else:
        st.info("왼쪽 사이드바에서 조건을 선택하고 '검색 시작' 버튼을 눌러주세요.")

st.sidebar.markdown("---")
st.sidebar.info("이 추천기는 여러분의 게임 탐색을 돕기 위해 만들어졌습니다.")
