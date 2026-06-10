from materials.app import data as db
from materials.app.schemas import MaterialCreate, MaterialUpdate


def _normalize_text(value: str) -> str:
    return value.strip().lower()


def _paginate(items: list[dict], limit: int, offset: int) -> list[dict]:
    return items[offset : offset + limit]


def _is_duplicate_material(
    course_name: str,
    title: str,
    excluded_material_id: int | None = None,
) -> bool:
    normalized_course_name = _normalize_text(course_name)
    normalized_title = _normalize_text(title)

    for material_id, material in db.materials_db.items():
        if excluded_material_id is not None and material_id == excluded_material_id:
            continue

        same_course = _normalize_text(material["course_name"]) == normalized_course_name
        same_title = _normalize_text(material["title"]) == normalized_title

        if same_course and same_title:
            return True

    return False


def create_material(payload: MaterialCreate) -> dict:
    if _is_duplicate_material(payload.course_name, payload.title):
        raise ValueError("Material already exists for this course")

    material = {
        "id": db.next_id,
        "course_name": payload.course_name,
        "title": payload.title,
        "content": payload.content,
        "file_url": payload.file_url,
    }

    db.materials_db[db.next_id] = material
    db.next_id += 1

    return material


def get_all_materials(limit: int = 10, offset: int = 0) -> list[dict]:
    materials = list(db.materials_db.values())
    return _paginate(materials, limit, offset)


def get_material(material_id: int) -> dict | None:
    return db.materials_db.get(material_id)


def update_material(material_id: int, payload: MaterialUpdate) -> dict | None:
    if material_id not in db.materials_db:
        return None

    material = db.materials_db[material_id]
    provided_fields = payload.model_fields_set

    updated_course_name = payload.course_name if "course_name" in provided_fields else material["course_name"]

    updated_title = payload.title if "title" in provided_fields else material["title"]

    if _is_duplicate_material(
        updated_course_name,
        updated_title,
        excluded_material_id=material_id,
    ):
        raise ValueError("Material already exists for this course")

    if "course_name" in provided_fields:
        material["course_name"] = payload.course_name

    if "title" in provided_fields:
        material["title"] = payload.title

    if "content" in provided_fields:
        material["content"] = payload.content

    if "file_url" in provided_fields:
        material["file_url"] = payload.file_url

    return material


def delete_material(material_id: int) -> bool:
    if material_id in db.materials_db:
        del db.materials_db[material_id]
        return True

    return False


def get_by_course(
    course_name: str,
    limit: int = 10,
    offset: int = 0,
) -> list[dict]:
    normalized_course_name = _normalize_text(course_name)

    materials = [
        material
        for material in db.materials_db.values()
        if _normalize_text(material["course_name"]) == normalized_course_name
    ]

    return _paginate(materials, limit, offset)


def search_materials(
    query: str,
    limit: int = 10,
    offset: int = 0,
) -> list[dict]:
    normalized_query = _normalize_text(query)

    materials = [
        material
        for material in db.materials_db.values()
        if (
            normalized_query in _normalize_text(material["course_name"])
            or normalized_query in _normalize_text(material["title"])
            or normalized_query in _normalize_text(material["content"])
        )
    ]

    return _paginate(materials, limit, offset)
