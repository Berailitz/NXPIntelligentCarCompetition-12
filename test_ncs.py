"Test network with test images."
#! /usr/bin/env python3

import argparse
import glob
import logging
import operator
import time
import os
import cv2
from monitor.config import IMAGE_TEST_FOLDER, LOG_PATH, NETWORK_GRAPH_FILENAME
from monitor.mess import get_current_time, set_logger, try_int
from monitor.ncs import NCSDevice


def test_ncs(graph_path, test_folder):
    jpg_list = glob.glob(os.path.join(test_folder, "*.jpg"))
    image_list = [cv2.imread(jpg_file, cv2.IMREAD_GRAYSCALE)
                  for jpg_file in jpg_list]
    image_counter = len(jpg_list)
    with NCSDevice(0) as ncs:
        ncs.load_graph(graph_path)
        inference_result = ncs.inference(image_list)
    ocr_results = [max(enumerate(
        infer_probabilitie), key=operator.itemgetter(1)) for infer_probabilitie in inference_result]
    logging.info("File\tResult\tError")
    error_counter = 0
    start_time = time.time()
    for jpg_index, ocr_result in enumerate(ocr_results):
        jpg_filename = jpg_list[jpg_index]
        jpg_basename = os.path.basename(jpg_filename)
        real_digit = try_int(os.path.splitext(
            jpg_basename)[0].split('_')[-1])
        if real_digit is None:
            logging.error('Cannot prase filename `{}`.'.format(jpg_filename))
            continue
        else:
            ocr_digit = ocr_result[0]
            is_error = (ocr_digit != real_digit)
            if is_error:
                error_counter += 1
            logging.info("{}\t{}\t{}".format(
                jpg_basename, ocr_digit, is_error))
    end_time = time.time()
    logging.info("Error rate: {} / {} ({}%).".format(error_counter,
                                                     image_counter, 100 * error_counter / image_counter))
    logging.info("Test ended. (in `{}`s)".format(end_time - start_time))


def main():
    set_logger('{}/log_build_mnist_{}.txt'.format(LOG_PATH, get_current_time()))
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph-path', type=str, default=NETWORK_GRAPH_FILENAME,
                        help='Path to graph file')
    parser.add_argument('--test-folder', type=str, default=IMAGE_TEST_FOLDER,
                        help='Folder containing test jpgs')
    flags, _unparsed = parser.parse_known_args()
    test_ncs(**flags.__dict__)


if __name__ == '__main__':
    main()
