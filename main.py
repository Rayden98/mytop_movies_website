from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json

my_api = "179b3c2fe3e5a904712a46090a4e44a5"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new_movies_collection.db"
db = SQLAlchemy()
db.init_app(app)
list_movies = []
results = None


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


class RateMovieForm(FlaskForm):
    rating = StringField("Your rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

# with app.app_context():
#    db.create_all()

# with app.app_context():
#    new_movie = Movie(
#        title="Phone Booth",
#        year=2002,
#        description="Publicist Stuart  Shepard finds himself trapped in a phone booth, pinned down by an extortionist's "
#                    "sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads "
#                    "tot a jaw-dropping climax.",
#        rating=7.3,
#        ranking=10,
#        review="My  favourite character was the caller.",
#        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg",
#    )
#    db.session.add(new_movie)
#    db.session.commit()

# with app.app_context():
#    new_movie = Movie(
#        title="Avatar The Way of Water",
#        year=2022,
#        description="Set more than a decade after the events of the first film, learn the story of the Sully family ("
#                    "Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each "
#                    "other safe, the battles they fight to stay alive, and the tragedies they endure.",
#        rating=7.3,
#        ranking=9,
#        review="I laked the water",
#        img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
#    )
#    db.session.add(new_movie)
#    db.session.commit()


@app.route("/")
def home():

    list_movies.clear()

    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    my_all_movies = result.scalars().all()

    for i in range(len(my_all_movies)):
        my_all_movies[i].ranking = len(my_all_movies) - i
    db.session.commit()

    with app.app_context():
        all_movies_object = Movie.query.all()
        for movie in all_movies_object:
            my_movie = {}
            my_movie["title"] = movie.title
            my_movie["year"] = movie.year
            my_movie["description"] = movie.description
            my_movie["rating"] = movie.rating
            my_movie["ranking"] = movie.ranking
            my_movie["review"] = movie.review
            my_movie["img_url"] = movie.img_url
            list_movies.append(my_movie)

    return render_template("index.html", list_movies=list_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    #form = RateMovieForm()
    if request.method == "POST":
        print("my post")
        # UPDATE RATING
        movie_title = request.form['name']
        print(movie_title)
        movie_to_update = db.session.execute(db.select(Movie).where(Movie.title == movie_title)).scalar()
        movie_to_update.rating = request.form["rating"]
        db.session.commit()

        # UPDATE REVIEW
        movie_title = request.form['name']
        movie_to_update = db.session.execute(db.select(Movie).where(Movie.title == movie_title)).scalar()
        movie_to_update.review = request.form["review"]
        db.session.commit()

        return redirect(url_for('home'))

    movie_title = request.args.get('title')
    # movie_selected = db.get_or_404(Movie, movie_title)
    movie_selected = db.session.execute(db.select(Movie).where(Movie.title == movie_title)).scalar()
    return render_template("edit.html", movie=movie_selected)


@app.route("/delete")
def delete():
    with app.app_context():
        print("hello")
        movie_title = request.args.get('title')
        print("hello2")
        print(movie_title)
        book_to_delete = db.session.execute(db.select(Movie).where(Movie.title == movie_title)).scalar()
        db.session.delete(book_to_delete)
        db.session.commit()

        return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    list_movies_same_name = []
    form = MovieForm()

    # Adding the new information
    my_new_information = form.title.data
    if form.validate_on_submit():
        global results
        print(my_new_information)
        original_string = my_new_information
        modified_string = original_string.replace(" ", "%")

        url = f"https://api.themoviedb.org/3/search/movie?query={modified_string}&include_adult=false&language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxNzliM2MyZmUzZTVhOTA0NzEyYTQ2MDkwYTRlNDRhNSIsInN1YiI6IjY0YTVhNWE0ZGExMGYwMDBjNTkzYjM0NiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.YpAi3NpePERbIt_f32Q4pfeFrKIhLZmFWnyIUK9EQUQ"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        results = data["results"]

        list_movies_same_name = []
        for each in results:
            movie_same_name = {}
            movie_same_name["title"] = each["title"]
            movie_same_name["release_date"] = each["release_date"]
            movie_same_name["id"] = each["id"]
            list_movies_same_name.append(movie_same_name)
        return render_template("select.html", form=form, lis_of_movies=list_movies_same_name)

    return render_template("add.html", form=form)


@app.route("/select", methods=["GET", "POST"])
def select():
    print("hello1")
    global results
    print("hello2")
    movie_title = request.args.get("id")

    data_movie = None


    print(movie_title)
    for i in results:
        id = int(movie_title)
        print("hello3")
        if i["id"] == id:
            print(i["title"])
            data_movie = i
            print(i)
            with app.app_context():
                new_movie = Movie(
                    title=i["title"],
                    year=i["release_date"],
                    description=i["overview"],
                    rating=1,
                    ranking=1,
                    review="none",
                    img_url=f"https://image.tmdb.org/t/p/original{i['poster_path']}",
                )
                db.session.add(new_movie)
                print("hello4")
                db.session.commit()
                print("hello5")
                results.clear()
                print(new_movie)
                print(new_movie.title)
        return render_template("edit.html", movie=new_movie)




if __name__ == '__main__':
    app.run(debug=True)
