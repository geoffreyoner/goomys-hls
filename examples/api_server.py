import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from goomys_hls import Client, DownloadConfigHLS

app = FastAPI(title="Goomys HLS API")
jobs = {}

class DownloadReq(BaseModel):
    url: str
    path: str = "./downloads"

async def process(job_id: str, req: DownloadReq):
    try:
        client = Client()
        video = await client.get_video(req.url)
        
        jobs[job_id]["title"] = video.title
        jobs[job_id]["status"] = "downloading"

        def on_progress(pct):
            jobs[job_id]["progress"] = pct

        config = DownloadConfigHLS(path=req.path)
        output = await config.download(video, on_progress=on_progress)
        
        jobs[job_id]["status"] = "done"
        jobs[job_id]["output"] = output
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

@app.post("/download")
async def start_download(req: DownloadReq, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id": job_id,
        "url": req.url,
        "status": "queued",
        "progress": 0.0,
        "title": None,
        "output": None,
        "error": None
    }
    bg.add_task(process, job_id, req)
    return {"job_id": job_id}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]