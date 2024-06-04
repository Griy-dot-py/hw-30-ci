from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from . import database
from . import schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("start up")
    try:
        await database.init()
        yield
    finally:
        print("shut down")
        await database.close_all()


app = FastAPI(lifespan=lifespan)


@app.get("/recipe/", tags=["recipe"])
async def get_recipes() -> list[schemas.RecipeShortInfo]:
    """Get short info for each recipe"""

    return await database.get_recipes()


@app.get(
    "/recipe/{id}",
    tags=["recipe"],
    responses={
        200: {"model": schemas.RecipeFullInfo},
        404: {"description": "Recipe not found"},
    },
)
async def get_recipe(id: int) -> schemas.RecipeFullInfo:
    """Get detailed info for a special recipe"""

    recipe = await database.get_recipe(id)
    if recipe is None:
        raise HTTPException(404, "Not Found")
    return recipe
