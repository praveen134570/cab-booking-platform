import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.future import select
from app.config import settings
from app.database import get_db
from app.models import User

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
) -> User:
    token = credentials.credentials if credentials else "mock_token"
    try:
        if settings.CLERK_PEM_PUBLIC_KEY:
            payload = jwt.decode(
                token,
                settings.CLERK_PEM_PUBLIC_KEY.replace('\\n', '\n'),
                algorithms=["RS256"]
            )
            clerk_id = payload.get("sub")
        else:
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                clerk_id = payload.get("sub", "dev_user_1")
            except Exception:
                clerk_id = "dev_user_1"
                payload = {"name": "Test User", "email": "test@cabplatform.local"}

        result = await db.execute(select(User).where(User.clerk_id == clerk_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                clerk_id=clerk_id,
                name=payload.get("name", "Test User"),
                email=payload.get("email", f"{clerk_id}@example.com")
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(exc)}"
        )
