# Model information and guide

## Dependencies
The `conda` Python package manager has been used to install all software maintained on the Anaconda cloud. Pip is used for the rest.

All dependencies can be installied with the following:

`conda install torch -y`

## Training the Model

We use a simple feedforward neural network to generate the scores for each class. The model expects a 
one-hot vector of classes taken and spits out a vector of scores for classes it thinks the student should
take in the next semester. 



## Files and directories:
 - `recommendation_model.py` - stores the model architecture
 - `train.py` - contains the training script
 - `utils.py` - contains all helpers for training and model usage
