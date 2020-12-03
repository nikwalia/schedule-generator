import torch
import torch.nn as nn
import torch.nn.functional as F

class FFNN(nn.Module):
    '''
    Feed forward neural network 

    :param input_size: input dimension for NN
    :param hidden_size: hidden dimension for NN
    '''

    def __init__(self, input_size, hidden_size):
        super(FFNN, self).__init__()
        self.input_dim = input_size
        self.hidden_dim = hidden_size
        self.fc1 = nn.Linear(input_size, hidden_size) 
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, input_size)  
    
    def forward(self, inp):
        fc1_out = self.fc1(inp)
        relu_out = self.relu(fc1_out)
        fc2_out = self.fc2(relu_out)
        return fc2_out
