from socketserver import TCPServer

from common.configs.manipulator import settings
from manipulator.request_handler import ManipulatorCommandHandler
from common.configs.logger import logging


if __name__ == "__main__":
    logging.info(f"Manipulator listening on port {settings.PORT}")
    with TCPServer(("0.0.0.0", settings.PORT), ManipulatorCommandHandler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Manipulator shutting down...")
