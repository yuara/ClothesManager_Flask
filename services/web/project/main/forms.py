from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, HiddenField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import lazy_gettext as _l
from project import db
from project.models import User, Location


class EditProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About Me"), validators=[Length(min=0, max=140)])
    location_area = SelectField(_l("Area"), coerce=int, id="select_area")
    location_pref = SelectField(
        _l("Prefecture"), coerce=int, id="select_pref", validators=[DataRequired()],
    )
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # Show a user name in placeholder
        self.original_username = original_username

        # Set dropdown choices
        self.location_area.choices = (
            db.session.query(Location.area_id, Location.area_name)
            .distinct(Location.area_name)
            .all()
        )
        self.location_pref.choices = db.session.query(
            Location.id, Location.pref_name
        ).all()

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
