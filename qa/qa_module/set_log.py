import logging


class Log:
    def __init__(self, name="LoggingTest", file="test.log") -> None:
        self.logger: logging.Logger = logging.getLogger(name)

        sh = logging.StreamHandler()
        self.logger.addHandler(sh)

        fh = logging.FileHandler(file, mode="w")
        self.logger.addHandler(fh)

    def set_level(self, level=20):
        self.logger.setLevel(level)
