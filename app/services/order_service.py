from app.db.connection import SessionLocal
from app.models.order import Order
from sqlalchemy import select

async def get_order_status(order_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalars().first()
        return order.status if order else "Order not found"
