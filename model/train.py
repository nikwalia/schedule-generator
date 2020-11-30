import sys
import time
import argparse

from tqdm import tqdm
import torch
import numpy as np
import torch.nn as nn
from torch.optim import AdamW

from db.mysql_engine import loadEngine
from model.recommendation_model import LSTM, FFNN
from model.utils import load_checkpoint, save_checkpoint, setup_model, TrackDataset

def calculate_accuracy(predicted, expected):
    """
    Method to calculate accuracy of model with Euclidean distance.

    :param predicted: List of model predictions
    :param expected: List of expected values from model

    :returns: Euclidean distance between predicted and expected
    """
    # expected: [ 0 0 0 0 1 0 1 0 0 0 0 0 0 1]
    # predicte: [ 0.01 0.16 0.11 ... ]
    z = 1/torch.cdist(predicted, expected, p=2.0)
    m = 1/(1 + np.exp(-z))
    return torch.norm(m)

def train(args, model, train_dataloader, valid_dataloader):
    """
    Method to handle training the model.

    :param model: model to train
    :param args: arguments passed in via command line
    :param train_dataloader: Dataloader containing training data
    :param valid_dataloader: Dataloader containing validation data
    """

    # initialize Adam (weight fix) optimizer
    optimizer = AdamW(model.parameters(), lr=args.lr, eps=args.eps)
    criterion = nn.BCEWithLogitsLoss()

    model.to(args.device)
    total_t0 = time.time()
    avg_loss = 0

    for epoch_i in tqdm(range(args.epochs)):
        print('\n====== Epoch {:} / {:} ======'.format(epoch_i + 1, args.epochs))

        t0 = time.time()
        epoch_loss = 0

        # zero gradients and begin training
        model.zero_grad()
        model.train()

        for step, (inputs, expected) in tqdm(enumerate(train_dataloader)):
            model.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs[0], expected[0])

            epoch_loss += loss.item()

            loss.backward()

            # clip gradients to handle explosive gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            model.zero_grad()
        
        avg_train_loss = epoch_loss / len(train_dataloader)
        training_time = time.time() - t0

        print("\nAverage training loss: {0:.2f}".format(avg_train_loss))
        print("Training epoch took: {:}".format(training_time))

        # begin evaluation
        model.eval()

        t0 = time.time()
        total_eval_accuracy = 0
        total_eval_loss = 0

        for step, (inputs, expected) in tqdm(enumerate(valid_dataloader)):
            
            with torch.no_grad():
                outputs = model(inputs)
                loss = criterion(outputs, expected)

                total_eval_accuracy += calculate_accuracy(inputs, expected)
                total_eval_loss += loss.item()

        avg_val_accuracy = total_eval_accuracy / len(valid_dataloader)
        print("Accuracy: {0:.2f}".format(avg_val_accuracy))

        avg_val_loss = total_eval_loss / len(valid_dataloader)
        print("Validation Loss: {0:.2f}".format(avg_val_loss))
        avg_loss += avg_train_loss

        validation_time = time.time() - t0
        print("Validation took: {:}".format(validation_time))

    total_time = time.time() - total_t0
    print("Training took: {:}".format(total_time))
    return avg_loss/args.epochs, total_time
    

def predict(model, args, test_loader, num_classes):
    """
    Method to handle model prediction.

    :param model: model to train
    :param args: arguments passed in via command line
    :param input_data: data to be passed into model
    """
    outputs = torch.empty(len(test_loader), num_classes)
    for step, batch in tqdm(enumerate(test_loader)):
        with torch.no_grad():
            output = model(batch)
            outputs[step] = output

    return outputs

def main(ap: argparse.ArgumentParser):
    """
    Main runner to execute training/validation of model.

    :param ap: Argument parser holding all command line input
    """
    ap.add_argument("--mode", type=str, default="train", help="Mode to run from command line")
    ap.add_argument("--lr", type=float, default=2e-5, help="Learning rate for optimizer")
    ap.add_argument("--eps", type=float, default=1e-8, help="Epsilon for optimizer")
    ap.add_argument("--epochs", type=int, default=5, help="Number of epochs to train for")
    ap.add_argument("--batchsize", type=int, default=5, help="Batch size for data iteration")
    ap.add_argument("--hiddensize", type=int, default=256, help="Size for hidden layer")
    ap.add_argument("--traindata", type=str, default="Computer Science, BS-General", help="Track for train data")
    ap.add_argument("--validdata", type=str, default="Computer Science, BS-General", help="Track for validation data")
    ap.add_argument("--testdata", type=str, default="Computer Science, BS-General", help="Track for test data")
    ap.add_argument("--device", type=str, default="cpu", help="Device to train on")
    args = ap.parse_args()

    engine = loadEngine()

    if 'train' in args.mode:
      
        # if one track doesn't exist, fill it in with other
        # if both are different, do not continue
        train_track = args.traindata
        valid_track = args.validdata
        if train_track != valid_track:
            if not train_track:
                train_track = valid_track
            elif not valid_track:
                valid_track = train_track
            else:
                raise ValueError('Invalid track argument.')
        # NOTE: data should be formatted in (inputs, expected) format
        # TODO: get data and feed it in
        
        # load in data based on track
        train_dataset = TrackDataset(engine, train_track)
        valid_dataset = TrackDataset(engine, valid_track)

        train_loader = torch.utils.data.DataLoader(dataset=train_dataset, 
                                                   batch_size=args.batchsize, 
                                                   shuffle=True)

        valid_loader = torch.utils.data.DataLoader(dataset=valid_dataset, 
                                                   batch_size=args.batchsize, 
                                                   shuffle=False)

        model = setup_model(engine, args.traindata, args.hiddensize)
        loss, total_time = train(args, model, train_loader, valid_loader)

        save_checkpoint('saved_models/' + train_track + '-model', model, args.epochs, loss, total_time)

    elif 'predict' in args.mode:
        # This predict option is only to be used for inference
        # Do not use this in the actual application
        # NOTE: data should be formatted in (inputs) format
        test_track = args.testdata
        test_dataset = TrackDataset(engine, test_track)
        test_loader = torch.utils.data.DataLoader(dataset=test_dataset, 
                                                  batch_size=1, 
                                                  shuffle=False)

        predict(model, args, test_loader)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    main(ap)
    