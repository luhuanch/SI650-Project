"""
This program uses data from Review and Cosine to find truthful and fake reviews.

truthful reviews: has more than 5 reactions and more than 80 percent of people
                  think it's useful.
fake reviews: 1. reviews from table Cosine will be treated as fake reviews;
              2. reviews wrote by users who wrote more than 3 reviews in the table
              Cosine will be treated as fake reviews;
              3. reviews with more than 10 reactions and less than 10 percent find
              it useful will be treated as fake reviews.
"""
import sqlite3
from time import time
import re

t0 = time()
conn = sqlite3.connect("reviews_with_Cosine.db")
cur = conn.cursor()

# get review ids from Cosine and treat these as fake reviews
cur.execute("SELECT review_id_1, review_id_2 from Cosine")
rows = cur.fetchall()
duplicate_reviews = []
for row in rows:
    duplicate_reviews.append(row[0])
    duplicate_reviews.append(row[1])
fake_review_ids = [i for i in set(duplicate_reviews)]
truthful_review_ids = []

# find fake review writers
fake_count = {}
cur.execute("SELECT review_id, user_id, helpfulness from Review")
rows = cur.fetchall()
for row in rows:
    if row[0] in fake_review_ids:
        try:
            fake_count[row[1]] += 1
        except:
            fake_count[row[1]] = 1
fake_users = [item[0] for item in fake_count.items() if item[1]>=3]

# add reviews written by fake users to fake_review_ids
# add helpful reviews to truthful reviews
for row in rows:
    if not row[0] in fake_review_ids:
        if row[1] in fake_users:
            fake_review_ids.append(row[0])
            continue
        helpfulness = re.findall(r'[0-9]+', row[2])
        if int(helpfulness[1]) >= 10 and int(helpfulness[0])/int(helpfulness[1]) <= 0.1:
            fake_review_ids.append(row[0])
            continue
        if int(helpfulness[1]) >= 5 and int(helpfulness[0])/int(helpfulness[1]) >= 0.8:
            truthful_review_ids.append(row[0])

# create a table labels to store fake(0) and truthful(1) reviews
cur.execute("DROP TABLE IF EXISTS Labels")
cur.execute("create table Labels(label integer, review_id integer)")
fake_reviews = zip(len(fake_review_ids)*[0], fake_review_ids)
truthful_reviews = zip(len(truthful_review_ids)*[1], truthful_review_ids)
cur.executemany("INSERT INTO Labels (label, review_id) VALUES (?, ?)", fake_reviews)
cur.executemany("INSERT INTO Labels (label, review_id) VALUES (?, ?)", truthful_reviews)
conn.commit()
conn.close()
print ("time used:", time()-t0)
