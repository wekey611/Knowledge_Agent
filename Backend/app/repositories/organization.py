import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app import models, schemas, settings


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
            joined_at=datetime.utcnow()
        )
        self.db.add(new_member)
        await self.db.commit()
        await self.db.refresh(new_member)

        return new_org

    async def get_my_org(self, user_id: schemas.user.UserOut):
        owner_id = user_id.id
        stmt = select(models.auth.Organization).where((models.auth.Organization.owner_id == owner_id))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_org(self, org_id: int, user_id: schemas.user.UserOut):
        owner_id = user_id.id
        stmt = select(models.auth.Organization).where(
            (models.auth.Organization.owner_id == owner_id) & (models.auth.Organization.id == org_id))
        result = await self.db.execute(stmt)
        return result.scalars().first()

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

    async def delete_org(self,org_id: int,user: schemas.user.UserOut):
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
