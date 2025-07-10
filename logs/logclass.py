# app/logs/logclass.py
from logs import json, os, datetime, RotatingFileHandler, logging


class JSONLogger:
    def __init__(self, log_dir="logs", max_bytes=5 * 1024 * 1024 * 1024, backup_count=3):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        full_log_dir = os.path.join(base_dir, log_dir)
        os.makedirs(full_log_dir, exist_ok=True)

        self.combined_log_file = os.path.join(full_log_dir, "combined.log")
        self.request_log_file = os.path.join(full_log_dir, "request.log")
        self.error_log_file = os.path.join(full_log_dir, "error.log")

        self.combined_logger = self._setup_logger("combined_logger", self.combined_log_file, max_bytes, backup_count)
        self.request_logger = self._setup_logger("request_logger", self.request_log_file, max_bytes, backup_count)
        self.error_logger = self._setup_logger("error_logger", self.error_log_file, max_bytes, backup_count)

    def _setup_logger(self, name, log_file, max_bytes, backup_count):
        """Configures a logger with file rotation and JSON format"""

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

        return logger

    def log_request(self, request):
        """Logs the request information from the Flask `request` object"""

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "type": "request",
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "ip": request.remote_addr,
            "body": self._get_request_body(request),
        }

        self._log(self.request_logger, self.combined_logger, log_data)

    def log_error(self, error_message, stack_trace=None):
        """Logs error information in JSON format"""

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "type": "error",
            "message": error_message,
        }
        if stack_trace:
            log_data["stack_trace"] = stack_trace

        self._log(self.error_logger, self.combined_logger, log_data)

    def _log(self, specific_logger, combined_logger, log_data):
        """Writes data to the specified logger and general logger"""

        log_json = json.dumps(log_data, ensure_ascii=False)
        specific_logger.info(log_json)
        combined_logger.info(log_json)

    @staticmethod
    def _get_request_body(request):
        """Retrieves the body of the request, if there is one"""

        try:
            if request.data:
                return request.get_json() or request.data.decode("utf-8")
            return None
        except Exception as e:
            return f"Error decoding body: {e}"


class JSONFormatter(logging.Formatter):
    """Formatter for outputting logs in JSON format"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.msg,
        }
        return json.dumps(log_data, ensure_ascii=False)


logger = JSONLogger()
