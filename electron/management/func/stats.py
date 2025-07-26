import aiosqlite

async def getdb():
    conn = await aiosqlite.connect('management/db/stats.db')
    await conn.execute("PRAGMA journal_mode = WAL")
    await conn.execute("PRAGMA temp_store = MEMORY")
    return conn