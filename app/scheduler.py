import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from .models import Chat
from . import db


def cleanup_old_images():

    folder = os.path.join(
        'app',
        'static',
        'uploads',
        'chat_images'
    )

    if not os.path.exists(folder):
        return

    now = time.time()

    for filename in os.listdir(folder):

        file_path = os.path.join(folder, filename)

        if os.path.isfile(file_path):

            file_age = now - os.path.getmtime(file_path)

            days_old = file_age / (60 * 60 * 24)

            # Delete after 1 minute
            if days_old > 3:

                image_url = f"/static/uploads/chat_images/{filename}"

                # Find related chat
                chat = Chat.query.filter_by(
                    image_path=image_url
                ).first()

                # Delete image
                os.remove(file_path)

                print(f"Deleted image: {filename}")

                # Delete related chat
                if chat:

                    db.session.delete(chat)

                    db.session.commit()

                    print(f"Deleted chat: {chat.id}")


def start_scheduler():

    scheduler = BackgroundScheduler()

    # Run every 1 minute
    scheduler.add_job(
        cleanup_old_images,
        'interval',
        minutes=1
    )

    scheduler.start()

    print("Image cleanup scheduler started...")