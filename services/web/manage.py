from project import create_app, db, cli
from project.models import User, Post, Notification, Message, Task

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
    }
