from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, InputRequired
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from project import db
from project.models import User, Clothes, Category


class ClothesForm(FlaskForm):
    form_name = HiddenField("form_name")
    name = StringField(_l("Name"), validators=[Length(min=0, max=20)])
    parent_category = SelectField(_l("Category"), coerce=int, id="select_parent")
    child_category = SelectField(
        "", coerce=int, validators=[DataRequired()], id="select_child"
    )
    note = TextAreaField(_l("Note"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Submit"))

    def __init__(self, *args, **kwargs):
        super(ClothesForm, self).__init__(*args, **kwargs)
        self.parent_category.choices = (
            db.session.query(Category.parent_id, Category.parent_name)
            .distinct(Category.parent_name)
            .all()
        )
        self.child_category.choices = db.session.query(
            Category.id, Category.child_name
        ).all()


class OutfitForm(FlaskForm):
    name = StringField(_l("Name"), validators=[Length(min=0, max=30)])
    jackets = SelectField(_l("Jackets"), coerce=int, default=0)
    tops_1 = SelectField(_l("Tops 1"), coerce=int, validators=[DataRequired()])
    tops_2 = SelectField(_l("Tops 2"), coerce=int, default=0)
    bottoms = SelectField(_l("Bottoms"), coerce=int, validators=[DataRequired()])
    note = TextAreaField(_l("Note"), validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(OutfitForm, self).__init__(*args, **kwargs)

        self.jackets.choices = [
            (x.id, x.name)
            for x in Clothes.query.join(User, User.id == Clothes.owner_id)
            .join(Category, Category.id == Clothes.category_id)
            .filter(User.id == current_user.id)
            .filter(Category.parent_name == "Outerwears")
            .all()
        ]
        self.jackets.choices.insert(0, (0, "None"))

        self.tops_1.choices = [
            (x.id, x.name)
            for x in Clothes.query.join(User, User.id == Clothes.owner_id)
            .join(Category, Category.id == Clothes.category_id)
            .filter(User.id == current_user.id)
            .filter(Category.parent_name == "Tops")
            .all()
        ]

        self.tops_2.choices = [
            (x.id, x.name)
            for x in Clothes.query.join(User, User.id == Clothes.owner_id)
            .join(Category, Category.id == Clothes.category_id)
            .filter(User.id == current_user.id)
            .filter(Category.parent_name == "Tops")
            .all()
        ]
        self.tops_2.choices.insert(0, (0, "None"))

        self.bottoms.choices = [
            (x.id, x.name)
            for x in Clothes.query.join(User, User.id == Clothes.owner_id)
            .join(Category, Category.id == Clothes.category_id)
            .filter(User.id == current_user.id)
            .filter(Category.parent_name == "Bottoms")
            .all()
        ]
