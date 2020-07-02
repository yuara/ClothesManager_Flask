import json
import sys
import time
import crochet
from flask import render_template, jsonify
from rq import get_current_job
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging
from project.scraper import TenkiSpider
from project import create_app, db
from project.models import User, Post, Task
from project.email import send_email

app = create_app()
app.app_context().push()

crochet.setup()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification(
            "task_progress", {"task_id": job.get_id(), "progress": progress}
        )
        if progress >= 100:
            task.complete = True
        db.session.commit()


def _get_spider_settings():
    settings = Settings()
    pipelines = {
        "project.scraper.ValidationPipeline": 100,
        "project.scraper.TenkiPipeline": 200,
    }
    settings.set("DOWNLOAD_DELAY", 3)
    settings.set("ITEM_PIPELINES", pipelines)
    return settings


@crochet.run_in_reactor
def scrape_with_crocher(logging=False):
    crawl_runner = CrawlerRunner(_get_spider_settings())

    if logging:
        configure_logging()

    crawl_runner.crawl(TenkiSpider)


def export_posts(user_id):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            data.append(
                {"body": post.body, "timestamp": post.timestamp.isoformat() + "Z"}
            )
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)

        try:
            send_email(
                "[ClothesManager] Your blog posts",
                sender=app.config["ADMINS"][0],
                recipients=[user.email],
                text_body=render_template("email/export_posts.txt", user=user),
                html_body=render_template("email/export_posts.html", user=user),
                attachments=[
                    (
                        "posts.json",
                        "application/json",
                        json.dumps({"posts": data}, indent=4),
                    )
                ],
                sync=True,
            )

        except:
            print(data)
    except:
        app.logger.error("Unhandled exception", exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)
