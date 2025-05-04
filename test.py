from sklearn.decomposition import NMF
import numpy as np

from surprise import Dataset, SVD
from surprise.model_selection import cross_validate


# Load the movielens-100k dataset (download it if needed),
data = Dataset.load_builtin("ml-100k")

# We'll use the famous SVD algorithm.
algo = SVD()

# Run 5-fold cross-validation and print results
cross_validate(algo, data, measures=["EQM", "EMA"], cv=5, verbose=True)




# Exemple de matrice utilisateur-élément avec des notes
R = np.array([
    [5, 3, 0, 1],
    [4, 0, 0, 1],
    [1, 1, 0, 5],
    [0, 0, 5, 4],
    [0, 1, 5, 4],
])

# Application de la NMF
model = NMF(n_components=2, init='random', random_state=0)
W = model.fit_transform(R)
H = model.components_

# Reconstruction de la matrice approximée
R_approx = np.dot(W, H)

print("Matrice reconstruite :")
print(R_approx)
print("Matrice W :")
print(W)
print("Matrice H :")
print(H)
print("Matrice originale :")
print(R)