from datetime import timedelta
from time import sleep

from fastapi import Depends, FastAPI
from fastapi_redis import redis_client
from fastapi import BackgroundTasks
from starlette.staticfiles import StaticFiles
from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate, MyModel
from app.users import auth_backend, current_active_user, fastapi_users

app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()


@app.get("/redis_db/{key,value}")  # both are fine, we could aslo do it like "/{key},{value}"
async def redis_db(key, value, background_tasks: BackgroundTasks):
    print(key, value)
    redis_client.set_in_background(background_tasks, key, MyModel(data='some_data_that_expires'),
                                   expiration=timedelta(days=1))

    return {"key": key, "value": value}


@app.post("/files/")
async def create_files(files: List[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/file_form_demo")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/")
async def main():
    content = """
    <!DOCTYPE html>
<html>

<head>
	<link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.0.2/tailwind.min.css" rel="stylesheet">
	<style>
	img {
		filter: sepia(1) hue-rotate(190deg) opacity(.46) grayscale(.7)
	}
	</style>
</head>

<body data-new-gr-c-s-check-loaded="14.1076.0" data-gr-ext-installed="">
<form action="/docs/" enctype="multipart/form-data" method="get">

	<div class="frame-root">
		<div class="frame-content">
			<section class="text-gray-600 body-font">
				<div class="container mx-auto flex px-5 py-24 md:flex-row flex-col items-center">
					<div class="lg:flex-grow md:w-1/2 lg:pr-24 md:pr-16 flex flex-col md:items-start md:text-left mb-16 md:mb-0 items-center text-center">
						<h1 class="title-font sm:text-4xl text-3xl mb-4 font-medium text-gray-900">This is Scraper APIs Backend, if you want to controle the headless scraper<br class="hidden lg:inline-block"></h1>
						<p class="mb-8 leading-relaxed">please go to api documentation</p>
						<div class="flex justify-center">
							<a href="https://soulmate-backend-56d9bbl6p-asadbukharee.vercel.app/docs">
								<input type="submit" value="See API Docs" class="inline-flex text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none hover:bg-indigo-600 rounded text-lg">
							</a>
						</div>
					</div>
					<div class="lg:max-w-lg lg:w-full md:w-1/2 w-5/6"><img class="object-cover object-center rounded" alt="hero" src="https://img.freepik.com/premium-vector/welcome-beautiful-inscription-text-decorate-invitation-banner-more-welcome-blue-inscription-modern-style_110464-247.jpg?w=720"></div>
				</div>
			</section>
		</div>
	</div>
</form>
</body>
</html>
        """
    return HTMLResponse(content=content)
