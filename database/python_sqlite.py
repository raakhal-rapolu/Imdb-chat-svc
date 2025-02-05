#!/usr/bin/env python3


import pandas as pd
import sqlite3

# Load the CSV file with correct encoding
df = pd.read_csv("/home/raakhal-rapolu/PycharmProjects/imdb-chatbot-svc/tmp/imdb_top_1000.csv")

# Rename columns to match SQL table
df.rename(columns={
 "Series_Title": "title",
 "Released_Year": "year",
 "Certificate": "certificate",
 "Runtime": "runtime",
 "Genre": "genre",
 "IMDB_Rating": "imdb_rating",
 "Overview": "overview",
 "Meta_score": "meta_score",
 "Director": "director",
 "Star1": "star1",
 "Star2": "star2",
 "Star3": "star3",
 "Star4": "star4",
 "No_of_Votes": "votes",
 "Gross": "gross"
}, inplace=True)

# Convert 'year' to integer, handling non-numeric cases
df["year"] = pd.to_numeric(df["year"], errors='coerce').fillna(0).astype(int)

# Convert 'meta_score' and 'votes' to integer
df["meta_score"] = pd.to_numeric(df["meta_score"], errors='coerce').fillna(0).astype(int)
df["votes"] = pd.to_numeric(df["votes"], errors='coerce').fillna(0).astype(int)

# Remove " min" from runtime
df["runtime"] = df["runtime"].str.replace(" min", "", regex=True)

# Handle empty values by replacing NaN with empty string
df.fillna("", inplace=True)

# Connect to SQLite database (creates a new DB if it doesn't exist)
conn = sqlite3.connect('imdb_movies.db')
cur = conn.cursor()

# Create the movies table if it doesn't exist
cur.execute("""
CREATE TABLE IF NOT EXISTS movies (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT,
 year INTEGER,
 certificate TEXT,
 runtime TEXT,
 genre TEXT,
 imdb_rating REAL, 
 overview TEXT,
 meta_score INTEGER,
 director TEXT,
 star1 TEXT,
 star2 TEXT,
 star3 TEXT,
 star4 TEXT,
 votes INTEGER,
 gross TEXT
)
""")

# Insert data into the movies table
for _, row in df.iterrows():
 cur.execute("""
 INSERT INTO movies (title, year, certificate, runtime, genre, imdb_rating, overview, meta_score, director, star1, star2, star3, star4, votes, gross)
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
 """, (
 row['title'], row['year'], row['certificate'], row['runtime'], row['genre'],
 row['imdb_rating'], row['overview'], row['meta_score'], row['director'],
 row['star1'], row['star2'], row['star3'], row['star4'], row['votes'], row['gross']
 ))



conn.commit()

# Execute a PRAGMA statement to get the table schema
cur.execute("PRAGMA table_info(movies);")

# Fetch all results
schema = cur.fetchall()

print(schema)
cur.close()
conn.close()

print("Movies data inserted successfully into 'imdb_movies.db'!")