import aiosqlite

async def getdb():
    conn = await aiosqlite.connect('db/stats.db')
    await conn.execute("PRAGMA journal_mode = WAL")
    await conn.execute("PRAGMA temp_store = MEMORY")
    return conn

async def statsTable():
    conn = await getdb()
    c = await conn.cursor()
    await c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            banned TEXT DEFAULT NULL
        )
    """)
    await c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            open BOOLEAN DEFAULT TRUE
        )
    """)
    await c.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            onion TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await conn.commit()
    await conn.close()

async def checkStats():
    conn = await getdb()
    c = await conn.execute("SELECT COUNT(*) FROM users")
    users_count = await c.fetchone()
    c = await conn.execute("SELECT COUNT(*) FROM messages")
    messages_count = await c.fetchone()
    c = await conn.execute("SELECT COUNT(*) FROM servers")
    servers_count = await c.fetchone()
    c = await conn.execute("SELECT COUNT(*) FROM reports WHERE open = TRUE")
    reports_count = await c.fetchone()
    
    stats = {
        "users": users_count[0],
        "messages": messages_count[0],
        "servers": servers_count[0],
        "reports": reports_count[0]
    }
    
    await conn.close()
    return stats