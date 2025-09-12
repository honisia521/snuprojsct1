import requests
import json
import streamlit as st

# secrets.toml에서 열쇠 가져오기
client_id = st.secrets["twitch"]["client_id"]
client_secret = st.secrets["twitch"]["client_secret"]

# 임시 열쇠(Access Token) 받는 코드 (한 번만 실행되도록 캐싱)
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
        st.error(f"Access Token 오류: {e}")
        return None

access_token = get_access_token()

if access_token:
    # ⭐️ 이 부분이 새로 추가된 '검색창' 코드입니다.
    user_query = st.text_input("찾고 싶은 게임 이름을 입력하세요:", "")

    if user_query:
        # IGDB에 게임 데이터 요청
        igdb_url = "https://api.igdb.com/v4/games"

        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}"
        }

        # 사용자가 입력한 내용을 가지고 API에 요청합니다.
        query_body = f'fields name, genres.name, summary, rating; search "{user_query}"; limit 10;'

        try:
            igdb_response = requests.post(igdb_url, headers=headers, data=query_body)
            igdb_response.raise_for_status()

            games = igdb_response.json()

            if games:
                st.write(f"**'{user_query}'에 대한 검색 결과입니다.**")
                for game in games:
                    st.write(f"### {game.get('name', '이름 없음')}")
                    
                    genres = game.get('genres')
                    if genres:
                        genre_names = [genre.get('name') for genre in genres]
                        st.write(f"**장르:** {', '.join(genre_names)}")
                        
                    st.write(f"**줄거리:** {game.get('summary', '줄거리 정보가 없습니다.')}")
                    st.write("---")
            else:
                st.write(f"'{user_query}'에 대한 검색 결과를 찾지 못했습니다. 다른 이름으로 검색해보세요.")

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 오류가 발생했습니다: {e}")
