from sqlalchemy import Column, ForeignKey, Table, select
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionBase
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    lazyload,
    mapped_column,
    relationship,
    sessionmaker,
)

engine = create_async_engine("sqlite+aiosqlite:///database.db")
AsyncSession = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSessionBase
)
session: AsyncSessionBase


class Base(DeclarativeBase):
    pass


recipe2ingredient = Table(
    "recipe2ingredient",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipe.id"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredient.id"), primary_key=True),
)


class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    views: Mapped[int] = mapped_column(default=0)
    cooking_time: Mapped[float]

    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary=recipe2ingredient, back_populates="recipes", lazy="joined"
    )

    @hybrid_property
    def cooking_time_in_minutes(self):
        return self.cooking_time / 60


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    recipes: Mapped[list[Recipe]] = relationship(
        secondary=recipe2ingredient, back_populates="ingredients"
    )


async def get_recipes() -> list[Recipe]:
    async with session.begin():
        recipes = [
            *await session.scalars(
                select(Recipe)
                .options(lazyload(Recipe.ingredients))
                .order_by(Recipe.views.desc(), Recipe.cooking_time.asc())
            )
        ]
        for recipe in recipes:
            recipe.views += 1
    return recipes


async def get_recipe(id: int) -> Recipe | None:
    async with session.begin():
        recipe = await session.get(Recipe, id)
        if recipe is None:
            return recipe
        recipe.views += 1
    return recipe


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    global session
    session = AsyncSession()


async def close_all():
    global session
    await session.close_all()
    await engine.dispose()
