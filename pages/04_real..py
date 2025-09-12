import streamlit as st
import requests
import urllib.parse

# secrets.toml 파일에서 RAWG API 키를 불러옵니다.
rawg_api_key = st.secrets["rawg_api_key"]

# 앱의 제목과 설명을 설정합니다.
st.title("🎮 RAWG 게임 검색기")
st.markdown("궁금한 게임의 이름을 입력하거나, 옆 필터를 사용해 보세요.")

# --- 여기에 새로운 사이드바 기능을 추가합니다! ---
# 장르 목록 (RAWG API의 slug와 매칭)
genre_list = {
    "액션": "action",
    "인디": "indie",
    "어드벤처": "adventure",
    "RPG": "role-playing-games-rpg",
    "전략": "strategy",
    "슈팅": "shooter",
    "캐주얼": "casual",
    "시뮬레이션": "simulation",
    "퍼즐": "puzzle",
    "아케이드": "arcade",
    "레이싱": "racing",
    "스포츠": "sports"
}

# 1. Streamlit 사이드바를 만듭니다.
with st.sidebar:
    st.header("🔍 필터")
    
    # 2. 장르 드롭다운 메뉴를 만듭니다.
    selected_genre_korean = st.selectbox("장르", ["선택 안 함"] + list(genre_list.keys()))
    
    # 3. 별점 슬라이더를 만듭니다.
    min_rating = st.slider("최소 별점", min_value=0.0, max_value=5.0, value=0.0, step=0.5)

# --- 사이드바 기능 끝 ---

# 사용자에게 게임 이름을 입력받는 입력창을 만듭니다.
game_name = st.text_input("게임 이름 검색", placeholder="예: Grand Theft Auto V")

# API 요청 URL을 초기화합니다.
base_url = f"https://api.rawg.io/api/games?key={rawg_api_key}"
params = {}

# 4. 사용자가 필터를 선택했는지 확인하고, API 파라미터에 추가합니다.
if selected_genre_korean != "선택 안 함":
    params['genres'] = genre_list[selected_genre_korean]
    
# RAWG API는 평점 필터로 'metacritic'을 사용합니다.
if min_rating > 0.0:
    # RAWG API는 0~100점 기준으로 필터링하므로, 5점 만점을 100점 만점으로 변환합니다.
    params['metacritic'] = f"{int(min_rating * 20)},100"

# 5. 검색어가 있으면 검색 파라미터를 추가합니다.
if game_name:
    params['search'] = urllib.parse.quote_plus(game_name)

# 6. 검색 버튼을 누르거나 필터가 변경되면 실행됩니다.
if st.button("검색") or (selected_genre_korean != "선택 안 함") or (min_rating > 0.0):
    if params:
        try:
            # 최종 URL을 조합하여 RAWG API에 요청을 보냅니다.
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            games = data.get("results", [])

            # 검색 결과를 화면에 보여줍니다.
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
                st.info("검색 결과가 없습니다.")
        
        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 오류가 발생했습니다: {e}")
    else:
        st.warning("검색할 게임 이름을 입력하거나, 장르와 별점 필터를 사용해 주세요.")
