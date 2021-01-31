import json
from pathlib import Path
import numpy as np


class DictDataFile:
    """This class is a dict interface to the annotation index file

    The annotation index file can be opened, read from and saved to.
    """
    def __init__(self, index_path):
        """Open an index file or create a new one if path does not exist
        """
        self.index_path = Path(index_path)
        self.db = {}
        try:
            with self.index_path.open() as fd:
                self.db = json.load(fd)
        except FileNotFoundError:
            # We have already created an empty db dict
            pass
        except json.decoder.JSONDecodeError:
            # If file is empty, continue with empty db dict
            # otherwise raise error since json is invalid
            if self.index_path.stat.st_size != 0:
                raise

    def commit(self):
        """Commit the index database to the persistent file
        """
        with self.index_path.open("w") as fd:
            json.dump(self.db, fd, indent=2, sort_keys=True)

    def __iter__(self):
        return iter(self.db)

    def __getitem__(self, name):
        return self.db[name]

    def __setitem__(self, name, value):
        self.db[name] = value

    def __getattr__(self, name):
        return getattr(self.db, name)

    def __setattr__(self, name, value):
        if "_%s__initialised" % self.__class__.__name__ not in self.__dict__:
            # Allow set new attributes in __init__ method
            return dict.__setattr__(self, name, value)
        else:
            return setattr(self.db, name, value)


def image_data_bunch_from_data_file(index_path, seed=0, **kwargs):
    """This factory creates a fastai ImageDataBunch from an index
    """
    from fastai.vision.data import ImageDataBunch

    db = DictDataFile(index_path)

    def label_from_key(fpath):
        return db[fpath]

    # Set the numpy seed to we get deterministic splits of traing/validation data
    # then reset it to the previous value so we don't affect the rest of the application
    old_state = np.random.get_state()
    try:
        if seed is not None:
            np.random.seed(seed)
        return ImageDataBunch.from_name_func(fnames=list(db.keys()), label_func=label_from_key, **kwargs)
    finally:
        np.random.set_state(old_state)
