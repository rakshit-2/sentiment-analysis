"""Seed script to create initial admin user."""
import asyncio
from app.database.connection import connect_to_mongo, get_database
from app.auth.password import hash_password
from app.models.user import AdminUserDB


async def seed_admin_user():
    """Create the initial admin user if it doesn't exist."""
    # Initialize database connection
    await connect_to_mongo()
    
    db = get_database()
    collection = db["admin_users"]
    
    # Check if admin user already exists
    existing_user = collection.find_one({"username": "admin_01"})
    
    if existing_user:
        print("✅ Admin user 'admin_01' already exists.")
        return
    
    # Create admin user
    admin_user = AdminUserDB(
        username="admin_01",
        password_hash=hash_password("password"),
        is_active=True
    )
    
    collection.insert_one(admin_user.to_dict())
    print("✅ Admin user 'admin_01' created successfully!")
    print("   Username: admin_01")
    print("   Password: password")


if __name__ == "__main__":
    asyncio.run(seed_admin_user())
