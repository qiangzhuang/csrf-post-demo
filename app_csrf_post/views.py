from flask import Flask, g, request, session, render_template, flash, redirect
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from . import app, db, models


@app.route("/")
def index():

	# if not valid session return login page
	# if valid session, redirect to show account funds page
	try:
		if session['logged_in']:
			return redirect("/accountsummary", code=302, Response=None)
	except:
		pass
	return redirect("/login", code=302, Response=None)

@app.route("/accountsummary")
def summary():
	try:
		if session['logged_in']:
			u = models.UserAccount.query.filter_by(username=session['username']).first()
			return render_template("accountsummary.html", amount = u.amount)
	except:
		pass
	return redirect("/login", code=302, Response=None)

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		user = models.UserAccount.query.filter_by(username=request.form["username"]).first()
		print "checking login"
		if user and user.pass_is_equal(request.form["password"]):
			print "valid login, creating session"
			session["logged_in"] = True
			session["username"] = request.form["username"]
			return redirect("/accountsummary")
		else:
			flash("Invalid login")
	elif request.method == "GET":
		try:
			if session['logged_in']:
				return redirect("/accountsummary")
		except:
			pass

	return render_template("login.html")

@app.route("/logout")
def logout():
	#destroy session
	session["logged_in"] = False
	session.pop("username", None)
	session.pop("logged_in", None)
	session.clear()
	return redirect("/login")

@app.route("/transfer", methods=["POST"])
def transfer():
	transferto = request.form["username"]
	amount = float()
	try:
		amount = float(request.form["amount"])
		print amount
		user = models.UserAccount.query.filter_by(username=request.form["username"]).first()
		print user
		if user:
			currentuser = models.UserAccount.query.filter_by(username=session["username"]).first()
			currentuser.amount = currentuser.amount - amount
			user.amount = user.amount + amount
			db.session.commit()
		else:
			flash("User does not exist, transfer failed", category='message')
			return redirect("/accountsummary", code=302, Response=None)
	except:
		flash("transfer unsuccessful", category='message')
		return redirect("/accountsummary", code=302, Response=None)
	print transferto, amount
	flash("transfer successful to {0}: {1}".format(transferto, amount))
	return redirect("/accountsummary", code=302, Response=None)

