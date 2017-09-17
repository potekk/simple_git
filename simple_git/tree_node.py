import gzip
import json

import os

import shutil

from .utils import sha1_file


class FileState:
    """
    Enum for file states
    """
    NEW = 1
    MODIFIED = 2
    STAGED = 3
    THE_SAME = 4


class TreeNode:
    IGNORE_DIRS = ['.sgit']

    def __init__(self, parent=None, files_meta=None):
        self.parent = parent
        self.files_meta = files_meta or {}

    def create_file_meta(self, filename, file_hash, fobj_filename):
        file_meta = {
            'filename': filename,
            'hash': file_hash,
            'fobj_filename': fobj_filename,
        }
        return file_meta

    def dump(self, filename):
        me_json = {
            'parent': self.parent,
            'files_meta': self.files_meta
        }
        with open(filename, 'w') as fd:
            json.dump(me_json, fd, indent=2)

    def dumps(self):
        me_json = {
            'parent': self.parent,
            'files_meta': self.files_meta
        }
        return json.dumps(me_json, indent=2)

    @staticmethod
    def loads(text):
        me_json = json.loads(text)
        parent = me_json['parent']
        files_meta = me_json['files_meta']
        return TreeNode(parent, files_meta)

    @staticmethod
    def load(filename):
        with open(filename) as f:
            return TreeNode.loads(f.read())

    def determine_files_changes(self, prev_node, root_directory):
        file_states = {}
        for base_dir, _, filename_list in os.walk(root_directory):
            for filename in filename_list:
                filename_abs = os.path.join(base_dir, filename)
                file_states['filename'] = self.get_file_state(prev_node, filename_abs)

        return file_states

    @staticmethod
    def get_file_state(prev_node, filename_abs):
        if filename_abs not in prev_node.file_meta:
            return FileState.NEW
        prev_file_meta = prev_node.file_meta['filename_abs']
        file_hash = sha1_file(filename_abs)
        if prev_file_meta['hash'] == file_hash:
            return FileState.THE_SAME
        else:
            return FileState.MODIFIED

    def add_file(self, filename):
        file_hash = sha1_file(filename)
        if filename not in self.files_meta:
            self.create_new_file_obj(file_hash, filename)
        else:
            prev_file_meta = self.files_meta[filename]
            if prev_file_meta['hash'] == file_hash:
                pass  # The files match
            else:
                os.unlink(prev_file_meta['fobj_filename'])
                self.create_new_file_obj(file_hash, filename)

    def create_new_file_obj(self, file_hash, filename, obj_path):
        stored_file = self.store_file(filename, file_hash, obj_path)
        file_meta = self.create_file_meta(filename, file_hash, stored_file)
        self.update_files_meta(filename, file_meta)

    def store_file(self, filename, file_hash, obj_path):
        base_dir = obj_path
        out_filename_abs = os.path.join(base_dir, file_hash)
        with gzip.open(out_filename_abs, 'w') as f_out:
            with open(filename) as f_in:
                shutil.copyfileobj(f_in, f_out)
        return out_filename_abs

    def update_files_meta(self, filename, file_meta):
        self.files_meta[filename] = file_meta
