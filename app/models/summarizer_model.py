# app/models/summarizer_model.py

from transformers import pipeline

summarizer_model = pipeline(task="summarization", model="facebook/bart-large-cnn", framework="pt")