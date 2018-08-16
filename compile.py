"Compile network to binary graph file."
#! /usr/bin/env python3

import argparse
import os
from monitor.config import LOG_PATH, MNIST_INFERENCE_PATH_PREFIX, NETWORK_GRAPH_FILENAME
from monitor.mess import get_current_time, set_logger

def compile_graph(model_prefix: str, graph_path: str):
    os.system("mvNCCompile {}.meta -s 12 -in input -on output -o {}".format(model_prefix, graph_path))

def main():
    set_logger('{}/log_build_mnist_{}.txt'.format(LOG_PATH, get_current_time()))
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph-path', type=str, default=NETWORK_GRAPH_FILENAME,
                        help='Path to graph file')
    parser.add_argument('--model-prefix', type=str, default=MNIST_INFERENCE_PATH_PREFIX,
                        help='Path prefix to trained model')
    flags, _unparsed = parser.parse_known_args()
    compile_graph(**flags.__dict__)

if __name__ == '__main__':
    main()
