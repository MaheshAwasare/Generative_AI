# -*- coding: utf-8 -*-
"""Positional Encoding.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tBKZ5R9NhnMTU9BhId5fCYPAH3yNlL_W
"""

import keras
import numpy as np
vocab = {"The": 1, "cat": 2, "sat": 3, "on": 4, "mat": 5, "the":6}
seq = "The cat sat on the mat".split()
seq = [vocab[word] if word in vocab else vocab["the"] for word in seq]

embd_dim = 256
max_len = 100

embedding_matrix = keras.initializers.glorot_uniform()((len(vocab)+1, embd_dim))

pos_encoding = keras.initializers.glorot_uniform()((1, max_len, embd_dim))

seq_embedded  = []
for i, word_id in enumerate(seq):
   word_embd = embedding_matrix[word_id]
   pos_embd = pos_encoding[0][i]
   token_embd = word_embd + pos_embd
   seq_embedded.append(token_embd)

seq_embedded = np.array(seq_embedded)
print(seq_embedded.shape)

seq_embedded  = []
for i, word_id in enumerate(seq):
   word_embd = embedding_matrix[word_id]
   pos_embd = pos_encoding[0][i]
   token_embd = word_embd + pos_embd
   seq_embedded.append(token_embd)

seq_embedded = np.array(seq_embedded)
print("seq_embedded")
print(seq_embedded)
print(seq_embedded.shape)