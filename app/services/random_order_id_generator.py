from datetime import datetime
from app.services.memory_service import save_memory_fact
import random

def generate_order_id(length=5):
    # Generate only digits
    return ''.join(random.choices("0123456789", k=length))

async def create_order(user_id: str, item_name: str):
    order_id = generate_order_id()
    status = "Pending"
    timestamp = datetime.now().isoformat()

    # Save in Mem0AI & NeonDB
    content = f"{status}|{timestamp}|{item_name}"
    await save_memory_fact(user_id, f"order_{order_id}", content)
    print(f"[DEBUG] Saving in Mem0AI: user_id={user_id}, key=order_{order_id}, content={content}")

    return order_id, status
