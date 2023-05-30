import nltk
import tkinter
import PyPDF2
from pymongo import MongoClient
import logging
import re

# Download necessary NLTK packages
nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

# Connect to MongoDB
#client = MongoClient('mongodb://localhost:27017')
client = MongoClient('mongodb://penguin:27017')
db = client['pdfData']
collection = db['parsedData']

#grammar = """
#    Chunk: {<.*>+}
#    }<CD>{"""
#    }<LS>{"""
#    }<CD>{"""
#chunk_parser = nltk.RegexpParser(grammar)


# Function to parse PDF and extract text
def extract_text_from_pdf(file_path):
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
def tokenize_text(text):
    sentences = nltk.sent_tokenize(text)
#    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
#    tagged_sentences = [nltk.pos_tag(tokens) for tokens in tokenized_sentences]
    return sentences

def extract_ordinances_from_minutes(sentences):
    ordinances=False
    ordinance_text=[]
    for sentence in sentences:
        sentence=re.sub('\n','',sentence).strip()
        if(ordinances):
            end_flag_position = get_end_ordinance_flag_position(sentence)
            if end_flag_position >= 0:
                ordinances=False
                ordinance_text.append(sentence[0:end_flag_position])
            ordinance_text.append(sentence)
        else:
            ordinance_text_position = sentence.find("ORDINANCES")
            if ordinance_text_position >= 0:
                new_var = sentence[ordinance_text_position:]
                ordinance_text.append(new_var)
#        if sentence.find("10.A.") >= 0:
                ordinances=True
    return ''.join(ordinance_text)

def get_end_ordinance_flag_position(sentence):
    flag1 = sentence.find("CONTINUE MEETING")
    if flag1 >= 0:
        return flag1
    else:
        flag2 = sentence.find("STAFF ADMINISTRATIVE ITEMS")
        if flag2 >= 0:
            return flag2
        else:
            flag3 = sentence.find("AGENDA MANAGEMENT")
            if flag3 >= 0:
                return flag3
            else:
                flag4 = sentence.find("COUNCILMEMBER DISCUSSION ITEMS")
                return flag4

def extract_date_from_minutes(sentences):
    date_finder = "CITY COUNCIL MINUTES"
    date_index = sentences[0].find(date_finder)
    text_with_date = sentences[0][date_index+len(date_finder):date_index+100].lstrip()
    tokenized_text_with_date = nltk.word_tokenize(text_with_date)
    if tokenized_text_with_date[2]==',':
        date = int(tokenized_text_with_date[3])*10000+int(tokenized_text_with_date[1])
    else:
        date = int(tokenized_text_with_date[4])*10000+int(tokenized_text_with_date[1])*10+int(tokenized_text_with_date[2])
    month_text = tokenized_text_with_date[0][0:3]
    date+= 100*convert_month_text_to_ordinal(month_text)
    return date

# Example usage
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230425.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230321.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230321_spe.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230314.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230311.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230228.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230222.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230214.pdf'  # Replace with your PDF file path
#pdf_file = 'sampledata/SantaMonica/Minutes/m20230124.pdf'  # Replace with your PDF file path
pdf_file = 'sampledata/SantaMonica/Minutes/m20230110.pdf'  # Replace with your PDF file path

# Parse PDF and extract text
minutes_text = extract_text_from_pdf(pdf_file)

# Tokenize and tag the text using NLTK
minutes_sentences = tokenize_text(minutes_text)
meeting_date = extract_date_from_minutes(minutes_sentences)
logging.error("Date: "+str(meeting_date))

ordinances_text = extract_ordinances_from_minutes(minutes_sentences)
logging.error("Ordinances Text: "+str(ordinances_text))
 
# Insert parsed data into MongoDB
collection.insert_one({'meeting_date': meeting_date, 'meeting_ordinances_text': ordinances_text, 'meeting_minutes_text': minutes_text, 'meetings_minutes_sentences': minutes_sentences})

# Close the MongoDB connection
client.close()