import aiosqlite

async def getdb():
    conn = await aiosqlite.connect('management/db/config.db')
    await conn.execute("PRAGMA journal_mode = WAL")
    await conn.execute("PRAGMA temp_store = MEMORY")
    return conn

async def configTable():
    conn = await getdb()
    c = await conn.cursor()
    await c.execute("""
        CREATE TABLE IF NOT EXISTS config (
            superuser TEXT DEFAULT '',
            superuserpw TEXT DEFAULT ''
    )""")
    await conn.commit()
    await conn.close()

async def checkConfig():
    conn = await getdb()
    c = await conn.execute("SELECT * FROM config")
    row = await c.fetchone()
    await c.close()
    await conn.close()
    return row

async def addSuperuser(username, password):
    conn = await getdb()
    c = await conn.cursor()
    await c.execute("Select * from config")
    row = await c.fetchone()
    if row:
        await conn.close()
        return False
    await c.execute("INSERT INTO config (superuser, superuserpw) VALUES (?, ?)", (username, password))
    await conn.commit()
    await conn.close()
    return True

async def checkSuperuser(username, password):
    conn = await getdb()
    c = await conn.execute("SELECT * FROM config WHERE superuser = ? AND superuserpw = ?", (username, password))
    row = await c.fetchone()
    await conn.close()
    return row is not None