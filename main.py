from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    def __init__(self, title, body): 
        self.title = title
        self.body = body


@app.route('/')
def index_redirect():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def index():
    #TODO fix problem with text in fields being cut off at first space after error
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
            post = Blog(blog_title, blog_body)
            db.session.add(post)
            db.session.commit()
            id = post.id
        return redirect('/blog?id='+str(id))

    if request.args.get('id'):
        id = request.args.get('id')
        post = Blog.query.filter_by(id=id).first()
        return render_template('display-post.html', title=post.title, body=post.body)

    posts = Blog.query.order_by(desc(Blog.pub_date)).all()
    return render_template('blog.html', posts=posts)

@app.route('/new-post')
def new_post():
    return render_template('new-post.html')

if __name__ == '__main__':
    app.run()