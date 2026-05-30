from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

text = """
Artificial intelligence is transforming business
operations through automation and better decisions.
"""

result = summarizer(
    text,
    max_length=50,
    min_length=10,
    do_sample=False
)

print(result)