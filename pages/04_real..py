import streamlit as st
import requests
import urllib.parse

# secrets.toml 파일에서 RAWG API 키를 불러옵니다.
rawg_api_key = st.secrets["rawg_api_key"]

# 앱의 제목과 설명을 설정합니다.
st.title("🎮 RAWG 게임 검색기")
st.markdown("궁금한 게임의 이름을 입력하고 검색해 보세요.")

# 사용자에게 게임 이름을 입력받는 입력창을 만듭니다.
game_name = st.text_input("게임 이름 검색", placeholder="예: Grand Theft Auto V")

# 사용자가 검색 버튼을 누르면 이 코드가 실행됩니다.
if st.button("검색"):
    if game_name:
        try:
            # API 요청 URL을 만듭니다.
            search_url = f"https://api.rawg.io/api/games?key={rawg_api_key}&search={urllib.parse.quote_plus(game_name)}"

            # RAWG API에 요청을 보냅니다.
            response = requests.get(search_url)
            response.raise_for_status()

            data = response.json()
            games = data.get("results", [])

            # 검색 결과를 화면에 보여줍니다.
            if games:
                st.subheader(f"'{game_name}'의 검색 결과입니다:")
                
                for game in games:
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        if game["background_image"]:
                            st.image(game["background_image"], width=100)
                        else:
                            st.write("이미지 없음")
                    
                    with col2:
                        st.write(f"**{game['name']}**")
                        st.write(f"출시일: {game['released'] or '정보 없음'}")
                        
                        # --- 여기서부터 추가된 부분입니다! ---
                        
                        # 게임 평점을 표시합니다.
                        rating = game.get('rating', '정보 없음')
                        st.write(f"평점: {rating} / 5.0")

                        # 게임 플랫폼을 가져와 표시합니다.
                        # 'platforms' 데이터는 'platform' 안에 'name'이 또 들어있어 조금 복잡해요.
                        platforms = [p['platform']['name'] for p in game.get('platforms', [])]
                        if platforms:
                            st.write(f"플랫폼: {', '.join(platforms)}")
                        else:
                            st.write("플랫폼: 정보 없음")
                            
                        # --- 추가된 부분 끝 ---
                        
                        genres = [genre['name'] for genre in game.get('genres', [])]
                        if genres:
                            st.write(f"장르: {', '.join(genres)}")
                        else:
                            st.write("장르: 정보 없음")

                        st.markdown("---")
            else:
                st.info(f"'{game_name}'에 대한 검색 결과가 없습니다.")

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 오류가 발생했습니다: {e}")
    else:
        st.warning("검색할 게임 이름을 입력해 주세요.")
