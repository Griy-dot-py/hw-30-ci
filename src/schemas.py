from pydantic import BaseModel


class Base(BaseModel):
    class Config:
        from_attributes = True


class Ingredient(Base):
    name: str

class RecipeBase(Base):
    name: str


class RecipeShortInfo(RecipeBase):
    views: int
    cooking_time_in_minutes: float


class RecipeFullInfo(RecipeBase):
    cooking_time: float
    ingredients: list[Ingredient]
    description: str
