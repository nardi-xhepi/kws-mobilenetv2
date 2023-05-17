import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AudioProcessingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        result = ""
        if text_data is not None:
            result = await self.receive_text(text_data)
        elif bytes_data is not None:
            result = await self.receive_bytes(bytes_data)

        await self.send(text_data=json.dumps({
            'prediction': result
        }))

    async def receive_text(self, text_data):
        # Handle text data.
        return "Text result"

    async def receive_bytes(self, bytes_data):
        return "Test result"
