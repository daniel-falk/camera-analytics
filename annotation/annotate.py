import click
import json
import cv2
import os
from pathlib import Path
from vi3o.image import imread
from vi3o.debugview import DebugViewer
from pyglet.window import key as keysym


class Annotator(DebugViewer):
    def __init__(self, img_dir, index_path):
        super().__init__()

        self.image_paths = list(Path(img_dir).glob("*"))
        self.index_path = index_path
        self.open_index()

        self.exit = False
        self.next_idx = None
        self.current_idx = 0
        self._len = None
        self.left_to_annotate = self._calc_not_annotated()

    def open_index(self):
        self.db = {}
        try:
            with open(self.index_path) as fd:
                self.db = json.load(fd)
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            if os.stat(self.index_path).st_size != 0:
                raise

    def annotate(self):
        for img_path in self.next():
            img = imread(img_path)
            color = (0, 255, 0) if self.left_to_annotate == 0 else (255, 0, 0)
            img = cv2.putText(
                img,
                "%d: %s" % (self.current_idx, self.db.get(img_path, "-")),
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                4,
                color,
                10,
            )
            self.view(img, pause=True)
            print("Not annotated images: %d/%d" % (self.left_to_annotate, len(self)))

    def next(self):
        while not self.exit:
            if self.next_idx is not None:
                self.current_idx, self.next_idx = self.next_idx, None
            else:
                # Find next not annotated image
                while True:
                    self.current_idx = (self.current_idx + 1) % len(self)
                    if (
                        self._get_path() not in self.db.keys()
                        or self.left_to_annotate == 0
                    ):
                        break

            yield self._get_path()

    def write_to_file(self):
        with open(self.index_path, "w") as fd:
            json.dump(self.db, fd, indent=2, sort_keys=True)

    def _set_state(self, new_state):
        if self._get_path() not in self.db:
            self.left_to_annotate -= 1
        self.db[self._get_path()] = new_state

    def _get_path(self, index=None):
        if index is None:
            index = self.current_idx
        return str(self.image_paths[index].resolve())

    def on_key_press(self, key, modifiers):
        """Overrides the standard key event receiver
        """
        DebugViewer.paused = False
        if key == keysym.UP:
            self._set_state("open")
        elif key == keysym.DOWN:
            self._set_state("closed")
        elif key == keysym.LEFT:
            self.next_idx = self.current_idx - 1
            if self.next_idx < 0:
                self.next_idx += len(self)
        elif key == keysym.RIGHT:
            self.next_idx = (self.current_idx + 1) % len(self)
        elif key == keysym.Q:
            self.exit = True

    def _calc_not_annotated(self):
        num = 0
        for idx in range(len(self)):
            if self._get_path(index=idx) not in self.db.keys():
                num += 1
        return num

    def __len__(self):
        if self._len is None:
            self._len = len(self.image_paths)
        return self._len


@click.command()
@click.argument("image-dir")
@click.option("--output", default="index.json")
def do_annotate(image_dir, output):
    annotator = Annotator(image_dir, output)
    print("Initialized with %d images" % len(annotator))
    annotator.annotate()
    annotator.write_to_file()


if __name__ == "__main__":
    do_annotate()
