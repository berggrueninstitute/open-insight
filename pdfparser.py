import nltk
import tkinter
import PyPDF2
from pymongo import MongoClient
import logging
import re
import json
from objdict import ObjDict


# Download necessary NLTK packages
nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

# Connect to MongoDB
#client = MongoClient('mongodb://localhost:27017')
client = MongoClient('mongodb://penguin:27017')
db = client['santa_monica_data']
collection = db['parsed_minutes_pdfs']

return_object = ObjDict()


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
        sentence = remove_noise(sentence)
        if(ordinances):
            end_flag_position = get_end_ordinance_flag_position(sentence)
            if end_flag_position >= 0:
                ordinances=False
                ordinance_text.append(sentence[0:end_flag_position])
            else:
                ordinance_text.append(sentence)
        else:
            ordinance_text_position = sentence.find("ORDINANCES")
            if ordinance_text_position >= 0:
                new_var = sentence[ordinance_text_position:]
                ordinance_text.append(new_var)
                ordinances=True
    return ''.join(ordinance_text)

def remove_noise(sentence):
    sentence=re.sub('\n','',sentence).strip()
    docusign_envelope_id = sentence.find('DocuSign Envelope ID')
    if docusign_envelope_id >= 0:
        sentence = ''.join([sentence[0:docusign_envelope_id], sentence[find_docusign_end(sentence, docusign_envelope_id):]])
    return sentence

def find_docusign_end(sentence, start):
    current = start + 61 # seems to be magic number
    while current < len(sentence):
        new_var = sentence[current]
        if new_var >= '0' and sentence[current] <= '9':
            new_var1 = sentence[current+1]
            if new_var1 >= '0' and sentence[current+1] <= '9':
                new_var2 = sentence[current+2]
                if new_var2 >= '0' and sentence[current+2] <= '9':
                    new_var3 = sentence[current+3]
                    if new_var3 >= '0' and sentence[current+3] <= '9':
                        return current+4
                    else:
                        current+=4
                else:
                    current+=3
            else:
                current+=2
        else:
            current+=1



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
            
def extract_ordinances_from_text(ordinances_text):
    ordinances = []
    ordinance_index = 0
    current_text = ordinances_text[ordinances_text.find(':')+1:].strip()
    while True:
        ordinance_object = ObjDict()
        ordinance_number = ''.join(['10.',chr(ord('A')+ordinance_index),'.'])
        ordinance_object.meetingnoteslineitem=ordinance_number
        ordinance_number_index = current_text.find(ordinance_number)
        ordinance_subject = current_text[:ordinance_number_index].strip()
        ordinance_object.subject = ordinance_subject
        end_ordinance_title_index = current_text.find(', was presented')
        ordinance_object.title = current_text[ordinance_number_index+5:end_ordinance_title_index].strip()
        recommended_action_index = current_text.find('Recommended Action')
        current_text = current_text[recommended_action_index+len('Recommended Action'):].strip()
        next_colon_index = current_text.find(':')
        next_period_index = current_text.find('.')
        if next_colon_index>=0 and next_colon_index < next_period_index:
            recommended_actions_end_index = current_text.find('Questions asked')
            recommended_action_text = current_text[:recommended_actions_end_index].strip()
            recommended_action_text = recommended_action_text[recommended_action_text.find('1.'):]
            ordinance_object.Recommended_Actions=[]
            recommended_action_ordinal = 1
            while len(recommended_action_text) > 0:
                recommended_action = ObjDict()
                recommended_action.ordinal = recommended_action_ordinal
                next_ordinal_index = recommended_action_text.find(str(recommended_action_ordinal+1)+".")
                if next_ordinal_index > 0:
                    another_next_ordinal_index = recommended_action_text.rindex(str(recommended_action_ordinal+1)+".")
                    if(next_ordinal_index!=another_next_ordinal_index):
                        logging.error(''.join(["Possible Problem Reading Ordinance ",ordinance_number," Recommended Action #",str(recommended_action_ordinal)," due to unclear next index."]))
                        next_ordinal_index=another_next_ordinal_index
                    recommended_action.content = recommended_action_text[len(str(recommended_action_ordinal))+1:next_ordinal_index]
                    recommended_action_text = recommended_action_text[next_ordinal_index:]
                else:
                    recommended_action.content = recommended_action_text[len(str(recommended_action_ordinal))+1:]
                    recommended_action_text = ''
                recommended_action_ordinal+=1
                ordinance_object.Recommended_Actions.append(recommended_action)
            current_text = current_text[recommended_actions_end_index:]
        else:
            ordinance_object.Recommended_Actions = current_text[:next_period_index+1].strip()
            current_text = current_text[next_period_index+1:]

        ayes_index = current_text.find('AYES')
        current_text = current_text[ayes_index:].strip()
        noes_index = current_text.find('NOES')
        absent_index = current_text.find('ABSENT')
        ayes_text = current_text[5:noes_index].strip()
        noes_text = current_text[noes_index+5:absent_index].strip()
        current_text = current_text[absent_index:].strip()
        end_of_absent_index = get_end_of_absent_index(current_text)
        absent_text = current_text[len('ABSENT:'):end_of_absent_index].strip()
        current_text = current_text[end_of_absent_index:].strip()
        ordinance_object.AYES = parse_voters(ayes_text)
        ordinance_object.NOES = parse_voters(noes_text)
        ordinance_object.ABSENT = parse_voters(absent_text)

        ordinances.append(ordinance_object)

        ordinance_index+=1

        if len(current_text) == 0:
            break

    return ordinances

def parse_voters(text):
    to_return = []

    pro_tem_index = text.find("Mayor Pro Tem")
    if pro_tem_index >= 0:
        pro_tem_text = text[pro_tem_index+len("Mayor Pro Tem"):].strip()
        next_comma = pro_tem_text.find(",")
        if next_comma > 0:
            pro_tem_text = pro_tem_text[:next_comma]
        to_return.append({"name": pro_tem_text, "title": "Mayor Pro Tem"})

    mayor_index = text.find("Mayor")
    if mayor_index == pro_tem_index:
        new_index = text.rfind("Mayor")
        if new_index!=mayor_index:
            mayor_index=new_index
        else:
            mayor_index=-1 
    if mayor_index >= 0:
        mayor_text = text[mayor_index+5:].strip()
        next_comma = mayor_text.find(",")
        if next_comma > 0:
            mayor_text = mayor_text[:next_comma]
        to_return.append({"name": mayor_text, "title": "Mayor"})

    council_index = text.find("Councilmembers")
    if council_index >= 0:
        if mayor_index < 0:
            mayor_index=999999999
        if pro_tem_index < 0:
            pro_tem_index=999999999
        if min(mayor_index, pro_tem_index) > council_index:
            council_text = text[council_index+len("Councilmembers"):min(mayor_index, pro_tem_index)].strip()
        council_names = get_names_from_comma_list(council_text)
        for name in council_names:
            to_return.append({"name": name, "title": "Councilmember"})
    else:
        council_index = text.find("Councilmember")
        if council_index >= 0:
            council_text = text[council_index+len("Councilmember"):].strip()
            next_comma = council_text.find(",")
            if next_comma > 0:
                council_text = council_text[:next_comma]
            to_return.append({"name": council_text, "title": "Concilmember"})

    
    return to_return

def get_names_from_comma_list(text):
    to_return = []
    work_text = text
    while True:
        next_comma_index = work_text.find(",")
        if next_comma_index < 0:
            if len(work_text) > 0:
                to_return.append(work_text)
            return to_return
        else:
            to_return.append(work_text[:next_comma_index])
            work_text=work_text[next_comma_index+1:].strip()

def get_end_of_absent_index(text):
    index = len('ABSENT:')
    while True:
        if text[index:].startswith('None'):
            return index+len('None')
        else:
            index+=1
    
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


def extract_minutes_object_from_pdf(file):
    minutes_text = extract_text_from_pdf(file)
    # Tokenize the text using NLTK
    minutes_sentences = tokenize_text(minutes_text)
    meeting_date = extract_date_from_minutes(minutes_sentences)
    ordinances_text = extract_ordinances_from_minutes(minutes_sentences)

    to_return = ObjDict()
    to_return.date = str(meeting_date)
    to_return.ordinances = extract_ordinances_from_text(ordinances_text)
 

    collection.insert_one({"minutes": to_return,'meeting_date': meeting_date, 'meeting_ordinances_text': ordinances_text, 'meeting_minutes_text': minutes_text})
    return to_return


pdf_file=[]
pdf_file.append('sampledata/SantaMonica/Minutes/m20230425.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230321.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230321_spe.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230314.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230311.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230228.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230222.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230214.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230124.pdf')
pdf_file.append('sampledata/SantaMonica/Minutes/m20230110.pdf')


minutes_object = extract_minutes_object_from_pdf(pdf_file[len(pdf_file)-1])
return_json = minutes_object.dumps()
print(json.dumps(json.loads(return_json), indent=2))

client.close()