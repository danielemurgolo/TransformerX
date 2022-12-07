import tensorflow as tf

from transformerx.layers.positional_encoding import AbsolutePositionalEncoding
from transformerx.layers.transformer_decoder_block import TransformerDecoderBlock


class TransformerDecoder(tf.keras.layers.Layer):
    """Transformer decoder that encompasses one or more TransformerDecoderBlock blocks.

    Transformer decoder that encompasses one or more TransformerDecoderBlock blocks.

    The TransformerDecoder processes the input sequences and produces the output sequences.
    It also generates attention weights for each of the two attention layers in each of the
    TransformerDecoderBlock blocks.

    Parameters
    ----------
    vocab_size : int
        Vocabulary size.
    depth : int
        Dimension of each input sequence.
    norm_shape : str
        Shape of the normalization layer.
    ffn_num_hiddens : int
        Number of hidden units in the feed-forward network.
    num_heads : int
        Number of attention heads.
    n_blocks : int
        Number of encoder blocks.
    dropout : float
        Dropout rate.

    Attributes
    ----------
    depth : int
        The depth (i.e., number of channels) of the input and output representations.
    n_blocks : int
        The number of TransformerDecoderBlock blocks in the decoder.
    embedding : tf.keras.layers.Embedding
        The embedding layer that maps the input sequences to their input representations.
    pos_encoding : AbsolutePositionalEncoding
        The absolute positional encoding layer that adds position information to the input
        representations.
    blocks : List[TransformerDecoderBlock]
        The list of TransformerDecoderBlock blocks that process the input sequences.
    dense : tf.keras.layers.Dense
        The dense layer that maps the output representations to the output sequences.
    """


    def __init__(
            self,
            vocab_size,
            depth,
            norm_shape,
            ffn_num_hiddens,
            num_heads,
            n_blocks,
            dropout,
    ):
        super().__init__()
        self.depth = depth
        self.n_blocks = n_blocks
        self.embedding = tf.keras.layers.Embedding(vocab_size, depth)
        self.pos_encoding = AbsolutePositionalEncoding(depth, dropout)
        self.blocks = [
            TransformerDecoderBlock(
                    depth,
                    norm_shape,
                    ffn_num_hiddens,
                    num_heads,
                    dropout,
                    i,
            )
            for i in range(n_blocks)
        ]
        self.dense = tf.keras.layers.Dense(vocab_size)

    def init_state(self, enc_outputs, enc_valid_lens):
        return [enc_outputs, enc_valid_lens, [None] * self.n_blocks]

    def call(self, X, state, **kwargs):


        X = self.pos_encoding(
                self.embedding(X) * tf.math.sqrt(tf.cast(self.depth, dtype=tf.float32)),
                **kwargs,
        )
        # 2 attention layers in decoder
        self._attention_weights = [[None] * len(self.blocks) for _ in range(2)]
        for i, blk in enumerate(self.blocks):
            X, state = blk(X, state, **kwargs)
            # Decoder self-attention weights
            self._attention_weights[0][i] = blk.attention1.attention.attention_weights
            # Encoder-decoder attention weights
            self._attention_weights[1][i] = blk.attention2.attention.attention_weights
        return self.dense(X), state

    @property
    def attention_weights(self):
        return self._attention_weights
