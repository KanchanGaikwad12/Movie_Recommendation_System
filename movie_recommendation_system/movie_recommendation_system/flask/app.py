from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import sqlite3

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pickle

app = Flask(__name__)
app.secret_key = '5766ghghgg7654dfd7h997f'
      

@app.route('/')
def home():
    return render_template('signup.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists in the database
        conn = sqlite3.connect('C:/Users/Admin/Desktop/movie_recommendation_system/database/Users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user is not None:
            # If the user already exists, add a flash message and redirect back to the signup page
            session['message'] = 'Username already taken. Please choose another one.'
            
            return redirect(url_for('signup', error='Username already exist.'))
        
            
        else:
            # If the user does not exist, insert the new user into the database and redirect to the login page
            conn = sqlite3.connect('C:/Users/Admin/Desktop/movie_recommendation_system/database/Users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            
            return redirect(url_for('login'))
        
    elif request.args.get('error') is None:    
        return render_template('signup.html')
        
    else:   
        error = request.args.get('error')
        return render_template('signup.html', error=error)



@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('C:/Users/Admin/Desktop/movie_recommendation_system/database/Users.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user is not None:
            session['username'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
   else:
        return render_template('login.html')


@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html', current_user=session['username'])
    return redirect(url_for('login'))   



@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        conn = sqlite3.connect('C:/Users/Admin/Desktop/movie_recommendation_system/database/Users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_feedback (name, email, subject, message) VALUES (?, ?, ?, ?)", (name, email, subject, message))
        conn.commit()
        conn.close()
        return redirect(url_for('contactus'))
    
    
    return render_template('contactus.html') 
    
    
###### machine learning code
df = pd.read_csv('movies_dataset.csv')

df['Description'] = df['Description'].str.lower()

df['Description'] = df['Description'].str.replace('[^\w\s]','')

stop_words = set(stopwords.words('english'))
df['Description'] = df['Description'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df['Description'])

cosine_sim = cosine_similarity(tfidf_matrix)

def get_recommendations(title, cosine_sim=cosine_sim, df=df):
    
    indices = pd.Series(df.index, index=df['Title']).drop_duplicates()
    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    
    movie_titles = ", ".join(df['Title'].iloc[movie_indices].values)

    return movie_titles

@app.route('/movie')
def movie_recommender():
    return render_template('movie.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')


@app.route('/predict',methods=['POST'])
def predict():
#     '''
#     For rendering results on HTML GUI
    
#     '''
    if request.method=='POST':
        
        user_input = request.form.get('movie_name')
        prediction = get_recommendations(user_input)
        
        return render_template('movie.html', prediction_text='{}'.format(prediction))
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
