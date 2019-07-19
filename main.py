from flask import Flask, request, redirect, render_template, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime

#TODO: create Sign Up link

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id): 
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='poster')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

# @app.route('/')
# def index_redirect():
#     return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
        if not request.form['title']:
            body = request.form['body']
            flash('Please enter a title')
            return render_template('new-post.html', body=body)
        elif not request.form['body']:
            title = request.form['title']
            flash('Post cannot be empty!')
            return render_template('/new-post.html', title=title)
        else:
            blog_title = request.form['title']
            blog_body = request.form['body']
            user = User.query.filter_by(username=session['username']).first()
            user_id = user.id
            post = Blog(blog_title, blog_body, user_id)
            db.session.add(post)
            db.session.commit()
            id = post.id
        return redirect('/blog?id='+str(id))

    if request.args.get('user'):
        user = request.args.get('user')
        user_id = User.query.filter_by(username=user).first().id
        #print (str(user.username))
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user-page.html', posts=posts)

    if request.args.get('id'):
        id = request.args.get('id')
        post = Blog.query.filter_by(id=id).first()
        return render_template('display-post.html', title=post.title, body=post.body)

    posts = Blog.query.order_by(desc(Blog.pub_date)).all()
    return render_template('blog.html', posts=posts)

@app.route('/')
def index():
    users = User.query.all()
    for user in users:
        return render_template('index.html', users=users)

@app.route('/new-post')
def new_post():
    return render_template('new-post.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username=request.args.get('username')
    if not username:
        username = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(username)

        #validate username
        if len(username) < 3 or len(username) > 16:
            flash('User Names must be between 3 and 16 characters')
        if ' ' in username:
            flash('User Names may not contain spaces')
        if not username:
            flash('Please enter a username')
        
        #validate password
        if len(password) < 3 or len(password) > 20:
            flash('Password must be between 3 and 20 characters')
        if not password:
            flash('Please enter a password')

        #check for correct password
        else:
            user = User.query.filter_by(username=username).first()
            if user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/blog')
            else:
                flash('User password incorrect, or user does not exist',)


    
    return render_template('login.html', username=username)

# @app.route('/validate', methods=['POST'])
# def validate():
#     username = request.form['username']
#     password = request.form['password']

    
#     #validate username
#     if len(username) < 3 or len(username) > 16:
#         flash('User Names must be between 3 and 16 characters')
#     if ' ' in username:
#         flash('User Names may not contain spaces')
#     if not username:
#         flash('Please enter a username')
    
#     #validate password
#     if len(password) < 3 or len(password) > 20:
#         flash('Password must be between 3 and 20 characters')
#     if not password:
#         flash('Please enter a password')

#     #check for correct password
#     else:
#         user = User.query.filter_by(username=username).first()
#         if user and user.password == password:
#             session['username'] = username
#             response = make_response(render_template('blog.html'))
#             response.set_cookie('username', user.username)
#             flash("Logged in")
#             return response
#         else:
#             flash('User password incorrect, or user does not exist',)
            
#     return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #validate username
        if len(username) < 3 or len(username) > 16:
            flash('User Names must be between 3 and 16 characters')
        if ' ' in username:
            flash('User Names may not contain spaces')
        if not username:
            flash('Please enter a username')
        
        #validate password
        if password != verify:
            flash('Passwords must match!')
        if len(password) < 3 or len(password) > 20:
            flash('Password must be between 3 and 20 characters')
        if not password:
            flash('Please enter a password')
        if not verify:
            flash('Please verify password')

        #check for existing user
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if password != verify:
                flash("Passwords must match")
                return render_template('signup.html')
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("You've successfully signed up!")
            print(session)
            return redirect('/blog')
        else:
            flash("This username is already taken.")

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()