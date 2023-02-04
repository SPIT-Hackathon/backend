import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.signal import argrelextrema
import math

from pytube import YouTube
import pywhisper
import pandas as pd
from transformers import pipeline
from pathlib import Path
# Get the transcription of the video



def get_transcription(video_url):
    streams = YouTube(video_url).streams
    title = streams[0].title
    print(title)
    audio_file = streams.filter(only_audio=True).first().download(filename=r"audio_files\audio.mp4")
    # print(audio_file)
    # audio_file = Path(audio_file)
    # print(audio_file)
    whisper_model = pywhisper.load_model("base")
    transcription = whisper_model.transcribe(audio_file)

    df = pd.DataFrame(transcription['segments'], columns=['start', 'end', 'text'])
    print(df)

    print(transcription['text'])

    return [transcription,title]


def get_summary(text):
  summarizer = pipeline("summarization", model="stevhliu/my_awesome_billsum_model")
  summary = summarizer(text)
  return summary


# Get the chunks of the video
para_model = SentenceTransformer('all-mpnet-base-v2')

#utility function for chunking

def preprocess_corpus(text):
  sentences = text.split('. ')
  #unifying lengths
  # Get the length of each sentence
  sentece_length = [len(each) for each in sentences]
  # Determine longest outlier
  long = np.mean(sentece_length) + np.std(sentece_length) *2
  # Determine shortest outlier
  short = np.mean(sentece_length) - np.std(sentece_length) *2
  # Shorten long sentences
  text = ''
  for each in sentences:
      if len(each) > long:
          # let's replace all the commas with dots
          comma_splitted = each.replace(',', '.')
      else:
          text+= f'{each}. '
  sentences = text.split('. ')
  # Now let's concatenate short ones
  text = ''
  for each in sentences:
      if len(each) < short:
          text+= f'{each} '
      else:
          text+= f'{each}. '
  return text

def rev_sigmoid(x:float)->float:
    return (1 / (1 + math.exp(0.5*x)))
    
def activate_similarities(similarities:np.array, p_size=10)->np.array:
        """ Function returns list of weighted sums of activated sentence similarities
        Args:
            similarities (numpy array): it should square matrix where each sentence corresponds to another with cosine similarity
            p_size (int): number of sentences are used to calculate weighted sum 
        Returns:
            list: list of weighted sums
        """
        # To create weights for sigmoid function we first have to create space. P_size will determine number of sentences used and the size of weights vector.
        x = np.linspace(-10,10,p_size)
        # Then we need to apply activation function to the created space
        y = np.vectorize(rev_sigmoid) 
        # Because we only apply activation to p_size number of sentences we have to add zeros to neglect the effect of every additional sentence and to match the length ofvector we will multiply
        activation_weights = np.pad(y(x),(0,similarities.shape[0]-p_size))
        ### 1. Take each diagonal to the right of the main diagonal
        diagonals = [similarities.diagonal(each) for each in range(0,similarities.shape[0])]
        ### 2. Pad each diagonal by zeros at the end. Because each diagonal is different length we should pad it with zeros at the end
        diagonals = [np.pad(each, (0,similarities.shape[0]-len(each))) for each in diagonals]
        ### 3. Stack those diagonals into new matrix
        diagonals = np.stack(diagonals)
        ### 4. Apply activation weights to each row. Multiply similarities with our activation.
        diagonals = diagonals * activation_weights.reshape(-1,1)
        ### 5. Calculate the weighted sum of activated similarities
        activated_similarities = np.sum(diagonals, axis=0)
        return activated_similarities

#
def get_chunks(corpus):
  """ arg :
    corpus = String of text"
  """

  text = preprocess_corpus(corpus)
  sentences = text.split('. ')

  embeddings = para_model.encode(sentences)
  similarities = cosine_similarity(embeddings)
  print(similarities.shape)
  activated_similarities = activate_similarities(similarities, p_size=10)

  minmimas = argrelextrema(activated_similarities, np.less, order=2) 

  split_points = [each for each in minmimas[0]]
  
  res = []

  sent = ""
  for num,s in enumerate(sentences):
    if num in split_points:
        res.append(sent)
        sent = s + ". "
    else:
        sent = sent + s + '. '
  return res
