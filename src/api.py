from abc import ABC, abstractmethod
from textwrap import dedent
from flask import Flask, request, jsonify
import threading
from werkzeug.serving import make_server

from src.config import settings

__all__ = ["TokenManager"]

class SessionServerInterface(ABC):
    def __init__(self, port: int = settings.API_PORT):
        self.app = Flask(__name__)
        self.port = port
        self.token = None
        self.token_event = threading.Event()
        self.server = None
        self._setup_routes()
    
    @abstractmethod
    def _setup_routes(self): ...

    def start_server(self):
        self.server = make_server('0.0.0.0', self.port, self.app)
        self.server.serve_forever()

    def shutdown_server(self):
        if self.server:
            self.server.shutdown()
            self.server = None

    def wait_for_token(self):
        # start the flask server in a separate thread
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        # wait until the token is received
        self.token_event.wait()
        # reset the event for future use
        self.token_event.clear()
        # ensure the server thread has finished
        server_thread.join()
        return self.token

class TokenManager(SessionServerInterface):
    def _setup_routes(self):
        @self.app.route('/token', methods=['POST'])
        def receive_token():
            data = request.get_json()
            if not data or 'token' not in data:
                return jsonify({'error': 'Token not provided'}), 400
            self.token = data['token']
            self.token_event.set()  # Signal that the token has been received
            threading.Thread(target=self.shutdown_server).start()
            return jsonify({'status': 'Token received'})
        
        @self.app.route('/status', methods=['GET'])
        def status():
            return jsonify({'status': 'Awaiting token submission'})

    def wait_for_token(self):
        console_message = dedent(f"""
        Linkedin just sent a token to the bot!
        Waiting for token submission at:
        0.0.0.0:{self.port}/token

        Please submit a POST request to the /token endpoint with the JSON payload structured as follows:
        {{
            "token": "<your_token_here>"
        }}

        Replace "<your_token_here>" with your actual token value.
        """)
        print(console_message)
        return super().wait_for_token()
