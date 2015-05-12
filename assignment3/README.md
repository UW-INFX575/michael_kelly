# Overview
This script analyzes natural language text using two methods: Latend Drichlet Allocation (LDA) and Cultural Holes analysis. Toy data is used for easy evaluation and comparison of methods.

## LDA Method
LDA is a generative model for automatically discovering the topics of documents. The model assumes that documents consist of a mixture of topics and that each topic has a certain probability of generating a certain word. The model takes as parameters a specified number of topics and the number of words to represent each topic. Using probability distributions, the model yields the topics of a document identified by words from that topics, which are selected from the topics probability distribution of words.

In order to perform LDA, I first convert the natural language text into unigrams, with stop words removed and remaining words stemmed. Then I combine all documents into a list of strings and convert that into a term-document matrix (TDM). The threshold for a word appearing in the TDM is set to one: so any word that appears in the document will be represented in the matrix.

### Patent Data
Using a sample data set of 10 patent documents, I produce 20 topics that comprise all the topics in the documents set. This parameter simply to use 2 topics per document.

### Silly Sentences
LDA is also done on a simple set of 5 sentences comprising two topics, food and pets, with credit to [Edwin Chen](http://blog.echen.me/2011/08/22/introduction-to-latent-dirichlet-allocation/) for the example. When these sentences are mixed together into a document, my implementation of LDA performs well in identifying the two topics with only a few words misplaced (Chinchillas are not food!).

## Cultural Holes (Jargon Distance)
Communication within a group tends towards efficiency: commonly used ideas are conveyed with shorter words and phrases that uncommon ideas. The terminology that is common, terse, and well-understood by one group may be unfamiliar to another. We call this in-group language jargon. Cultural Holes is a method for measuring the communication inefficiency between two groups who may have similar or vastly different terminology. 

Jargon distance is measured by analyzing terms in the documents of one group and those of another and, treating the first group as a message sender and the other as a message reader, and computing the efficiency of the communication as the ratio of the average message length within the sender group (Shannon entropy) to the average message length between fields (Cover and Thomas cross entropy). The final jargon distance, or cultural hole, is the inefficiency of the communication: 1 - the efficiency.

To implement this method I convert the documents of each group into unigrams with stop words removed and remaining words stemmed. I take a frequency count of unigrams in each group and then convert these to probability distributions (known in Cultural Holes jargon as codebooks). 

In order to compute cross entropy in the next step, the probability distributions must contain non-zero probabilities for terms across both groups and there must be a probability distribution for the entire corpus of both groups. I do this by initializing the probability distributions for the groups as a Python dictionary with keys for all terms in the entire corpus and default values set to the alpha value of 0.01. Probabilities from the group are then added into the dictionary, replacing the default values where the keys exist and leaving them in place where they don't.

With all three probability distributions created, the formula for Jargon Distance can be computed. 

### Silly Sentences
The jargon distance between the silly sentence about food and pets is 0.41 -- relatively high because the data set is small and there is only one common word between groups.

### Generated Text
For a more robust example, I used two different filler text generators: [Cat Ipsum](http://www.catipsum.com/) and [Hipster Ipsum](http://hipsum.co/). Because the algorithm depends on English wordlists to stop and stem, I use English only text (no actual lorum ipsum nonwords). The jargon distance between groups is 0.08. To test that the algorithm is working properly, I give it documents split in two groups which actually belong to one group and measure the distance: only 0.027.

## Conclusion
These two methods serve different purposes: LDA is a method for generating topics for a set of documents while Cultural Holes measures how different two groups of documents are from each other in terms of message inefficiency. Results from the toy data sets show the algorithms performing as expected.




