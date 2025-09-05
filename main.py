import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# ... (나머지 코드 그대로) ...

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# --- 1. 게임 데이터 준비 (현재 코드의 상세 정보 + 추천을 위한 태그 확장) ---
games = {
    "리그 오브 레전드": {"장르": "AOS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.5, "설명": "5대5 팀 전략 게임. 다양한 챔피언과 전략으로 승리하세요.", "태그": "팀 전략, 경쟁, AOS, 무료, MOBA, e스포츠"},
    "배틀그라운드": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.0, "설명": "최후의 1인이 될 때까지 싸우는 배틀로얄 게임.", "태그": "생존, 슈팅, 배틀로얄, 멀티플레이어, FPS"},
    "마인크래프트": {"장르": "샌드박스", "난이도": "하", "플레이어 수": "싱글/멀티", "평점": 4.8, "설명": "블록으로 이루어진 세상에서 자유롭게 탐험하고 건축하세요.", "태그": "자유도, 건설, 탐험, 창의력, 샌드박스, 캐주얼"},
    "스타크래프트 리마스터": {"장르": "RTS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.2, "설명": "전설적인 실시간 전략 게임. 3가지 종족으로 우주를 지배하세요.", "태그": "전략, RTS, SF, e스포츠, 빌드오더"},
    "어몽 어스": {"장르": "추리", "난이도": "하", "플레이어 수": "멀티", "평점": 3.9, "설명": "우주선 안의 임포스터를 찾아내는 마피아 게임.", "태그": "마피아, 심리, 추리, 캐주얼, 멀티플레이어"},
    "젤다의 전설 브레스 오브 더 와일드": {"장르": "액션 어드벤처", "난이도": "중", "플레이어 수": "싱글", "평점": 4.9, "설명": "광활한 하이랄을 탐험하며 미스터리를 풀어가는 오픈월드 어드벤처.", "태그": "판타지, 오픈월드, 어드벤처, 퍼즐, 스토리, 싱글플레이"},
    "폴가이즈": {"장르": "파티", "난이도": "하", "플레이어 수": "멀티", "평점": 3.7, "설명": "엉뚱한 장애물 코스를 통과하는 캐주얼 배틀 로얄.", "태그": "캐주얼, 파티게임, 배틀로얄, 멀티플레이어, 미니게임"},
    "사이버펑크 2077": {"장르": "RPG", "난이도": "상", "플레이어 수": "싱글", "평점": 4.1, "설명": "미래 도시 나이트 시티에서 펼쳐지는 광대한 오픈월드 RPG.", "태그": "미래, 오픈월드, RPG, 스토리, 사이버펑크, 싱글플레이"},
    "엘든 링": {"장르": "액션 RPG", "난이도": "최상", "플레이어 수": "싱글/멀티", "평점": 4.7, "설명": "광활한 판타지 세계에서 고난이도의 액션 RPG를 경험하세요.", "태그": "소울라이크, 판타지, 오픈월드, 액션, 고난이도, RPG"},
    "오버워치 2": {"장르": "FPS", "난이도": "중", "플레이어 수": "멀티", "평점": 4.3, "설명": "영웅 기반의 팀 대전 FPS. 다양한 영웅과 전략으로 목표를 달성하세요.", "태그": "팀 전략, FPS, 영웅 슈터, 무료, 멀티플레이어, e스포츠"},
    "로스트아크": {"장르": "MMORPG", "난이도": "중", "플레이어 수": "멀티", "평점": 4.4, "설명": "방대한 세계관과 화려한 액션의 MMORPG.", "태그": "판타지, 핵앤슬래시, MMORPG, 스토리, 레이드, 성장"},
    "발로란트": {"장르": "FPS", "난이도": "상", "플레이어 수": "멀티", "평점": 4.2, "설명": "정교한 총격전과 요원 스킬을 활용하는 전략 FPS.", "태그": "전략 슈터, FPS, e스포츠, 무료, 멀티플레이어"},
    "디아블로 4": {"장르": "액션 RPG", "난이도": "중", "플레이어 수": "싱글/멀티", "평점": 4.0, "설명": "어두운 판타지 세계에서 악마를 사냥하는 핵앤슬래시 RPG.", "태그": "다크 판타지, 핵앤슬래시, RPG, 파밍, 액션, 스토리"}
}

df_games = pd.DataFrame.from_dict(games, orient='index')
df_games.index.name = '게임 이름'

# 추천 시스템을 위한 'combined_features' 생성
df_games['combined_features'] = df_games['장르'] + ' ' + df_games['태그'] + ' ' + df_games['설명']
df_games['combined_features'] = df_games['combined_features'].fillna('') # NaN 값 처리

# --- 2. 추천 시스템 구축 (TF-IDF 기반) ---
tfidf = TfidfVectorizer(stop_words=None) # 한국어 처리이므로 stop_words는 None
tfidf_matrix = tfidf.fit_transform(df_games['combined_features'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
indices = pd.Series(df_games.index, index=df_games.index).drop_duplicates()

def get_recommendations_by_game(title, cosine_sim=cosine_sim, df=df_games, indices=indices):
    if title not in indices:
        return []
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:7]  # 자기 자신 제외하고 상위 6개 추천
    game_indices = [i[0] for i in sim_scores]
    return df.iloc[game_indices]

def get_recommendations_by_keywords(keywords, cosine_sim=cosine_sim, df=df_games, tfidf_vectorizer=tfidf):
    if not keywords.strip():
        return pd.DataFrame() # 빈 데이터프레임 반환

    user_input_tfidf = tfidf_vectorizer.transform([keywords])
    user_cosine_sim = linear_kernel(user_input_tfidf, tfidf_matrix)

    sim_scores = list(enumerate(user_cosine_sim[0]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[0:6] # 상위 6개 추천
    game_indices = [i[0] for i in sim_scores]
    return df.iloc[game_indices]


# --- 3. Streamlit 앱 구성 ---
st.set_page_config(layout="wide", page_title="궁극의 게임 추천기")

st.title("🎮 궁극의 게임 추천기")
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .game-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        background-color: #f9f9f9;
    }
    .game-title {
        color: #FF4B4B; /* Streamlit 기본 primary 색상 */
    }
    </style>
    """, unsafe_allow_html=True)

st.write("나에게 딱 맞는 게임을 찾아보세요! 다양한 필터와 추천 방식으로 게임을 탐색할 수 있습니다.")

# --- 메인 콘텐츠 영역과 사이드바 분리 ---
col_main, col_sidebar = st.columns([3, 1])

with col_sidebar: # 사이드바는 오른쪽에 배치
    st.header("🎯 추천 필터 및 방식")
    st.markdown("---")

    # 추천 방식 선택
    recommendation_mode = st.radio(
        "어떤 방식으로 추천받으시겠어요?",
        ("필터로 게임 탐색", "이 게임과 비슷한 게임 찾기", "키워드로 게임 찾기"),
        index=0 # 기본값 설정
    )
    st.markdown("---")


    # --- 기존 필터링 기능 (사이드바에 유지) ---
    if recommendation_mode == "필터로 게임 탐색":
        st.subheader("🔍 게임 필터링")
        all_genres = ["모두"] + sorted(list(df_games["장르"].unique()))
        selected_genre = st.selectbox("장르", all_genres, key="filter_genre")

        all_difficulties = ["모두"] + sorted(list(df_games["난이도"].unique()))
        selected_difficulty = st.selectbox("난이도", all_difficulties, key="filter_difficulty")

        all_player_counts = ["모두"] + sorted(list(df_games["플레이어 수"].unique()))
        selected_player_count = st.selectbox("플레이어 수", all_player_counts, key="filter_player_count")

        min_rating = st.slider("최소 평점", 0.0, 5.0, 3.0, 0.1, key="filter_min_rating")

        # 필터링된 게임 목록 준비
        filtered_games_by_filter = df_games.copy()
        if selected_genre != "모두":
            filtered_games_by_filter = filtered_games_by_filter[filtered_games_by_filter["장르"] == selected_genre]
        if selected_difficulty != "모두":
            filtered_games_by_filter = filtered_games_by_filter[filtered_games_by_filter["난이도"] == selected_difficulty]
        if selected_player_count != "모두":
            filtered_games_by_filter = filtered_games_by_filter[filtered_games_by_filter["플레이어 수"] == selected_player_count]
        filtered_games_by_filter = filtered_games_by_filter[filtered_games_by_filter["평점"] >= min_rating]

    elif recommendation_mode == "이 게임과 비슷한 게임 찾기":
        st.subheader("💖 선호 게임 기반 추천")
        selected_game_for_recommendation = st.selectbox(
            "좋아하는 게임을 선택해주세요:",
            ['--선택--', *sorted(df_games.index.tolist())],
            key="rec_game_select"
        )
        if selected_game_for_recommendation != '--선택__':
            recommended_games_df = get_recommendations_by_game(selected_game_for_recommendation)
        else:
            recommended_games_df = pd.DataFrame()

    elif recommendation_mode == "키워드로 게임 찾기":
        st.subheader("💡 키워드 추천")
        keywords_input = st.text_input("원하는 키워드를 입력하세요 (예: 오픈월드, 협동, 스토리)", key="rec_keywords")
        if st.button("키워드로 추천받기", key="btn_keywords_rec"):
            if keywords_input:
                recommended_games_df = get_recommendations_by_keywords(keywords_input)
            else:
                st.warning("키워드를 입력해주세요!")
                recommended_games_df = pd.DataFrame()
        else:
            recommended_games_df = pd.DataFrame()


with col_main: # 메인 콘텐츠 영역
    st.header(f"✨ {recommendation_mode} 결과")

    if recommendation_mode == "필터로 게임 탐색":
        display_games = filtered_games_by_filter
        if display_games.empty:
            st.info("선택한 조건에 맞는 게임이 없습니다. 필터를 조정해 보세요.")
    else: # "이 게임과 비슷한 게임 찾기" 또는 "키워드로 게임 찾기"
        display_games = recommended_games_df
        if display_games.empty:
            if recommendation_mode == "이 게임과 비슷한 게임 찾기":
                st.info("좋아하는 게임을 선택하시면 비슷한 게임을 추천해 드립니다.")
            elif recommendation_mode == "키워드로 게임 찾기":
                st.info("키워드를 입력하고 '키워드로 추천받기' 버튼을 눌러보세요.")

    # 게임 카드 형식으로 결과 표시
    if not display_games.empty:
        # 결과를 2열로 분할하여 표시 (모바일에서는 1열)
        display_cols = st.columns(2)
        for i, (game_name, game_info) in enumerate(display_games.iterrows()):
            with display_cols[i % 2]:
                st.markdown(f'<div class="game-card">', unsafe_allow_html=True)
                st.markdown(f'<h3 class="game-title">{game_name}</h3>', unsafe_allow_html=True)
                # 이미지 추가 (예시, 실제 이미지 URL이 필요)
                # st.image(f"images/{game_name}.jpg", width=150) # 이미지 파일이 있다면
                st.write(f"**장르:** {game_info['장르']}")
                st.write(f"**난이도:** {game_info['난이도']}")
                st.write(f"**플레이어 수:** {game_info['플레이어 수']}")
                st.write(f"**평점:** {game_info['평점']} / 5.0")
                st.markdown(f"**설명:** {game_info['설명']}")
                st.markdown(f'</div>', unsafe_allow_html=True)


st.sidebar.markdown("---")
st.sidebar.info("이 추천기는 여러분의 게임 탐색을 돕기 위해 만들어졌습니다.")
