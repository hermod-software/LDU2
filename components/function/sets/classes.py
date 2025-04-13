from PIL import Image
import os
import yaml

from components.shared_instances import set_database
from components.function.logging import log

log("loading setgroup classes")

class SetGroup: # we dont call it set because it's a reserved word in python
    PATH = os.path.join("components", "assets", "sets")
    def __init__(self, folder):

        self.items = []
        self.path = os.path.join(SetGroup.PATH, folder)

        with open(os.path.join(self.path, "set.yml"), encoding="utf-8-sig") as f:
            self.info = yaml.safe_load(f)

        self.name = self.info.get("set_name", "unknown_set")
        self.set_type = self.info.get("set_type", "unknown")
        self.set_date = self.info.get("set_date", "unknown")
        self.author = self.info.get("author", "unknown")
        self.author_id = self.info.get("author_id", "unknown")

        self.load_items()

        log(f"loaded set {self.name} with {len(self.items)} items")

        set_database.append(self)   

    def load_items(self):
            self.items_list = self.info.get("items", [])
            
            if "items" not in self.info:
                log(f"no items found in set {self.name}")
                return
            
            for item in self.items_list:
                item_name = item.get("name", "unknown_item")
                item_path = item.get("image")
                item_path = os.path.join(self.path, item_path)
                if not os.path.exists(item_path):
                    log(f"image for item {item_name} not found: {item_path}")
                    continue
                item_obj = SetItem(item_name, self.set_type, self, item_path)
                self.items.append(item_obj)
                
    def __str__(self):
        return f"SetGroup({self.name}, {self.set_type}, [{', '.join(self.items)}])"

class SetItem:
    def __init__(self, name, item_type, parent, image_path):
        self.name = name
        self.item_type = item_type
        self.parent = parent
        self.image_path = image_path
        self._image = None

    @property
    def image(self): # lazy loading of images when first accessed
        if self._image is None:
            try:
                self._image = Image.open(self.image_path)
            except FileNotFoundError:
                log(f"image for card {self.name} not found: {self.image_path}")
                self._image = None
        return self._image
    
    def __str__(self):
        return f"A {self.item_type.lower()} appeared: **{self.name.title()}**!\nset: {self.parent.name.title()}\nauthor: {self.parent.author}"

def init_sets():
    for folder in os.listdir(SetGroup.PATH):
        
        SetGroup(folder)

def reload_sets():
    global set_database
    log("~1reloading sets")
    set_database = []
    init_sets()

init_sets()