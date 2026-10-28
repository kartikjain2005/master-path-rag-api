from services.embedding_service import embed_text


sample_text = """
Normalization organizes data in relational database tables.
"""

vector = embed_text(sample_text)

print("Embedding generated successfully!")
print("Vector dimensions:", len(vector))
print("First 5 values:", vector[:5])