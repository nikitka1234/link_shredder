import os
import random
import string

from flask import Flask, render_template, redirect

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class URLForm(FlaskForm):
    original_url = StringField('Ссылка ', validators=[DataRequired(message="Поле не должно быть пустым")])
    submit = SubmitField('Укоротить ссылку')


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'

db = SQLAlchemy(app)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(255))
    short = db.Column(db.String(255))
    visits = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Urls {self.id}: {self.title[:20]}..."


with app.app_context():
    db.create_all()


def get_short():
    while True:
        short = ''.join(random.choices(string.ascii_letters + string.ascii_letters, k=6))

        if Urls.query.filter(Urls.short == short).first():
            continue

        return short


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm()

    if form.validate_on_submit():
        ur = Urls()
        ur.original_url = form.original_url.data
        ur.short = get_short()
        db.session.add(ur)
        db.session.commit()

        return redirect("/urls")

    return render_template("index.html", form=form)


@app.route("/urls", methods=["GET"])
def urls():
    ur = Urls.query.all()
    return render_template("urls.html", urls=ur[::-1])


@app.route("/<string:short>", methods=["GET"])
def short_url(short):
    ur = Urls.query.filter(Urls.short == short).first()

    if ur:
        ur.visits += 1
        db.session.add(ur)
        db.session.commit()

        return redirect(ur.original_url)

    return "Пусто"
