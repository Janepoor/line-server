from abc import abstractmethod
import tornado.web
from tornado import gen

from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import json
import socket
import logging

# user defined packages
from ..handler_utils import parse_input
from ..handler_utils import parse_urlencoded

VALID_KEYS = ["wangqifei", "winston", "kevin"]
MAX_WORKERS = 30

log = logging.getLogger(__name__)


class BasicHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    """
    basic type for all other handlers
    """
    def set_default_headers(self):

        log.debug("Set default header")

        origin = self.request.headers.get('Origin', "")
        self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header("Accept-Encoding", "gzip")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Accept")

    def initialize(self):
        pass

    def options(self):
        return

    def verify(self):
        data = getattr(self.request, 'request_data', None)
        return data

    @tornado.gen.coroutine
    def post(self):
        res = yield self.background_task()
        self.write(res)

    @tornado.gen.coroutine
    def get(self):
        res = yield self.background_task()
        self.write(res)

    @abstractmethod
    @run_on_executor
    def background_task(self):
        pass

    def prepare(self):
        """
        This is before passing the security check , and before any http method: get/post/option
        Should be override if you don't want to process data, otherwise will parse the request data for each request
        :return:
        """

        # Don't do any process and auth for option call
        if self.request.method == "OPTIONS":
            return

        if getattr(self.request, 'request_data', None):
            return
        try:
            setattr(self.request, 'request_data', self.process_data())
        except Exception as e:
            log.error("Error preparing request data", exc_info=True)
        return

    def process_data(self):
        try:
            log.info("Received User %s request for %s", self.request.method, self.__class__.__name__)
            content_type = self.request.headers.get("Content-Type", "")
            if content_type.startswith("application/json"):
                data = json.loads(self.request.body, encoding="utf8")
                self.set_header("Content-Type", "application/json")
            elif content_type.startswith("application/x-www-form-urlencoded"):
                data = parse_urlencoded(self.request.body)
            elif content_type.startswith("multipart/form-data"):
                data = self.process_multipart_data()
            else:
                data = parse_input(self.request.uri)
        except Exception as e:
            log.error("Error parsing request data", exc_info=True)
            return {}
        return data

    def process_multipart_data(self):
        data = {}

        # get the file field
        for file_name in self.request.files:
            log.info("Found file %s", file_name)
            files = self.request.files[file_name]
            file = files[0]
            data[file_name] = {}
            data[file_name]['value'] = file['body']
            for key, value in file.items():
                if key != 'body':
                    data[file_name][key] = value

        # get the other text field
        args = self.request.body_arguments
        # unicode string
        for key in args:
            try:
                # log.info(key)
                val = self.get_arguments(key)[0]
                # log.info(val)
                data[key] = val
            except Exception as e:
                log.error("Error parsing multi part request", exc_info=True)

        return data

    def validate_ip(self, addr):
        try:
            socket.inet_pton(socket.AF_INET, addr)
            return True
        except socket.error:
            log.warning("Invalid IP address")
            return False

    def parse_client_ip(self):
        log.debug("CHECK IP")
        ips = self.request.headers.get_list("X-Real-IP")
        if not ips:
            # aws lb use X-Forwarded-For
            log.warning("COULDN'T FIND X-REAL-IP")
        else:
            # TODO: find out reason why X REAL IP COME, (not from nginx but phillipine ip 49.144.137.27,)
            log.debug("REAL-IP HEADER FOUND: %s", ips)
        # always use X-Forwarded-For which is set by CDN and LB
        ips = self.request.headers.get_list("X-Forwarded-For")

        if not ips:
            log.debug("NO CLIENT IP FOUND")
            return None
        ips = ips[0]
        ips = ips.strip("\r\n")
        ips = ips.split(',')
        if ips:
            if len(ips) == 2 or len(ips) == 3:
                # by default, if there is no user set IP header, CDN and LB will create 2 IP headers
                if len(ips) == 2:
                    log.debug("NORMAL IP HEADER")
                else:
                    log.debug("USER BRING SELF IP HEADER")
                # count from backend in case user append multiple headers
                real_client_ip = ips[-2]
                if not self.validate_ip(real_client_ip):
                    return None
                log.debug("CLIENT IP IS %s", real_client_ip)
                return real_client_ip
            else:
                log.debug("UNRECOGNIZED IP HEADER LENGTH " + ",".join(ips))
                return None
        else:
            log.debug("NO CLIENT IP FOUND")
            return None