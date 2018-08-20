import base64
import json
import logging
from tornado import websocket, web
from .bus import queues

class IndexHandler(web.RequestHandler):
    def get(self, video_id):
        self.render('live.html', video_id=video_id)


class SocketHandler(websocket.WebSocketHandler):
    """ Handler for websocket queries. """
    def __init__(self, application, request):
        """ Initialize the Redis store and framerate monitor. """
        super().__init__(application, request)
        self.video_id = None

    def check_origin(self, origin):
        return True

    def open(self, video_id):
        logging.info('Open camera `{}`.'.format(video_id))
        self.video_id = video_id
        queues['id_queue'].put(video_id)
        logging.info("id_queue size {}".format(queues['id_queue'].qsize()))

    def on_message(self, message):
        """ Retrieve image ID from database until different from last ID,
        then retrieve image, de-serialize, encode and send to client. """
        try:
            index = int(message) + 1
        except ValueError:
            index = 1
        if index % 100 == 0:
            logging.info('Sending frame `{}`.'.format(index))
        queues['task_queue'].put(index)
        logging.info("Task size {}".format(queues['task_queue'].qsize()))
        self.write_message(json.dumps(queues['ws_queue'].get(), ensure_ascii=False))

    def on_close(self):
        logging.warning("WebSocket `{}` closed.".format(self.video_id))
