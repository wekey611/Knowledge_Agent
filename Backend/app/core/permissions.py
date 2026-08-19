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


async def check_org_member(org_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(models.auth.OrganizationMember).where(models.auth.OrganizationMember.user_id == current_user.id,
                                                        models.auth.OrganizationMember.org_id == org_id)
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有组织成员权限")
    return current_user


async def require_org_member(org_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await check_org_member(org_id=org_id, current_user=current_user, db=db)


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != models.user.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
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


# 知识库读取权限
async def check_knowledge_base_access(kb_id: int, current_user=Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
    # 1. 查询知识库
    stmt = select(models.knowledge.KnowledgeBase).where(
        models.knowledge.KnowledgeBase.id == kb_id,
        models.knowledge.KnowledgeBase.deleted == False,
    )

    result = await db.execute(stmt)
    kb = result.scalar_one_or_none()

    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    # 2. 公共知识库
    if kb.scope == models.knowledge.KnowledgeSource.PUBLIC:
        return kb

    # 3. 个人知识库
    if kb.scope == models.knowledge.KnowledgeSource.PERSONAL:
        if kb.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有知识库读取权限",
            )

        return kb

    # 4. 组织知识库
    if kb.scope == models.knowledge.KnowledgeSource.ORG:
        await check_org_member(
            org_id=kb.org_id,
            current_user=current_user,
            db=db,
        )

        return kb

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="没有知识库读取权限",
    )

async def check_knowledge_base_owner(kb_id: int, current_user=Depends(get_current_user),
                                      db: AsyncSession = Depends(get_db)):
    stmt = select(models.knowledge.KnowledgeBase).where(
        models.knowledge.KnowledgeBase.id == kb_id,
        models.knowledge.KnowledgeBase.deleted == False,
    )
    kb = (await db.execute(stmt)).scalar_one_or_none()

    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在",
        )

    if kb.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有知识库所有权",
        )
    return current_user
