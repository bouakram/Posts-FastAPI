import time
from typing import Type
import psycopg2
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status
from psycopg2.extras import RealDictCursor
from . import model, schema
from .db import engine, get_db

model.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host='localhost', database="fastapi", user="postgres",
                                password="boughazi/1997", cursor_factory=RealDictCursor)
        cur = conn.cursor()
        print("connecting to database was successful")
        break
    except Exception as error:
        print("connecting to database faild")
        print('error', error)
        time.sleep(3)


@app.get("/")
async def root():
    return {"message": "hello world !"}


@app.get("/posts",  response_model=list[schema.Post])
async def root(db: Session = Depends(get_db)):
    # cur.execute(""" SELECT * FROM posts ORDER BY created_at DESC """)
    # posts = cur.fetchall()
    posts = db.query(model.Post).all()
    print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=list[schema.Post])
async def root(post: schema.CreatePost, db: Session = Depends(get_db)):
    # cur.execute(""" INSERT INTO posts VALUES (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #             (post.title, post.content, post.published))
    # new_post = cur.fetchone()
    # conn.commit()
    new_post = db.Post(post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "post created successfully", "data": new_post}


@app.get("/posts/{id}", response_model=list[schema.Post])
async def create_post(id: int, db: Session = Depends(get_db)):
    # cur.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cur.fetchone()
    post = db.query(model.Post).filter(model.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    return {"data": post}


@app.put("/posts/{id}", status_code=status.HTTP_201_CREATED)
async def create_post(id: int, updatedpost: schema.CreatePost, db: Session = Depends(get_db)):
    # cur.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #             (post.title, post.content, post.published, str(id)))
    # post = cur.fetchone()
    post_query = db.query(model.Post).filter(model.Post.id == id).first()
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    # conn.commit()
    post_query.update(updatedpost.model_dump(), synchronize_sessions=False)
    db.commit()
    return {"message": f"post with id = {id} was successfully updated"}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def create_post(id: int, db: Session = Depends(get_db)):
    # cur.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # post = cur.fetchone()
    post_query = db.query(model.Post).filter(model.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    # conn.commit()
    post_query.delete(synchronize_sessions=False)
    db.commit()
    return {"message": f"post with id = {id} was successfully dleted"}
