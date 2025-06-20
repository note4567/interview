import logging


class Log:
    def __init__(self, name="LoggingTest", file_path="./") -> None:
        self.logger: logging.Logger = logging.getLogger(name)

        sh = logging.StreamHandler()
        self.logger.addHandler(sh)

        fh = logging.FileHandler(file_path, mode="w")
        self.logger.addHandler(fh)

        formatter = logging.Formatter("%(asctime)s: %(message)s")
        sh.setFormatter(formatter)
        fh.setFormatter(formatter)

    def set_level(self, level=20) -> None:

        self.logger.setLevel(level)
