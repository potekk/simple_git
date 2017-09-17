import os
import shutil

from .exceptions import InitException, SimpleGitRepositoryNotFoundException, IntegrityException
from .tree_node import TreeNode, FileState
from .utils import check_file_exists, sha1_file


class SimpleGit:
    """

    """
    SGIT_DIR = '.sgit'

    def __init__(self):
        pass

    def init_cmd(self, args):
        """
        Init simple git repository
        Create hidden directory named SGIT_DIR in project directory.
        Prevent double init
        """

        self._init_paths(args.cwd, True)
        self._assert_init_is_possible()
        self._create_init_dir()

    def add_cmd(self, args):
        """
        Add files to staging
        """

        self._init_paths(args.cwd)
        files_abs = [os.path.abspath(os.path.join(self.ACT_DIR, f)) for f in args.files]
        self._add_files_to_stag(files_abs)

    def commit_cmd(self, args):
        """

        :param _args:
        :return:
        """
        self._init_paths(args.cwd)
        self._commit()

    def status_cmd(self, args):
        """

        :param _args:
        :return:
        """
        self._init_paths(args.cwd)
        self._determine_status()

    def _init_paths(self, act_dir, is_init=False):
        self.ACT_DIR = act_dir
        self.SGIT_PROJECT_DIR = act_dir if is_init else self._find_root_dir(act_dir)
        self.SGIT_ROOT_DIR = os.path.join(self.SGIT_PROJECT_DIR, self.SGIT_DIR)
        self.SGIT_OBJECTS_DIR = os.path.join(self.SGIT_ROOT_DIR, 'objects')
        self.SGIT_HEAD = os.path.join(self.SGIT_ROOT_DIR, 'HEAD')
        self.SGIT_STAG = os.path.join(self.SGIT_ROOT_DIR, 'STAG')
        self.SGIT_FILES_DIR = os.path.join(self.SGIT_OBJECTS_DIR, 'files')
        self.SGIT_TREE_DIR = os.path.join(self.SGIT_OBJECTS_DIR, 'tree')
        self.SGIT_ROOT_NODE = os.path.join(self.SGIT_TREE_DIR, 'root_node')

    def _create_init_dir(self):
        os.mkdir(self.SGIT_ROOT_DIR)
        os.mkdir(self.SGIT_OBJECTS_DIR)
        os.mkdir(self.SGIT_FILES_DIR)
        os.mkdir(self.SGIT_TREE_DIR)

        self._create_tree_node(self.SGIT_ROOT_NODE)
        self._create_tree_node(self.SGIT_STAG, self.SGIT_ROOT_NODE)
        self._move_head_ptr(self.SGIT_ROOT_NODE)

    def _find_root_dir(self, act_dir):
        fs_root_dir = os.path.abspath(os.sep)
        while act_dir != fs_root_dir:
            if os.path.exists(os.path.join(act_dir, self.SGIT_DIR)):
                return act_dir
            act_dir = os.path.dirname(act_dir)

        raise SimpleGitRepositoryNotFoundException

    def _assert_init_is_possible(self):
        if check_file_exists(os.path.join(self.SGIT_ROOT_DIR, self.SGIT_DIR)):
            raise InitException()

    def _create_tree_node(self, filename, parent=None, files_meta=None):
        with open(filename, 'w') as tn_fd:
            tn_fd.write(TreeNode(parent, files_meta).dumps())

    def _move_head_ptr(self, dst_ptr):
        with open(self.SGIT_HEAD, 'w') as head_fd:
            head_fd.write(dst_ptr)

    def _add_files_to_stag(self, files):
        stag_node = TreeNode.load(self.SGIT_STAG)
        self._add_files_rec(files, stag_node)
        stag_node.dump(self.SGIT_STAG)

    def _add_files_rec(self, files, sgit_node):
        all_add_files = []
        for add_file in files:
            if os.path.isdir(add_file):
                for nested_dir, _, nested_files in os.walk(add_file):
                    for nested_f in nested_files:
                        nested_add_file_abs = os.path.join(nested_dir, nested_f)
                        all_add_files.append(nested_add_file_abs)
            else:
                all_add_files.append(add_file)

        for add_file in all_add_files:
            sgit_node.add_file_to_node(add_file, self.SGIT_FILES_DIR)

    def _commit(self):
        if self._staging_changed():
            new_node_filename = self._get_node_name()
            shutil.copyfile(self.SGIT_STAG, new_node_filename)

            self._update_staging_file(new_node_filename)
            self._move_head_ptr(new_node_filename)

    def _update_staging_file(self, new_node_filename):
        stag_node = TreeNode.load(self.SGIT_STAG)
        stag_node.parent = new_node_filename
        stag_node.dump(self.SGIT_STAG)

    def _staging_changed(self):
        stag_node = TreeNode.load(self.SGIT_STAG)
        prev_commit_node = TreeNode.load(stag_node.parent)

        return stag_node.files_meta != prev_commit_node.files_meta

    def _get_node_name(self):
        new_node_hash = sha1_file(self.SGIT_STAG)
        return os.path.join(self.SGIT_TREE_DIR, new_node_hash)

    def _determine_status(self):
        head_node = self._get_head_node()
        stag_node = TreeNode.load(self.SGIT_STAG)
        files_status = self._get_files_status(head_node.files_meta, stag_node.files_meta)
        self._print_status(files_status)

    def _get_files_status(self, head_files_meta, stag_files_meta):
        project_file_list = self.list_project_files(self.SGIT_PROJECT_DIR, [self.SGIT_DIR])
        status_map = {}
        for filename in project_file_list:
            f_hash = sha1_file(filename)
            if filename in head_files_meta:
                f_status = self.handle_indexed_file(filename, f_hash, head_files_meta, stag_files_meta)
            else:
                f_status = self.handle_not_indexed_file(filename, f_hash, stag_files_meta)

            status_map[filename] = f_status
        return status_map

    def handle_indexed_file(self, filename, f_hash, head_files_meta, stag_files_meta):
        if filename not in stag_files_meta:
            # Staging derives indexed files from last commit
            raise IntegrityException

        h_hash = head_files_meta[filename]['hash']
        s_hash = stag_files_meta[filename]['hash']
        if f_hash == s_hash:
            if f_hash == h_hash:
                # file does not change
                f_status = FileState.THE_SAME
            else:
                # file differ from last commit but staged
                f_status = FileState.STAGED
        else:
            # file modified
            f_status = FileState.MODIFIED

        return f_status

    def handle_not_indexed_file(self, filename, f_hash, stag_files_meta):
        if filename in stag_files_meta:
            s_hash = stag_files_meta[filename]['hash']
            if f_hash == s_hash:
                # new file added to staging
                f_status = FileState.STAGED
            else:
                # new file added to staging and later modified
                f_status = FileState.MODIFIED
        else:
            # new file
            f_status = FileState.NEW
        return f_status

    def _print_status(self, files_status):
        for f, status in files_status.iteritems():
            relative_filepath = os.path.relpath(f)
            if status == FileState.NEW:
                print relative_filepath, "(new file)"
            elif status == FileState.STAGED:
                print relative_filepath, "(staged file)"
            elif status == FileState.MODIFIED:
                print relative_filepath, "(modified file)"

    def list_project_files(self, directory, exclude):
        all_files = []
        for f in os.listdir(directory):
            if f in exclude:
                continue  # skip excluded files
            f_abs = os.path.join(directory, f)
            if os.path.isdir(f_abs):
                all_dir_files = self.list_project_files(f_abs, [])
                all_files.extend(all_dir_files)
            else:
                all_files.append(f_abs)
        return all_files

    def _get_head_node(self):
        with open(self.SGIT_HEAD) as f_head:
            head_node_filename = f_head.readline()
            return TreeNode.load(head_node_filename)
