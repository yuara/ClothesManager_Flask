from flask_login import current_user
from project import db
from project.models import (
    User,
    Category,
    Clothes,
    ClothesIndex,
    category_index,
)


def suggest(user_index_id):
    user_clothes = (
        db.session.query(category_index.c.conditional, Category.id, Clothes.name,)
        .join(category_index, (category_index.c.category_id == Category.id))
        .join(Clothes, Clothes.category_id == Category.id)
        .join(User, User.id == Clothes.owner_id)
        .filter(User.id == current_user.id)
        .filter(category_index.c.clothes_index_id == user_index_id)
    )
    return user_clothes
