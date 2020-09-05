from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectField,
    HiddenField,
    SubmitField,
)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import lazy_gettext as _l
from project import db
from project.models import User, Location


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Login"))


class RegistrationForm(FlaskForm):
    form_name = HiddenField("form_name")
    username = StringField(_l("Username"), validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    location_area = SelectField(_l("Area"), coerce=int, id="select_area")
    location_pref = SelectField(
        _l("Prefecture"), coerce=int, id="select_pref", validators=[DataRequired()],
    )
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Repeat Password"), validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField(_l("Sign Up"))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # Set choises of dropdown for location_area and location_pref
        self.location_area.choices = (
            db.session.query(Location.area_id, Location.area_name)
            .distinct(Location.area_name)
            .all()
        )
        self.location_pref.choices = db.session.query(
            Location.id, Location.pref_name
        ).all()

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l("Please use a different username."))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l("Please use a different email address."))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset."))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Repeat Password"), validators=[DataRequired(), EqualTo("passowrd")]
    )
    submit = SubmitField(_l("Request Password Reset"))
