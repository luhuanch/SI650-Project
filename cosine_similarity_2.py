"""
This program retrieves reviews from reviews.db and calculates the similarities
between reviews to search for identical reviews, which will later be labelled
as fake reviews.

Due to memery limit, the list length is set to 30000.
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
from time import time
import sqlite3
import numpy
import re

# retrieving reviews from database
conn = sqlite3.connect('reviews.db')
cur = conn.cursor()
q = 'SELECT review_id, review_text FROM Review'
cur.execute(q)
rows = cur.fetchall()

# calculating similarities using pairwise_distances from sklearn
t0 = time()
review_lst = [x[1] for x in rows]
vecs = CountVectorizer().fit_transform(review_lst[0:50000])
cos_sim = 1 - pairwise_distances(vecs, metric='cosine')
print ("calculating similarities takes: ", time()-t0)

# detecting identical reviews with a threshold of 0.9
repetitions = zip(numpy.where((cos_sim > 0.9))[0], \
                  numpy.where((cos_sim > 0.9))[1], \
                  cos_sim[numpy.where((cos_sim > 0.9))])

# eliminating duplicate pairs
repetitions_clean = [(x[0]+1, x[1]+1, x[2]) for x in repetitions if x[0]>x[1]]

# write identical reviews into database
cur.executemany("INSERT INTO Cosine VALUES (?, ?, ?)", repetitions_clean)
conn.commit()
conn.close()
print ("time used: ", time()-t0)
