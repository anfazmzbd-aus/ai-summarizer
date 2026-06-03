# app/models/summarizer_model.py

from transformers import pipeline

summarizer_model = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)