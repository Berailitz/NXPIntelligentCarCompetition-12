"""Build MNIST format database from images in `config.IMAGE_SAMPLE_FOLDER`."""
#!/usr/env/python3
# -*- coding: UTF-8 -*

import argparse
import glob
import logging
import os
from array import *
from random import shuffle
from PIL import Image
from monitor.config import LOG_PATH, MNIST_DATABASE_FOLDER, IMAGE_SAMPLE_FOLDER, NETWORK_IMAGE_DIMENSIONS
from monitor.mess import get_current_time, set_logger, try_int


def build_database(file_list: list, database_basename: str):
    image_counter = len(file_list)
    database_header = array('B')
    data_array_image = array('B')
    data_array_label = array('B')
    width = NETWORK_IMAGE_DIMENSIONS[0]
    height = NETWORK_IMAGE_DIMENSIONS[1]
    for jpg_filename in file_list:
        label = try_int(os.path.splitext(
            os.path.basename(jpg_filename))[0].split('_')[-1])
        if label is None:
            logging.error('Cannot prase filename `{}`.'.format(jpg_filename))
            image_counter -= 1
            continue
        else:
            image = Image.open(jpg_filename)
            pixels = image.load()
            for x in range(0, width):
                for y in range(0, height):
                    data_array_image.append(pixels[y, x])
            data_array_label.append(label)

    hexval = "{0:#0{1}x}".format(image_counter, 6)  # number of files in HEX
    database_header.extend([0, 0, 8, 1, 0, 0])
    database_header.append(int('0x'+hexval[2:][:2], 16))
    database_header.append(int('0x'+hexval[2:][2:], 16))
    data_array_label = database_header + data_array_label

    if max([width, height]) <= 256:
        database_header.extend([0, 0, 0, width, 0, 0, 0, height])
    else:
        raise ValueError('Image exceeds maximum size: 256x256 pixels')
    database_header[3] = 3  # Changing MSB for image data (0x00000803)
    data_array_image = database_header + data_array_image

    image_database_filename = database_basename + '-images-idx3-ubyte'
    label_database_filename = database_basename + '-labels-idx1-ubyte'
    with open(image_database_filename, 'wb') as output_file:
        data_array_image.tofile(output_file)
    with open(label_database_filename, 'wb') as output_file:
        data_array_label.tofile(output_file)
    os.system('gzip {}'.format(image_database_filename))
    os.system('gzip {}'.format(label_database_filename))
    logging.info('Build ended. (`{}` images built).'.format(image_counter))

def build_mnist(image_folder: str, database_folder: str):
    jpg_filenames = glob.glob(os.path.join(image_folder, '*.jpg'))
    image_counter = len(jpg_filenames)
    logging.info('Build MNIST database `{}` from `{}`. (`{}` images found)'.format(
        database_folder, image_folder, image_counter))
    shuffle(jpg_filenames)
    train_image_counter = round(0.9 * image_counter)
    test_image_counter = image_counter - train_image_counter
    logging.info('Build train database from `{}` images.'.format(train_image_counter))
    build_database(jpg_filenames[:train_image_counter], os.path.join(database_folder, 'train'))
    logging.info('Build train database from `{}` images.'.format(test_image_counter))
    build_database(jpg_filenames[-test_image_counter:], os.path.join(database_folder, 'test'))
    logging.info("All done.")

def main():
    set_logger('{}/log_build_mnist_{}.txt'.format(LOG_PATH, get_current_time()))
    parser = argparse.ArgumentParser()
    parser.add_argument('--database-folder', type=str, default=MNIST_DATABASE_FOLDER,
                        help='Folder to store MNIST database')
    parser.add_argument('--image-folder', type=str, default=IMAGE_SAMPLE_FOLDER,
                        help='Folder containing target jpgs')
    flags, _unparsed = parser.parse_known_args()
    build_mnist(**flags.__dict__)


if __name__ == '__main__':
    main()
