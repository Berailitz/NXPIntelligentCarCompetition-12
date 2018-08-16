"""Build an inference version network from trained network."""
#!/usr/env/python3
# -*- coding: UTF-8 -*

import argparse
import sys
import tensorflow as tf
from monitor.config import MNIST_INFERENCE_PATH_PREFIX, MNIST_MODEL_PATH_PREFIX

flags = None


def deepnn(x):
    """deepnn builds the graph for a deep net for classifying digits.

    Args:
        x: an input tensor with the dimensions (N_examples, 784), where 784 is the
        number of pixels in a standard MNIST image.

    Returns:
        A tuple (y, keep_prob). y is a tensor of shape (N_examples, 10), with values
        equal to the logits of classifying the digit into one of 10 classes (the
        digits 0-9). keep_prob is a scalar placeholder for the probability of
        dropout.
    """
    # Reshape to use within a convolutional neural net.
    # Last dimension is for "features" - there is only one here, since images are
    # grayscale -- it would be 3 for an RGB image, 4 for RGBA, etc.
    with tf.name_scope('reshape'):
        x_image = tf.reshape(x, [-1, 28, 28, 1])

    # First convolutional layer - maps one grayscale image to 32 feature maps.
    with tf.name_scope('conv1'):
        W_conv1 = weight_variable([5, 5, 1, 32])
        b_conv1 = bias_variable([32])
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)

    # Pooling layer - downsamples by 2X.
    with tf.name_scope('pool1'):
        h_pool1 = max_pool_2x2(h_conv1)

    # Second convolutional layer -- maps 32 feature maps to 64.
    with tf.name_scope('conv2'):
        W_conv2 = weight_variable([5, 5, 32, 64])
        b_conv2 = bias_variable([64])
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

    # Second pooling layer.
    with tf.name_scope('pool2'):
        h_pool2 = max_pool_2x2(h_conv2)

    # Fully connected layer 1 -- after 2 round of downsampling, our 28x28 image
    # is down to 7x7x64 feature maps -- maps this to 1024 features.
    with tf.name_scope('fc1'):
        W_fc1 = weight_variable([7 * 7 * 64, 1024])
        b_fc1 = bias_variable([1024])

        h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    # NPS remove dropout layers

    # Map the 1024 features to 10 classes, one for each digit
    with tf.name_scope('fc2'):
        W_fc2 = weight_variable([1024, 10])
        b_fc2 = bias_variable([10])

        # NPS return only y_conv and skip dropout
        y_conv = tf.matmul(h_fc1, W_fc2) + b_fc2
    return y_conv


def conv2d(x, W):
    """conv2d returns a 2d convolution layer with full stride."""
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    """max_pool_2x2 downsamples a feature map by 2X."""
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')


def weight_variable(shape):
    """weight_variable generates a weight variable of a given shape."""
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    """bias_variable generates a bias variable of a given shape."""
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def main(_):

    # NPS remove import data

    # Create the model
    # NPS replaced line with named input node
    x = tf.placeholder(tf.float32, [None, 784], name="input")

    # NPS remove placeholder

    # NPS no longer returning keep_prob from deepnn()
    # Build the graph for the deep net
    y_conv = deepnn(x)
    #NPS add softmax layer with name of output
    output = tf.nn.softmax(y_conv, name='output')

    # NPS remove training code

    # NPS added line
    saver = tf.train.Saver(tf.global_variables())

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # NPS adding sess and saver stuff here
        sess.run(tf.local_variables_initializer())

        # read the previously saved network.
        saver.restore(sess, flags.model_prefix)

        # save the version of the network that can be compiled for NCS
        saver.save(sess, flags.model_inference_prefix)

        # NPS removing training code


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-prefix', type=str, default=MNIST_MODEL_PATH_PREFIX,
                        help='Path prefix to trained model')
    parser.add_argument('--model-inference-prefix', type=str, default=MNIST_INFERENCE_PATH_PREFIX,
                        help='Path prefix to inference model')
    flags, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
