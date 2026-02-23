import sys
import math
import bs4 as bs
import urllib.request
import re
import PyPDF2
import nltk
from nltk.stem import WordNetLemmatizer 
import spacy

https://en.wikipedia.org/wiki/Data_analysis                              For url


C:\Users\riyag\OneDrive\sem3\Text-Summarization-master\Output\Wiki-Artificial-Intelligence-Summary.txt                   for txt


A quip in Tesler's Theorem says "AI is whatever hasn't been done yet. These issues have been explored by myth, fiction and philosophy since antiquity. Marvin Minsky agreed, writing, "within a generation ... They failed to recognize the difficulty of some of the remaining tasks. By 1985, the market for AI had reached over a billion dollars. In 2011, a Jeopardy! champions, Brad Rutter and Ken Jennings, by a significant margin. No. 1 ranking for two years. Goals can be explicitly defined or induced. AI often revolves around the use of algorithms. An algorithm is a set of unambiguous instructions that a mechanical computer can execute.[b] A complex algorithm is often built on top of other, simpler, algorithms. These learners could therefore derive all possible knowledge, by considering every possible hypothesis and matching them against the data. These inferences can be obvious, such as "since the sun rose every morning for the last 10,000 days, it will probably rise tomorrow morning as well". Besides classic overfitting, learners can also disappoint by "learning the wrong lesson". Faintly superimposing such a pattern on a legitimate image results in an "adversarial" image that the system misclassifies.[c]
 This gives rise to two classes of models: structuralist and functionalist. The functional model refers to the correlating data to its computed counterpart.
 The general problem of simulating (or creating) intelligence has been broken down into sub-problems. The traits described below have received the most attention.
 they became exponentially slower as the problems grew larger. They solve most of their problems using fast, intuitive judgments.
 However, if the agent is not the only actor, then it requires that the agent can reason under uncertainty. This calls for an agent that can not only assess its environment and make predictions but also evaluate its predictions and adapt based on its assessment.
 Emergent behavior such as this is used by evolutionary algorithms and swarm intelligence.
 Applications include speech recognition, facial recognition, and object recognition. Computer vision is the ability to analyze visual input. AI is heavily used in robotics. Motion planning is the process of breaking down a movement task into "primitives" such as individual joint movements. Moravec's paradox can be extended to many forms of social intelligence. Many advances have general, cross-domain significance. Researchers disagree about many issues. This includes embodied, situated, behavior-based, and nouvelle AI. Nowadays results of experiments are often rigorously measurable, and are sometimes (with difficulty) reproducible. A few of the most general of these methods are discussed below.
 The result is a search that is too slow or never completes. Heuristics limit the search for solutions into a smaller sample size.
 Other optimization algorithms are simulated annealing, beam search and random optimization.















# Execute this line if you are running this code for the first time
nltk.download('wordnet')

# Initializing few variables
nlp = spacy.load('en_core_web_sm')
lemmatizer = WordNetLemmatizer()

# Step 2. Define functions for Reading Input Text

# Function to Read .txt File and return its Text
def file_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read().replace("\n", ' ')
        return text

# Function to Read PDF File and return its Text
def pdfReader(pdf_path):
    with open(pdf_path, 'rb') as pdfFileObject:
        pdfReader = PyPDF2.PdfReader(pdfFileObject)
        count = len(pdfReader.pages)
        print("\nTotal Pages in pdf = ", count)

        c = input("Do you want to read the entire pdf? [Y]/N: ")
        if c == 'N' or c == 'n':
            start_page = int(input("Enter start page number (Indexing starts from 0): "))
            end_page = int(input(f"Enter end page number (Less than {count}): "))
            
            if start_page < 0 or start_page >= count:
                print("\nInvalid Start page given")
                sys.exit()
                
            if end_page < 0 or end_page >= count:
                print("\nInvalid End page given")
                sys.exit()
        else:
            start_page = 0
            end_page = count - 1
        
        text = ""
        for i in range(start_page, end_page + 1):
            page = pdfReader.pages[i]
            text += page.extract_text()

    return text

# Function to Read Wikipedia page URL and return its Text
def wiki_text(url):
    scrap_data = urllib.request.urlopen(url)
    article = scrap_data.read()
    parsed_article = bs.BeautifulSoup(article, 'lxml')
    
    paragraphs = parsed_article.find_all('p')
    article_text = ""

    for p in paragraphs:
        article_text += p.text

    # Removing all unwanted characters
    article_text = re.sub(r'\[[0-9]*\]', '', article_text)
    return article_text

# Step 3. Getting Text 

input_text_type = int(input("Select one way of inputting your text: \
\n1. Type your Text (or Copy-Paste) \
\n2. Load from .txt file \
\n3. Load from .pdf file \
\n4. From Wikipedia Page URL\n\n"))

if input_text_type == 1:
    text = input("Enter your text: \n\n")

elif input_text_type == 2:
    txt_path = input("Enter file path: ")
    text = file_text(txt_path)
    
elif input_text_type == 3:
    file_path = input("Enter file path: ")
    text = pdfReader(file_path)
    
elif input_text_type == 4:
    wiki_url = input("Enter Wikipedia URL to load Article: ")
    text = wiki_text(wiki_url)
    
else:
    print("Sorry! Wrong Input, Try Again.")

# Step 4. Defining functions to create Tf-Idf Matrix

# Function to calculate frequency of word in each sentence
def frequency_matrix(sentences):
    freq_matrix = {}
    stopWords = nlp.Defaults.stop_words

    for sent in sentences:
        freq_table = {}  # dictionary with 'words' as key and their 'frequency' as value
        
        # Getting all words from the sentence in lowercase
        words = [word.text.lower() for word in sent if word.text.isalnum()]
        
        for word in words:
            word = lemmatizer.lemmatize(word)  # Lemmatize the word
            if word not in stopWords:  # Reject stopwords
                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1

        freq_matrix[sent[:15]] = freq_table

    return freq_matrix

# Function to calculate Term Frequency (TF) of each word
def tf_matrix(freq_matrix):
    tf_matrix = {}

    for sent, freq_table in freq_matrix.items():
        tf_table = {}  # dictionary with 'word' itself as a key and its TF as value

        total_words_in_sentence = len(freq_table)
        for word, count in freq_table.items():
            tf_table[word] = count / total_words_in_sentence

        tf_matrix[sent] = tf_table

    return tf_matrix

# Function to find how many sentences contain a 'word'
def sentences_per_words(freq_matrix):
    sent_per_words = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in sent_per_words:
                sent_per_words[word] += 1
            else:
                sent_per_words[word] = 1

    return sent_per_words

# Function to calculate Inverse Document Frequency (IDF) for each word
def idf_matrix(freq_matrix, sent_per_words, total_sentences):
    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}

        for word in f_table.keys():
            idf_table[word] = math.log10(total_sentences / float(sent_per_words[word]))

        idf_matrix[sent] = idf_table

    return idf_matrix

# Function to calculate Tf-Idf score of each word
def tf_idf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}

    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):

        tf_idf_table = {}

        # word1 and word2 are same
        for (word1, tf_value), (word2, idf_value) in zip(f_table1.items(), f_table2.items()):
            tf_idf_table[word1] = float(tf_value * idf_value)

        tf_idf_matrix[sent1] = tf_idf_table

    return tf_idf_matrix

# Function to rate every sentence with some score calculated on the basis of Tf-Idf
def score_sentences(tf_idf_matrix):
    sentenceScore = {}

    for sent, f_table in tf_idf_matrix.items():
        total_tfidf_score_per_sentence = 0

        total_words_in_sentence = len(f_table)
        for word, tf_idf_score in f_table.items():
            total_tfidf_score_per_sentence += tf_idf_score

        if total_words_in_sentence != 0:
            sentenceScore[sent] = total_tfidf_score_per_sentence / total_words_in_sentence

    return sentenceScore

# Function Calculating average sentence score
def average_score(sentence_score):
    total_score = 0
    for sent in sentence_score:
        total_score += sentence_score[sent]

    average_sent_score = total_score / len(sentence_score)

    return average_sent_score

# Function to return summary of article
def create_summary(sentences, sentence_score, threshold):
    summary = ''

    for sentence in sentences:
        if sentence[:15] in sentence_score and sentence_score[sentence[:15]] >= threshold:
            summary += " " + sentence.text

    return summary

# Step 5. Using all functions to generate summary

# Counting number of words in original article
original_words = text.split()
original_words = [w for w in original_words if w.isalnum()]
num_words_in_original_text = len(original_words)

# Converting received text into spaCy Doc object
text = nlp(text)

# Extracting all sentences from the text in a list
sentences = list(text.sents)
total_sentences = len(sentences)

# Generating Frequency Matrix
freq_matrix = frequency_matrix(sentences)

# Generating Term Frequency Matrix
tf_matrix = tf_matrix(freq_matrix)

# Getting number of sentences containing a particular word
num_sent_per_words = sentences_per_words(freq_matrix)

# Generating ID Frequency Matrix
idf_matrix = idf_matrix(freq_matrix, num_sent_per_words, total_sentences)

# Generating Tf-Idf Matrix
tf_idf_matrix = tf_idf_matrix(tf_matrix, idf_matrix)

# Generating Sentence score for each sentence
sentence_scores = score_sentences(tf_idf_matrix)

# Setting threshold to average value (You are free to play with other values)
threshold = average_score(sentence_scores)

# Getting summary
summary = create_summary(sentences, sentence_scores, 1.3 * threshold)
print("\n\n")
print("*" * 20, "Summary", "*" * 20)
print("\n")
print(summary)
print("\n\n")
print("Total words in original article = ", num_words_in_original_text)
print("Total words in summarized article = ", len(summary.split()))