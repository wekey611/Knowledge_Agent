from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from app import models, schemas


class OrganizationRepository:
    def __init__(self, db=AsyncSession):
        self.db = db

    async def create(self, user_data: schemas.user.UserOut,
                     organization_data: schemas.organization.OrganizationCreate):
        owner_id = user_data.id

        new_org = models.auth.Organization(**organization_data.dict(exclude={"owner_id"}), owner_id=owner_id)
        # org_into =organization_data

        self.db.add(new_org)
        await self.db.commit()
        await self.db.refresh(new_org)

        new_member = models.auth.OrganizationMember(
            user_id=owner_id,
            org_id=new_org.id,
            role=models.auth.OrganizationRole.OWNER,
        )
        self.db.add(new_member)
        await self.db.commit()
        await self.db.refresh(new_member)

        return new_org

    async def get_my_org(self, user):
        """获取我的组织"""
        stmt = (
            select(models.auth.Organization)
            .options(
                selectinload(models.auth.Organization.owner),
                selectinload(models.auth.Organization.members)
                .selectinload(models.auth.OrganizationMember.user)
            )
            .outerjoin(
                models.auth.OrganizationMember
            )
            .where(
                (models.auth.Organization.owner_id == user.id)
                |
                (models.auth.OrganizationMember.user_id == user.id)
            )
        )

        result = await self.db.execute(stmt)

        return result.scalars().unique().all()

    async def get_org(self, org_id: int):
        """获取组织详情"""
        stmt = select(models.auth.Organization).where(models.auth.Organization.id == org_id)
        result = await self.db.execute(stmt)
        org = result.scalar_one_or_none()
        if org:
            org.members = await self.get_members(org_id)
        return org

    async def revise_org(self, org_id: int, organization_data: schemas.organization.OrganizationUpdate):
        stmt = select(models.auth.Organization).where(models.auth.Organization.id == org_id)
        result = await self.db.execute(stmt)
        org = result.scalars().first()
        if org:
            org.name = organization_data.name
            org.description = organization_data.description

        await self.db.commit()
        await self.db.refresh(org)
        return org

    async def delete_org(self, org_id: int, user: schemas.user.UserOut):
        stmt = select(models.auth.Organization).where(models.auth.Organization.id == org_id)
        result = await self.db.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            return False

        if org.owner_id != user.id:
            raise PermissionError("Only the organization owner can delete it")

        await self.db.execute(
            delete(models.auth.OrganizationMember).where(models.auth.OrganizationMember.org_id == org_id)
        )

        await self.db.refresh(org)
        await self.db.delete(org)

        await self.db.commit()
        return True

    # 获取组织人员
    async def get_members(self, org_id) -> list[schemas.organization.OrganizationMemberOut]:
        stmt = (
            select(models.auth.OrganizationMember)
            .where(
                models.auth.OrganizationMember.org_id == org_id,
            )
            .options(
                selectinload(models.auth.OrganizationMember.user)
            )
            .order_by(models.auth.OrganizationMember.joined_at)
        )
        result = await self.db.execute(stmt)
        members = result.scalars().all()

        return members

    # 添加成员
    async def add_member(self, org_id: int, member_data: schemas.organization.OrganizationMemberCreate):
        stmt = select(models.auth.Organization).where(models.auth.Organization.id == org_id)
        result = await self.db.execute(stmt)
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        user_stmt = select(models.user.User).where(models.user.User.id == member_data.user_id)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        member = models.auth.OrganizationMember(
            user_id=member_data.user_id,
            org_id=org_id,
            role=member_data.role,
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def revise_member(self, org_id: int, user_id: int,
                            member_data: schemas.organization.OrganizationMemberUpdate):
        stmt = select(models.auth.OrganizationMember).where(
            models.auth.OrganizationMember.org_id == org_id,
            models.auth.OrganizationMember.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        if member.role == models.auth.OrganizationRole.OWNER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="你不能修改管理员！")

        member.role = member_data.role
        await self.db.commit()
        await self.db.refresh(member)
        return member

    # 移除成语
    async def remove_member(self, org_id: int, user_id: int):
        stmt = select(models.auth.OrganizationMember).where(
            models.auth.OrganizationMember.org_id == org_id,
            models.auth.OrganizationMember.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()

        if member.role == models.auth.OrganizationRole.OWNER or member.role == models.auth.OrganizationRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="你不能删除管理员！")

        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        await self.db.execute(
            delete(models.auth.OrganizationMember).where(
                models.auth.OrganizationMember.org_id == org_id,
                models.auth.OrganizationMember.user_id == user_id,
            )
        )
        await self.db.commit()

        return True

    # 退出组织
    async def quit_org(self, org_id: int, user: schemas.user.UserOut):
        stmt = select(models.auth.OrganizationMember).where(
            models.auth.OrganizationMember.org_id == org_id,
            models.auth.OrganizationMember.user_id == user.id,
        )
        result = await self.db.execute(stmt)
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        if member.role == models.auth.OrganizationRole.OWNER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="你是这个组织的所有者，你不能退出。")

        await self.db.execute(
            delete(models.auth.OrganizationMember).where(
                models.auth.OrganizationMember.org_id == org_id,
                models.auth.OrganizationMember.user_id == user.id,
            )
        )
        await self.db.commit()

        return True
