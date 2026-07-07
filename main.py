from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

#
class Blog(BaseModel):
    title: str
    body: str
    published_at: Optional[bool]

#
@app.get("/")
def read_root():
    return {"Hello": "World"}

#
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

#
@app.put("/items/{item_id}")
def update_item(item_ide: int, item: Blog):
    return {"item_id": item.name, "item_id": item_id}

#
@app.post("/blog")
def create_blog(blog: Blog):
    return f"Blog is created with title as {blog.title}"