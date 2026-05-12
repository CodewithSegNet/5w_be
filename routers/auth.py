"""
Authentication router — login, register, current user.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt

from database import get_db
from models.admin import Admin
from config import get_settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()


# ── Schemas ──────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: dict


class AdminResponse(BaseModel):
    id: int
    email: str
    full_name: str


# ── Helpers ──────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# ── Auth Dependency ──────────────────────────────────────
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: int = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Admin).where(Admin.id == int(admin_id)))
    admin = result.scalar_one_or_none()
    if admin is None:
        raise credentials_exception
    return admin


# ── Routes ───────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.email == req.email))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(req.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(admin.id)})
    return TokenResponse(
        access_token=token,
        admin={"id": admin.id, "email": admin.email, "full_name": admin.full_name},
    )


@router.post("/register", response_model=AdminResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if any admin exists — first registration is open, rest require auth
    result = await db.execute(select(Admin))
    existing = result.scalars().all()

    if len(existing) > 0:
        raise HTTPException(status_code=403, detail="Registration is closed. Contact an existing admin.")

    # Check duplicate email
    result = await db.execute(select(Admin).where(Admin.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    admin = Admin(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
    )
    db.add(admin)
    await db.flush()
    await db.refresh(admin)

    return AdminResponse(id=admin.id, email=admin.email, full_name=admin.full_name)


@router.get("/me", response_model=AdminResponse)
async def get_me(admin: Admin = Depends(get_current_admin)):
    return AdminResponse(id=admin.id, email=admin.email, full_name=admin.full_name)


# ── Admin User Management ────────────────────────────────
class AdminUpdateRequest(BaseModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None


class AdminListResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("/users", response_model=list[AdminListResponse])
async def list_admins(db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Admin).order_by(Admin.id))
    admins = result.scalars().all()
    return [AdminListResponse(id=a.id, email=a.email, full_name=a.full_name, created_at=str(a.created_at)) for a in admins]


@router.get("/users/{user_id}", response_model=AdminResponse)
async def get_admin(user_id: int, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Admin).where(Admin.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return AdminResponse(id=user.id, email=user.email, full_name=user.full_name)


@router.put("/users/{user_id}", response_model=AdminResponse)
async def update_admin(user_id: int, req: AdminUpdateRequest, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    result = await db.execute(select(Admin).where(Admin.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if req.email is not None:
        # Check duplicate
        dup = await db.execute(select(Admin).where(Admin.email == req.email, Admin.id != user_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = req.email
    if req.full_name is not None:
        user.full_name = req.full_name
    if req.password is not None:
        if len(req.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        user.hashed_password = hash_password(req.password)
    await db.flush()
    await db.refresh(user)
    return AdminResponse(id=user.id, email=user.email, full_name=user.full_name)


@router.delete("/users/{user_id}")
async def delete_admin(user_id: int, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    result = await db.execute(select(Admin).where(Admin.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    return {"detail": "Admin deleted"}
