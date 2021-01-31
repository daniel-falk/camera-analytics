import cv2
import click
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim
from vi3o.image import imread
from prettytable import PrettyTable

class Net(torch.nn.Module):
    def __init__(self, input_shape):
        super().__init__()
        self.fc1 = nn.Linear(np.prod(input_shape), 1000)
        self.fc2 = nn.Linear(1000, 2)

    def forward(self, x):
        x = self.fc1(x)
        x = nn.functional.relu(x)
        x = self.fc2(x)
        return x


def train(dataset, input_shape):
    net = Net(input_shape)
    optimizer = torch.optim.SGD(net.parameters(), lr=0.01)
    loss = nn.CrossEntropyLoss()
    net.train()
    for i, (path, label) in enumerate(dataset.items_forever()):
        # Read the input data and transform the label to index
        img = imread(path)
        img = cv2.resize(img, input_shape, interpolation=cv2.INTER_NEAREST)
        data = torch.Tensor(img[:,:,0].flatten())
        target = torch.Tensor([0 if label == "open" else 1]).type(torch.long)

        # Calculate gradients
        optimizer.zero_grad()
        output = net(data)
        batch_loss = loss(output.view(1, -1), target)
        batch_loss.backward()  # Compute sum of gradients
        optimizer.step()

        print(f"Iteration {i}: Output {output} vs expected {target} - loss: {batch_loss}")


class DataSet:
    def __init__(self, db):
        self.db = db
        self._len = None

        self.num_open, self.num_closed = 0, 0
        for label in db.values():
            if label == "open":
                self.num_open += 1
            else:
                self.num_closed += 1

    def items_forever(self):
        while True:
            key = np.random.choice(list(self.db.keys()))
            yield key, self.db[key]

    def __len__(self):
        if self._len is None:
            self._len = len(self.db)
        return self._len


class MultiDataSet(DataSet):
    def __init__(self, db, balanced=True, train=0.8, validate=0.1, seed=0):
        super().__init__(db.copy())


        old_state = np.random.get_state()
        try:
            if seed is not None:
                np.random.seed(seed)
            if balanced:
                num_min = min(self.num_open, self.num_closed)
                num_train = int(num_min * train)
                num_validate = int(num_min * validate)
                train_db = self._pop_balanced(num_train)
                validate_db = self._pop_balanced(num_validate)
            else:
                num_train = int(len(self.db) * train)
                num_validate = int(len(self.db) * validate)
                train_db = self._pop(num_train)
                validate_db = self._pop(num_validate)
        finally:
            np.random.set_state(old_state)

        self.train, self.validate, self.test = (DataSet(db) for db in (train_db, validate_db, self.db))

    def _pop(self, amount):
        if amount == 0:
            return {}
        num = len(self.db)
        idx = np.random.choice(range(num), amount, replace=False)
        keys = np.array(list(self.db.keys()))[idx]
        new_db = {key: self.db.pop(key) for key in keys}
        return new_db

    def _pop_balanced(self, amount_each):
        if amount_each == 0:
            return {}
        all_keys = list(self.db.keys())
        all_open_keys = [key for key in all_keys if self.db[key] == "open"]
        all_closed_keys = list(set(all_keys) - set(all_open_keys))
        new_db = {}
        def pop_random(key_list):
            key = np.random.choice(key_list)
            key_list.remove(key)
            new_db[key] = self.db.pop(key)
        for _ in range(amount_each):
            pop_random(all_open_keys)
            pop_random(all_closed_keys)
        return new_db


@click.command()
@click.argument("index-path")
@click.option("--input-width", default=192)
@click.option("--input-height", default=108)
def do_train(index_path, input_width, input_height):
    input_shape = (int(input_height), int(input_width))
    with open(index_path) as fd:
        db = json.load(fd)

    data = MultiDataSet(db, balanced=False, train=0.9)

    tab = PrettyTable(["Dataset name", "Num open", "Num closed"])
    for name in ("train", "validate", "test"):
        dataset = getattr(data, name)
        tab.add_row([name, dataset.num_open, dataset.num_closed])
    print(tab)

    train(data.train, input_shape)


if __name__ == "__main__":
    do_train()
