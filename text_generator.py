# -*- coding: utf-8 -*-
"""Text_Generator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BXpLzM6gVWaE4WDGKnPp67S9EiXS0X5g
"""

from transformers import AutoTokenizer, AutoModelForCausalLM

checkpoint = "gpt2-large"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint)

prompt = "Hugging Face Company is"
inputs = tokenizer(prompt, return_tensors="pt")

outputs = model.generate(**inputs, penalty_alpha=0.6, top_k=4, max_new_tokens=100)
tokenizer.batch_decode(outputs, skip_special_tokens=True)

prompt = "The best programming language is "
inputs = tokenizer(prompt, return_tensors="pt")
print(inputs)
outputs = model.generate(**inputs, penalty_alpha=0.6, top_k=4, max_new_tokens=100)
tokenizer.batch_decode(outputs, skip_special_tokens=True)

from transformers import AutoModelForCausalLM, AutoTokenizer

prompt = "I play sports because"
checkpoint = "distilgpt2"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
inputs = tokenizer(prompt, return_tensors="pt")

model = AutoModelForCausalLM.from_pretrained(checkpoint)
outputs = model.generate(**inputs)
tokenizer.batch_decode(outputs, skip_special_tokens=True)