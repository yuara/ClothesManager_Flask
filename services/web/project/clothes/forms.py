from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, InputRequired
from flask_babel import lazy_gettext as _l
from project import db
from project.models import Clothes, Category


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
    name = StringField(_l("Name"), validators=[Length(min=1, max=30)])
    tops = SelectField(_l("Tops"), coerce=int, validators=[DataRequired()])
    bottoms = SelectField(_l("Bottoms"), coerce=int, validators=[DataRequired()])
    note = TextAreaField(_l("Note"), validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(OutfitForm, self).__init__(*args, **kwargs)

        tops_list = Category.get_id_by_parent_id(1)
        bottoms_list = Category.get_id_by_parent_id(2)

        self.tops.choices = [
            (x.id, x.name) for x in Clothes.get_clothes_by_categoris(tops_list)
        ]
        self.bottoms.choices = [
            (x.id, x.name) for x in Clothes.get_clothes_by_categoris(bottoms_list)
        ]
