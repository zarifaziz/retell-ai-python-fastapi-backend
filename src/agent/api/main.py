import json

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from retell import APIConnectionError, APIStatusError, RateLimitError, Retell

from ..settings import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retell_client = Retell(api_key=settings.retell.api_key)


@app.get("/health")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "healthy"})


# Handle webhook from Retell server. This is used to receive events from Retell server.
# Including call_started, call_ended, call_analyzed
@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        post_data = await request.json()
        valid_signature = await retell_client.verify(
            json.dumps(post_data, separators=(",", ":")),
            api_key=settings.retell.api_key,
            signature=str(request.headers.get("X-Retell-Signature")),
        )
        if not valid_signature:
            print(
                "Received Unauthorized",
                post_data["event"],
                post_data["data"]["call_id"],
            )
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})
        if post_data["event"] == "call_started":
            print("Call started event", post_data["data"]["call_id"])
        elif post_data["event"] == "call_ended":
            print("Call ended event", post_data["data"]["call_id"])
        elif post_data["event"] == "call_analyzed":
            print("Call analyzed event", post_data["data"]["call_id"])
        else:
            print("Unknown event", post_data["event"])
        return JSONResponse(status_code=200, content={"received": True})
    except Exception as err:
        print(f"Error in webhook: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


# Only used for web call frontend to register call so that frontend don't need api key.
# If you are using Retell through phone call, you don't need this API. Because
# this.twilioClient.ListenTwilioVoiceWebhook() will include register-call in its function.
@app.post("/register-call-on-your-server")
async def handle_register_call(request: Request):
    try:
        post_data = await request.json()
        call_response = await retell_client.call.register(
            agent_id=post_data["agent_id"],
            audio_websocket_protocol="web",
            audio_encoding="s16le",
            sample_rate=post_data[
                "sample_rate"
            ],  # Sample rate has to be 8000 for Twilio
        )
        print(f"Call response: {call_response}")
    except Exception as err:
        print(f"Error in register call: {err}")
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )


@app.post("/create-web-call")
async def create_web_call(request: Request):
    try:
        post_data = await request.json()
        agent_id = post_data.get("agent_id")
        metadata = post_data.get("metadata")
        retell_llm_dynamic_variables = post_data.get("retell_llm_dynamic_variables")

        payload = {"agent_id": agent_id}

        if metadata:
            payload["metadata"] = metadata

        if retell_llm_dynamic_variables:
            payload["retell_llm_dynamic_variables"] = retell_llm_dynamic_variables

        headers = {
            "Authorization": f"Bearer {settings.retell.api_key}",  # Replace with your actual Bearer token
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.retellai.com/v2/create-web-call",
                json=payload,
                headers=headers,
            )

        response.raise_for_status()
        return JSONResponse(status_code=201, content=response.json())
    except httpx.HTTPStatusError as exc:
        print(f"Error creating web call: {exc.response.json()}")
        return JSONResponse(
            status_code=500, content={"error": "Failed to create web call"}
        )
    except APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)
        return JSONResponse(status_code=500, content={"error": "API Connection Error"})
    except RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        return JSONResponse(status_code=429, content={"error": "Rate Limit Exceeded"})
    except APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        return JSONResponse(
            status_code=e.status_code, content={"error": "API Status Error"}
        )
    except Exception as err:
        print(f"Error: {err}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})


if __name__ == "__main__":
    uvicorn.run(
        "src.agent.api.main:app",
        host="0.0.0.0",
        port=settings.fastapi.port,
        reload=settings.fastapi.reload,
        server_header=False,
    )
