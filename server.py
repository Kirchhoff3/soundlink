from flask import Flask, render_template, request, session, redirect, url_for, Response, current_app
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb
import yaml

app = Flask(__name__)

def create_app():

    app = Flask(__name__)
    app.secret_key = 'your secret key'
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'datauzay123'
    app.config['MYSQL_DB'] = 'music'
    mysql = MySQL(app)


    @app.route("/main")
    def home_page():
        if 'loggedin' in session:
            name = session['name']
            role = session['role']
            cur = mysql.connection.cursor()
            q1 = "SELECT * from advertisement"
            cur.execute(q1)
            ads = cur.fetchall()
            return render_template("main_page.html", name = name, role = role, ads = ads)
    
    @app.route("/myprofile")
    def profile():
        if 'loggedin' in session:
            role = session['role']
            user_id = session['user_id']
            q1 = "SELECT * from user WHERE user_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(q1, [user_id])
            data1 = cur.fetchone()
            bio = data1[2]
            
            if role == 'company':
                q2 = "SELECT * from advertisement WHERE user_id = %s"
                cur.execute(q2, [user_id])
                data2 = cur.fetchall()
                if data2:
                    ad = data2
                    apps = None
                    ads = None
                else:
                    info = None
                    active = None
                    ad_id = None
                    apps = None
                    ads = None
                    ad = []
            else:
                ad = None
                active = None
                ad_id = None
                info = None
                q3 = "SELECT * from application WHERE user_id = %s"
                q4 = "SELECT * from advertisement"
                cur.execute(q3, [user_id])
                data3 = cur.fetchall()
                cur.execute(q4)
                ads = cur.fetchall()
                if data3:
                    apps = data3
                else:
                    apps = []
                    ads = None
            
            return render_template("profile.html", bio = bio, name = session['name'], role = role, ad = ad, apps = apps, ads = ads)
        else:
            return redirect(url_for('login'))

    @app.route('/apply/<int:ad_id>', methods = ['GET', 'POST'])
    def apply(ad_id):
        cur = mysql.connection.cursor()
        name = session['name']
        role = session['role']
        user_id = session['user_id']
        if role == 'musician':
            if request.method == 'POST':
                userdata = request.form
                songname = userdata['songname']
                link = userdata['link']
                q1 = "INSERT INTO application(user_id, ad_id, song_name, link, username, accepted) VALUES(%s, %s, %s, %s, %s, %s)"
                cur.execute(q1, (user_id, ad_id, songname, link, name, 0))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('home_page'))
            return render_template("apply.html")


    @app.route("/", methods = ['GET', 'POST'])
    def login():

        if request.method == 'POST' and 'mail' in request.form and 'password' in request.form:
            # Create variables for easy access
            mail = request.form['mail']
            password = request.form['password']
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM mail_p WHERE mail = %s AND password = %s', (mail, password,))
            # Fetch one record and return result
            account = cursor.fetchone()
            
    
            if account:
                our_mail = account['mail']
                cursor.execute('SELECT * FROM mail_u WHERE mail = %s', [our_mail])
                # Fetch one record and return result
                mail_a = cursor.fetchone()
                user_id_fetch = mail_a['user_id']
                # If account exists in accounts table in out database
                cursor.execute('SELECT * FROM user WHERE user_id = %s', [user_id_fetch])
                # Fetch one record and return result
                taken_id = cursor.fetchone()
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['mail'] = account['mail']
                session['user_id'] = user_id_fetch
                session['name'] = taken_id['name']
                session['role'] = taken_id['role']
                # Redirect to home page
                return redirect(url_for('home_page'))
            else:
                # Account doesnt exist or username/password incorrect
                error = 'Incorrect username/password!'
                return 'Incorrect username/password!<a href="/" class="button">Try Again</a>'
        return render_template("login.html")
    
    @app.route("/register", methods = ['GET', 'POST'])
    def register():

        error = ''
        if request.method == 'POST'and 'uname' in request.form and 'password' in request.form and 'mail' in request.form and 'role' in request.form:

            userdata = request.form
            name = userdata['uname']
            role = userdata['role']
            mail = userdata['mail']
            password = userdata['password']
            cur = mysql.connection.cursor()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM mail_p WHERE mail = %s', [mail])
            control = cursor.fetchone()
            if control:
                error = 'Account already exists!'
            else:
                q1 = "INSERT INTO mail_p(mail, password) VALUES(%s, %s)"
                q2 = "INSERT INTO user(name, role) VALUES(%s, %s)"
                q3 = "INSERT INTO mail_u(mail, user_id) VALUES(%s, %s)" 
                cur.execute(q1, (mail, password))
                cur.execute(q2, (name, role))
                lastid = cur.lastrowid
                cur.execute(q3, (mail, lastid))

                mysql.connection.commit()
                cur.close()
                return redirect(url_for('login'))
        return render_template("register.html", error = error)
    

    @app.route("/edit_profile", methods = ['GET', 'POST'])
    def edit():
        if request.method == 'POST':
            userdata = request.form
            bio = userdata['bio']
            user_id = session['user_id']
            cur = mysql.connection.cursor()
            q2 = "UPDATE user SET biography=%s WHERE user.user_id = %s"
            cur.execute(q2, (bio, user_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('profile'))


        return render_template("edit.html", role = session['role'])

    @app.route("/account")
    def account():
        if 'loggedin' in session:
            role = session['role']
            return render_template("account.html", role = role)
        else:
            return redirect(url_for('login'))

    @app.route("/advertise", methods = ['GET', 'POST'])
    def advertise():
        name = session['name']
        role = session['role']
        user_id = session['user_id']
        if request.method == 'POST':
            active = 1
            cur = mysql.connection.cursor()   
            userdata = request.form
            info = userdata['info']
            q1 = "INSERT INTO advertisement(user_id, info, username, active) VALUES(%s, %s, %s, %s)"
            cur.execute(q1, (user_id, info, name, active))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('profile'))

        return render_template("advertise.html", name = name, role = role)

    @app.route('/logout')
    def logout():   
        # Remove session data, this will log the user out
        session.pop('loggedin', None)
        session.pop('mail', None)
        session.pop('user_id', None)
        session.pop('name', None)
        # Redirect to login page
        return redirect(url_for('login'))
    
    @app.route('/remove_ad/<int:ad_id>')
    def remove(ad_id):
        cur = mysql.connection.cursor()
        q2 = "UPDATE advertisement SET active=%s WHERE ad_id = %s"
        cur.execute(q2, (0, ad_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('profile'))   

    @app.route('/delete_ad/<int:ad_id>')
    def delete(ad_id):
        cur = mysql.connection.cursor()
        q2 = "DELETE FROM advertisement WHERE ad_id = %s;"
        cur.execute(q2, [ad_id])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('profile'))     

    @app.route("/applications/<int:ad_id>")
    def apps(ad_id):
        if 'loggedin' in session:
            name = session['name']
            role = session['role']
            cur = mysql.connection.cursor()
            q1 = "SELECT * FROM application WHERE ad_id = %s"
            cur.execute(q1, [ad_id])
            apps = cur.fetchall()
            return render_template("applications.html", name = name, role = role, apps = apps)
        
        else:
            return redirect(url_for('login'))
    
    @app.route('/confirm/<int:app_id>')
    def confirm_app(app_id):
        cur = mysql.connection.cursor()
        q2 = "UPDATE application SET accepted=%s WHERE app_id = %s;"
        cur.execute(q2, (1, app_id))
        q3 = "SELECT * FROM application WHERE app_id = %s;"
        cur.execute(q3, [app_id])
        app = cur.fetchone()
        ad_id = app[1]
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('apps', ad_id = ad_id))

    @app.route('/cancel_app/<int:app_id>')
    def delete_app(app_id):
        cur = mysql.connection.cursor()
        q2 = "DELETE FROM application WHERE app_id = %s;"
        cur.execute(q2, [app_id])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('profile'))
    
    @app.route('/search', methods = ['GET', 'POST'])
    def search():
        name = session['name']
        role = session['role']
        key = request.form['key']
        key = '%' + key + '%'
        cur = mysql.connection.cursor()
        q2 = "SELECT * FROM advertisement WHERE info LIKE %s OR username LIKE %s;"
        cur.execute(q2, (key, key))
        results = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template("search.html", results = results, role = role)

    @app.route('/contact/<int:app_id>')
    def contact(app_id):
        cur = mysql.connection.cursor()
        q1 = "SELECT user_id FROM application WHERE app_id = %s;"
        cur.execute(q1, [app_id])
        user = cur.fetchone()
        q2 = "SELECT * FROM mail_u WHERE user_id = %s;"
        cur.execute(q2, [user])
        data = cur.fetchone()
        mail = data[1]
        q3 = "SELECT * FROM user WHERE user_id = %s;"
        cur.execute(q3, [user])
        applier = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        return render_template("contact.html", mail = mail, applier = applier)



    return app



if __name__  == "__main__":
   
    
    app = create_app()
    
    app.run(host="0.0.0.0", port=8080, debug = True)
