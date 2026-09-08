import streamlit as st
import pickle

import requests
def fetch_poster(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": st.secrets["TMDB_API_KEY"]
    }

    response = requests.get(url, params=params)

    data = response.json()

    poster_path = data["poster_path"]

    return "https://image.tmdb.org/t/p/w500" + poster_path

 
similarity=pickle.load(open('similarity.pkl','rb'))

def recommend(movie_selected):
    movie_index=movies[movies['title']==movie_selected].index[0] 
    distance=similarity[movie_index]
    movies_list=sorted(list(enumerate(distance)),reverse=True,key=lambda x :x[1]) 
    movies_list=movies_list[1:6] 

    recommended_movies=[]
    recommended_posters = []
    for i in movies_list:
        movie_id=movies.iloc[i[0]] .movie_id
        recommended_movies.append((movies.iloc[i[0]] .title))
        poster = fetch_poster(movie_id)
        recommended_posters.append(poster)
    return recommended_movies, recommended_posters


movies=pickle.load(open('movies.pkl','rb'))


st.title("Movie Recommender System")

selcted_movie_name=st.selectbox("Select a movie" ,movies['title'].values)

if st.button("Recommend"):
   recommendations,posters=recommend(selcted_movie_name)

   cols=st.columns(5)

   for i in range(5):
      with cols[i]:
        st.image(posters[i])
        st.write(recommendations[i])
   