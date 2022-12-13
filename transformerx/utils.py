import os

import tensorflow as tf


def masked_softmax(X, attention_mask):
    """Perform softmax operation by masking elements on the last axis."""

    # x: 3D tensor, attention_mask: 1D or 2D tensor
    def _sequence_mask(X, attention_mask, value=0):
        maxlen = X.shape[1]
        mask = tf.range(start=0, limit=maxlen, dtype=tf.float32)[None, :] < tf.cast(
                attention_mask[:, None], dtype=tf.float32
        )
        print("here x2: ", X.shape, attention_mask.shape)

        if len(X.shape) == 3:
            return tf.where(tf.expand_dims(mask, axis=-1), X, value)
        else:
            return tf.where(mask, X, value)

    if attention_mask is None:
        return tf.nn.softmax(X, axis=-1)
    else:
        shape = X.shape
        if len(attention_mask.shape) == 1:
            attention_mask = tf.repeat(attention_mask, repeats=shape[1])
        else:
            attention_mask = tf.reshape(attention_mask, shape=-1)
        # On the last axis, replace masked elements with a very large negative
        # value, whose exponentiation outputs 0
        print("here x: ", X)
        X = _sequence_mask(tf.reshape(X, shape=(-1, shape[-1])), attention_mask, value=0)
        print("here x2: ", X.shape, attention_mask.shape)
        print("here x3: ", tf.reshape(X, shape=shape).shape)
        return tf.nn.softmax(tf.reshape(X, shape=shape), axis=-1)


def use_device(device):
    if device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    else:
        pass


def exists(val):
    return val is not None