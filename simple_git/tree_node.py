import json


class TreeNode:
    def __init__(self, parent, files_meta):
        self.parent = parent
        self.files_meta = files_meta

    def to_json(self):
        me_json = {
            'parent': self.parent,
            'files_meta': self.files_meta
        }
        return json.dumps(me_json)

    def from_json(self, text):
        me_json = json.loads(text)
        self.parent = me_json['parent']
        self.files_meta = me_json['files_meta']
