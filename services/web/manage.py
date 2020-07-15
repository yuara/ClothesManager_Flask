from project import create_app, db, cli
from project.models import (
    User,
    Post,
    Notification,
    Message,
    Task,
    Clothes,
    Category,
    Outfit,
    Forecast,
    Location,
    ClothesIndex,
    category_index,
)

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_content():
    return {
        "db": db,
        "User": User,
        "Post": Post,
        "Message": Message,
        "Notification": Notification,
        "Task": Task,
        "Clothes": Clothes,
        "Category": Category,
        "Outfit": Outfit,
        "Forecast": Forecast,
        "Location": Location,
        "ClothesIndex": ClothesIndex,
        "category_index": category_index,
    }
