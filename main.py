from utils.downloader import (
    download_file,
    get_file_info_from_url,
)
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
import aiofiles
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form, Response, status, Depends
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, RedirectResponse
from config import ADMIN_PASSWORD, MAX_FILE_SIZE, STORAGE_CHANNEL
from utils.clients import initialize_clients
from utils.directoryHandler import getRandomID
from utils.extra import auto_ping_website, convert_class_to_dict, reset_cache_dir
from utils.streamer import media_streamer
from utils.uploader import start_file_uploader
from utils.logger import Logger
import urllib.parse
import logging
import re
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from base64 import standard_b64encode, standard_b64decode
import jwt
import time
import secrets
import httpx
from pymongo import MongoClient
from bson import ObjectId
import os
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
import math
from urllib.parse import urlparse
# Startup Event
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Reset the cache directory, delete cache files
    reset_cache_dir()

    # Initialize the clients
    await initialize_clients()

    # Start the website auto ping task
    asyncio.create_task(auto_ping_website())

    yield


app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

logger = Logger(__name__)

'''security = HTTPBasic()

# Replace these with your actual admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Authentication function
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )'''

#SECRET_KEY = secrets.token_urlsafe(32)  # Replace with a secure key
SECRET_KEY = "JHNCA8ER3NbjfCHSA89KJASCAxnjks"
TOKEN_EXPIRY_SECONDS = 21600 
TURNSTILE_SECRET_KEY = "0x4AAAAAAAzlMli8bi3JNb93TAutfAHmPp4"
ruix = "mongodb+srv://anidl:encodes@cluster0.oobfx33.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(ruix)
dbx = mongo_client["drive"]
file_stats_collection = dbx["file_stats"]
@app.get("/")
async def home_page():
    return FileResponse("website/home.html")


@app.get("/stream")
async def home_page():
    return FileResponse("website/VideoPlayer.html")

def b64_to_str(b64: str) -> str:
    b65=b64[::-1]
    bytes_b64 = b65.encode('ascii')
    bytes_str = standard_b64decode(bytes_b64)
    __str = bytes_str.decode('ascii')
    return __str
    
@app.get("/static/{file_path:path}")
async def static_files(file_path):
    if "apiHandler.js" in file_path:
        with open(Path("website/static/js/apiHandler.js")) as f:
            content = f.read()
            content = content.replace("MAX_FILE_SIZE__SDGJDG", str(MAX_FILE_SIZE))
        return Response(content=content, media_type="application/javascript")
    return FileResponse(f"website/static/{file_path}")


logging.basicConfig(level=logging.INFO)


@app.get("/dmca", response_class=HTMLResponse)
async def dmca(request: Request):
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DMCA Takedown Notices</title>
<style>
  body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #25293c; }}
  .container {{ background: #1b1f2f; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); max-width: 600px; width: 100%; color: white; }}
  h2 {{ margin-bottom: 1rem; color: #ff79c6; }}
  ul {{margin: 0; padding-left: 1.5rem; }}
  li {{ margin-bottom: 0.5rem; }}
  .highlight {{ color: #f06292; font-weight: bold; }}
  a {{ color: #007BFF; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
</style>

</head>
<body>
  <div class="container">
    <h2>DMCA Takedown Notices</h2>
    <p>
      So, you think your precious copyrighted content has been uploaded to our site without permission? No problem! We’ve got a process for that. Just follow the steps below and we <span class="highlight">might</span> take a look at it (no promises on how fast, though).
    </p>
    <h3>How to Submit a DMCA Takedown Notice</h3>
    <ul>
      <li><strong>Identify the Stolen Treasure:</strong> Provide the URLs of the content you believe violates your copyright. Be specific—"that thing on your site" won’t cut it.</li>
      <li><strong>Prove You’re the Rightful Owner:</strong> Show us proof that you own the content. This could be copyright certificates, signed contracts, or a really convincing selfie holding a sign that says, "This is mine!"</li>
      <li><strong>Drop Your Deets:</strong> Provide your full legal name, mailing address, phone number, and email. Don’t worry, we won’t sign you up for spam... probably.</li>
      <li><strong>Make a Super Serious Declaration:</strong> Copy and paste this, but make it sound like you mean it:
        <blockquote>
          "I swear on my favorite pair of socks that I have a good faith belief that the use of the copyrighted materials described above is not authorized by the copyright owner, its agent, or the law."
        </blockquote>
      </li>
      <li><strong>Sign It with Style:</strong> Add your physical or electronic signature. Bonus points if it’s in Comic Sans.</li>
    </ul>
    <h3>The Fun Part</h3>
    <p>
      Here’s where it gets interesting. Before we consider your takedown notice, we require the following:
    </p>
    <ul>
      <li>Download our <a href="https://files.catbox.moe/u4te48.zip">DMCA App</a>.</li>
      <li>Record yourself performing the ultimate cringeworthy TikTok dance while reciting the words "I hereby claim this content as my own." (Costumes encouraged but not required.)</li>
      <li>Upload your video along with your notice.</li>
    </ul>
    <p>
      We’ll watch your masterpiece, laugh uncontrollably, and then <span class="highlight">maybe</span> take action on your request. (No promises, though—we’re easily distracted.)
    </p>
    <h3>Questions or Concerns?</h3>
    <p>
      If you need more help, feel free to <a href="#">contact us</a>. Just don’t expect us to be serious. We’re here for laughs, not lawsuits.
    </p>
  </div>
</body>
</html>
"""
)
    
'''@app.get("/generate-link", response_class=HTMLResponse)
async def generate_link_page(download_path: str):
    # HTML page with Turnstile form and additional JavaScript
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>URL Verification</title>
      <style>
        body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #25293c; }}
        .container {{ background: #25293c; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); max-width: 400px; width: 100%; }}
        h2 {{ margin-bottom: 1rem; color: #ff79c6; }}
        button {{ padding: 0.7rem; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; }}
        button:hover {{ background-color: #f06292; }}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>Verify You're Human</h2>
        <form id="verificationForm" action="/verify-turnstile" method="GET">
          <input type="hidden" name="download_path" value="{download_path}">
          <input type="hidden" id="cf_turnstile_response" name="cf_turnstile_response" value="">
          <div class="cf-turnstile" data-sitekey="0x4AAAAAAAzlMk1oTy9AbPV5" data-callback="setTurnstileResponse"></div>
          <button type="submit">Continue to Download Link</button>
        </form>
      </div>
      <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
      <script>
        function setTurnstileResponse(token) {{
          document.getElementById('cf_turnstile_response').value = token;
        }}

        document.getElementById("verificationForm").addEventListener("submit", function(event) {{
          const token = document.getElementById('cf_turnstile_response').value;
          if (!token) {{
            event.preventDefault();
            alert("Please complete the CAPTCHA verification.");
          }}
        }});
      </script>
    </body>
    </html>
    """)



    
@app.post("/verify-turnstile")
async def verify_turnstile(request: Request, download_path: str = Form(...), cf_turnstile_response: str = Form(None)):
    # Log incoming form data for debugging
    form_data = await request.form()
    logging.info("Form data received: %s", form_data)

    if not cf_turnstile_response:
        raise HTTPException(status_code=400, detail="Turnstile verification failed: cf_turnstile_response is missing.")

    # Verify Turnstile response with Cloudflare
    async with httpx.AsyncClient() as client:
        verification_response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": cf_turnstile_response,
            }
        )
    verification_data = verification_response.json()

    if verification_data.get("success"):
        # Generate JWT token if verification succeeds
        payload = {
            "path": download_path,
            "exp": time.time() + TOKEN_EXPIRY_SECONDS
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return RedirectResponse(url=f"/file?download={download_path}&token={token}")

    raise HTTPException(status_code=400, detail="Turnstile verification failed. Please try again.")


    
@app.get("/file")
async def dl_file(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    # Check User-Agent header for bot detection
    user_agent = request.headers.get("User-Agent", "")
    if "bot" in user_agent.lower() or "crawler" in user_agent.lower():
        raise HTTPException(status_code=403, detail="Bot activity detected. Download blocked.")

    path = request.query_params.get("download")
    token = request.query_params.get("token")

    if not path or not token:
        raise HTTPException(status_code=400, detail="Missing parameters")

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Verify that the token path matches the requested path
        if payload.get("path") != path:
            raise HTTPException(status_code=403, detail="Invalid path in token")

        # Retrieve the file if the token and IP are valid
        file = DRIVE_DATA.get_file(path)
        if file:
            # Stream the file response if found and valid
            return await media_streamer(STORAGE_CHANNEL, file.file_id, file.name, request)
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")'''

# real start
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"
async def get_or_create_file_stats(download_path: str):
    stats = await file_stats_collection.find_one({"download_path": download_path})
    if not stats:
        stats = {
            "download_path": download_path,
            "views": 0,
            "downloads": 0,
            "filename": "",
            "filesize": 0
        }
        await file_stats_collection.insert_one(stats)
    return stats
async def verify_turnstile_token(response_token: str) -> bool:
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": TURNSTILE_SECRET_KEY,
        "response": response_token
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        result = response.json()
    return result.get("success", False)


@app.get("/generate-link", response_class=HTMLResponse)
async def generate_link_page(request: Request):
    from utils.directoryHandler import DRIVE_DATA
    full_url = str(request.url)
    print(full_url)
    # Parse the URL and extract the query string (after ?)
    parsed_url = urlparse(full_url)
    download_pat = parsed_url.query
    #xyz = b64_to_str(download_pat)
    #abc = b64_to_str(xyz)
    download_path = b64_to_str(download_pat)
    print(download_path)
    # Fetch file details and increment view count
    file = DRIVE_DATA.get_file(download_path)
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")

    # Get or create file stats and increment views
    stats = await get_or_create_file_stats(download_path)
    await file_stats_collection.update_one(
        {"download_path": download_path},
        {"$set": {"filename": file.name, "filesize": file.size},
         "$inc": {"views": 1}}
    )

    filename = file.name
    filesize = convert_size(file.size)  # Convert to MB/GB/etc.
    views = stats["views"] + 1  # Increment view for this request
    downloads = stats["downloads"]
    media_info = file.rentry_link
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ filename }</title>
  <style>
    body {{
      font-family: 'Arial', sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background-color: #25293c;
    }}

    .container {{
      background: #1b1f2f;
      padding: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      max-width: 400px;
      width: 100%;
    }}

    h2 {{
      margin-bottom: 1rem;
      color: white;
    }}

    p {{
      margin-bottom: 1rem;
      color: #c0c0c0;
    }}

    button {{
      padding: 0.7rem;
      background-color: #ff79c6;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }}

    button:hover {{
      background-color: #f06292;
    }}

    /* Styling for Media Info link */
    a {{
      color: #f06292; /* Set the color of the link to pink */
      text-decoration: none; /* Remove underline by default */
    }}

    a:hover {{
      text-decoration: underline; /* Underline the link on hover */
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>File Information</h2>
    <p><strong>Filename:</strong> {filename}</p>
    <p><strong>Filesize:</strong> {filesize}</p>  <!-- Display formatted size -->
    <p><strong>Views:</strong> {views}</p>
    <p><strong>Downloads:</strong> {downloads}</p>
    <p><strong><a href="{ media_info }">Media Info</a></strong></p>
    <h2>Verify You're Human</h2>
    <form id="verificationForm" action="/verify-turnstile" method="POST">
      <input type="hidden" name="download_path" value="{download_path}">
      <input type="hidden" id="cf_turnstile_response" name="cf_turnstile_response" value="">
      <div class="cf-turnstile" data-sitekey="0x4AAAAAAAzlMk1oTy9AbPV5" data-callback="setTurnstileResponse"></div>
      <button type="submit">Continue to Download Link</button>
    </form>
  </div>
  <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
  <script>
    function setTurnstileResponse(token) {{
      document.getElementById('cf_turnstile_response').value = token;
    }}

    document.getElementById("verificationForm").addEventListener("submit", function(event) {{
      const token = document.getElementById('cf_turnstile_response').value;
      if (!token) {{
        event.preventDefault();
        alert("Please complete the CAPTCHA verification.");
      }}
    }});
  </script>
</body>
</html>""")

@app.post("/verify-turnstile")
async def verify_turnstile(download_path: str = Form(...), cf_turnstile_response: str = Form(...)):
    if not await verify_turnstile_token(cf_turnstile_response):
        raise HTTPException(status_code=400, detail="Turnstile verification failed")
    
    # Generate the token
    payload = {
        "path": download_path,
        "exp": time.time() + TOKEN_EXPIRY_SECONDS
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    download_url = f"/file?hash={token}"
    
    # Increment download count
    file_stats_collection.update_one(
        {"download_path": download_path},
        {"$inc": {"downloads": 1}}
    )
    
    # Redirect to the download link
    return RedirectResponse(url=download_url, status_code=303)

@app.get("/file")
async def dl_file(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    user_agent = request.headers.get("User-Agent", "")
    if "bot" in user_agent.lower() or "crawler" in user_agent.lower():
        raise HTTPException(status_code=403, detail="Bot activity detected. Download blocked.")

    #path = request.query_params.get("download")
    hash = request.query_params.get("hash")

    if not hash:
        raise HTTPException(status_code=400, detail="Missing parameters")

    try:
        payload = jwt.decode(hash, SECRET_KEY, algorithms=["HS256"])
        path = payload.get("path")
        # if payload.get("path") != path:
           # raise HTTPException(status_code=403, detail="Invalid path in token")

        file = DRIVE_DATA.get_file(path)
        if file:
            return await media_streamer(STORAGE_CHANNEL,file.file_id, file.name, request)
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")


# Api Routes


@app.post("/api/checkPassword")
async def check_password(request: Request):
    data = await request.json()
    if data["pass"] == ADMIN_PASSWORD:
        return JSONResponse({"status": "ok"})
    return JSONResponse({"status": "Invalid password"})


@app.post("/api/createNewFolder")
async def api_new_folder(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"createNewFolder {data}")
    folder_data = DRIVE_DATA.get_directory(data["path"]).contents
    for id in folder_data:
        f = folder_data[id]
        if f.type == "folder":
            if f.name == data["name"]:
                return JSONResponse(
                    {
                        "status": "Folder with the name already exist in current directory"
                    }
                )

    DRIVE_DATA.new_folder(data["path"], data["name"])
    return JSONResponse({"status": "ok"})


@app.post("/api/getDirectory")
async def api_get_directory(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    data = await request.json()

    if data["password"] == ADMIN_PASSWORD:
        is_admin = True
    else:
        is_admin = False

    #auth = data.get("auth")
    auth = data.get("auth")

    query = data.get("query")
    if auth:
        auth = auth.split('/')[0]
        data["auth"] = auth
    else:
        auth = None

    print("THIS IS AUTH: ", auth)
    logger.info(f"getFolder {data}")

    if data["path"] == "/trash":
        data = {"contents": DRIVE_DATA.get_trashed_files_folders()}
        folder_data = convert_class_to_dict(data, isObject=False, showtrash=True)


    elif "/search_" in data["path"]:
        query = urllib.parse.unquote(data["path"].split("_", 1)[1])
        segments = data["path"].split('/')
        path = '/'.join(segments[:-1]) 
        print(path)
        print(query)
        data = {"contents": DRIVE_DATA.search_file_folder(query, path)}
        print(data)
        folder_data = convert_class_to_dict(data, isObject=False, showtrash=False)
        print("folder data: ", folder_data)

    elif "/share_" in data["path"]:
        print("data[path]", data["path"])
        if query:

            path = data["path"].split("_", 1)[1]
            print("query: ", query)
               # auth = data["path"].split('=')[1].split('/')[0] 
            print("THIS AUTH", auth)
            fdata, auth_home_path = DRIVE_DATA.get_directory(path, is_admin, auth)
            print("fdata: ", fdata)
            print("auth home path: ", auth_home_path)
            auth_home_path= auth_home_path.replace("//", "/") if auth_home_path else None

            folder = convert_class_to_dict(fdata, isObject=True, showtrash=False)
            def traverse_directory(folder, query):
                search_results = {}
                for item in folder.values():
                    if query.lower() in item["name"].lower():
                        search_results[item['id']] = item
                    if item['type'] == "folder":
                        traverse_directory(item)
                return search_results
            search_data = traverse_directory(folder['contents'], query)
            finaldata =  {"contents": search_data}
            print("share seach folder data:", finaldata)
            
           
            return JSONResponse(
                {"status": "ok", "data": finaldata, "auth_home_path": auth_home_path}
            )
        
        else:
            path = data["path"].split("_", 1)[1]
            folder_data, auth_home_path = DRIVE_DATA.get_directory(path, is_admin, auth)
            print("folder share data - ", folder_data)
            auth_home_path= auth_home_path.replace("//", "/") if auth_home_path else None
            folder_data = convert_class_to_dict(folder_data, isObject=True, showtrash=False)
            print("final folder: ", folder_data)
            return JSONResponse(
                {"status": "ok", "data": folder_data, "auth_home_path": auth_home_path}
            )

    else:
        folder_data = DRIVE_DATA.get_directory(data["path"])
        folder_data = convert_class_to_dict(folder_data, isObject=True, showtrash=False)
    return JSONResponse({"status": "ok", "data": folder_data, "auth_home_path": None})




"""SAVE_PROGRESS = {}

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(...),
    password: str = Form(...),
    id: str = Form(...),
    total_size: str = Form(...),
):
    global SAVE_PROGRESS

    if password != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    total_size = int(total_size)
    SAVE_PROGRESS[id] = ("running", 0, total_size)

    ext = file.filename.lower().split(".")[-1]
    cache_dir = Path("./cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    file_location = cache_dir / f"{id}.{ext}"

    file_size = 0

    async with aiofiles.open(file_location, "wb") as buffer:
        # Read file in chunks (adjust chunk size as needed)
        chunk_size = 1024 * 1024  # 1MB
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break  # End of file

            SAVE_PROGRESS[id] = ("running", file_size, total_size)
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                await buffer.close()
                file_location.unlink()
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds {MAX_FILE_SIZE} bytes limit",
                )
            await buffer.write(chunk)

    SAVE_PROGRESS[id] = ("completed", file_size, file_size)
    asyncio.create_task(
        start_file_uploader(file_location, id, path, file.filename, file_size)
    )
    return JSONResponse({"id": id, "status": "ok"}) """



SAVE_PROGRESS = {}
UPLOAD_DIRECTORY = "./cache"

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = Form(...),
    path: str = Form(...),
    password: str = Form(...),
    filenamex: str = Form(...),
    id: str = Form(...),
    chunkIndex: int = Form(...),
    totalChunks: int = Form(...),
    filename: str = Form(...),
    total_size: int = Form(...)
):
    global SAVE_PROGRESS

    if password != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"}, status_code=403)

    # Create upload directory
    upload_dir = Path(UPLOAD_DIRECTORY) / path
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Temporary file path for chunks
    temp_file_path = upload_dir / f"{filename}.part"

    # Append the chunk to the temporary file
    async with aiofiles.open(temp_file_path, "ab") as f:
        chunk = await file.read()
        await f.write(chunk)

    SAVE_PROGRESS[id] = {
        "status": "running",
        "uploaded_chunks": chunkIndex + 1,
        "total_chunks": totalChunks,
        "uploaded_size": (chunkIndex + 1) * 50 * 1024 * 1024,
        "total_size": total_size,
    }

    # If all chunks are received, assemble the final file
    if chunkIndex + 1 == totalChunks:
        final_file_path = upload_dir / filenamex

        async with aiofiles.open(final_file_path, "wb") as final_file:
            async with aiofiles.open(temp_file_path, "rb") as temp_file:
                while data := await temp_file.read(1024 * 1024):  # Read 1MB at a time
                    await final_file.write(data)

        # Remove temporary file
        os.remove(temp_file_path)
        asyncio.create_task(
            start_file_uploader(final_file_path, id, path, filenamex, total_size)
        )
        SAVE_PROGRESS[id] = {
            "status": "completed",
            "uploaded_chunks": totalChunks,
            "total_chunks": totalChunks,
            "uploaded_size": total_size,
            "total_size": total_size,
        }

    return JSONResponse({"status": "ok", "progress": SAVE_PROGRESS[id]})
# uploading final file to storage server


    return JSONResponse({"id": id, "status": "ok"})
        
@app.post("/api/getSaveProgress")
async def get_save_progress(request: Request):
    global SAVE_PROGRESS

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"getUploadProgress {data}")
    try:
        progress = SAVE_PROGRESS[data["id"]]
        return JSONResponse({"status": "ok", "data": progress})
    except:
        return JSONResponse({"status": "not found"})


@app.post("/api/getUploadProgress")
async def get_upload_progress(request: Request):
    from utils.uploader import PROGRESS_CACHE

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"getUploadProgress {data}")

    try:
        progress = PROGRESS_CACHE[data["id"]]
        return JSONResponse({"status": "ok", "data": progress})
    except:
        return JSONResponse({"status": "not found"})


@app.post("/api/cancelUpload")
async def cancel_upload(request: Request):
    from utils.uploader import STOP_TRANSMISSION
    from utils.downloader import STOP_DOWNLOAD

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"cancelUpload {data}")
    STOP_TRANSMISSION.append(data["id"])
    STOP_DOWNLOAD.append(data["id"])
    return JSONResponse({"status": "ok"})


@app.post("/api/renameFileFolder")
async def rename_file_folder(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"renameFileFolder {data}")
    DRIVE_DATA.rename_file_folder(data["path"], data["name"])
    return JSONResponse({"status": "ok"})


@app.post("/api/trashFileFolder")
async def trash_file_folder(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"trashFileFolder {data}")
    DRIVE_DATA.trash_file_folder(data["path"], data["trash"])
    return JSONResponse({"status": "ok"})


@app.post("/api/deleteFileFolder")
async def delete_file_folder(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"deleteFileFolder {data}")
    DRIVE_DATA.delete_file_folder(data["path"])
    return JSONResponse({"status": "ok"})


@app.post("/api/getFileInfoFromUrl")
async def getFileInfoFromUrl(request: Request):

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"getFileInfoFromUrl {data}")
    try:
        file_info = await get_file_info_from_url(data["url"])
        return JSONResponse({"status": "ok", "data": file_info})
    except Exception as e:
        return JSONResponse({"status": str(e)})


@app.post("/api/startFileDownloadFromUrl")
async def startFileDownloadFromUrl(request: Request):
    data = await request.json()
    print("fukin data: ", data)
    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"startFileDownloadFromUrl {data}")
    try:
        id = getRandomID()
        asyncio.create_task(
            download_file(data["url"], id, data["path"], data["filename"], data["singleThreaded"])
        )
        return JSONResponse({"status": "ok", "id": id})
    except Exception as e:
        return JSONResponse({"status": str(e)})


@app.post("/api/getFileDownloadProgress")
async def getFileDownloadProgress(request: Request):
    from utils.downloader import DOWNLOAD_PROGRESS

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"getFileDownloadProgress {data}")

    try:
        progress = DOWNLOAD_PROGRESS[data["id"]]
        return JSONResponse({"status": "ok", "data": progress})
    except:
        return JSONResponse({"status": "not found"})


@app.post("/api/getFolderShareAuth")
async def getFolderShareAuth(request: Request):
    from utils.directoryHandler import DRIVE_DATA

    data = await request.json()

    if data["password"] != ADMIN_PASSWORD:
        return JSONResponse({"status": "Invalid password"})

    logger.info(f"getFolderShareAuth {data}")

    try:
        auth = DRIVE_DATA.get_folder_auth(data["path"])
        return JSONResponse({"status": "ok", "auth": auth})
    except:
        return JSONResponse({"status": "not found"})


