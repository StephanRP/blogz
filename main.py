from flask import Flask, request, redirect, render_template, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    #def __repr__(self):
    #    return '<Blog %r>' % self.name

@app.route("/")
def index():
    if not request.args:
        username = User.query.order_by(User.id).all()
        return render_template('index.html',title="Users", username=username)
    elif request.args.get('id') and request.args.get('user'):
        user_id = request.args.get('id')
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        blog = Blog.query.filter_by(id=user_id).all()
        return render_template('user_blogs.html', blog=blog, user=user)
    elif request.args.get('user'):
        user_id = request.args.get('id')
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        blog = Blog.query.filter_by(id=user_id).all()
        return render_template('user_blogs.html', blog=blog, user=user)
        

        
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET']) # Not sure if needed yet
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET']) #not sure if needed yet
def signup():
    user_error = ''
    pass_error = ''
    v_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if username == '':
            user_error = 'Input field empty'
        if password == '':    
            pass_error = 'Input field empty'
        if verify == '':
            v_error = 'Input field empty'
        if existing_user:
            user_error = "Username already exists"
        if password != verify:
            pass_error = "Passwords do not match"
            v_error = pass_error
        if len(username) < 3:
            user_error ="Input field must be longer than 3 characters"
        if len(password) < 3:
            pass_error = "Input field must be longer than 3 characters"
        elif not existing_user and password == verify and password != '' and username != '' and verify != '':
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
    return render_template('signup.html', user_error=user_error, pass_error=pass_error, v_error=v_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog')
def blog():
    encoded_error = request.args.get("error")

    if not request.args:
        blogs = Blog.query.all()
        blog_body = Blog.query.all()
        user = User.query.all()
        blog_id = request.args.get('id')
        return render_template('blogs.html',title="Build A Blog", 
        blogs=blogs, blog_body=blog_body)
    
    elif request.args.get('id'):
        blog_id = request.args.get('id')
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_post.html', blog=blog, user=user, username=username)

    elif request.args.get('user'):
        user_id = request.args.get('id')
        username = request.args.get('user')
        user = User.query.filter_by(username=username).first()
        blog = Blog.query.filter_by(id=user_id).all()
        return render_template('user_blogs.html', blog=blog, user=user)

    if request.endpoint == 'newpost':
        return redirect('/newpost')
    
    if request.endpoint == 'blog':
        return redirect('/blog')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    error = None
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_name = request.form['blog_name'] 
        blog_body = request.form['blog_body']
        if blog_name == '':
            error = 'No title provided'
        if blog_body == '':
            error = "No content provided"
        else:     
            new_blog_body = Blog(blog_name, blog_body, owner) #not sure if owner_id connects to actual user id
            db.session.add(new_blog_body)
            db.session.commit()
            return redirect(url_for('blog', id=new_blog_body.id))

    return render_template('newpost.html',title="Build A Blog", error=error)


app.secret_key = 'secretkey'
if __name__ == '__main__':
    app.run()