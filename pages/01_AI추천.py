import streamlit as st
import pandas as pd

# --- 샘플 게임 데이터 ---
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요."},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임."},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요."},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요."},
    "어몽 어스": {"장르": "추리", "난이도": "하", "플레이어 수": "멀티", "평점": 3.9, "설명": "우주선 안의 임포스터를 찾아내는 마피아 게임."},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요."},
    "로스트아크": {"장르": "MMORPG", "난이도": "중", "플레이어 수": "멀티", "평점": 4.4, "설명": "방대한 세계관과 화려한 액션의 MMORPG."},
    "발로란트": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.2, "설명": "정교한 총격전과 요원 스킬을 활용하는 전략 FPS."},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG."}
}

df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

st.set_page_config(layout="wide", page_title="무료 게임 추천")

st.title("🎮 AI 없이도 동작하는 게임 추천 (무료)")
st.write("좋아하는 게임이나 스타일을 선택하면 유사한 게임을 추천해드립니다!")

# --- 추천 방식 ---
recommendation_type = st.radio("추천 방식 선택:", ("선호 게임 선택", "자유로운 텍스트 설명"), index=0)

def recommend_by_game(selected_game, n=3):
    # 같은 장르 게임 중 추천 (본인 게임 제외)
    genre = df_games.loc[selected_game, "장르"]
    similar = df_games[df_games["장르"] == genre].drop(selected_game, errors='ignore')
    return similar.head(n)

def recommend_by_text(user_text, n=3):
    # 간단 키워드 매칭으로 추천
    keywords = user_text.lower().split()
    scores = {}
    for game, info in games.items():
        text = f"{game} {info['장르']} {info['설명']}".lower()
        score = sum(text.count(k) for k in keywords)
        if score > 0:
            scores[game] = score
    sorted_games = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    recommended = [df_games.loc[g] for g, s in sorted_games[:n]]
    return pd.DataFrame(recommended)

# --- 처리 ---
if recommendation_type == "선호 게임 선택":
    selected_game = st.selectbox("좋아하는 게임 선택:", ['--선택--', *sorted(df_games.index.tolist())])
    if selected_game != '--선택--' and st.button("추천받기"):
        result = recommend_by_game(selected_game)
        st.subheader(f"💡 '{selected_game}'와 비슷한 게임 추천")
        st.table(result)

elif recommendation_type == "자유로운 텍스트 설명":
    user_desc = st.text_area("원하는 게임 스타일을 입력:", height=100)
    if st.button("추천받기"):
        if user_desc.strip():
            result = recommend_by_text(user_desc)
            st.subheader(f"💡 '{user_desc}'에 맞는 게임 추천")
            st.table(result)
        else:
            st.warning("게임 스타일을 입력해주세요!")
