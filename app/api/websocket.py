import base64
import json
import re
import uuid
import logging

from agents import Runner
from fastapi import APIRouter, WebSocket
from openai.types.responses import ResponseTextDeltaEvent

from app.services.memory_service import get_memory_facts, extract_and_save_memory
from app.services.bot_service import bot_agent, config
from app.services.gemini_voice_agent import SimpleGeminiVoice

logger = logging.getLogger(__name__)
router = APIRouter()

async def stream_audio_to_client(websocket, voice_client):
    """
    Gemini se aane wala audio websocket client ko send karega.
    """
    async for msg in voice_client.ws:
        try:
            response = json.loads(msg)
            audio_data = response["serverContent"]["modelTurn"]["parts"][0]["inlineData"]["data"]
            decoded_audio = base64.b64decode(audio_data)
            await websocket.send_bytes(decoded_audio)
        except Exception:
            pass

voice_client = None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = str(uuid.uuid4())
    logger.info("WS connected: user=%s", user_id)
    
    global voice_client

    try:
        while True:
            try:
                message = await websocket.receive()
            except RuntimeError:
                # Client disconnected
                break

            if "bytes" in message:
                raw_audio = message["bytes"]
                try:
                    await voice_client.ws.send(json.dumps({ #type: ignore
                        "realtime_input": {
                            "media_chunks": [{
                                "data": base64.b64encode(raw_audio).decode(),
                                "mime_type": "audio/pcm",
                            }]
                        }
                    }))
                except Exception as e:
                    print("Error sending audio to Gemini:", e)


            elif "text" in message:
                data = message["text"]

                try:
                    parsed = json.loads(data)
                    
                    if parsed.get("type") == "control":
                        action = parsed.get("action")
                        if action == "start_audio":
                            if voice_client is None:
                                voice_client = SimpleGeminiVoice()
                                await voice_client.start()
                                print("✅ Voice agent started on button click")
                                
                        elif action == "stop_audio":
                            if voice_client:
                                try:
                                    await voice_client.ws.close()  # stop the voice WS connection
                                except Exception as e:
                                    print("Error stopping voice client:", e)
                                voice_client = None
                                print("🛑 Voice agent stopped")
                                
                    elif parsed.get("type") == "text":
                        user_text = parsed.get("text")
                        
                        user_id = parsed.get("user_id", user_id)
                                                
                        # Only call AI agent if this is not an order creation/status query
                        memory_context = await get_memory_facts(user_id)
                        memory_str = " | ".join([f"{k}: {v}" for k, v in memory_context.items()])
                        prompt = f"Memory: {memory_str}\nUser says: {user_text}"
                        result = Runner.run_streamed(bot_agent, input=prompt, run_config=config)
                        async for event in result.stream_events():
                            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                                chunk = event.data.delta
                                await websocket.send_text(json.dumps({
                                    "type": "ai_chunk",
                                    "text": chunk
                                }))
                        await extract_and_save_memory(user_id, user_text)
                        # Final AI response
                        await websocket.send_text(json.dumps({
                            "type": "ai_final",
                            "text": result.final_output
                        }))

                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "ai_chunk",
                        "text": f"Echo: {data} (error: {str(e)})"
                    }))
    except Exception as e:
        print("WebSocket crashed:", e)
    finally:
        await websocket.close()
        print("WebSocket connection closed")

