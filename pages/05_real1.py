import requests
import json
import streamlit as st
from googletrans import Translator
import os

# --- 1. secrets.toml에서 API 열쇠 가져오기 ---
# Streamlit Cloud에서는 secrets.toml에 있는 값을 os.environ에서 가져올 수 있습니다.
# 로컬 개발 환경에서는 secrets.toml에서 직접 가져옵니다.
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
st.title("🎮 IGDB 게임 추천 시스템")
st.write("Twitch IGDB API를 활용하여 게임 정보를 검색하고 추천해 드립니다.")
st.header("게임 이름 검색 (한글/영어)")
st.warning("🚨 한글 검색 시 번역 오류로 인해 정확한 결과가 나오지 않을 수 있습니다.")

access_token = get_access_token()

if access_token:
    user_query = st.text_input("찾고 싶은 게임 이름을 입력하세요:", placeholder="예: GTA V 또는 스타듀 밸리")

    if user_query:
        # 사용자가 입력한 내용을 영어로 번역
        english_query = translate_to_english(user_query)
        st.write(f"**'{user_query}'**를 영어로 번역: **'{english_query}'**")

        # --- 5. IGDB API에 게임 데이터 요청 ---
        igdb_url = "https://api.igdb.com/v4/games"

        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        }

        query_body = f'fields name, genres.name, summary, rating, cover.url; search "{english_query}"; limit 10;'

        try:
            igdb_response = requests.post(igdb_url, headers=headers, data=query_body)
            igdb_response.raise_for_status()
            games = igdb_response.json()

            if games:
                st.write(f"**'{user_query}'에 대한 검색 결과입니다.**")
                for game in games:
                    st.write("---")
                    st.write(f"### {game.get('name', '이름 없음')}")
                    
                    genres = game.get('genres')
                    if genres:
                        genre_names = [genre.get('name') for genre in genres]
                        st.write(f"**장르:** {', '.join(genre_names)}")
                    
                    st.write(f"**줄거리:** {game.get('summary', '줄거리 정보가 없습니다.')}")
                    
                    # 별점 표시
                    rating = game.get('rating')
                    if rating:
                        stars = int(round(rating / 20))  # 100점 만점을 5점 만점으로 변환
                        st.write(f"**평점:** {'⭐' * stars} ({rating:.1f}/100점)")

            else:
                st.write(f"'{user_query}'에 대한 검색 결과를 찾지 못했습니다. 다른 이름으로 검색해보세요.")

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 오류가 발생했습니다: {e}")
