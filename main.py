import streamlit as st
import pandas as pd

# 게임 데이터 (예시)
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요."},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임."},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요."},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요."},
    "어몽 어스": {"장르": "추리", "난이도": "하", "플레이어 수": "멀티", "평점": 3.9, "설명": "우주선 안의 임포스터를 찾아내는 마피아 게임."},
    "젤다의 전설 브레스 오브 더 와일드": {"장르": "액션 어드벤처", "난이도": "중", "플레이어 수": "싱글", "평점": 4.9, "설명": "광활한 하이랄을 탐험하며 미스터리를 풀어가는 오픈월드 어드벤처."},
    "폴가이즈": {"장르": "파티", "난이도": "하", "플레이어 수": "멀티", "평점": 3.7, "설명": "엉뚱한 장애물 코스를 통과하는 캐주얼 배틀 로얄."},
    "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG."}
}

df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

st.set_page_config(layout="wide")
st.title("🎮 나만의 게임 추천기")

# 사이드바 필터
st.sidebar.header("추천 필터")

# 장르 필터
all_genres = ["모두"] + list(df_games["장르"].unique())
selected_genre = st.sidebar.selectbox("장르", all_genres)

# 난이도 필터
all_difficulties = ["모두"] + list(df_games["난이도"].unique())
selected_difficulty = st.sidebar.selectbox("난이도", all_difficulties)

# 플레이어 수 필터
all_player_counts = ["모두"] + list(df_games["플레이어 수"].unique())
selected_player_count = st.sidebar.selectbox("플레이어 수", all_player_counts)

# 최소 평점 필터
min_rating = st.sidebar.slider("최소 평점", 0.0, 5.0, 3.0, 0.1)

# 필터링된 게임 목록
filtered_games = df_games.copy()

if selected_genre != "모두":
    filtered_games = filtered_games[filtered_games["장르"] == selected_genre]
if selected_difficulty != "모두":
    filtered_games = filtered_games[filtered_games["난이도"] == selected_difficulty]
if selected_player_count != "모두":
    filtered_games = filtered_games[filtered_games["플레이어 수"] == selected_player_count]

filtered_games = filtered_games[filtered_games["평점"] >= min_rating]

st.header("추천 게임 목록")

if not filtered_games.empty:
    for i, (game_name, game_info) in enumerate(filtered_games.iterrows()):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.subheader(game_name)
            # 이미지 추가 (예시, 실제 이미지 URL이 필요)
            # st.image(f"images/{game_name}.jpg", width=150) # 이미지 파일이 있다면
            st.write(f"**장르:** {game_info['장르']}")
            st.write(f"**난이도:** {game_info['난이도']}")
            st.write(f"**플레이어 수:** {game_info['플레이어 수']}")
            st.write(f"**평점:** {game_info['평점']} / 5.0")
        with col2:
            st.write(game_info['설명'])
        st.markdown("---") # 게임 사이에 구분선
else:
    st.info("선택한 조건에 맞는 게임이 없습니다. 필터를 조정해 보세요.")

st.sidebar.markdown("---")
st.sidebar.info("이 사이트는 게임 추천을 위한 예시입니다.")
