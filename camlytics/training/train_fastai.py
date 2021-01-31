import click
import numpy as np
from collections import defaultdict
from prettytable import PrettyTable
from fastai.vision import (
        cnn_learner,
        models,
)
from fastai.callbacks.tensorboard import LearnerTensorboardWriter
from fastai.metrics import Precision, Recall
from functools import partial
from pathlib import Path

from camlytics.annotation.data_file import image_data_bunch_from_data_file


def train(data):
    learn = cnn_learner(data, models.resnet18, metrics=[Precision(), Recall()])
    learn.callback_fns.append(partial(
        LearnerTensorboardWriter,
        base_dir=Path("data/tensorboard/camlytics_fastai"),
        name="deterministic-data")
    )
    learn.fit_one_cycle(20, 1e-2)
    learn.save("finetune-epoch-20")

    import pdb; pdb.set_trace()


@click.command()
@click.argument("index-path")
@click.option("--width", default=192)
@click.option("--height", default=108)
def do_train(index_path, width, height):
    data = image_data_bunch_from_data_file(index_path, path=".", size=(height, width), seed=10)

    data_metrics = defaultdict(dict)
    dataset_names = ["Training", "Validation", "Test"]
    datasets = (data.train_ds, data.valid_ds, data.test_ds)
    for name, dataset in zip(dataset_names, datasets):
        if dataset:
            for label in dataset.y.classes:
                data_metrics[label][name] = sum(np.array([str(lbl) for lbl in dataset.y]) == str(label))


    tab = PrettyTable(["Class"] + dataset_names)
    for label, datasets in data_metrics.items():
        tab.add_row([label] + [datasets.get(name, 0) for name in dataset_names])
    print(tab)

    train(data)


if __name__ == "__main__":
    do_train()
