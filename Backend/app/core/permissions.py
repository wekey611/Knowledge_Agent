from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app import models
from sqlalchemy import select
from app.core.oauth2 import get_current_user


async def check_org_admin(
        org_id: int,
        current_user,
        db: AsyncSession,
):
    stmt = select(models.auth.OrganizationMember).where(
        models.auth.OrganizationMember.user_id == current_user.id,
        models.auth.OrganizationMember.org_id == org_id,
        models.auth.OrganizationMember.role.in_([
            models.auth.OrganizationRole.ADMIN,
            models.auth.OrganizationRole.OWNER,
        ])
    )

    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有组织管理员权限"
        )

    return member


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != models.user.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


async def require_org_member(org_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(models.auth.OrganizationMember).where(models.auth.OrganizationMember.user_id == current_user.id,
                                                        models.auth.OrganizationMember.org_id == org_id)
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization member access required")
    return current_user


async def require_org_owner(org_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(models.auth.OrganizationMember).where(models.auth.OrganizationMember.user_id == current_user.id,
                                                        models.auth.OrganizationMember.org_id == org_id,
                                                        models.auth.OrganizationMember.role ==
                                                        models.auth.OrganizationRole.OWNER)
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Owner role required for this operation")
    return current_user


async def require_org_admin(
    org_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await check_org_admin(
        org_id=org_id,
        current_user=current_user,
        db=db,
    )
