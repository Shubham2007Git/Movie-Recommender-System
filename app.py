
import streamlit as st
import pickle
import requests
import os

# 1. Page Configuration
st.set_page_config(
    page_title="CineMatch | Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern UI Styling (CSS)
st.markdown("""
<style>
    /* Global background adjustments */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1e1b4b 0%, #0f172a 50%, #030712 100%);
        color: #f8fafc;
    }
    
    /* Hero Title Styling */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 2.5rem;
    }

    /* Movie Card Design */
    .movie-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .movie-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(139, 92, 246, 0.25);
        border-color: rgba(139, 92, 246, 0.5);
    }
    .movie-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #f1f5f9;
        margin-top: 10px;
        line-height: 1.3;
    }

    /* Button Enhancements */
    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.2rem;
        font-size: 1.05rem;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        opacity: 0.95;
        transform: scale(1.02);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 3. Data & Poster Fetching with Caching
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    movies_path = os.path.join(base_dir, 'model', 'movies.pkl')
    similarity_path = os.path.join(base_dir, 'model', 'similarity.pkl')
    
    movies = pickle.load(open(movies_path, 'rb'))
    similarity = pickle.load(open(similarity_path, 'rb'))
    return movies, similarity

movies, similarity = load_data()

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": st.secrets["TMDB_API_KEY"]}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=60"

def recommend(movie_selected):
    movie_index = movies[movies['title'] == movie_selected].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        
    return recommended_movies, recommended_posters

# 4. Header Section
st.markdown('<div class="hero-title">CineMatch</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Discover your next favorite movie using content-based machine learning</div>', unsafe_allow_html=True)

# 5. Search Bar & Recommendation Trigger
search_col, btn_col = st.columns([4, 1], gap="medium")

with search_col:
    selected_movie_name = st.selectbox(
        "Select a movie",
        movies['title'].values,
        label_visibility="collapsed"
    )

with btn_col:
    recommend_clicked = st.button("Recommend ✨")

# 6. Display Recommendations
if recommend_clicked:
    with st.spinner("Finding recommendations..."):
        names, posters = recommend(selected_movie_name)
    
    st.markdown("---")
    st.markdown(f"#### Top picks similar to **{selected_movie_name}**")
    
    cols = st.columns(5, gap="medium")
    for i in range(5):
        with cols[i]:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{posters[i]}" style="width: 100%; border-radius: 8px; object-fit: cover; aspect-ratio: 2/3;" />
                <div class="movie-title">{names[i]}</div>
            </div>
            """, unsafe_allow_html=True)