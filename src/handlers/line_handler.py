from tornado.concurrent import run_on_executor

# user defined packages
from handlers.basics.base_handler import BasicHandler
from business_logic.line_operation import get_line


class GetLineHandler(BasicHandler):
    @run_on_executor
    def background_task(self):
        data = self.verify()
        import pdb
        pdb.set_trace()
        result = get_line(data=data)
        return result