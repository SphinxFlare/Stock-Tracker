# # tasks/update_tasks.py

# from App.celery_worker import celery
# import asyncio
# import os
# import datetime
# from App.Services.stock_service import update_user_stocks
# from App.Config.database import get_db
# from App.Models.user import User
# from sqlalchemy.future import select
# import logging



# TRACKER_FILE = os.path.expanduser("~/.last_update_run")

# # def has_already_run_today():
# #     if not os.path.exists(TRACKER_FILE):
# #         return False
# #     with open(TRACKER_FILE, 'r') as f:
# #         last_run = f.read().strip()
# #     return last_run == str(datetime.date.today())

# # def mark_as_run_today():
# #     with open(TRACKER_FILE, 'w') as f:
# #         f.write(str(datetime.date.today()))

# # @celery.task
# # def run_update_for_all_users():
# #     if has_already_run_today():
# #         print("✅ Already updated today. Skipping task.")
# #         return
# #     print("🌀 Running daily stock update task...")
# #     asyncio.run(run_async_update_for_all_users())
# #     mark_as_run_today()


# # async def run_async_update_for_all_users():
# #     async for session in get_db():
# #         result = await session.execute(select(User.id))
# #         user_ids = result.scalars().all()
        
# #         for user_id in user_ids:
# #             print(f"🚀 Updating stocks for user {user_id}")
# #             await update_user_stocks(user_id, session)


# from App.Models.stock import StockAnalysisSnapshot  # Import your snapshot model
# from datetime import datetime

# async def has_real_update_today(session, user_id):
#     today = datetime.utcnow().date()
#     result = await session.execute(
#         select(StockAnalysisSnapshot)
#         .where(StockAnalysisSnapshot.user_id == user_id)
#         .where(StockAnalysisSnapshot.timestamp >= datetime(today.year, today.month, today.day))
#     )
#     snapshot = result.scalars().first()
#     return snapshot is not None


# @celery.task
# def run_update_for_all_users():
#     print("🌀 Checking if update is needed...")
#     asyncio.run(run_async_update_for_all_users())



# async def run_async_update_for_all_users():
#     async for session in get_db():
#         result = await session.execute(select(User.id))
#         user_ids = result.scalars().all()

#         for user_id in user_ids:
#             print(f"🔎 Checking updates for user {user_id}...")

#             updated_today = await has_real_update_today(session, user_id)
#             if updated_today:
#                 print(f"✅ User {user_id} already has today's snapshot. Skipping.")
#                 continue

#             print(f"🚀 Updating stocks for user {user_id}...")
#             await update_user_stocks(user_id, session)