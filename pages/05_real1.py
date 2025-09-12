import streamlit as st
import requests
import urllib.parse
from googletrans import Translator
import asyncio

# --- 1. RAWG API 키 불러오기 ---
# secrets.toml 파일에서 RAWG API 키를 불러옵니다.
rawg_api_key = st.secrets["rawg_api_key"]

# --- 2. 비동기 번역 함수 ---
translator = Translator()

async def translate_korean_to_english_async(text):
    """비동기 방식으로 한국어를 영어로 번역하는 함수"""
    try:
        if any('\uac00' <= char <= '\ud7a3' for char in text):
            result = await asyncio.to_thread(translator.translate, text, dest='en')
            return result.text
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {e}")
    return text

def translate_korean_to_english(text):
    """동기 방식으로 비동기 함수를 실행하는 래퍼 함수"""
    return asyncio.run(translate_korean_to_english_async(text))

# --- 3. Streamlit 앱 UI 구성 ---
st.set_page_config(layout="wide", page_title="궁극의 RAWG 게임 검색기")
st.title("🎮 궁극의 RAWG 게임 검색기")
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

    # 검색 텍스트 입력창
    game_name = st.text_input("게임 이름 검색 (한글/영어)", placeholder="예: GTA V 또는 그랜드")
    st.caption("🚨 한글 검색 시 번역 오류로 인해 정확한 결과가 나오지 않을 수 있습니다.")

    # 플레이어 수 선택
    player_tags = {
        "모두": "",
        "싱글플레이": "singleplayer",
        "멀티플레이": "multiplayer"
    }
    selected_player_korean = st.selectbox("플레이어 수", list(player_tags.keys()))

    # 장르 선택
    genre_list = {
        "액션": "action", "인디": "indie", "어드벤처": "adventure", "RPG": "role-playing-games-rpg",
        "전략": "strategy", "슈팅": "shooter", "캐주얼": "casual", "시뮬레이션": "simulation",
        "퍼즐": "puzzle", "아케이드": "arcade", "레이싱": "racing", "스포츠": "sports"
    }
    selected_genre_korean = st.selectbox("장르", ["선택 안 함"] + list(genre_list.keys()))
    
    # 최소 별점 슬라이더
    min_rating = st.slider("최소 별점", min_value=0.0, max_value=5.0, value=0.0, step=0.1)

    st.markdown("---")
    search_button = st.button("검색 시작")

# --- 4. 검색 로직 실행 및 결과 표시 ---
with col_main:
    st.header("✨ 검색 결과")
    
    # 검색 버튼이 눌렸을 때만 API 호출
    if search_button:
        base_url = f"https://api.rawg.io/api/games?key={rawg_api_key}"
        params = {}

        if game_name:
            translated_game_name = translate_korean_to_english(game_name)
            params['search'] = urllib.parse.quote_plus(translated_game_name)

        if selected_genre_korean != "선택 안 함":
            params['genres'] = genre_list[selected_genre_korean]

        if selected_player_korean != "모두":
            params['tags'] = player_tags[selected_player_korean]
            
        if min_rating > 0.0:
            params['metacritic'] = f"{int(min_rating * 20)},100"

        if params:
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()

                data = response.json()
                games = data.get("results", [])

                if games:
                    st.subheader("🎲 검색 결과입니다:")
                    for game in games:
                        col1, col2 = st.columns([1, 4])
                        
                        with col1:
                            if game.get("background_image"):
                                st.image(game["background_image"], width=100)
                            else:
                                st.write("이미지 없음")
                        
                        with col2:
                            st.markdown(f'<h3 class="game-title">{game["name"]}</h3>', unsafe_allow_html=True)
                            st.write(f"**출시일:** {game.get('released', '정보 없음')}")
                            
                            rating = game.get('rating', '정보 없음')
                            st.write(f"**평점:** {rating} / 5.0")
                            
                            platforms = [p['platform']['name'] for p in game.get('platforms', []) if p.get('platform')]
                            if platforms:
                                st.write(f"**플랫폼:** {', '.join(platforms)}")
                            else:
                                st.write("**플랫폼:** 정보 없음")
                            
                            genres = [genre['name'] for genre in game.get('genres', []) if genre]
                            if genres:
                                st.write(f"**장르:** {', '.join(genres)}")
                            else:
                                st.write("**장르:** 정보 없음")

                            st.markdown("---")
                else:
                    st.info("검색 결과가 없습니다. 다른 필터를 사용해보세요.")
            
            except requests.exceptions.RequestException as e:
                st.error(f"API 요청 중 오류가 발생했습니다: {e}")
        else:
            st.warning("검색할 게임 이름을 입력하거나, 장르와 별점 필터를 사용해 주세요.")
    else:
        st.info("왼쪽 사이드바에서 조건을 선택하고 '검색 시작' 버튼을 눌러주세요.")

st.sidebar.markdown("---")
st.sidebar.info("이 추천기는 여러분의 게임 탐색을 돕기 위해 만들어졌습니다.")
