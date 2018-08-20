from multiprocessing import Queue

queues = {
    "bytes_queue": Queue(),
    "ws_queue": Queue(),
    "task_queue": Queue(),
    "image_queue_a": Queue(), # digit
    "image_queue_b": Queue(), # cross
    "image_queue_c": Queue(), # chess
    "id_queue": Queue(),
}
