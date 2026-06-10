from pydantic import BaseModel, Field, field_validator


class MaterialBase(BaseModel):
    course_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the course associated with the material",
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Material title",
    )
    content: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="Material content or description",
    )
    file_url: str | None = Field(
        default=None,
        max_length=500,
        description="Optional URL for an external material file",
    )

    @field_validator("course_name", "title", "content")
    @classmethod
    def strip_and_validate_not_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty or contain only spaces")

        return value

    @field_validator("file_url")
    @classmethod
    def validate_file_url(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            return None

        if not value.startswith(("http://", "https://")):
            raise ValueError("file_url must start with http:// or https://")

        return value


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    course_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated course name",
    )
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
        description="Updated material title",
    )
    content: str | None = Field(
        default=None,
        min_length=5,
        max_length=5000,
        description="Updated material content",
    )
    file_url: str | None = Field(
        default=None,
        max_length=500,
        description="Updated material file URL",
    )

    @field_validator("course_name", "title", "content")
    @classmethod
    def strip_and_validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty or contain only spaces")

        return value

    @field_validator("file_url")
    @classmethod
    def validate_optional_file_url(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            return None

        if not value.startswith(("http://", "https://")):
            raise ValueError("file_url must start with http:// or https://")

        return value


class MaterialResponse(BaseModel):
    id: int
    course_name: str
    title: str
    content: str
    file_url: str | None = None
