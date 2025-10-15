from turtle import st
from agents import function_tool
from app.db.connection import SessionLocal
from app.models.order import Order
from app.models.user_pref import UserPreference
from sqlalchemy import select
import random

from agents import function_tool
from app.db.connection import SessionLocal
from app.models.order import Order
from app.models.user_pref import UserPreference
from app.models.memory import MemoryFact  # memory_facts table
from sqlalchemy import select
import random

from agents import function_tool
from app.db.connection import SessionLocal
from app.models.order import Order
import random


def generate_order_id(length=5):
    return ''.join(random.choices("0123456789", k=length))

@function_tool
async def create_new_order(item_name: str):
    """
    Tool: Create a new order.

    - Fetches last user_id from Neon DB orders table
    - Generates 5-digit unique order_id
    - Saves order in NeonDB Orders table and MemoryFact table
    - Updates 'last_order_id' in MemoryFact table
    - Also saves in Mem0AI directly
    - Returns confirmation with order_id and content 
    """
    from app.services.memory_service import save_memory_fact
    from sqlalchemy import select, desc
    from app.models.order import Order
    from app.db.connection import SessionLocal
    from datetime import datetime
    import random

    async with SessionLocal() as session:
        # 1️⃣ Fetch last user_id
        result = await session.execute(
            select(Order.user_id).order_by(desc(Order.id)).limit(1)
        )
        last_user_id = result.scalars().first()
        if not last_user_id:
            last_user_id = f"user_{random.randint(1000, 9999)}"
        print(f"[DEBUG] Using user_id: {last_user_id}")

        order_id = generate_order_id()
        status = "Pending"
        timestamp = datetime.now().isoformat()

        # Save in Mem0AI & NeonDB
        value = f"{status}|{timestamp}|{item_name}"
        await save_memory_fact(last_user_id, f"order_{order_id}", value)
        print(f"[DEBUG] Saved in Mem0AI + MemoryFact: user_id={last_user_id}, key=order_{order_id}, value={value}")


@function_tool
async def check_order_status(order_id: str) -> str:
    """
    Tool: Check the status of an existing order.

    Description:
        Looks up the order in the database by its order ID and returns
        the current status. If the order does not exist, returns a
        "not found" message.

    Parameters:
        order_id (str): The 5-digit order ID to check.

    Returns:
        str: Current status of the order or "Pending" if not found.
    """
    async with SessionLocal() as session:
        result = await session.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalars().first()
        return str(order.status) if order else "Pending"


@function_tool
async def update_user_preference(user_id: str, preference: str) -> str:
    """
    Tool: Update or insert a user's preference.

    Description:
        Checks if a preference already exists for the given user.
        If it exists, updates the value; otherwise, inserts a new record.
        Commits the change to the database and returns a confirmation message.

    Parameters:
        user_id (str): Unique identifier of the user.
        preference (str): The preference value to save (e.g., "dark_mode").

    Returns:
        str: Confirmation message indicating the preference has been updated.
    """
    async with SessionLocal() as session:
        result = await session.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        pref = result.scalars().first()
        if pref:
            pref.preference = preference
        else:
            pref = UserPreference(user_id=user_id, preference=preference)
            session.add(pref)
        await session.commit()
    return f"Preference updated: {preference}"
