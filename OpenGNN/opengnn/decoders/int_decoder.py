import tensorflow as tf


class IntDecoder():

    def __init__(self):
        pass

    def decode(self,
               inputs: tf.Tensor,
               sequence_length: tf.Tensor,
               vocab_size: int = None,
               initial_state: tf.Tensor = None,
               sampling_probability=None,
               embedding=None,
               mode=tf.estimator.ModeKeys.TRAIN):
        # pass
        print("decode inputs: ", inputs)
        pass
        return ids, logits, decoder_loss

    def dynamic_decode(self):
        pass

    def dynamic_decode_and_search(self):
        pass
