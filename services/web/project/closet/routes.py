from sqlalchemy.orm import aliased
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app,
    jsonify,
)
from flask_login import current_user, login_required
from flask_babel import _
from project import db
from project.closet.forms import (
    ClothesForm,
    OutfitForm,
)
from project.models import (
    User,
    Clothes,
    Category,
    Outfit,
)
from project.closet import bp


# lead to a child category dropdown with parent_id you selected
@bp.route("/_get_categories/")
def _get_categories():
    parent = request.args.get("parent", 1, type=int)
    categories = [
        (x.id, x.child_name) for x in Category.query.filter_by(parent_id=parent).all()
    ]
    return jsonify(categories)


@bp.route("/clothes/", methods=["POST", "GET"])
@login_required
def clothes():
    # Add Clothes Form
    form = ClothesForm(form_name="ClothesForm")
    if form.validate_on_submit() and request.form["form_name"] == "ClothesForm":
        if form.name.data:
            _name = form.name.data
        else:
            # the added clothes will be named like t-shirt 1, pants 1
            # if not input the name form
            _category = Category.query.filter_by(id=form.child_category.data).first()
            _count = (
                current_user.own_clothes.filter_by(category_id=_category.id).count() + 1
            )
            _name = f"{_category.child_name} {_count}"

        clothes = Clothes(
            name=_name,
            note=form.note.data,
            category_id=form.child_category.data,
            owner=current_user,
        )
        db.session.add(clothes)
        db.session.commit()
        flash(_("You added your clothes!"))
        return redirect(url_for("closet.clothes"))

    page = request.args.get("page", 1, type=int)
    user_clothes = (
        db.session.query(
            Clothes.name, Clothes.timestamp, Category.parent_name, Category.child_name
        )
        .join(Category, Category.id == Clothes.category_id)
        .join(User, User.id == Clothes.owner_id)
        .filter(User.id == current_user.id)
        .order_by(Clothes.timestamp.desc())
        .paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    )
    next_url = (
        url_for("closet.clothes", page=user_clothes.next_num)
        if user_clothes.has_next
        else None
    )
    prev_url = (
        url_for("closet.clothes", page=user_clothes.prev_num)
        if user_clothes.has_prev
        else None
    )
    return render_template(
        "closet/clothes.html",
        title=_("Clothes"),
        form=form,
        user_clothes=user_clothes.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/add_clothes/", methods=["GET", "POST"])
@login_required
def add_clothes():
    form = ClothesForm(form_name="ClothesForm")
    if form.validate_on_submit() and request.form["form_name"] == "ClothesForm":
        if form.name.data:
            _name = form.name.data
        else:
            _category = Category.query.filter_by(id=form.child_category.data).first()
            _count = (
                current_user.own_clothes.filter_by(category_id=_category.id).count() + 1
            )
            _name = f"{_category.child_name} {_count}"
        clothes = Clothes(
            name=_name,
            note=form.note.data,
            category_id=form.child_category.data,
            owner=current_user,
        )
        db.session.add(clothes)
        db.session.commit()
        flash(_("You added your clothes!"))
        return redirect(url_for("closet.clothes"))
    return render_template("closet/add_clothes.html", title=_("Add Clothes"), form=form)


@bp.route("/outfits/", methods=["POST", "GET"])
@login_required
def outfits():
    # Set Outfit Form
    form = OutfitForm()
    if form.validate_on_submit():
        if form.name.data:
            _name = form.name.data
        else:
            # the added outfit will be named like outfit 1, outfit 2
            # if not input the name form
            _count = current_user.outfits.count() + 1
            _name = f"Outfit {_count}"

        # If not set outerwears and tops 2, put None
        _outerwear = None if form.outerwears.data == 0 else form.outerwears.data
        _top_2 = None if form.tops_2.data == 0 else form.tops_2.data

        outfit = Outfit(
            name=_name,
            note=form.note.data,
            owner_id=current_user.id,
            outerwear_id=_outerwear,
            top_1_id=form.tops_1.data,
            top_2_id=_top_2,
            bottom_id=form.bottoms.data,
        )
        db.session.add(outfit)
        db.session.commit()
        flash(_("You set your outfit!!"))
        return redirect(url_for("closet.outfits"))

    # if a user has clothes
    _clothes = current_user.own_clothes.count()
    has_clothes = True if _clothes > 0 else False

    c1 = aliased(Clothes)
    c2 = aliased(Clothes)
    c3 = aliased(Clothes)
    c4 = aliased(Clothes)

    page = request.args.get("page", 1, type=int)
    user_outfits = (
        db.session.query(
            Outfit.name, Outfit.timestamp, c1.name, c2.name, c3.name, c4.name
        )
        .outerjoin(c1, c1.id == Outfit.outerwear_id)
        .outerjoin(c2, c2.id == Outfit.top_1_id)
        .outerjoin(c3, c3.id == Outfit.top_2_id)
        .outerjoin(c4, c4.id == Outfit.bottom_id)
        .join(User, User.id == Outfit.owner_id)
        .filter(User.id == current_user.id)
        .order_by(Outfit.timestamp.desc())
        .paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    )
    next_url = (
        url_for("closet.outfits", page=user_outfits.next_num)
        if user_outfits.has_next
        else None
    )
    prev_url = (
        url_for("closet.outfits", page=user_outfits.prev_num)
        if user_outfits.has_prev
        else None
    )
    return render_template(
        "closet/outfits.html",
        title=_("Outfits"),
        form=form,
        has_clothes=has_clothes,
        user_outfits=user_outfits.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/set_outfit/", methods=["GET", "POST"])
@login_required
def set_outfit():
    form = OutfitForm()
    if form.validate_on_submit():
        if form.name.data:
            _name = form.name.data
        else:
            _count = current_user.outfits.count() + 1
            _name = f"Outfit {_count}"

        _outerwear = None if form.outerwears.data == 0 else form.outerwears.data
        _top_2 = None if form.tops_2.data == 0 else form.tops_2.data

        outfit = Outfit(
            name=_name,
            note=form.note.data,
            owner_id=current_user.id,
            outerwear_id=_outerwear,
            top_1_id=form.tops_1.data,
            top_2_id=_top_2,
            bottom_id=form.bottoms.data,
        )
        db.session.add(outfit)
        db.session.commit()
        flash(_("You set your outfit!!"))
        return redirect(url_for("closet.outfits"))

    return render_template("/closet/set_outfit.html", title=_("Set Outfit"), form=form,)
