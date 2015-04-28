# Overview
Perform basic Natural Language Processing on patent description documents and store results in cloud storage.

**ngramFrequencyCount.py** retrieves text files and performs a frequency count on unique unigrams, bigrams, and trigrams for each file as well as aggregate counts for all files. Data is saved as csv files in the output directory.

**queryStringAuthentication.py** uploads the contents of the output directory to a specified AWS S3 bucket, sets the file permission to private, and creates an authenticated URL with time-expiration for access to each file.

# NLP Method
This script was written to perform ngram analysis on patent descriptions. In order to produce meaningful ngrams, the text had to be filtered for stop words and stemmed. 

I used the [Natural Language Toolkit (NLTK)](http://www.nltk.org/) for its stop word dictionary and ability to tokenize strings. Removing NLTK stop words from the patent descriptions, however, was insufficient in  reducing the text to meaningful words. Extraneous punctuation and alphanumeric lists (such as a) ... b) ... etc.) remained in the text. So I chose to convert all text to lowercase and regexp filter for only alphabetic characters before running the stop word filter. This produced cleaner results without distorting the meaning of the text. At this point I stem the words and tokenize them. 

NLTK has a handy function for frequency count, `nltk.FreqDist()`, which accepts a list, in this case a list of unigram strings or bi/tri-gram tuples, and produces a list of tuples with the count of each item and can then be sorted. In order to also take the aggregate ngram counts of all documents, I use aggregate lists for each type of ngram.

Files are written locally using the csv module.

# AWS S3 Method
In order to interface with AWS S3 through Python, I used the [Boto Modules](https://boto.readthedocs.org/en/latest/), which allows for connecting to an S3 bucket, creating a key in that bucket, and setting the contents of the key from a local file (`set_contents_from_filename()`).

Using the [os.path module](https://docs.python.org/2/library/os.path.html) I iterated through files in the output directory, uploading each to the S3 bucket and generating an authenticated query string URL for each file with Boto's `generate_url()` function.

