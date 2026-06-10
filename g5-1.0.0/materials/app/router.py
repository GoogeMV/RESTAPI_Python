from fastapi import APIRouter, HTTPException, Path, Query
from materials.app.schemas import MaterialCreate, MaterialUpdate, MaterialResponse
from materials.app import service

router = APIRouter()


@router.post("/", response_model=MaterialResponse, status_code=201)
def create_material(payload: MaterialCreate):
    try:
        return service.create_material(payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/", response_model=list[MaterialResponse])
def list_materials(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of materials returned",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of materials skipped before returning results",
    ),
):
    return service.get_all_materials(limit=limit, offset=offset)


@router.get("/search", response_model=list[MaterialResponse])
def search_materials(
    q: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Search keyword used for course name, title or content",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of materials returned",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of materials skipped before returning results",
    ),
):
    materials = service.search_materials(query=q, limit=limit, offset=offset)

    if not materials:
        raise HTTPException(
            status_code=404,
            detail="No materials found for this search query",
        )

    return materials


@router.get("/course/{course_name}", response_model=list[MaterialResponse])
def get_course_materials(
    course_name: str = Path(
        ...,
        min_length=2,
        description="Course name used to filter materials",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of materials returned",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of materials skipped before returning results",
    ),
):
    materials = service.get_by_course(
        course_name=course_name,
        limit=limit,
        offset=offset,
    )

    if not materials:
        raise HTTPException(
            status_code=404,
            detail="No materials found for this course",
        )

    return materials


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int = Path(
        ...,
        gt=0,
        description="Material ID must be a positive integer",
    ),
):
    material = service.get_material(material_id)

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return material


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    payload: MaterialUpdate,
    material_id: int = Path(
        ...,
        gt=0,
        description="Material ID must be a positive integer",
    ),
):
    try:
        material = service.update_material(material_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return material


@router.delete("/{material_id}")
def delete_material(
    material_id: int = Path(
        ...,
        gt=0,
        description="Material ID must be a positive integer",
    ),
):
    if not service.delete_material(material_id):
        raise HTTPException(status_code=404, detail="Material not found")

    return {"message": "Material deleted successfully"}
