from subprocess import Popen, PIPE
from threading import Thread
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class Debugger:
    def __init__(self):
        self.ws = None
        self.process = None
        self.thread = None

    def start(self, websocket, msg):
        if msg.get("command") == "initialize":
            self.ws = websocket
            logger.info("Starting debugpy adapter process")

            import sys

            python_path = sys.executable
            self.process = Popen(
                [python_path, "-m", "debugpy.adapter"],
                stdout=PIPE,
                stdin=PIPE,
                stderr=PIPE,
                bufsize=0,
            )
            self.thread = Thread(target=self._read_output, daemon=True)
            self.thread.start()

    def _read_output(self):
        logger.debug("Starting to read debug adapter output")
        while True:
            output = self.process.stdout.readline()
            if not output:
                logger.info("Debug adapter output stream ended")
                error = self.process.stderr.read()
                if error:
                    logger.error(f"Debugpy error: {error.decode('utf-8')}")
                break
            if output.lower().startswith(b"content-length: "):
                length = int(output.split(b":")[1].strip())
                logger.debug(f"Message length: {length}")
                self.process.stdout.readline()
                content_bytes = self.process.stdout.read(length)
                content_str = content_bytes.decode()
                message = json.loads(content_str)
                logger.debug(f"Received from debug adapter: {message}")
                if self.ws:
                    Thread(
                        target=lambda: asyncio.run(
                            self.ws.send_text(json.dumps(message))
                        ),
                        daemon=True,
                    ).start()

    def send_message(self, msg):
        payload = json.dumps(msg)
        content = f"Content-Length: {len(payload)}\r\n\r\n{payload}".encode()
        assert self.process and self.process.stdin
        self.process.stdin.write(content)
        self.process.stdin.flush()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
