from multiprocessing import Queue

queues = {
    "bytes_queue": Queue(),
    "ws_queue": Queue(),
    "task_queue": Queue(),
    "image_queue_a": Queue(),
    "image_queue_b": Queue(),
    "id_queue": Queue(),
}
