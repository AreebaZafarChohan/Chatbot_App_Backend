from agents import function_tool
from app.db.connection import SessionLocal
from app.models.order import Order
from app.models.user_pref import UserPreference
from sqlalchemy import select

@function_tool
async def check_order_status(order_id: str) -> str:
    """Fetch real order status from NeonDB"""
    async with SessionLocal() as session:
        result = await session.execute(select(Order).where(Order.order_id == order_id))
        order = result.scalars().first()
        return str(order.status) if order else "Order ID not found."
    
    
@function_tool
async def update_user_preference(user_id: str, preference: str) -> str:
    """Update or insert real user preference in NeonDB"""
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
