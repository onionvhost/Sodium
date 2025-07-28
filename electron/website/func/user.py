import aiosqlite

async def getdb():
    conn = await aiosqlite.connect("db/stats.db")
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA temp_store = MEMORY")
    return conn

async def addUser(username: str, password: str):
    conn = await getdb()
    c = await conn.cursor()
    await c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if await c.fetchone():
        await conn.close()
        return False
    await c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    await conn.commit()
    await conn.close()
    return True

async def getUser(username: str, password: str):
    conn = await getdb()
    c = await conn.cursor()
    await c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    if not await c.fetchone():
        await conn.close()
        return False
    await conn.close()
    return True