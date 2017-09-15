import os

import shutil

from .tree_node import TreeNode
from .exceptions import InitException
from .utils import check_file_exists, sha1_file


class SimpleGit:
    """

    """
    SGIT_DIR = '.sgit'
    SGIT_OBJECTS_DIR = 'objects'
    SGIT_HEAD = 'HEAD'
    SGIT_STAG = 'STAG'
    SGIT_FILES_DIR = 'objects/files'
    SGIT_ROOT_NODE = 'root_node'

    def __init__(self, root_dir):
        self.SGIT_ROOT_DIR = root_dir

    def init_cmd(self, args):
        """

        :param args:
        :return:
        """
        #self._assert_init_is_possible()
        self._create_init_dir()

    def add_cmd(self, args):
        """

        :param args:
        :return:
        """
        files_abs = [os.path.join(self.SGIT_ROOT_DIR, f) for f in args.files]
        self.add_files_to_stag(files_abs)
        print files_abs

    def commit_cmd(self, args):
        """

        :param args:
        :return:
        """
        self.commit()

    def status_cmd(self, args):
        """

        :param args:
        :return:
        """
        print 'status'

    def _assert_init_is_possible(self):
        if check_file_exists(os.path.join(self.SGIT_ROOT_DIR, self.SGIT_DIR)):
            raise InitException()

    def _create_init_dir(self):
        # .sgit dir
        sgit_dir_abs = os.path.join(self.SGIT_ROOT_DIR, self.SGIT_DIR)
        os.mkdir(sgit_dir_abs)

        # objects dir
        sgit_objects_dir_abs = os.path.join(sgit_dir_abs, self.SGIT_OBJECTS_DIR)
        os.mkdir(sgit_objects_dir_abs)

        # files dir
        sgit_files_dir_abs = os.path.join(sgit_dir_abs, self.SGIT_FILES_DIR)
        os.mkdir(sgit_files_dir_abs)

        # .init file
        sgit_root_node_file = os.path.join(sgit_objects_dir_abs, self.SGIT_ROOT_NODE)
        self._create_tree_node(sgit_root_node_file)

        # STAG file
        sgit_stag_file = os.path.join(sgit_dir_abs, self.SGIT_STAG)
        self._create_tree_node(sgit_stag_file, sgit_root_node_file)

        # HEAD file
        sgit_head_file = os.path.join(sgit_dir_abs, self.SGIT_HEAD)
        self._move_head_pointer(sgit_head_file, sgit_root_node_file)

    def _get_stag_filename(self):
        return os.path.join(self.SGIT_ROOT_DIR, self.SGIT_DIR, self.SGIT_STAG)

    def _get_object_path(self):  # TODO change everywhere
        return os.path.join(self.SGIT_ROOT_DIR, self.SGIT_DIR, self.SGIT_OBJECTS_DIR)

    def _create_tree_node(self, filename, parent=None, files_meta=None):
        with open(filename, 'w') as tn_fd:
            tn_fd.write(TreeNode(parent, files_meta).dumps())

    def _move_head_pointer(self, sgit_head_file, tree_node_file_to_point):
        with open(sgit_head_file, 'w') as head_fd:
            head_fd.write(tree_node_file_to_point)

    def add_files_to_stag(self, files):
        stag_filename = self._get_stag_filename()
        stag_node = TreeNode.load(stag_filename)
        self._add_files_rec(files, stag_node)
        stag_node.dump(stag_filename)

    def _add_files_rec(self, files, tree_node):
        files_to_add = []
        for f in files:
            if os.path.isdir(f):
                for base_dir, _, dir_files in os.walk(f):
                    for dir_file in dir_files:
                        new_file_abs = os.path.join(base_dir, dir_file)
                        files_to_add.append(new_file_abs)
            else:
                files_to_add.append(f)

        map(lambda x: tree_node.add_file(x), files_to_add)

    def commit(self):
        if self.stag_changed():
            stag_filename = self._get_stag_filename()
            node_hash = sha1_file(stag_filename)
            node_filename = os.path.join(self._get_object_path(), node_hash)
            print 'AAA', stag_filename, node_filename
            shutil.copyfile(stag_filename, node_filename)

            # update parent pointer
            stag_node = TreeNode.load(stag_filename)
            stag_node.parent = node_filename
            stag_node.dump(stag_filename)


    def stag_changed(self):
        return True  # TODO
