from flask import Flask, render_template, current_app, abort
from flask_mysqldb import MySQL
from datetime import datetime
import server




def home_page():
    
    
    return render_template("main_page.html", )


def profile():

    return render_template("profile.html", profile = sorted(profile))


def login():
    return render_template("login.html")


def register():
    return render_template("register.html")

