import nltk
import PyPDF2
from pymongo import MongoClient

# Download necessary NLTK packages
nltk.download('punkt')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['pdfData']
collection = db['parsedData']

# Function to parse PDF and extract text
def parse_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages

        text = ''
        for page_num in range(num_pages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

        return text

# Function to tokenize and tag the text using NLTK
def tokenize_and_tag(text):
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(tokens) for tokens in tokenized_sentences]

    return tagged_sentences

# Example usage
pdf_file = 'example.pdf'  # Replace with your PDF file path

# Parse PDF and extract text
parsed_text = parse_pdf(pdf_file)

# Tokenize and tag the text using NLTK
tagged_text = tokenize_and_tag(parsed_text)

# Insert parsed data into MongoDB
collection.insert_one({'text': parsed_text, 'tagged_text': tagged_text})

# Close the MongoDB connection
client.close()