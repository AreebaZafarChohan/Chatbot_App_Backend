# from datetime import datetime
# from app.services.memory_service import get_memory_facts, save_memory_fact

# async def get_order_status(user_id: str, order_id: str):
#     memory = await get_memory_facts(user_id)
#     print(f"[DEBUG] Memory for {user_id}: {memory}")
#     key = f"order_{order_id}"
#     if key not in memory:
#         print(f"[DEBUG] Key {key} not found")
#         return "Order ID not found."

#     content = memory[key]  # format: "status|timestamp|item_name"
#     status, ts_str, item_name = content.split("|")
#     created_at = datetime.fromisoformat(ts_str)
#     now = datetime.now()

#     # Update status based on elapsed time
#     elapsed_hours = (now - created_at).total_seconds() / 3600
#     if elapsed_hours >= 24:
#         status = "Delivered"
#     elif elapsed_hours >= 12:
#         status = "Out for delivery"
#     elif elapsed_hours >= 6:
#         status = "Shipped"

#     # Update memory with new status
#     new_content = f"{status}|{ts_str}|{item_name}"
#     await save_memory_fact(user_id, key, new_content)

#     return status
