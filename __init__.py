# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, redirect, session, flash, request
from dbconnect import connection
from wtforms import Form, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from datetime import datetime
import time
from functools import wraps


PER_PAGE = 10
 
app = Flask(__name__)
app.config["SECRET_KEY"] = "Thisi23omeRa0nd0mstr2ingt0K22PThisS3cr3t"

def format_datetime(timestamp):
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("You need to login first.")
			return redirect(url_for('login_page'))
	return wrap


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    c,conn = connection()
    user_id = c.execute("SELECT uid FROM users WHERE username = %s", session['username'])
    user_id = c.fetchone()[0]

    return user_id

@app.route('/')
def homepage():
        return render_template("index.html")


@app.route('/about/')
def notice_page():
    return render_template("notice.html")

@app.route('/<username>/')
@login_required
def user_board(username):
	try:
		c, conn = connection()
		user_id = get_user_id(session['username'])
		message = c.execute("SELECT posts.*, users.* FROM posts, users WHERE posts.author_id = users.uid AND users.uid = %s ORDER BY posts.pub_date DESC LIMIT 50", (user_id))
		message = c.fetchall()

		c.close()
		conn.close()
		gc.collect()
		return render_template("board.html", messages=message)
	except Exception, e:
		flash(e)
		return render_template("notice.html")
	



@app.route('/board/', defaults={'page':1})
@app.route('/board/page/<int:page>')
def board(page):
	try:
		
		startat = (page - 1) * PER_PAGE
		# username, text, published time을 보여줘야 함..
		c, conn = connection()
		message = c.execute("SELECT posts.*, users.* FROM posts, users WHERE posts.author_id = users.uid ORDER BY posts.pub_date DESC LIMIT %s, %s;", (startat, PER_PAGE))
		message = c.fetchall()
		print message[2:4]
		c.close()
		conn.close()
		gc.collect()
		next_page = page + 1
		prev_page = page - 1
		#current_page = requests.get(page)
		#print current_page
		
		
		
		return render_template("board.html", messages=message, next_page=next_page, prev_page=prev_page)

	except Exception, e:
		flash(e)
		return render_template("notice.html")

@app.route('/post/', methods=['POST'])
@login_required
def add_post():
	if request.form['text']:
		c,conn = connection()
		user_id = get_user_id(session['username'])
		c.execute("INSERT INTO posts (author_id, text, pub_date, hashtag) VALUES (%s, %s, %s, %s)", 
			(user_id, request.form['text'], int(time.time()), request.form['hashtag']))
		conn.commit()
		flash("Thanks for sharing!")
		c.close()
		conn.close()
		gc.collect()
	return redirect(url_for('board'))

@app.route('/<hashtag>/')
def hashpage(hashtag):
	try:
		c, conn = connection()
		
		message = c.execute("SELECT posts.* FROM posts WHERE posts.hashtag = %s ORDER BY posts.pub_date" (hashtag))
		message = c.fetchall()
		c.close()
		conn.close()
		gc.collect()
		return render_template("hashtag.html", messages=message)


	except Exception, e:
		flash(e)
		return redirect(url_for('board'))





@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''

    try:
        c, conn = connection()
        
        if request.method == 'POST':

            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))
            data = c.fetchone()[2]           

            if sha256_crypt.verify(request.form['password'], data):
            
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in! Welcome "+str(session['username'])+"!!")

                return redirect(url_for("board"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)  





@app.route("/logout/")
@login_required
def logout():
	session.clear()
	flash("You have been logged out!")
	gc.collect()
	return redirect(url_for('board'))

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=2, max=20)])
    password = PasswordField('Password', [validators.Required()])
    email = TextField('Email', [validators.Required(), validators.Length(min=2, max=40)])

@app.route('/register/', methods=["GET", "POST"])
def register_page():
	try:
		form = RegistrationForm(request.form)
		if request.method == "POST" and form.validate():
			username = form.username.data
			password = sha256_crypt.encrypt((str(form.password.data)))
			email = form.email.data
			c, conn = connection()

			x = c.execute("SELECT * FROM users WHERE username = %s", (username,))

			if int(x) > 0:
				flash("That username is already taken, please choose another")
				return render_template('register.html', form=form)

			else:
				c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
			          (thwart(username), thwart(password), thwart(email)))

				conn.commit()
				flash("Thanks for registering!")
				c.close()
				conn.close()
				gc.collect()

		
				session['logged_in'] = True
				session['username'] = username

				return redirect(url_for('board'))

		return render_template("register.html", form=form)
		
	except Exception as e:
		return(str(e))




app.jinja_env.filters['datetimeformat'] = format_datetime


if __name__ == "__main__":
	app.run(debug=True, host = '0.0.0.0')