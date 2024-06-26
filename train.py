import requests
import torch
import torch.nn as nn
from torch.nn import functional as F

url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'

response = requests.get(url)
response.raise_for_status() 

# write contents to files
with open('input.txt', 'wb') as file:
    file.write(response.content)

# read file for inspection
with open('input.txt', 'r', encoding='utf-8') as f:
  text = f.read()

# extract unique characters
chars = sorted(list(set(text)))
vocab_size = len(chars)

# create a mapping from characters to integers
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }
encode = lambda s: [stoi[c] for c in s] # encoder: take a string, output a list of integers
decode = lambda l: ''.join([itos[i] for i in l]) # decoder: take a list of integers, output a string

# data preprocessing
data = torch.tensor(encode(text), dtype=torch.long) # represent text using integers
n = int(0.9*len(data)) # first 90% for training data, last 10% for validation data
train_data = data[:n]
val_data = data[n:]

# define hyperparameters
block_size = 8 # furtherst length we can go
batch_size = 4 # process 4 blocks in parallel

x = train_data[:block_size]
y = train_data[1:block_size+1]
for t in range(block_size):
  context = x[:t+1]
  target = y[t]
  print(f"when input is {context}, target is {target}")

torch.manual_seed(1337)

def get_batch(split):
  data = train_data if split == 'train' else val_data
  ix = torch.randint(len(data) - block_size, (batch_size,))
  x = torch.stack([data[i:i+block_size] for i in ix])
  y = torch.stack([data[i+1:i+block_size+1] for i in ix])
  return x,y

xb, yb = get_batch('train') # xb is out input to the transformer
for b in range(batch_size):
  for t in range(block_size):
    context = xb[b, :t+1]
    target = yb[b, t]
    print(f"when input is {context}, target is {target}")

class BigramLanguageModel(nn.Module):
  def __init__(self, vocab_size):
    # each token directly reads off the logits for the next token from a lookup table
    self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)
  
  def forward(self, idx, targets):
    logits = self.token_embedding_table(idx)
    return logits
