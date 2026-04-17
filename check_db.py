import asyncio
from sqlalchemy import text
from app.database import async_session

async def main():
    async with async_session() as db:
        result = await db.execute(text("SELECT idinstitucion, nombre FROM institucion LIMIT 5"))
        for row in result:
            print(row)

asyncio.run(main())