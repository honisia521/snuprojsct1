import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. 게임 데이터 ---
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요.", "태그": "MOBA, 전략, 팀플레이, 경쟁"},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임.", "태그": "배틀로얄, 슈터, 생존, 멀티플레이어"},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요.", "태그": "샌드박스, 건축, 탐험, 창의성"},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요.", "태그": "RTS, 전략, SF, e스포츠"},
    "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG.", "태그": "RPG, 오픈월드, SF, 액션, 스토리"},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요.", "태그": "액션RPG, 다크판타지, 고난이도, 탐험, 스토리"},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG.", "태그": "다크 판타지, 핵앤슬래시, RPG, 파밍, 액션, 스토리"}
}
df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

# --- 2. TF-IDF 및 코사인 유사도 계산 ---
# '장르', '설명', '태그' 열을 합쳐 하나의 문자열로 만듭니다.
df_games['combined_features'] = df_games.apply(
    lambda row: f"{row['장르']} {row['설명']} {row['태그']}", axis=1
)

# TF-IDF 벡터화
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df_games['combined_features'])

# 코사인 유사도 행렬 계산
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# 게임 이름과 인덱스를 매핑하는 시리즈 생성
indices = pd.Series(df_games.index, index=df_games.index)

# --- 3. 추천 함수 ---
def get_recommendations(game_name, cosine_sim_matrix, df, top_n=5):
    if game_name not in df.index:
        return None

    idx = indices[game_name]
    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 자기 자신을 제외하고 가장 유사한 top_n 게임 추출
    game_indices = [i[0] for i in sim_scores if i[0] != idx][:top_n]
    return df.iloc[game_indices]

# --- 4. Streamlit UI ---
st.set_page_config(layout="wide", page_title="TF-IDF 기반 게임 추천")
st.title("🎮 TF-IDF 기반 게임 추천기")
st.markdown("""
<style>
    .game-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        background-color: #f9f9f9;
    }
    .game-title {
        color: #FF4B4B;
        font-size: 1.2em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
st.write("좋아하는 게임을 선택하여 비슷한 게임을 추천받으세요!")

# 사용자 입력
selected_game = st.selectbox(
    "좋아하는 게임을 선택하세요:",
    ['--선택--', *sorted(df_games.index.tolist())],
    key="game_select"
)

if selected_game != '--선택--':
    st.info(f"'{selected_game}'와(과) 비슷한 게임을 추천해 드릴게요!")
    
    with st.spinner("유사 게임을 찾는 중입니다..."):
        recommended_games = get_recommendations(selected_game, cosine_sim, df_games, top_n=3)
        
    if recommended_games is not None and not recommended_games.empty:
        st.subheader("💡 추천 게임")
        
        display_cols = st.columns(3)
        for i, (game_name, game_info) in enumerate(recommended_games.iterrows()):
            with display_cols[i % 3]:
                st.markdown(f'<div class="game-card">', unsafe_allow_html=True)
                st.markdown(f'<h3 class="game-title">{game_name}</h3>', unsafe_allow_html=True)
                st.write(f"**장르:** {game_info['장르']}")
                st.write(f"**평점:** {game_info['평점']} / 5.0")
                st.markdown(f"**설명:** {game_info['설명']}")
                st.markdown(f'</div>', unsafe_allow_html=True)
    else:
        st.warning("추천할 게임을 찾을 수 없습니다. 다른 게임을 선택해 주세요.")import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. 게임 데이터 ---
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요.", "태그": "MOBA, 전략, 팀플레이, 경쟁"},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임.", "태그": "배틀로얄, 슈터, 생존, 멀티플레이어"},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요.", "태그": "샌드박스, 건축, 탐험, 창의성"},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요.", "태그": "RTS, 전략, SF, e스포츠"},
    "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG.", "태그": "RPG, 오픈월드, SF, 액션, 스토리"},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요.", "태그": "액션RPG, 다크판타지, 고난이도, 탐험, 스토리"},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG.", "태그": "다크 판타지, 핵앤슬래시, RPG, 파밍, 액션, 스토리"}
}
df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

# --- 2. TF-IDF 및 코사인 유사도 계산 ---
# '장르', '설명', '태그' 열을 합쳐 하나의 문자열로 만듭니다.
df_games['combined_features'] = df_games.apply(
    lambda row: f"{row['장르']} {row['설명']} {row['태그']}", axis=1
)

# TF-IDF 벡터화
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df_games['combined_features'])

# 코사인 유사도 행렬 계산
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# 게임 이름과 인덱스를 매핑하는 시리즈 생성
indices = pd.Series(df_games.index, index=df_games.index)

# --- 3. 추천 함수 ---
def get_recommendations(game_name, cosine_sim_matrix, df, top_n=5):
    if game_name not in df.index:
        return None

    idx = indices[game_name]
ㅍ
