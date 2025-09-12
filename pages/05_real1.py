import requests
import json
import streamlit as st

# 1. secrets.toml 파일에서 열쇠를 가져옵니다.
client_id = st.secrets["twitch"]["client_id"]
client_secret = st.secrets["twitch"]["client_secret"]

# 2. 임시 열쇠(Access Token)를 받는 코드입니다. 이 부분은 윗부분에 넣으세요.
twitch_token_url = "https://id.twitch.tv/oauth2/token"
token_params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}
token_response = requests.post(twitch_token_url, params=token_params)
access_token = token_response.json().get("access_token")

# 3. 이제 이 임시 열쇠로 게임 데이터를 요청합니다!
igdb_url = "https://api.igdb.com/v4/games"

headers = {
    "Client-ID": client_id,
    "Authorization": f"Bearer {access_token}"
}

# 4. 우리가 원하는 데이터를 정확히 요청하는 문장입니다.
# 'name', 'genres.name', 'summary'를 달라고 요청하는 거죠.
query_body = 'fields name, genres.name, summary; where name = "The Witcher 3";'

try:
    igdb_response = requests.post(igdb_url, headers=headers, data=query_body)
    igdb_response.raise_for_status()

    games = igdb_response.json()
    
    if games:
        st.write("🎉 '더 위쳐 3' 게임의 데이터를 성공적으로 가져왔습니다!")
        st.write(json.dumps(games, indent=2))
    else:
        st.write("오류: 게임 데이터를 찾지 못했습니다.")

except requests.exceptions.RequestException as e:
    st.write(f"오류가 발생했습니다: {e}")
