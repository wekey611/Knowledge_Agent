from fastapi import APIRouter, status, Depends, Path, BackgroundTasks
from app import repositories, core, schemas
from app.core.database import get_db, AsyncSession

router = APIRouter(
    prefix="/organization",
    tags=["organization"]
)


@router.post("", status_code=status.HTTP_200_OK, response_model=schemas.organization.OrganizationOut)
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


@router.get("/{org_id}", status_code=status.HTTP_200_OK, response_model=schemas.organization.OrganizationDetail)
async def get_org(
        org_id=Path(...),
        user=Depends(core.oauth2.require_org_member),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.get_org(org_id, user)


@router.patch("/{org_id}", status_code=status.HTTP_200_OK, response_model=schemas.organization.OrganizationDetail)
async def revise_org(
        organization_data: schemas.organization.OrganizationUpdate,
        org_id=Path(...),
        user=Depends(core.oauth2.require_org_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.revise_org(org_id, organization_data)


@router.delete("/{org_id}", status_code=status.HTTP_200_OK)
async def delete_org(
        org_id=Path(...),
        user=Depends(core.oauth2.require_org_admin),
        db: AsyncSession = Depends(get_db)
):
    repo = repositories.organization.OrganizationRepository(db)
    return await repo.delete_org(org_id, user)
