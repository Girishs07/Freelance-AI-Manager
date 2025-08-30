import pymysql

try:
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="freelance_ai_db",
        port=3306
    )
    print("✅ Database connection successful!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL Version: {version}")
    
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
