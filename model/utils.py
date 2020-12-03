import os
import json
import numpy as np

import torch
from torch.utils.data import Dataset

from db.mysql_engine import MySQLEngine
from model.recommendation_model import FFNN


def load_checkpoint(filename: str, model = None):
    '''
    Loads PyTorch checkpoint

    :param filename: name of file to import model from
    :param model: model type
    :returns: epoch
    '''
    print("Loading %s" % filename)
    checkpoint = torch.load(filename)

    if model:
        model.load_state_dict(checkpoint["state_dict"])
    else:
        with open(filename[:len(filename) - 4] + '.json') as config_file:
            config = json.load(config_file)
        model = FFNN(config['input_dim'], config['hidden_dim'])

    epoch = checkpoint["epoch"]
    loss = checkpoint["loss"]
    print("epoch = %d, loss = %f" % (checkpoint["epoch"], checkpoint["loss"]))
    return model

def save_checkpoint(filename: str, model, epoch: int, loss: float, time):
    '''
    Saves PyTorch checkpoint

    :param filename: name of file to import model from
    :param model: model type
    :param epoch: epochs trained
    :param loss: loss of model
    :param time: time taken to train model
    '''
    print("epoch = %d, loss = %f, time = %f" % (epoch, loss, time))
    if filename and model:
        checkpoint = {}

        checkpoint["state_dict"] = model.state_dict()
        checkpoint["epoch"] = epoch
        checkpoint["loss"] = loss

        filename = filename + "-epoch%d" % epoch + '.pth'
        torch.save(checkpoint, filename)
        print("Saved %s" % filename)

        config = {'input_dim': model.input_dim, 'hidden_dim': model.hidden_dim}
        with open(filename[:len(filename) - 4] + '.json', 'w+') as config_file:
            json.dump(config, config_file)



def setup_model(engine: MySQLEngine, track: str, hidden_size: int = None):
    """
    Creates a FFNN.

    :param engine (MySQLEngine): engine used to get classes
    :param track (str): the data to create the model for
    """
    classes = engine.wrapped_query(
                'SELECT course_id ' \
                'FROM student_info.courses ' \
                'WHERE interest LIKE "%%{}%%"'.format(track))
    vec_size = len(classes)

    if not hidden_size:
        hidden_size = vec_size * 3 // 2
    return FFNN(vec_size, hidden_size)


class TrackDataset(Dataset):
    """
    Course enrollments training dataset.
    """
    def __init__(self, engine: MySQLEngine, track: str):
        """
        Args:

        :param engine (MySQLEngine): connected to RDMS, used to fetch data
        :param track (str): the data to generate train examples for
        """
        command_str = "SELECT * " \
                        "FROM student_info.courses " \
                        "NATURAL JOIN student_info.enrollments " \
                        "WHERE courses.interest LIKE '%%{}%%' " \
                        "ORDER BY enrollments.net_id".format(track)
        results = engine.wrapped_query(command_str)
        
        combinations = list(set(results.set_index(['net_id', 'semester_taken']).index))

        classes = engine.wrapped_query(
                "SELECT course_id " \
                "FROM student_info.courses " \
                "WHERE interest LIKE '%%{}%%'".format(track)).to_numpy()

        res_vectors = []

        for combination in combinations:
            match_input_data = results.loc[(results['net_id'] == combination[0]) \
                            & (results['semester_taken'] == combination[1])]
            if len(match_input_data) == 0:
                continue
        
            match_output_data = results.loc[(results['net_id'] == combination[0]) \
                            & (results['semester_taken'] == combination[1] + 1)]
            if len(match_output_data) == 0:
                continue

            input_vector = np.sum(match_input_data['course_id'].to_numpy() == classes, axis=1)
            output_vector = np.sum(match_output_data['course_id'].to_numpy() == classes, axis=1)

            res_vectors.append([input_vector, output_vector])
        
        self.__data_vectors = np.array(res_vectors)


    def __len__(self):
        return len(self.__data_vectors)
    
    
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        return (torch.tensor(self.__data_vectors[idx, 0, :], dtype=torch.float32), torch.tensor(self.__data_vectors[idx, 1, :], dtype=torch.float32))
