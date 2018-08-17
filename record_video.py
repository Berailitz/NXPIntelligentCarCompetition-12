"""Capture video from camera and save to `config.VIDEO_CAPTURE_FOLDER`"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import argparse
import logging
import os
import cv2
from monitor.config import CAMERA_HEIGHT, CAMERA_WIDTH, LOG_PATH, MAIN_CAMERA_ID, VIDEO_CAPTURE_FOLDER
from monitor.mess import get_current_time, set_logger, try_int


def save_video(camera_id_in_str: str) -> None:
    camera_id = try_int(camera_id_in_str, MAIN_CAMERA_ID)
    logging.info("Capture video from camera `{}`".format(camera_id))
    camera = cv2.VideoCapture(camera_id)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    path_to_video_file = os.path.join(
        VIDEO_CAPTURE_FOLDER, 'capture_{}.avi'.format(get_current_time()))
    video_writer = cv2.VideoWriter(
        path_to_video_file, fourcc, 20.0, (CAMERA_WIDTH, CAMERA_HEIGHT), False)
    if camera.isOpened():
        logging.info("Camera `{}` opened.".format(camera_id))
        frame_index = 0
    try:
        while camera.isOpened():
            ret, frame = camera.read()
            if ret is True:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                video_writer.write(gray_frame)
                frame_index += 1
            else:
                break
    except:
        logging.warning("Stop capturing video `{}` from camera `{}` with `{}` frames saved.".format(
            path_to_video_file, camera_id, frame_index))
        camera.release()
        video_writer.release()


def main():
    """main func"""
    set_logger('{}/log_capture_video_{}.txt'.format(LOG_PATH, get_current_time()))
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', type=str,
                        help='Camera ID or video filename')
    flags, _unparsed = parser.parse_known_args()
    save_video(flags.camera)
    logging.warning("Camera cupture ended.")


if __name__ == '__main__':
    main()
