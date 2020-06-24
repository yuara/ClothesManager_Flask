from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired
from flask_babel import lazy_gettext as _l
from project import db
from project.models import User, Category, Shape


class EditProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About Me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l("Please use a different username."))


class PostForm(FlaskForm):
    post = TextAreaField(
        _l("Say something"), validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField(_l("Submit"))


class SearchForm(FlaskForm):
    q = StringField(_l("Search"), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enable" not in kwargs:
            kwargs["csrf_enable"] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class MessagesForm(FlaskForm):
    message = TextAreaField(
        _l("Message"), validators=[DataRequired(), Length(min=0, max=140)]
    )
    submit = SubmitField(_l("Submit"))


class ClothesForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired(), Length(min=1, max=20)])
    note = TextAreaField(
        _l("Note"), validators=[DataRequired(), Length(min=0, max=140)]
    )
    child_category = SelectField(
        _l("Category"), coerce=int, validators=[InputRequired()]
    )
    shape = SelectField(_l("Shape"), coerce=int, validators=[InputRequired()])
    submit = SubmitField(_l("Submit"))

    def __init__(self, *args, **kwargs):
        super(ClothesForm, self).__init__(*args, **kwargs)
        self.child_category.choices = [
            (x.child_id, x.child_name) for x in Category.query.all()
        ]
        self.shape.choices = [(x.id, x.name) for x in Shape.query.all()]
