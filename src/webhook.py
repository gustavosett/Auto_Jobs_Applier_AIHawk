from typing import Optional

import requests

from src.config import settings

__all__ = ["WebhookManager"]

class HookTypes:
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    REQUEST_TOKEN = 'request_token'

class WebhookManager:
    def __init__(self, webhook_uri: Optional[str] = None, bot_id: Optional[str] = None):
        # if the webhook URL and bot ID are not provided, the class will be used as a dummy class.
        if not webhook_uri and not bot_id:
            self.send_message = lambda *args, **kwargs: ...
            
        self.webhook_uri = webhook_uri
        self.bot_id = bot_id

    def send_message(self, message: str, hook_type: str = HookTypes.REQUEST_TOKEN):
        try:
            if not self.webhook_uri or not self.bot_id:
                raise ValueError("Webhook URL and Bot ID must be set in the environment variables.")
            headers = {
                'Content-Type': 'application/json',
            }
            if settings.WEBHOOK_TOKEN:
                headers['Authorization'] = settings.WEBHOOK_TOKEN
            
            payload = {
                'bot_id': self.bot_id,
                'message': message,
                'type': hook_type
            }
            response = requests.post(self.webhook_uri, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending message to webhook: {e}")

    def send_error(self, message: str):
        return self.send_message(f"❌ {message}", hook_type=HookTypes.ERROR)

    def send_success(self, message: str):
        return self.send_message(f"✅ {message}", hook_type=HookTypes.SUCCESS)

    def send_warning(self, message: str):
        return self.send_message(f"⚠️ {message}", hook_type=HookTypes.WARNING)
    
    def send_request_token(self, message: str):
        return self.send_message(f"🔐 {message}", hook_type=HookTypes.REQUEST_TOKEN)
