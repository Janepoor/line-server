import os
from tornado.httpserver import HTTPServer
import tornado.web
import logging
import tornado.ioloop

# user defined packages
import tornado_routes
import gb

log = logging.getLogger(__name__)


def get_tornado_application():
    return tornado.web.Application(tornado_routes.routes)


tornado_app = get_tornado_application()


def start_tornado_server():
    server = HTTPServer(tornado_app, xheaders=True)
    server.bind(12356)
    # start multiple tornado process
    server.start()
    log.info("Tornado Server is up!!! on PORT %s", 12356)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    start_tornado_server()