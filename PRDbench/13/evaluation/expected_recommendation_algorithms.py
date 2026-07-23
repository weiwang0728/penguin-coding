# Expected recommendation algorithm library usage examples
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from surprise import Dataset, Reader, SVD, KNNBasic

# 1. TF-IDF feature extraction
tfidf = TfidfVectorizer(max_features=5000)
tfidf_matrix = tfidf.fit_transform(documents)

# 2. Similarity computation
similarity_matrix = cosine_similarity(tfidf_matrix)

# 3. Matrix factorization
svd = TruncatedSVD(n_components=50)
reduced_matrix = svd.fit_transform(user_item_matrix)

# 4. Surprise library collaborative filtering
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df, reader)
algo = SVD(n_factors=50, n_epochs=20)
algo.fit(trainset)

# 5. KNN algorithm
knn_algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': True})
knn_algo.fit(trainset)