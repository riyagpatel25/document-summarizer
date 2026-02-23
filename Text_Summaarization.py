import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import sys
import math
import bs4 as bs
import urllib.request
import re
import nltk
from nltk.stem import WordNetLemmatizer
import spacy

# Download necessary resources
nltk.download('wordnet')
nlp = spacy.load('en_core_web_sm')
lemmatizer = WordNetLemmatizer()

# Function Definitions
def file_text(filepath):
    try:
        with open(filepath, 'r') as file:
            text = file.read().replace("\n", '')
            return text
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file: {str(e)}")
        return ""

def wiki_text(url):
    try:
        scrap_data = urllib.request.urlopen(url)
        article = scrap_data.read()
        parsed_article = bs.BeautifulSoup(article, 'lxml')
        paragraphs = parsed_article.find_all('p')
        article_text = ""
        for p in paragraphs:
            article_text += p.text
        article_text = re.sub(r'\[[0-9]*\]', '', article_text)
        return article_text
    except Exception as e:
        messagebox.showerror("Error", f"Could not retrieve Wikipedia article: {str(e)}")
        return ""

def process_text(input_text):
    if not input_text.strip():
        return None, None, None

    original_words = input_text.split()
    original_words = [w for w in original_words if w.isalnum()]
    num_words_in_original_text = len(original_words)

    text_doc = nlp(input_text)
    sentences = list(text_doc.sents)
    total_sentences = len(sentences)
    
    # Generate Frequency Matrix
    freq_matrix = frequency_matrix(sentences)
    tf_matrix_values = tf_matrix(freq_matrix)
    num_sent_per_words = sentences_per_words(freq_matrix)
    idf_matrix_values = idf_matrix(freq_matrix, num_sent_per_words, total_sentences)
    tf_idf_matrix_values = tf_idf_matrix(tf_matrix_values, idf_matrix_values)
    sentence_scores = score_sentences(tf_idf_matrix_values)
    threshold = average_score(sentence_scores)
    summary = create_summary(sentences, sentence_scores, 1.3 * threshold)

    return summary, num_words_in_original_text, len(summary.split())

def frequency_matrix(sentences):
    freq_matrix = {}
    stopWords = nlp.Defaults.stop_words
    for sent in sentences:
        freq_table = {}
        words = [word.text.lower() for word in sent if word.text.isalnum()]
        for word in words:
            word = lemmatizer.lemmatize(word)
            if word not in stopWords:
                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1
        freq_matrix[sent[:15]] = freq_table
    return freq_matrix

def tf_matrix(freq_matrix):
    tf_matrix = {}
    for sent, freq_table in freq_matrix.items():
        tf_table = {}
        total_words_in_sentence = len(freq_table)
        for word, count in freq_table.items():
            tf_table[word] = count / total_words_in_sentence
        tf_matrix[sent] = tf_table
    return tf_matrix

def sentences_per_words(freq_matrix):
    sent_per_words = {}
    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in sent_per_words:
                sent_per_words[word] += 1
            else:
                sent_per_words[word] = 1
    return sent_per_words

def idf_matrix(freq_matrix, sent_per_words, total_sentences):
    idf_matrix = {}
    for sent, f_table in freq_matrix.items():
        idf_table = {}
        for word in f_table.keys():
            idf_table[word] = math.log10(total_sentences / float(sent_per_words[word]))
        idf_matrix[sent] = idf_table
    return idf_matrix

def tf_idf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}
    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        tf_idf_table = {}
        for (word1, tf_value), (word2, idf_value) in zip(f_table1.items(), f_table2.items()):
            tf_idf_table[word1] = float(tf_value * idf_value)
        tf_idf_matrix[sent1] = tf_idf_table
    return tf_idf_matrix

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

def average_score(sentence_score):
    total_score = 0
    for sent in sentence_score:
        total_score += sentence_score[sent]
    average_sent_score = (total_score / len(sentence_score))
    return average_sent_score

def create_summary(sentences, sentence_score, threshold):
    summary = ''
    for sentence in sentences:
        if sentence[:15] in sentence_score and sentence_score[sentence[:15]] >= (threshold):
            summary += " " + sentence.text
    return summary

# GUI Functions
def display_summary(input_text):
    summary, original_count, summarized_count = process_text(input_text)
    if summary:
        result_window = tk.Toplevel(app)
        result_window.title("Summary Result")
        result_window.geometry("700x500")
        
        # Display Summary
        result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
        result_text.pack(expand=True, fill=tk.BOTH)
        result_text.insert(tk.INSERT, f"**Summary**\n\n{summary}\n\n")
        result_text.insert(tk.INSERT, f"Original Words: {original_count} | Summarized Words: {summarized_count}")
        result_text.configure(state='disabled')

    else:
        messagebox.showinfo("No Text", "Please provide valid input text.")

def get_text_from_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        input_text.delete(1.0, tk.END)
        input_text.insert(tk.END, file_text(file_path))

def get_text_from_url():
    url = url_input.get()
    if url:
        input_text.delete(1.0, tk.END)
        input_text.insert(tk.END, wiki_text(url))

def clear_text():
    input_text.delete(1.0, tk.END)
    url_input.delete(0, tk.END)

# Create the Main Application Window
app = tk.Tk()
app.title("Text Summarization App")
app.geometry("600x700")

# Frame for input methods
input_frame = tk.Frame(app)
input_frame.pack(pady=10)

# Buttons for file and URL input
btn_file = tk.Button(input_frame, text="Load from .txt File", command=get_text_from_file)
btn_file.grid(row=0, column=0, padx=5)

url_input = tk.Entry(input_frame, width=40)
url_input.grid(row=0, column=1, padx=5)

btn_url = tk.Button(input_frame, text="Load from URL", command=get_text_from_url)
btn_url.grid(row=0, column=2, padx=5)

# Textbox for typing or pasting text
input_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=20)
input_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Buttons for processing
button_frame = tk.Frame(app)
button_frame.pack(pady=10)

btn_summarize = tk.Button(button_frame, text="Summarize Text", command=lambda: display_summary(input_text.get("1.0", tk.END)))
btn_summarize.grid(row=0, column=0, padx=10)

btn_clear = tk.Button(button_frame, text="Clear", command=clear_text)
btn_clear.grid(row=0, column=1, padx=10)

app.mainloop()
