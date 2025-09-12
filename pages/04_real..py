import streamlit as st
import requests
import urllib.parse
from googletrans import Translator

# secrets.toml 파일에서 RAWG API 키를 불러옵니다.
rawg_api_key = st.secrets["rawg_api_key"]

# 번역기 객체를 만듭니다.
translator = Translator()

def translate_korean_to_english(text):
    """한국어를 영어로 번역하는 함수"""
    try:
        if any('\uac00' <= char <= '\ud7a3' for char in text):
            result = translator.translate(text, dest='en')
            return result.text
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {e}")
    return text

st.title("🎮 RAWG 게임 검색기")
st.markdown("궁금한 게임의 이름을 입력하거나, 옆의 필터들을 사용해 보세요.")

col1, col2 = st.columns([1, 1])

with col1:
    player_tags = {
        "모두": "",
        "싱글플레이": "singleplayer",
        "멀티플레이": "multiplayer"
    }
    selected_player_korean = st.selectbox("플레이어 수", list(player_tags.keys()))

with col2:
    genre_list = {
        "액션": "action", "인디": "indie", "어드벤처": "adventure", "RPG": "role-playing-games-rpg",
        "전략": "strategy", "슈팅": "shooter", "캐주얼": "casual", "시뮬레이션": "simulation",
        "퍼즐": "puzzle", "아케이드": "arcade", "레이싱": "racing", "스포츠": "sports"
    }
    selected_genre_korean = st.selectbox("장르", ["선택 안 함"] + list(genre_list.keys()))
    
game_name = st.text_input("게임 이름 검색 (한글/영어)", placeholder="예: GTA V 또는 그랜드")

# --- 이 부분이 수정되었습니다! ---
min_rating = st.slider("최소 별점", min_value=0.0, max_value=5.0, value=0.0, step=0.1) # step=0.1로 변경
# --- 수정 끝 ---

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

if st.button("검색"):
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
                        st.write(f"**{game['name']}**")
                        st.write(f"출시일: {game.get('released', '정보 없음')}")
                        
                        rating = game.get('rating', '정보 없음')
                        st.write(f"평점: {rating} / 5.0")
                        
                        platforms = [p['platform']['name'] for p in game.get('platforms', []) if p.get('platform')]
                        if platforms:
                            st.write(f"플랫폼: {', '.join(platforms)}")
                        else:
                            st.write("플랫폼: 정보 없음")
                            
                        genres = [genre['name'] for genre in game.get('genres', []) if genre]
                        if genres:
                            st.write(f"장르: {', '.join(genres)}")
                        else:
                            st.write("장르: 정보 없음")

                        st.markdown("---")
            else:
                st.info("
