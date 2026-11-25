import os
from dotenv import load_dotenv

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS","")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    rating: Mapped[float|int] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)

with app.app_context():
    db.create_all()


# Home page
@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating.desc()))
    all_movies = result.scalars().all()
    return render_template("index.html", movies=all_movies)


# Add movie form creation
class MovieForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    year = StringField(label="Year", validators=[DataRequired()])
    description = TextAreaField(label="Description")
    # Added coerce = int so WTForms converts and compares values as integers
    rating = SelectField(label="Rating", choices=[(1,"⭐"),(2,"⭐⭐"),(3,"⭐⭐⭐"),(4,"⭐⭐⭐⭐"),(5,"⭐⭐⭐⭐⭐")], coerce = int)
    ranking = SelectField(label="Ranking", choices=[(1,"⭐ (1 - Lowest)"), (2,"⭐⭐ (2 - Low)"), (3,"⭐⭐⭐ (3 - Average)"),(4,"⭐⭐⭐⭐ (4 - High)"),(5,"⭐⭐⭐⭐⭐ (5 - Top Rank)")], coerce = int)
    review = StringField(label="Review")
    img_url = StringField(label="Image URL")
    submit = SubmitField(label="Submit", render_kw={"onclick": "showLoader('Saving movie...')"},)

# Add movie form page and submission
@app.route("/add", methods=['GET', 'POST'])
def add():
    add_movie_form = MovieForm()
    if add_movie_form.validate_on_submit():
        new_movie = Movie(
            title = add_movie_form.title.data,
            year = int(add_movie_form.year.data),
            description = add_movie_form.description.data,
            rating = add_movie_form.rating.data,
            ranking = add_movie_form.ranking.data,
            review = add_movie_form.review.data,
            img_url = add_movie_form.img_url.data,
        )
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add.html", form=add_movie_form)


# Edit movie
@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    # movie_id = request.args.get("id")   # this is for URL: ?id=2
    movie_data = db.get_or_404(Movie, id)
    edit_movie_form = MovieForm(obj=movie_data)

    if edit_movie_form.validate_on_submit():
        movie_data.title = edit_movie_form.title.data
        movie_data.year  = int(edit_movie_form.year.data)
        movie_data.description = edit_movie_form.description.data
        movie_data.rating = edit_movie_form.rating.data
        movie_data.ranking = edit_movie_form.ranking.data
        movie_data.review = edit_movie_form.review.data
        movie_data.img_url = edit_movie_form.img_url.data

        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", form=edit_movie_form, movie=movie_data)


# Delete movie
@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    movie_data = db.get_or_404(Movie, id)
    db.session.delete(movie_data)
    db.session.commit()
    return redirect(url_for("home"))


# 404 - Page not found
@app.errorhandler(404)
def page_not_found(error):
    # Note the '404' status code returned after render_template
    return render_template("404.html"), 404



if __name__ == '__main__':
    app.run(debug=True)
