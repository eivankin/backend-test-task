from socketserver import StreamRequestHandler
import logging

from common.messages.from_controller import ControllerDecision


class ManipulatorCommandHandler(StreamRequestHandler):
    def handle(self) -> None:
        raw_data = self.rfile.readline()
        data = ControllerDecision.model_validate_json(raw_data)
        logging.info(f"Received command: {data.status.value}")
