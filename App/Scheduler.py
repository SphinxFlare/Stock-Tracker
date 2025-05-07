# App/Scheduler.py


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio
from App.Models.user import User
from App.Services.stock_service import update_user_stocks
from App.Config.database import get_db
from asyncio import get_event_loop, run_coroutine_threadsafe, get_running_loop



# Called in main.py's startup event
def start_scheduler(app):
    scheduler = AsyncIOScheduler()
    loop = get_event_loop()  # 🌍 Grab loop from main thread

    print("🚀 Scheduler started successfully!")

    @scheduler.scheduled_job(
        CronTrigger(hour=14, minute=00, timezone="UTC")  
    )
    def scheduled_task():
        print("⏰ Running test stock update task...")

        # ✅ Schedule coroutine to run in main event loop
        run_coroutine_threadsafe(run_all_user_updates(app), loop)

    scheduler.start()








# This runs your update function for all users
async def run_all_user_updates(app):
    print("🔁 run_all_user_updates called!")  # Ensure it's being called

    async_session = app.state.db_session  # The async session factory

    try:
        # Use async_session() to create an actual session object
        async with async_session() as session:  # Create a session here
            result = await session.execute(select(User.id))  # Fetch user IDs from DB
            user_ids = [row[0] for row in result.fetchall()]  # Extract user IDs

            if len(user_ids) == 0:
                print("❌ No users found in the database!")
                return  # No users to update

            print(f"👥 Found {len(user_ids)} user(s) to update.")

            for user_id in user_ids:
                try:
                    print(f"📈 Updating user {user_id}...")
                    await update_user_stocks(user_id, session)  # Call update for each user
                except Exception as e:
                    print(f"❌ Error updating user {user_id}: {e}")

    except Exception as e:
        print(f"❌ Error in run_all_user_updates: {e}")




