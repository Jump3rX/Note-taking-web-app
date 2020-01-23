from flask import Flask,render_template, request, session, url_for, redirect,flash
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key22'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'orderly' 
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('index'))
    return wrap


@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        entered_password = request.form['password']
        cur = mysql.connection.cursor()
        results = cur.execute("SELECT * FROM users WHERE email = %s",[email])
        if results > 0:
            data = cur.fetchone()
            db_password = data['password']

            if sha256_crypt.verify(entered_password,db_password):
                session['logged_in'] = True
                session['email'] = email
                flash('Log in success!',category='success') 
                return redirect(url_for('notes'))
            else:
                flash('Details incorrect!!',category='error')
                return render_template("index.html")
        else:
            flash("User does not exist, please register!")
            return redirect(url_for('signup'))

    return render_template('index.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = sha256_crypt.encrypt(str(request.form['password']))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name,email,password) VALUES(%s,%s,%s)",(name,email,password))
        mysql.connection.commit()
        cur.close()
        flash("Thanks for signing up!",category="success")
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/add_notes',methods=['GET','POST'])
@login_required
def add_notes():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO notes(title,body,author) VALUES(%s,%s,%s)",(title,body,session['email']))
        mysql.connection.commit()
        cur.close()
        flash('Note added successfuly',category='success')
    return render_template('add_notes.html')


@app.route('/notes')
@login_required
def notes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes WHERE author = %s",[session['email']])
    notes = cur.fetchall()
    cur.close()
    return render_template('notes.html',notes=notes)

@app.route('/single_note/<string:id>/')
@login_required
def single_note(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes WHERE noteId = %s",[id])
    note = cur.fetchone()
    return render_template('single_note.html',note=note)




@app.route('/edit_note/<string:noteId>',methods=['GET','POST'])
@login_required
def edit_note(noteId):
    cur = mysql.connection.cursor()
    cur.execute("SELECT title,body FROM notes WHERE noteId = %s",(noteId))
    e_note = cur.fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE notes SET title=%s, body=%s WHERE noteId = %s",(title,body,noteId))
        mysql.connection.commit()
        cur.close()
        flash('note Updated!!')
        return redirect(url_for('notes'))
    return render_template('edit_note.html',e_note=e_note)


@app.route('/delete_note/<string:noteId>',methods=['GET','POST'])
@login_required
def delete_note(noteId):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM notes WHERE noteId = %s",(noteId))
    mysql.connection.commit()
    cur.close()
    flash('Note Deleted!!')
    return redirect(url_for('notes'))

@app.route('/profile')
@login_required
def profile():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s",[session['email']])
    profile = cur.fetchone()
    cur.close()
    return render_template('profile.html',profile=profile)

@app.route('/edit_profile/<string:id>',methods=['GET','POST'])
@login_required
def edit_profile(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name,email FROM users WHERE id = %s",[id])
    profileDetails = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_password = sha256_crypt.encrypt(str(request.form['new-password']))

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",(name,email,new_password,id))
        mysql.connection.commit()
        cur.close()
        flash('Profile Updated succesfully!!')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html',profileDetails=profileDetails)

@app.route('/profile_delete/<string:id>')
@login_required
def profile_delete():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s",[id])
    mysql.connection.commit()
    cur.close()
    session.clear()
    return redirect(url_for('index'))

@app.route('/signout')
@login_required
def signout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
