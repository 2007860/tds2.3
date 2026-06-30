from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml, os

load_dotenv()

app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

defaults={
    "port":8000,
    "workers":1,
    "debug":False,
    "log_level":"info",
    "api_key":"default-secret-000"
}

def to_bool(v):
    return str(v).strip().lower() in ("true","1","yes","on")

def coerce(k,v):
    if k in ("port","workers"):
        return int(v)
    if k=="debug":
        return to_bool(v)
    return str(v)

@app.get("/")
def root():
    return {"status":"ok"}

@app.get("/effective-config")
def effective_config(set:list[str]=Query(default=[])):
    cfg=defaults.copy()

    env=os.getenv("APP_ENV","development")
    fn=f"config.{env}.yaml"
    if os.path.exists(fn):
        with open(fn) as f:
            y=yaml.safe_load(f) or {}
        for k,v in y.items():
            cfg[k]=coerce(k,v)

    # .env loaded into environment
    for ek,cv in [("APP_PORT","port"),("APP_DEBUG","debug"),("APP_LOG_LEVEL","log_level"),("APP_API_KEY","api_key"),("NUM_WORKERS","workers")]:
        if ek in os.environ:
            cfg[cv]=coerce(cv,os.environ[ek])

    for ek,cv in [("APP_PORT","port"),("APP_WORKERS","workers"),("APP_DEBUG","debug"),("APP_LOG_LEVEL","log_level"),("APP_API_KEY","api_key")]:
        if ek in os.environ:
            cfg[cv]=coerce(cv,os.environ[ek])

    for item in set:
        if "=" in item:
            k,v=item.split("=",1)
            cfg[k]=coerce(k,v)

    cfg["api_key"]="****"
    return cfg
