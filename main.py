from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(120))
    completed = db.Column(db.Boolean)

    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.completed = False

    #def __repr__(self):
    #    return '<Blog %r>' % self.name

@app.route("/")
def index():
    return render_template('base.html')

@app.route('/blog')
def blog():
    encoded_error = request.args.get("error")

    if not request.args:
        blogs = Blog.query.filter_by(completed=False).all()
        blog_body = Blog.query.filter_by(completed=False).all()
        completed_blogs = Blog.query.filter_by(completed=True).all()
        return render_template('blogs.html',title="Build A Blog", 
        blogs=blogs, blog_body=blog_body,completed_blogs=completed_blogs)
    
    elif request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('single_post.html', blog=blog)

    if request.endpoint == 'newpost':
        return redirect('/newpost')
    
    if request.endpoint == 'blog':
        return redirect('/blog')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    error = None
    if request.method == 'POST':
        blog_name = request.form['blog_name'] # was 'task'
        blog_body = request.form['blog_body']
        if blog_name == '':
            error = 'No title provided'
        if blog_body == '':
            error = "No content provided"
        else:     
            new_blog_body = Blog(blog_name, blog_body)
            db.session.add(new_blog_body)
            db.session.commit()
            return redirect(url_for('blog', id=new_blog_body.id))

    return render_template('newpost.html',title="Build A Blog", error=error)


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id']) # was task_id and 'task-id'
    blog = Blog.query.get(blog_id)
    blog.completed = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/')

app.secret_key = 'secretkey'
if __name__ == '__main__':
    app.run()