import re
from num2words import num2words
from better_profanity import profanity
import unicodedata

def expand_contractions(text):
    contractions = {
        "ain't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "can't've": "cannot have",
        "'cause": "because",
        "could've": "could have",
        "couldn't": "could not",
        "couldn't've": "could not have",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hadn't've": "had not have",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'd've": "he would have",
        "he'll": "he will",
        "he'll've": "he will have",
        "he's": "he is",
        "how'd": "how did",
        "how'd'y": "how do you",
        "how'll": "how will",
        "how's": "how is",
        "I'd": "I would",
        "I'd've": "I would have",
        "I'll": "I will",
        "I'll've": "I will have",
        "I'm": "I am",
        "I've": "I have",
        "isn't": "is not",
        "it'd": "it would",
        "it'd've": "it would have",
        "it'll": "it will",
        "it'll've": "it will have",
        "it's": "it is",
        "let's": "let us",
        "ma'am": "madam",
        "mayn't": "may not",
        "might've": "might have",
        "mightn't": "might not",
        "mightn't've": "might not have",
        "must've": "must have",
        "mustn't": "must not",
        "mustn't've": "must not have",
        "needn't": "need not",
        "needn't've": "need not have",
        "o'clock": "of the clock",
        "oughtn't": "ought not",
        "oughtn't've": "ought not have",
        "shan't": "shall not",
        "sha'n't": "shall not",
        "shan't've": "shall not have",
        "she'd": "she would",
        "she'd've": "she would have",
        "she'll": "she will",
        "she'll've": "she will have",
        "she's": "she is",
        "should've": "should have",
        "shouldn't": "should not",
        "shouldn't've": "should not have",
        "so've": "so have",
        "so's": "so is",
        "that'd": "that would",
        "that'd've": "that would have",
        "that's": "that is",
        "there'd": "there would",
        "there'd've": "there would have",
        "there's": "there is",
        "they'd": "they would",
        "they'd've": "they would have",
        "they'll": "they will",
        "they'll've": "they will have",
        "they're": "they are",
        "they've": "they have",
        "to've": "to have",
        "wasn't": "was not",
        "we'd": "we would",
        "we'd've": "we would have",
        "we'll": "we will",
        "we'll've": "we will have",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "what'll": "what will",
        "what'll've": "what will have",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "when's": "when is",
        "when've": "when have",
        "where'd": "where did",
        "where's": "where is",
        "where've": "where have",
        "who'll": "who will",
        "who'll've": "who will have",
        "who's": "who is",
        "who've": "who have",
        "why's": "why is",
        "why've": "why have",
        "will've": "will have",
        "won't": "will not",
        "won't've": "will not have",
        "would've": "would have",
        "wouldn't": "would not",
        "wouldn't've": "would not have",
        "y'all": "you all",
        "y'all'd": "you all would",
        "y'all'd've": "you all would have",
        "y'all're": "you all are",
        "y'all've": "you all have",
        "you'd": "you would",
        "you'd've": "you would have",
        "you'll": "you will",
        "you'll've": "you will have",
        "you're": "you are",
        "you've": "you have",
        "bc": "because",
        "wasn't": "was not",
        "we're": "we are",
        "sex": "intercourse",
        "cum": "sauce",
        "asshole": "anus",
        "piss": "pee",
    }
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
    return text

def normalize_numbers(text):
    text = re.sub(r"\$(\d+)M", r"\1 million dollars", text)
    text = re.sub(r"\$(\d+)B", r"\1 billion dollars", text)
    text = re.sub(r"\$(\d+)T", r"\1 trillion dollars", text)
    text = re.sub(r"\$(\d+)", r"\1 dollars", text)
    text = re.sub(r'\$(\d+)\+', ' plus', text)
    text = re.sub(r'(\d+)-(\d+)', r'\1 to \2', text)
    return re.sub(r'\d+', lambda x: num2words(int(x.group(0))), text)

def normalize_punctuation(text):

    # Ensure punctuation is followed by a space when appropriate
    text = re.sub(r'([.,!?])([A-Za-z0-9])', r'\1 \2', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r"\bpercent\b|%"," percent", text)

    # Remove space before punctuation marks
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = ''.join(c for c in text if not unicodedata.category(c).startswith('So'))
    return text

def normalize_text(text):
    profanity.load_censor_words()
    profanity.load_censor_words(whitelist_words=['pee', 'urine'])
    text = expand_contractions(text)
    text = normalize_numbers(text)
    text = profanity.censor( text, "" )
    text = normalize_punctuation(text)
    text = re.sub(r'\b(i)\b', 'I', text)
    return text

# text = "I believe it's bc teens are unassuming and don't know how to shutdown creepy men. It's very predatory. In my younger years, I was stalked in...I still get on as someone in thier 30s but it's very \"normal\" fuck, and sex too you piece of shit cum"
# print( normalize_text( text ) )

# print( normalize_text( "Bernie Sanders Says US Should Confiscate 100% Of Any Money Americans Make Above $999M: 'They Can Survive Just Fine' - what do you think ?" ) )