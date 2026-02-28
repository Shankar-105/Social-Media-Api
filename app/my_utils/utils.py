import bcrypt
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app import models
def hashPassword(password: str) -> str:
    # Convert password to bytes and truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]  # Truncate to 72 bytes
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

def verifyPassword(plain_password:str,hashed_password:str) -> bool:
    # Convert plain password to bytes and truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]  # Truncate to 72 bytes
    # Hash with the salt from the stored hash
    return bcrypt.hashpw(password_bytes, hashed_password.encode('utf-8')) == hashed_password.encode('utf-8')
# optional now --cleans up expired otps from the db
async def cleanUpExpiredOtps(db:AsyncSession):
    await db.execute(delete(models.OTP).where(models.OTP.expires_at<datetime.now()))
    await db.commit()