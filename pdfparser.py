import nltk
import PyPDF2
from pymongo import MongoClient

# Download necessary NLTK packages
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Connect to MongoDB
# client = MongoClient('mongodb://localhost:27017')
client = MongoClient('mongodb://penguin:27017')
db = client['pdfData']
collection = db['parsedData']

# Function to parse PDF and extract text
def parse_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)

        text = ''
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

        return text

# Function to tokenize and tag the text using NLTK
def tokenize_and_tag(text):
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(tokens) for tokens in tokenized_sentences]

    return tagged_sentences

# Example usage
pdf_file = 'sampledata/SantaMonica/Minutes/m20230425.pdf'  # Replace with your PDF file path

# Parse PDF and extract text
parsed_text = parse_pdf(pdf_file)

# Tokenize and tag the text using NLTK
tagged_text = tokenize_and_tag(parsed_text)

# Insert parsed data into MongoDB
collection.insert_one({'text': parsed_text, 'tagged_text': tagged_text})

# Close the MongoDB connection
client.close()