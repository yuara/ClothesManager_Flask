from datetime import datetime
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    jsonify,
    current_app,
)
from guess_language import guess_language
from flask_login import current_user, login_user, login_required
from flask_babel import _, get_locale
from project import db
from project.main.forms import (
    EditProfileForm,
    PostForm,
    SearchForm,
    MessagesForm,
)
from project.auth.forms import LoginForm, RegistrationForm
from project.models import (
    User,
    Post,
    Message,
    Notification,
    Category,
    Forecast,
    Location,
    ClothesIndex,
)
from project.suggest import suggest
from project.translate import translate
from project.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route("/home", methods=["POST", "GET"])
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    # Login and sign in form
    form = LoginForm()
    signin_form = RegistrationForm(form_name="RegistrationForm")

    # Login form
    if not signin_form.email.data and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("main.home"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("main.index"))

    # Sign in form
    if (
        signin_form.email.data
        and signin_form.validate_on_submit()
        and request.form["form_name"] == "RegistrationForm"
    ):
        user = User(
            username=signin_form.username.data,
            email=signin_form.email.data,
            location_id=signin_form.location_pref.data,
        )
        user.set_password(signin_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Registered the new user successfully!"))
        return redirect(url_for("main.home"))
    return render_template(
        "home.html", title=_("Home"), form=form, signin_form=signin_form
    )


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index/", methods=["GET", "POST"])
@login_required
def index():
    # Forecast data from user's location information
    user_forecast = (
        db.session.query(
            Forecast, Location.pref_name, Location.city_name, ClothesIndex.value
        )
        .join(Location, Location.id == Forecast.location_id)
        .join(ClothesIndex, ClothesIndex.id == Forecast.clothes_index_id)
        .join(User, User.location_id == Location.id)
        .filter(User.id == current_user.id)
        .order_by(Forecast.update_time.desc())
        .first()
    )

    # Get suggested clothes with forecast information from user's clothes
    if Forecast.query.first():
        # Pass clothes index id
        suggestions = suggest(user_forecast.Forecast.clothes_index_id)
        outerwears = suggestions.filter(Category.parent_id == 1).all()
        tops = suggestions.filter(Category.parent_id == 2).all()
        bottoms = suggestions.filter(Category.parent_id == 3).all()
    else:
        outerwears = None
        tops = None
        bottoms = None

    return render_template(
        "index.html",
        title=_("Dashboard"),
        forecast=user_forecast,
        outerwears=outerwears,
        tops=tops,
        bottoms=bottoms,
    )


@bp.route("/explore/")
@login_required
def explore():
    # All user's posts
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = url_for("main.explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main.explore", page=posts.prev_num) if posts.has_prev else None
    return render_template(
        "explore.html",
        title=_("Explore"),
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/user/<username>/", methods=["GET", "POST"])
@login_required
def user(username):
    # Post form
    post_form = PostForm()
    if post_form.validate_on_submit():
        # Check what language is used to the post
        language = guess_language(post_form.post.data)
        if language == "UNKNOWN" or len(language) > 5:
            language = ""
        post = Post(body=post_form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_("Your post is now live!"))
        return redirect(url_for("main.user", username=current_user.username))

    # Profile edit form
    edit_form = EditProfileForm(current_user.username)
    if edit_form.validate_on_submit():
        current_user.username = edit_form.username.data
        current_user.about_me = edit_form.about_me.data
        current_user.location_id = edit_form.location_pref.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("main.user", username=current_user.username))
        if request.method == "GET":
            edit_form.username.data = current_user.username
            edit_form.about_me.data = current_user.about_me
    user = User.query.filter_by(username=username).first_or_404()
    location = Location.query.filter_by(id=user.location_id).first()
    page = request.args.get("page", 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.user", username=current_user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=current_user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    return render_template(
        "user.html",
        user=user,
        location=location,
        posts=posts.items,
        edit_form=edit_form,
        post_form=post_form,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/user/<username>/popup/")
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user_popup.html", user=user)


@bp.route("/edit_profile/", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.location_id = form.location_pref.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("main.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title=_("Edit Profile"), form=form)


@bp.route("/user/post/", methods=["POST", "GET"])
@login_required
def post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        language = guess_language(post_form.post.data)
        if language == "UNKNOWN" or len(language) > 5:
            language = ""
        post = Post(body=post_form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_("Your post is now live!"))
        return redirect(url_for("main.user", username=current_user.username))
    page = request.args.get("page", 1, type=int)
    posts = current_user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.user", username=current_user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=current_user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    return render_template(
        "post.html",
        user=user,
        post_form=post_form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/follow/<username>/")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_("User %(username)s not found.", username=username))
        return redirect(url_for("main.index"))
    if user == current_user:
        flash(_("You cannot follow yourself!"))
        return redirect(url_for("main.user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_("You are following %(username)s!", username=username))
    return redirect(url_for("main.user", username=username))


@bp.route("/unfollow/<username>/")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_("User %(username)s not found.", username=username))
        return redirect(url_for("main.index"))
    if user == current_user:
        flash(_("You cannnot unfollow yourself!"))
        return redirect(url_for("main.user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_("You are not following %(username)s.", username=username))
    return redirect(url_for("main.user", username=username))


@bp.route("/translate/", methods=["POST"])
@login_required
def translate_text():
    return jsonify(
        {
            "text": translate(
                request.form["text"],
                request.form["source_language"],
                request.form["dest_language"],
            )
        }
    )


@bp.route("/search/")
@login_required
def search():
    print(g.search_form)
    # print(g.search_form.validate())
    # if not g.search_form.validate():
    #     return redirect(url_for("main.explore"))
    page = request.args.get("page", 1, type=int)
    users, utotal = User.search(
        g.search_form.q.data, page, current_app.config["POSTS_PER_PAGE"]
    )
    posts, ptotal = Post.search(
        g.search_form.q.data, page, current_app.config["POSTS_PER_PAGE"]
    )
    if not ptotal and not utotal:
        flash(_("No results found"))
        return redirect(url_for("main.explore"))
    next_url = (
        url_for("main.search", q=g.search_form.q.data, page=page + 1)
        if ptotal > page * current_app.config["POSTS_PER_PAGE"]
        else None
    )
    prev_url = (
        url_for("main.search", q=g.search_form.q.data, page=page - 1)
        if page > 1
        else None
    )
    return render_template(
        "search.html",
        title=_("search"),
        users=users,
        utotal=utotal,
        posts=posts,
        ptotal=ptotal,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/send_message/<recipient>/", methods=["GET", "POST"])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessagesForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification("unread_message_count", user.new_messages())
        db.session.commit()
        flash(_("Your message has been sent."))
        return redirect(url_for("main.user", username=recipient))
    return render_template(
        "send_message.html", title=_("Send Message"), form=form, recipient=recipient
    )


@bp.route("/messages/")
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification("unread_message_count", 0)
    db.session.commit()
    page = request.args.get("page", 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()
    ).paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    next_url = (
        url_for("main.messages", page=messages.next_num) if messages.has_next else None
    )
    prev_url = (
        url_for("main.messages", page=messages.prev_num) if messages.has_prev else None
    )
    return render_template(
        "messages.html", messages=messages.items, next_url=next_url, prev_url=prev_url
    )


@bp.route("/notifications/")
@login_required
def notifications():
    since = request.args.get("since", 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    return jsonify(
        [
            {"name": n.name, "data": n.get_data(), "timestamp": n.timestamp}
            for n in notifications
        ]
    )


@bp.route("/export_posts/")
@login_required
def export_posts():
    if current_user.get_task_in_progress("export_posts"):
        flash(_("An export task is currently in progress."))
    else:
        current_user.launch_task("export_posts", _("Exporting posts..."))
        db.session.commit()
    return redirect(url_for("main.user", username=current_user.username))
