from app.db.connection import SessionLocal
from app.models.user_pref import UserPreference
from sqlalchemy import select

async def update_user_preference(user_id: str, preference: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        pref = result.scalars().first()

        if pref:
            pref.preference = preference
        else:
            pref = UserPreference(user_id=user_id, preference=preference)
            session.add(pref)

        await session.commit()
        return pref.preference
