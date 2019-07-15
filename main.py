from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogz@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = "z!97tvMYD_E92zNVBGUq-_UzfGHQVk"
db = SQLAlchemy(app)


# Create Blog class for database persistence
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    posted = db.Column(db.DateTime, default=datetime.datetime.now())
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, posted):
        self.title = title
        self.body = body
        self.posted = posted

    def __repr__(self):
        return f'Post Title: "{self.title}" | Post Date: {self.posted}'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"Username: {self.username}"




@app.route("/blog")
def index():
    post_id = request.args.get('id')

    # If there's a GET parameter, sends to single-post form with post id
    if post_id:
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html', single_post=single_post)
    else:
        # Shows all blog posts in ascending order
        # all_posts = Blog.query.all()

        # Bonus mission to sort in descending order using DateTime
        all_posts = Blog.query.order_by(Blog.posted.desc()).all()
        return render_template("blog.html", all_posts=all_posts)


@app.route("/newpost", methods=["POST", "GET"])
def add_post():

    # If there's a title and body submitted, create the objext
    if request.method == "POST":
        post_date = request.args.get('posted')
        new_title = request.form["title"]
        new_body = request.form["body"]
        new_post = Blog(new_title, new_body, post_date)

        # Make sure there's something in title and body fields, commit to database
        if len(new_title) != 0 and len(new_body) != 0:
            db.session.add(new_post)
            db.session.commit()

            # Get the post id from just created objext and redirect to the single-post page
            post_link = f"/blog?id={new_post.id}"
            return redirect(post_link)

        # If there's nothing in the title or the body field,flash an error message
        # render form again, returning any submitted content
        else:
            flash("Posts require both a title and a body...try again!")
            return render_template("add_post.html", new_title=new_title, new_body=new_body, title="Add a Blog Entry")

    # Show the form
    else:
        return render_template("add_post.html")


if __name__ == "__main__":
    app.run()