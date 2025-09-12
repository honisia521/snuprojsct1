import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- 1. 데이터 로드 및 전처리 ---
# @st.cache_data 데코레이터는 Streamlit이 이 함수를 한 번만 실행하고 결과를 캐싱하도록 하여 성능을 최적화합니다.
# 데이터가 많아질수록 이 기능이 매우 중요해집니다.
@st.cache_data
def load_and_process_data():
    """게임 데이터를 로드하고 추천 시스템에 필요한 전처리를 수행합니다."""
    games = {
        "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요.", "태그": "MOBA, 전략, 팀플레이, 경쟁"},
        "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임.", "태그": "배틀로얄, 슈터, 생존, 멀티플레이어"},
        "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요.", "태그": "샌드박스, 건축, 탐험, 창의성"},
        "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요.", "태그": "RTS, 전략, SF, e스포츠"},
        "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG.", "태그": "RPG, 오픈월드, SF, 액션, 스토리"},
        "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요.", "태그": "액션RPG, 다크판타지, 고난이도, 탐험, 스토리"},
        "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG.", "태그": "다크 판타지, 핵앤슬래시, RPG, 파밍, 액션, 스토리"}
    }
    
    df = pd.DataFrame.from_dict(games, orient='index')
    df.index.name = '게임 이름'
    
    df['combined_features'] = df.apply(
        lambda row: f"{row['장르']} {row['설명']} {row['태그']}", axis=1
    )
    
    return df

# --- 2. 모델 학습 및 유사도 계산 ---
@st.cache_data
def train_model(df):
    """TF-IDF 벡터화 및 코사인 유사도 행렬을 계산합니다."""
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_features'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(df.index, index=df.index)
    return cosine_sim, indices

# 데이터와 모델을 한 번만 로드하도록 캐싱
df_games = load_and_process_data()
cosine_sim, indices = train_model(df_games)

# --- 3. 추천 함수 ---
def get_recommendations(game_name, cosine_sim_matrix, df, top_n=3):
    """선택된 게임과 유사한 게임을 추천합니다."""
    # .get_loc() 메서드를 사용해 KeyErrors와 같은 예외를 방지
    try:
        idx = df.index.get_loc(game_name)
    except KeyError:
        return pd.DataFrame() # 유효하지 않은 게임 이름일 경우 빈 데이터프레임 반환

    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 자기 자신을 제외하고 유사도 상위 top_n 게임의 인덱스를 가져옴
    game_indices = [i[0] for i in sim_scores if i[0] != idx][:top_n]

    return df.iloc[game_indices]

# --- 4. Streamlit UI 구성 ---
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
        
    if not recommended_games.empty:
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
        st.warning("추천할 게임을 찾을 수 없습니다. 다른 게임을 선택해 주세요.")
