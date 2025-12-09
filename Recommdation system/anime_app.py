import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

st.set_page_config(page_title="Anime Recommendation System", layout="wide")
st.title("🎌 Anime Recommendation System")
st.write("Type an anime name and get similar anime recommendations.")

# try to load anime.csv from current directory or fallback path
csv_names = ["anime.csv",
             os.path.join(os.getcwd(), "anime.csv"),
             r"C:\Users\91705\codes_vip\python_practice\Data Science Assignments\anime.csv",
             r"C:\Users\91705\codes_vip\python_practice\Data Science Assignments\Recommdation system\anime.csv"]

data = None
for p in csv_names:
    try:
        if p and os.path.exists(p):
            data = pd.read_csv(p)
            break
    except Exception:
        pass

if data is None:
    st.error("Could not find 'anime.csv'. Put it in the same folder as this script or update the path.")
    st.stop()

required_cols = ['name', 'genre']
for c in required_cols:
    if c not in data.columns:
        st.error(f"Dataset missing required column: {c}")
        st.stop()

data['genre'] = data['genre'].fillna('')
data['type'] = data['type'].fillna('Unknown') if 'type' in data.columns else 'Unknown'
data['episodes'] = data['episodes'].fillna('Unknown') if 'episodes' in data.columns else 'Unknown'
data['rating'] = data['rating'].fillna(0) if 'rating' in data.columns else 0
data['members'] = data['members'].fillna(0) if 'members' in data.columns else 0

tfidf = TfidfVectorizer(stop_words='english')
genre_matrix = tfidf.fit_transform(data['genre'])
cosine_sim = cosine_similarity(genre_matrix, genre_matrix)
indices = pd.Series(data.index, index=data['name']).drop_duplicates()

def recommend_anime(title, n=5):
    if title not in indices:
        return None
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    anime_indices = [i[0] for i in sim_scores]
    return data.iloc[anime_indices].copy()

with st.sidebar:
    st.header("Search & settings")
    name_input = st.text_input("Enter anime name", "")
    k = st.slider("How many recommendations", 1, 15, 5)
    show_sample = st.checkbox("Show dataset sample", value=False)

if show_sample:
    st.subheader("Dataset sample")
    st.dataframe(data.head(10))

if st.button("Recommend"):
    if not name_input:
        st.warning("Please type an anime name first.")
    else:
        recs = recommend_anime(name_input, n=k)
        if recs is None or recs.empty:
            st.error("Anime not found in dataset. Check spelling or try another title.")
        else:
            st.success(f"Top {len(recs)} recommendations for '{name_input}':")
            for i, row in recs.reset_index(drop=True).iterrows():
                st.markdown(f"**{i+1}. {row['name']}**")
                info = []
                if 'type' in data.columns:
                    info.append(f"Type: {row.get('type', 'Unknown')}")
                if 'episodes' in data.columns:
                    info.append(f"Episodes: {row.get('episodes', 'Unknown')}")
                if 'rating' in data.columns:
                    info.append(f"Rating: {row.get('rating', 0)}")
                if 'members' in data.columns:
                    info.append(f"Members: {int(row.get('members', 0))}")
                st.write(" • ".join(info))
                st.write("")
