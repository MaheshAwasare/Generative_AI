# -*- coding: utf-8 -*-
"""Translator_Using_Transformer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o7CdC3O1ZE6W83IofbAJ6PGBPY4S-r20
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Input, Embedding, Masking, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.metrics import SparseCategoricalAccuracy

# Replace these paths with the paths to your specific datasets
english_data_path = "path/to/english_dataset.txt"
french_data_path = "path/to/french_dataset.txt"

#pip install opustools-pkg  - to be done before you use next code

# Use the shell command to install opus-tools
!apt-get install opus-tools

#pip install opustools-pkg  - to be done before you use next code
import opustools

# Download English-Finnish parallel corpus
opus_reader = opustools.OpusRead(
    directory='Books',
    source='en',
    target='fi')
opus_reader.printPairs()

import zipfile
import os

def load_data_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Assuming there is only one file in the ZIP archive
        file_name = zip_ref.namelist()[0]
        with zip_ref.open(file_name) as file:
            # Decode bytes to string using UTF-8 encoding
            data = file.read().decode('utf-8')
    return [sentence.strip() for sentence in data.split('\n') if sentence.strip()]

# Provide the paths to your ZIP files
english_zip_path = "/content/Books_latest_xml_en.zip"
french_zip_path = "/content/Books_latest_xml_fi.zip"

# Load data from ZIP files
english_sentences = load_data_from_zip(english_zip_path)
french_sentences = load_data_from_zip(french_zip_path)


print(english_sentences)

english_tokenizer = keras.preprocessing.text.Tokenizer(filters='')
english_tokenizer.fit_on_texts(english_sentences)
english_seq = english_tokenizer.texts_to_sequences(english_sentences)

# Tokenize the sentences (you might want to use more sophisticated tokenization)



french_tokenizer = keras.preprocessing.text.Tokenizer(filters='')
french_tokenizer.fit_on_texts(french_sentences)


french_seq = french_tokenizer.texts_to_sequences(french_sentences)

# Manually add start and end tokens to the French tokenizer
start_token = '<start>'
end_token = '<end>'

french_tokenizer.word_index[start_token] = len(french_tokenizer.word_index) + 1
french_tokenizer.word_index[end_token] = len(french_tokenizer.word_index) + 1

# Add start and end tokens to the French sequences
french_seq = [[french_tokenizer.word_index[start_token]] + seq + [french_tokenizer.word_index[end_token]] for seq in french_seq]

# Add start and end tokens to the French sequences
french_seq = [[french_tokenizer.word_index['<start>']] + seq + [french_tokenizer.word_index['<end>']] for seq in french_seq]

# Pad sequences to the same length
max_len = max(max(map(len, english_seq)), max(map(len, french_seq)))
english_seq = tf.keras.preprocessing.sequence.pad_sequences(english_seq, maxlen=max_len, padding='post')
french_seq = tf.keras.preprocessing.sequence.pad_sequences(french_seq, maxlen=max_len, padding='post')

print(french_seq)
print(max_len)

import tensorflow as tf
from tensorflow.keras.layers import Layer

class PositionalEncoding(Layer):
    def __init__(self, max_len, embed_dim, **kwargs):
        super(PositionalEncoding, self).__init__(**kwargs)
        self.pos_encoding = self.positional_encoding(max_len, embed_dim)

    def build(self, input_shape):
        super(PositionalEncoding, self).build(input_shape)

    def call(self, x):
        return x + self.pos_encoding[:, :tf.shape(x)[1], :]

    def get_config(self):
        config = super(PositionalEncoding, self).get_config()
        return config

    def positional_encoding(self, max_len, embed_dim):
        angle_rads = self.get_angles(tf.range(max_len, dtype=tf.float32)[:, tf.newaxis],
                                     tf.range(embed_dim, dtype=tf.float32)[tf.newaxis, :],
                                     embed_dim)

        # apply sin to even indices in the array; 2i
        sines = tf.math.sin(angle_rads[:, 0::2])

        # apply cos to odd indices in the array; 2i+1
        cosines = tf.math.cos(angle_rads[:, 1::2])

        pos_encoding = tf.concat([sines, cosines], axis=-1)
        pos_encoding = pos_encoding[tf.newaxis, ...]
        return tf.cast(pos_encoding, dtype=tf.float32)

    def get_angles(self, pos, i, d_model):
        angle_rates = 1 / tf.pow(10000, (2 * (i // 2)) / tf.cast(d_model, tf.float32))
        return pos * angle_rates

# Define transformer block
def transformer_block(embed_dim, num_heads, ff_dim, dropout=0.1):
    inputs = Input(shape=(None, embed_dim))
    x = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim // num_heads)(inputs, inputs)
    x = Dropout(dropout)(x)

    # Add a Dense layer with the same units as the input embed_dim
    x = Dense(embed_dim, activation='relu')(x)

    res = x + inputs
    x = LayerNormalization(epsilon=1e-6)(res)
    x = x + Dense(embed_dim, activation='relu')(x)
    x = Dropout(dropout)(x)
    return Model(inputs=inputs, outputs=x)

import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Masking, Dense, Dropout, LayerNormalization, MultiHeadAttention
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.metrics import SparseCategoricalAccuracy
# Define the transformer model
def transformer_model(vocab_size, max_len, embed_dim=256, num_heads=8, ff_dim=512, num_blocks=4, dropout=0.1):
    inputs = Input(shape=(max_len,))
    embedding_layer = Embedding(input_dim=vocab_size, output_dim=embed_dim)(inputs)
    positional_encoding = PositionalEncoding(max_len, embed_dim)(embedding_layer)
    x = Masking(mask_value=0)(positional_encoding)  # Masking for padded zeros
    for _ in range(num_blocks):
        x = transformer_block(embed_dim, num_heads, ff_dim, dropout)(x)
    outputs = Dense(5, activation='softmax')(x)  # Change the output dimension to 5
    return Model(inputs=inputs, outputs=outputs)

unique_labels = set(french_seq.flatten())
print("Unique Labels:", unique_labels)

# Mapping dictionary
label_mapping = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}

# Apply mapping to the labels
mapped_labels = [[label_mapping[label] for label in sequence] for sequence in french_seq]

# Check the mapped labels
print(mapped_labels)

import numpy as np

# Compile the model
vocab_size_en = len(english_tokenizer.word_index) + 1
vocab_size_fr = len(french_tokenizer.word_index) + 1

# Map labels to [0, 4]
label_mapping = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
mapped_labels = [[label_mapping[label] for label in sequence] for sequence in french_seq]

model = transformer_model(vocab_size_en, max_len)
model.compile(optimizer=Adam(), loss=SparseCategoricalCrossentropy(), metrics=[SparseCategoricalAccuracy()])

# Train the model using mapped labels
model.fit(english_seq, np.array(mapped_labels), epochs=13, batch_size=64)

# Save the trained model
model.save("transformer_model.h5")

# Following code stops training when desired accuracy is reached so it saves some compute time. A callback is implemented and added during training inside fit method.

from tensorflow.keras.callbacks import EarlyStopping

import numpy as np

# Compile the model
vocab_size_en = len(english_tokenizer.word_index) + 1
vocab_size_fr = len(french_tokenizer.word_index) + 1

# Map labels to [0, 4]
label_mapping = {10: 0, 11: 1, 12: 2, 13: 3, 14: 4}
mapped_labels = [[label_mapping[label] for label in sequence] for sequence in french_seq]

model = transformer_model(vocab_size_en, max_len)
model.compile(optimizer=Adam(), loss=SparseCategoricalCrossentropy(), metrics=[SparseCategoricalAccuracy()])

# Save the trained model
model.save("transformer_model.h5")

# Define the threshold accuracy
accuracy_threshold = 0.90
import numpy as np

# Convert mapped_labels into a NumPy array
mapped_labels_array = np.array(mapped_labels)

# Train the model


# Create an EarlyStopping callback with min_delta set to 0
early_stopping_callback = EarlyStopping(monitor='sparse_categorical_accuracy', patience=3, restore_best_weights=True, min_delta=0)

# Train the model using early stopping
model.fit(english_seq, mapped_labels_array, epochs=13, batch_size=64, validation_split=0.2, callbacks=[early_stopping_callback])

# Save the trained model
model.save("transformer_model_early_stopping.h5")

config = model.get_config()

print(config)



import tensorflow as tf
from tensorflow.keras.layers import Layer

class PositionalEncoding(Layer):
    def __init__(self, max_len, embed_dim, **kwargs):

       super(PositionalEncoding, self).__init__(**kwargs)
       self.max_len = max_len
       self.embed_dim = embed_dim
       self.pos_encoding = self.positional_encoding(max_len, embed_dim)

    def build(self, input_shape):
        super(PositionalEncoding, self).build(input_shape)

    def call(self, x):
        return x + self.pos_encoding[:, :tf.shape(x)[1], :]

    def get_config(self):
         config = super(PositionalEncoding, self).get_config()
         config.update({'max_len': self.max_len, 'embed_dim': self.embed_dim})
         return config
    def positional_encoding(self, max_len, embed_dim):
        angle_rads = self.get_angles(tf.range(max_len, dtype=tf.float32)[:, tf.newaxis],
                                     tf.range(embed_dim, dtype=tf.float32)[tf.newaxis, :],
                                     embed_dim)

        # apply sin to even indices in the array; 2i
        sines = tf.math.sin(angle_rads[:, 0::2])

        # apply cos to odd indices in the array; 2i+1
        cosines = tf.math.cos(angle_rads[:, 1::2])

        pos_encoding = tf.concat([sines, cosines], axis=-1)
        pos_encoding = pos_encoding[tf.newaxis, ...]
        return tf.cast(pos_encoding, dtype=tf.float32)

    def get_angles(self, pos, i, d_model):
        angle_rates = 1 / tf.pow(10000, (2 * (i // 2)) / tf.cast(d_model, tf.float32))
        return pos * angle_rates

class PositionalEncoding(Layer):

    def __init__(self, max_len, embed_dim, trainable=False, **kwargs):
        super(PositionalEncoding, self).__init__(**kwargs)
        self.max_len = 5
        self.embed_dim = embed_dim
        self.trainable = trainable

        # Generate positional encoding during layer construction for efficiency
        self.pos_encoding = self.positional_encoding(max_len, embed_dim)

    def build(self, input_shape):
        super(PositionalEncoding, self).build(input_shape)

    def call(self, x):
        return x + self.pos_encoding[:, :tf.shape(x)[1], :]

    def get_config(self):
        config = super(PositionalEncoding, self).get_config()
        config.update({'max_len': self.max_len, 'embed_dim': self.embed_dim,
                       'trainable': self.trainable})
        return config

    def positional_encoding(self, max_len, embed_dim):

        angle_rads = self.get_angles(tf.range(max_len, dtype=tf.float32)[:, tf.newaxis],
                                           tf.range(embed_dim, dtype=tf.float32)[tf.newaxis, :],
                                           embed_dim)

        # apply sin to even indices in the array; 2i
        sines = tf.math.sin(angle_rads[:, 0::2])

        # apply cos to odd indices in the array; 2i+1
        cosines = tf.math.cos(angle_rads[:, 1::2])

        pos_encoding = tf.concat([sines, cosines], axis=-1)
        pos_encoding = pos_encoding[tf.newaxis, ...]
        return tf.cast(pos_encoding, dtype=tf.float32)

    def get_angles(self, pos, i, d_model):
        angle_rates = 1 / tf.pow(10000, (2 * (i // 2)) / tf.cast(d_model, tf.float32))
        return pos * angle_rates


def translate(model, english_sentence, english_tokenizer, finnish_tokenizer):
    # Tokenize the input sentence
    input_seq = english_tokenizer.texts_to_sequences([english_sentence])

    # Pad the sequence to match the model's input shape
    input_seq = tf.keras.preprocessing.sequence.pad_sequences(input_seq, maxlen=max_len, padding='post')

    # Get the model's prediction
    predicted_seq = model.predict(input_seq)

    # Convert the predicted sequence to words using the Finnish tokenizer
    finnish_translation = finnish_tokenizer.sequences_to_texts(predicted_seq)[0]

    return finnish_translation

# Example usage:

loaded_model = load_model("/content/transformer_model.h5", custom_objects={'PositionalEncoding': PositionalEncoding})

english_sentence = "This is an example sentence."
finnish_translation = translate(loaded_model, english_sentence, english_tokenizer, finnish_tokenizer)
print(f"English: {english_sentence}")
print(f"Finnish: {finnish_translation}")