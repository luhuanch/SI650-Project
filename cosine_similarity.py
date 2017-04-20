from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine
import sqlite3
import re

conn = sqlite3.connect('reviews.db')
cur = conn.cursor()

q = 'SELECT review_id, review_text FROM Review'
cur.execute(q)

rows = cur.fetchall()

for frow in rows:
    for srow in rows:
        if frow[1] == srow[1]:
            continue
        else:
            reviews = [frow[1], srow[1]]
            try:
                vect = CountVectorizer()
                count = vect.fit_transform(reviews)
                cosine = 1 - pairwise_distances(count, metric='cosine')[0][1]
            except:
                continue
            if cosine < 0.9:
                continue
            q = 'INSERT INTO Cosine VALUES (?, ?, ?)'
            cur.execute(q, (frow[0], srow[0], cosine))
            conn.commit()

conn.close()
