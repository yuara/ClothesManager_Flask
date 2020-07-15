from flask_login import current_user
from project import db
from project.models import (
    User,
    Category,
    Clothes,
    Outfit,
    Forecast,
    Location,
    ClothesIndex,
)


def suggest():
    user_index = (
        ClothesIndex.query.join(Forecast, Forecast.clothes_index_id == ClothesIndex.id)
        .join(Location, Location.id == Forecast.location_id)
        .join(User, User.location_id == Location.id)
        .filter(User.id == current_user.id)
        .first()
    )

    if user_index:
        category_condition = user_index.conditions.all()
        if category_condition:
            condition_id = [x.id for x in category_condition]
        category_list = user_index.categories.all()

        user_clothes = Clothes.query.filter_by(owner_id=current_user.id).all()

        outwears = []
        tops = []
        bottoms = []
        for clothes in user_clothes:
            for category in category_list:
                if clothes.category_id == category.id:
                    if category.parent_id == 1:
                        outwears.append(clothes)
                    elif category.parent_id == 2:
                        tops.append(clothes)
                    else:
                        bottoms.append(clothes)

        outfits = []
        if outwears:
            for outwear in outwears:
                for top in tops:
                    if category_condition:
                        if top.category_id in condition_id:
                            for bottom in bottoms:
                                outfits.append([outwear, top, bottom])
                        else:
                            for bottom in bottoms:
                                x = ["", top, bottom]
                                if x not in outfits:
                                    outfits.append(x)
                    else:
                        for bottom in bottoms:
                            outfits.append([outwear, top, bottom])
        else:
            for top in tops:
                for bottom in bottoms:
                    outfits.append(["", top, bottom])
        return outfits
    return
