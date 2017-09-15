import argparse

import os

from .simple_git import SimpleGit


def _init_arg_parser(cmd_handler):
    parser = argparse.ArgumentParser(prog='git', description='Simple Git')
    subparsers = parser.add_subparsers()

    # init cmd parser
    parser_init = subparsers.add_parser('init', help='Initialize simple git repository')
    parser_init.set_defaults(func=cmd_handler.init_cmd)

    # add cmd parser
    parser_add = subparsers.add_parser('add', help='Add file(s) to repository')
    parser_add.add_argument('files', nargs='+')
    parser_add.set_defaults(func=cmd_handler.add_cmd)

    # commit cmd parser
    parser_commit = subparsers.add_parser('commit', help='Commit changes')
    parser_commit.set_defaults(func=cmd_handler.commit_cmd)

    # status cmd parser
    parser_status = subparsers.add_parser('status', help='Show status of repository')
    parser_status.set_defaults(func=cmd_handler.status_cmd)

    return parser


def main():
    """
    The main routine
    """
    sgit_root_dir = os.getcwd()
    sgit = SimpleGit(sgit_root_dir)

    parser = _init_arg_parser(sgit)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
