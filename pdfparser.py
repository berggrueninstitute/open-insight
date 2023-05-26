import nltk
import tkinter

import PyPDF2

from pymongo import MongoClient

import logging

# Download necessary NLTK packages
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
#client = MongoClient('mongodb://penguin:27017')
db = client['pdfData']
collection = db['parsedData']

grammar = """
    Chunk: {<.*>+}
    }<CD>{"""
#    }<LS>{"""
#    }<CD>{"""
chunk_parser = nltk.RegexpParser(grammar)


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


def convert_month_text_to_ordinal(text):
    if text=="JAN": return 1
    elif text=="FEB": return 2
    elif text=="MAR": return 3
    elif text=="APR": return 4
    elif text=="MAY": return 5
    elif text=="JUN": return 6
    elif text=="JUL": return 7
    elif text=="AUG": return 8
    elif text=="SEP": return 9
    elif text=="OCT": return 10
    elif text=="NOV": return 11
    elif text=="DEC": return 12
    else: return -1

# Function to tokenize and tag the text using NLTK
def tokenize_and_tag(text):
    sentences = nltk.sent_tokenize(text)

    date_finder = "CITY COUNCIL MINUTES"
    date_index = sentences[0].find(date_finder)
    text_with_date = sentences[0][date_index+len(date_finder):date_index+100].lstrip()
    tokenized_text_with_date = nltk.word_tokenize(text_with_date)
    date = int(tokenized_text_with_date[3])*10000+int(tokenized_text_with_date[1])
    month_text = tokenized_text_with_date[0][0:3]
    date+= 100*convert_month_text_to_ordinal(month_text)
    logging.error("Date: "+str(date))

    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(tokens) for tokens in tokenized_sentences]
    ordinances=False
    for sentence in sentences:
        xx="sdfads"
        if sentence.find("ORDINANCES") >= 0:
            ordinances=True
        if ordinances:
            logging.error(sentence.strip())
        if sentence.find("CONTINUE MEETING") >= 0:
            ordinances=False
#            [(lambda x : logging.error(f"({x[0]}::::+ {x[1]}") if x[1]=='CD' else f"")(word) for word in sentence]
#        test = lambda x : logging.error(f"({x[0]}::::+ {x[1]}") if x[1]=='CD' else f""
#        [test(word) for word in sentence]

    return tagged_sentences

# Example usage
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230425.pdf'  # Replace with your PDF file path
pdf_file = 'sampledata/SantaMonica/Minutes/m20230321.pdf'  # Replace with your PDF file path

# Parse PDF and extract text
parsed_text = parse_pdf(pdf_file)

# Tokenize and tag the text using NLTK
tagged_text = tokenize_and_tag(parsed_text)

# Insert parsed data into MongoDB
#collection.insert_one({'text': parsed_text, 'tagged_text': tagged_text})

# Close the MongoDB connection
client.close()