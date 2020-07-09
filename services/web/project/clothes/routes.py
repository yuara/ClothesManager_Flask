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
from project.clothes.forms import (
    ClothesForm,
    OutfitForm,
)
from project.models import (
    Clothes,
    Category,
    Outfit,
)
from project.clothes import bp


@bp.route("/_get_categories/")
def _get_categories():
    parent = request.args.get("parent", 1, type=int)
    categories = [
        (x.id, x.child_name) for x in Category.query.filter_by(parent_id=parent).all()
    ]
    return jsonify(categories)


@bp.route("/closet/")
@login_required
def closet():
    page = request.args.get("page", 1, type=int)
    user_clothes = current_user.own_clothes.order_by(Clothes.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("clothes.closet", page=user_clothes.next_num)
        if user_clothes.has_next
        else None
    )
    prev_url = (
        url_for("clothes.closet", page=user_clothes.prev_num)
        if user_clothes.has_prev
        else None
    )
    user_clothes = user_clothes.items
    categories = [
        Category.query.filter_by(id=c.category_id).first() for c in user_clothes
    ]
    return render_template(
        "clothes/closet.html",
        clothes=zip(user_clothes, categories),
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/add_clothes/", methods=["GET", "POST"])
@login_required
def add_clothes():
    form = ClothesForm(form_name="ClothesForm")
    if request.method == "GET":
        return render_template(
            "clothes/add_clothes.html", title=_("Add clothes"), form=form
        )
    if form.validate_on_submit() and request.form["form_name"] == "ClothesForm":
        clothes = Clothes(
            name=form.name.data,
            note=form.note.data,
            category_id=form.child_category.data,
            owner=current_user,
        )
        db.session.add(clothes)
        db.session.commit()
        flash(_("You added your clothes!"))
    return redirect(url_for("clothes.closet"))


@bp.route("/outfits/")
@login_required
def outfits():
    page = request.args.get("page", 1, type=int)
    user_outfits = current_user.outfits.order_by(Outfit.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("clothes.outfits", page=user_outfits.next_num)
        if user_outfits.has_next
        else None
    )
    prev_url = (
        url_for("clothes.outfits", page=user_outfits.prev_num)
        if user_outfits.has_prev
        else None
    )
    return render_template(
        "clothes/outfits.html",
        outfits=user_outfits.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/set_outfit/", methods=["GET", "POST"])
@login_required
def set_outfit():
    form = OutfitForm()
    if form.validate_on_submit():
        outfit = Outfit(name=form.name.data, note=form.note.data, owner=current_user)
        db.session.add(outfit)
        outfit.put_clothes(Clothes.query.get(form.tops.data))
        outfit.put_clothes(Clothes.query.get(form.bottoms.data))
        db.session.commit()
        flash(_("You set your outfit!!"))
        return redirect(url_for("clothes.outfits"))
    return render_template("/clothes/set_outfit.html", title=_("Set Outfit"), form=form)
