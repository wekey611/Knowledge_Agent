from fastapi import APIRouter, status, Depends, Path
from app import repositories, core, schemas, models
from app.core.database import get_db, AsyncSession

router = APIRouter(
    prefix="/organization",
    tags=["organization"]
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.organization.OrganizationOut)
async def create_org(
        organization: schemas.organization.OrganizationCreate,
        user=Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.create(user, organization)


@router.get("", status_code=status.HTTP_200_OK, response_model=list[schemas.organization.OrganizationDetail])
async def get_my_org(
        user=Depends(core.oauth2.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.get_my_org(user)


# 获取组织详情
@router.get("/{org_id}", status_code=status.HTTP_200_OK, response_model=schemas.organization.OrganizationDetail)
async def get_org(
        org_id=Path(...),
        user=Depends(core.permissions.require_org_member),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.get_org(org_id)


@router.patch("/{org_id}", status_code=status.HTTP_200_OK, response_model=schemas.organization.OrganizationDetail)
async def revise_org(
        organization_data: schemas.organization.OrganizationUpdate,
        org_id=Path(...),
        user=Depends(core.permissions.require_org_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.revise_org(org_id, organization_data)


@router.delete("/{org_id}", status_code=status.HTTP_200_OK)
async def delete_org(
        org_id=Path(...),
        user=Depends(core.permissions.require_org_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.delete_org(org_id, user)


# 获取组织人员
@router.get("/{org_id}/members", status_code=status.HTTP_200_OK,
            response_model=list[schemas.organization.OrganizationMemberOut])
async def get_members(
        org_id: int = Path(...),
        user: models.user.User = Depends(core.permissions.require_org_member),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    members = await repo.get_members(org_id)

    return members


# 添加成员
@router.post("/{org_id}/members", status_code=status.HTTP_200_OK)
async def add_member(
        org_id: int = Path(...),
        member_data: schemas.organization.OrganizationMemberCreate = Depends(),
        _: models.user.User = Depends(core.permissions.require_org_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.add_member(org_id, member_data)


# 修改角色
@router.patch("{org_id}/members/{user_id}")
async def revise_member(
        member_data: schemas.organization.OrganizationMemberUpdate,
        org_id: int = Path(...),
        user_id: int = Path(...),
        _: models.user.User = Depends(core.permissions.require_org_owner),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.revise_member(org_id, user_id,member_data)

# 退出组织
@router.delete("/{org_id}/members/me")
async def quit_org(
        org_id: int = Path(...),
        user: models.user.User = Depends(core.permissions.require_org_member),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.quit_org(org_id, user)

# 移除成员
@router.delete("/{org_id}/members/{user_id}")
async def remove_member(
        org_id: int = Path(...),
        user_id: int = Path(...),
        _: models.user.User = Depends(core.permissions.require_org_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.remove_member(org_id, user_id)

