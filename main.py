import os
import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(v):
    return str(v).strip().lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    config = DEFAULTS.copy()

    # -----------------------------
    # YAML layer
    # -----------------------------
    env = os.getenv("APP_ENV", "development")
    yaml_file = f"config.{env}.yaml"

    if os.path.exists(yaml_file):
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f) or {}

        for k, v in data.items():
            config[k] = coerce(k, v)

    # -----------------------------
    # .env layer
    # -----------------------------
    env_file = dotenv_values(".env")

    mapping = {
        "APP_PORT": "port",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
        "NUM_WORKERS": "workers",
    }

    for env_key, cfg_key in mapping.items():
        if env_key in env_file:
            config[cfg_key] = coerce(cfg_key, env_file[env_key])

    # -----------------------------
    # OS environment layer
    # -----------------------------
    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for env_key, cfg_key in mapping.items():
        if env_key in os.environ:
            config[cfg_key] = coerce(cfg_key, os.environ[env_key])

    # -----------------------------
    # CLI overrides (?set=...)
    # -----------------------------
    for item in set:
        if "=" not in item:
            continue

        k, v = item.split("=", 1)
        config[k] = coerce(k, v)

    config["api_key"] = "****"

    return config