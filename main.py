from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import httpx
import asyncio
import os

app = FastAPI()

response_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*'
}

ADDON_FETCH_LIST = [
    "https://torrentioita.stremio-italia.eu/oResults=false/aHR0cHM6Ly90b3JyZW50aW8uc3RyZW0uZnVuL3Byb3ZpZGVycz15dHMsZXp0dixyYXJiZywxMzM3eCx0aGVwaXJhdGViYXksa2lja2Fzc3RvcnJlbnRzLHRvcnJlbnRnYWxheHksbWFnbmV0ZGwsaG9ycmlibGVzdWJzLG55YWFzaSx0b2t5b3Rvc2hvLGFuaWRleCxydXRvcixydXRyYWNrZXIsY29tYW5kbyxibHVkdix0b3JyZW50OSxpbGNvcnNhcm9uZXJvLG1lam9ydG9ycmVudCx3b2xmbWF4NGssY2luZWNhbGlkYWQsYmVzdHRvcnJlbnRzfGxhbmd1YWdlPWl0YWxpYW4=/manifest.json",
    "https://icv.stremio-italia.eu/manifest.json",
    "https://streamvix.hayd.uk/manifest.json",
    "https://tvvoo.hayd.uk/manifest.json",
    "https://streailer.elfhosted.com/manifest.json",
    "https://top-streaming.stream/username=temporary_username/manifest.json",
    "https://toast-translator.elfhosted.com/manifest.json",
    "https://toastflix.stremio-italia.eu/manifest.json",
    "https://trakt.realbestia.com/manifest.json",
    "https://easycatalogs.realbestia.com/manifest.json",
    "https://easystreams.realbestia.com/manifest.json",
    "https://mammamia.stremio-italia.eu/fFNDfEFXfExJVkVUVnxDQnxHU3xHSER8R098R0Z8RVN8UlR8VEl8T1NUfFZEfFNDX01GUHw=/manifest.json"
]

# Files Load
with open("manifest.json", "r", encoding="utf-8") as f:
    ADDONS = json.load(f)

with open("plugin_manifest.json", "r", encoding="utf-8") as f:
    PLUGIN_MANIFEST = json.load(f)


@app.get("/manifest.json")
async def manifest():
    return JSONResponse(ADDONS, headers=response_headers)


@app.get("/addon_catalog/{type}/{id}.json")
async def get_addon_catalog(type: str, id: str):
    addons = []
    tasks = []

    async with httpx.AsyncClient(timeout=20) as client:
        for addon in ADDON_FETCH_LIST:
            tasks.append(
                client.get(addon)
            )

        results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        if result.status_code == 200:
            result = result.json()

            # Config required force
            if result["id"] == "default.global.topstreaming.flixpatrol" or result["id"] == "org.stremio.mammamia" or result["id"] == "org.nuvio.trakt.recommendations":
                result["behaviorHints"] = {
                    "configurable": True,
                    "configurationRequired": True
                }
            
            # Append addons to list
            addons.append(
                {
                    "transportName": "http",
                    "transportUrl": ADDON_FETCH_LIST[i],
                    "manifest": result
                }
            )

    # Plugin Addon
    addons.append(
        {
            "transportName": "http",
            "transportUrl": "http://127.0.0.1:11470/plugin/manifest.json",
            "manifest": PLUGIN_MANIFEST
        }
    )
    
    return JSONResponse({"addons" : addons}, headers=response_headers)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))