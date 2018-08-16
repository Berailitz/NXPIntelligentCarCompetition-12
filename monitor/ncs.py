import numpy
import cv2
import os
import time
import logging
from mvnc import mvncapi as mvncapi2
from typing import List


class NCSGraph:
    def __init__(self, api2_graph, api2_fifo_in, api2_fifo_out):
        self._api2_graph = api2_graph
        self._api2_fifo_in = api2_fifo_in
        self._api2_fifo_out = api2_fifo_out

    def deallocate(self):
        self._api2_fifo_in.destroy()
        self._api2_fifo_out.destroy()
        self._api2_graph.destroy()

    def load_tensor(self, tensor):
        _userobj = None
        self._api2_graph.queue_inference_with_fifo_elem(self._api2_fifo_in, self._api2_fifo_out, tensor, _userobj)

    def get_result(self):
        output, _userobj = self._api2_fifo_out.read_elem()
        return output.tolist()


class NCSDevice(object):
    def __init__(self, index: int):
        self.index = index
        self.device = None
        self.graph = None

    def __del__(self):
        self.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def open(self) -> None:
        logging.info("Opening device `{}`.".format(self.index))
        devices = mvncapi2.enumerate_devices()
        self.device = mvncapi2.Device(devices[self.index])
        self.device.open()
        self.is_device_opened = True
    
    def load_graph(self, graph_filename: str):
        logging.info("Load graph from `{}`.".format(graph_filename))
        with open(graph_filename, mode='rb') as graph_f:
            in_memory_graph = graph_f.read()
            api2_graph = mvncapi2.Graph(os.path.basename(graph_filename))
            api2_fifo_in, api2_fifo_out = api2_graph.allocate_with_fifos(self.device, in_memory_graph,
                                                                         input_fifo_data_type=mvncapi2.FifoDataType.FP16,
                                                                         output_fifo_data_type=mvncapi2.FifoDataType.FP16)
            self.graph = NCSGraph(api2_graph, api2_fifo_in, api2_fifo_out)
        if self.graph is None:
            raise SystemError("Cannot open NCS device {} with graph {}.".format(self.index, graph_filename))

    def close(self):
        if self.graph is not None:
            self.graph.deallocate()
            self.graph = None
        if self.device is not None:
            logging.warning("Closing NCS device {}.".format(self.index))
            self.device.close()
            self.device.destroy()
            self.device = None

    def inference(self, resized_images: list) -> (List[float]):
        for resized_image in resized_images:
            image_for_inference = resized_image.astype(numpy.float32)
            image_for_inference[:] = ((image_for_inference[:]) * (1.0 / 255.0))
            self.graph.load_tensor(image_for_inference.astype(numpy.float16))
        output = []
        for i in range(len(resized_images)):
            output.append([round(x, 3) for x in self.graph.get_result()])
        return output
