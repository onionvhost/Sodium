import aiosqlite

async def getdb():
    conn = await aiosqlite.connect("db/user.db")
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA temp_store = MEMORY")
    return conn

async def addUser(username: str, password: str):
    conn = await getdb()
    c = await conn.cursor()
    await c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    await conn.commit()
    await conn.close()