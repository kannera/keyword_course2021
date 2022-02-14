from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_distances
import matplotlib.pyplot as plt
import wget, json, os , sys, re

SPACE_URL = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/embeddings/CORPUS_5_pmi.csv"
def get_wordspace(corpus):
  url = SPACE_URL.replace("CORPUS", corpus)
  tmp = wget.download(url)
  with open(tmp, "r", encoding="utf-8") as f:
    data = json.load(f)
  os.remove(tmp)
  wordspace = {x[0]:x[1:] for x in data}
  words = list(wordspace.keys())
  matrix = [wordspace[w] for w in words]
  distances = cosine_distances(matrix)
  return distances, words

def plot_wordspace(distances, words, lemma, N, other_words):
  neighbours = get_closest(lemma, distances, words, 600, other_words)
  subspace = get_subspace(distances, words, neighbours)
  mds = MDS(dissimilarity='precomputed')
  coords = mds.fit(subspace).embedding_
  plt.rcParams['figure.figsize'] = [30, 15]
  for w,x,y in zip(neighbours, coords[:,0], coords[:,1]):
    if w != lemma:
      plt.annotate(w, xy=(x,y), alpha=0.6, fontsize=13)
    else:
      plt.annotate(w, xy=(x,y), arrowprops={"width":1}, alpha=1.0, fontsize=18)
    plt.scatter(x,y)
  plt.show()

def list_closest_neighbours(distances, lemma, words, N):
  neighbours = get_closest(lemma, distances, words, 600, "closest")
  n_dists = {w:distances[words.index[lemma]][words.index[w]] for w in neighbours}
  for k,v in sorted(n_dists.items(), key=lambda x:x[1])[:N]:
    print(k, "\t", v)
  
def get_closest(lemma, distances, words, N, sample="closest"):
  distances = distances[words.index(lemma)]
  if sample == "closest":
    cap = sorted(distances)[N]
    return [words[i] for i,d in enumerate(distances) if d <= cap]
  elif sample == "random":
    return list(random.sample(words, N))+[lemma]
  
def get_subspace(distances, words, subset):
  subspace_indices = [words.index(w) for w in subset]
  return [[distances[i][ii] for ii in subspace_indices] for i in subspace_indices]
