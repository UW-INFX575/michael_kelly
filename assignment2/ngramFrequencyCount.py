import requests
import csv
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import *

# Retrieve documents from server
url = 'https://s3-us-west-2.amazonaws.com/uspto-patentsclaims/'
ids = range(6334220, 6334230) # range of document IDs to fetch

# Coerce numbers to strings for use as dict keys
ids = [str(doc_id) for doc_id in ids]

# Store contents of each document in dictionary
print 'Retrieving patent documents from server'
documents = {}
for doc_id in ids:
    documents[doc_id] = requests.get(url + doc_id + '.txt').content

    # Prepares a document for word analysis by removing punctuation
# and stop words, and then reducing remaining words to their stems
# Takes a document (string) and returns words (list of strings)
def stop_and_stem(document):
    # Convert to lowercase and remove punctuation from text
    tokenizer = RegexpTokenizer(r'[a-z]+')
    document = document.lower()
    document = tokenizer.tokenize(document)
    
    # Remove stop words
    stop = stopwords.words('english')
    words = [word for word in document if word not in stop]
    
    # Reduce words to their stem (truncate suffix)
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    
    # Function above returns unicode. Return to ASCII.
    words = [x.encode('UTF8') for x in words]
    
    return words

# Counts the unique occurences of ngrams in a list
# Takes a set of ngrams (list of strings or tuples)
# and returns a sorted list of tuples with frequency count.
# e.g. [('Hey', 'friend')...] --> [(('Hey', 'friend'), 4)...]
def count_unique_ngrams(ngrams):
    freq = nltk.FreqDist(ngrams).items()
    freq = sorted(freq, key=lambda tup: tup[-1], reverse=True)
    return freq


# Write the data to a local file
# Takes the name of the file to be written (string)
# and the data to be written (list of tuples).  
def write_count_file(file_name, data):
    with open('output/' + file_name + '.csv', 'w') as write_file:
        writer = csv.writer(write_file)
        for ngram, count in data:
            # for cleaner display, print ngram tuples as plain text
            if isinstance(ngram, tuple):
                ngram = ' '.join(map(str, ngram))
            values = [ngram, count]
            writer.writerow(values)

# In order to aggregate ngrams across all documents      
unigrams_agg = []
bigrams_agg = []
trigrams_agg = []

# Process each document
print 'Creating ngram frequency count files'
for doc_id, document in documents.items():
    # Remove punctuation, stop words, and stem
    words = stop_and_stem(document)
    
    # Hold the ngrams
    unigrams = words
    bigrams = list(nltk.bigrams(words))
    trigrams = list(nltk.trigrams(words))
    
    # Add ngrams to the aggregates
    unigrams_agg += unigrams
    bigrams_agg += bigrams
    trigrams_agg += trigrams
    
    # Create tuple with unique ngram and frequency count 
    unigrams_count = count_unique_ngrams(unigrams)
    bigrams_count = count_unique_ngrams(bigrams)
    trigrams_count = count_unique_ngrams(trigrams)
    
    # Write data to file per ngram per document
    write_count_file('unigrams-' + doc_id, unigrams_count)
    write_count_file('bigrams-' + doc_id, bigrams_count)
    write_count_file('trigrams-' + doc_id, trigrams_count)

    
# Get counts for ngrams aggregated across all documents
unigrams_agg = count_unique_ngrams(unigrams_agg)
bigrams_agg = count_unique_ngrams(bigrams_agg)
trigrams_agg = count_unique_ngrams(trigrams_agg)

# Write those to files as well
write_count_file('unigrams-combined', unigrams_agg)
write_count_file('bigrams_combined', bigrams_agg)
write_count_file('trigrams_combined', trigrams_agg)

print 'Complete'