import os

from .tree_node import TreeNode
from .exceptions import InitException
from .utils import check_file_exists


class SimpleGit:
    """

    """
    SGIT_DIR = '.sgit'
    SGIT_OBJECTS_DIR = 'objects'
    SGIT_HEAD = 'HEAD'
    SGIT_FILES_DIR = 'objects/files'
    SGIT_ROOT_NODE = 'root_node'

    def __init__(self, root_dir):
        self.SGIT_ROOT_DIR = root_dir

    def init_cmd(self, args):
        """

        :param args:
        :return:
        """
        self._assert_init_is_possible()
        self._create_init_dir()

    def add_cmd(self, args):
        print 'add files', args

    def commit_cmd(self, args):
        print 'commit'

    def status_cmd(self, args):
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
        self._create_tree_node(filename=sgit_root_node_file, parent=None, files_meta=[])

        # HEAD file
        sgit_head_file = os.path.join(sgit_dir_abs, self.SGIT_HEAD)
        self._move_head_pointer(sgit_head_file, sgit_root_node_file)

    def _create_tree_node(self, filename, parent, files_meta):
        with open(filename, 'w') as tn_fd:
            tn_fd.write(TreeNode(parent, files_meta).to_json())

    def _move_head_pointer(self, sgit_head_file, tree_node_file_to_point):
        with open(sgit_head_file, 'w') as head_fd:
            head_fd.write(tree_node_file_to_point)
