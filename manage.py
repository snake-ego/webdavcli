#!/usr/bin/env python3
import argparse
import logging
from logging.config import dictConfig
from os import path as op
from resources.commands import *
from resources.config import ConfigFromJSON

cfg = ConfigFromJSON()
dictConfig(cfg.logging) if cfg.get('logging') else None
logger = logging.getLogger()


def pull_commands(parser):
    parser.set_defaults(func=pull)
    parser.add_argument("filename", type=str, help="Name of remote file")
    parser.add_argument("-t", "--target", type=str, required=False, dest='target', help="Output directory")
    parser.add_argument("-d", "--decrypt", required=False, action='store_true', dest='decrypt', help="Decrypt file after uploads")
    parser.add_argument("--rm", required=False, action='store_true', dest='remove', help="Remove original file from server")


def push_commands(parser):
    parser.set_defaults(func=push)
    parser.add_argument("filepath", type=str, help="Upload file path")
    parser.add_argument("-e", "--encrypt", required=False, action='store_true', dest='encrypt', help="Encrypt file before upload")


def list_commands(parser):
    parser.set_defaults(func=ls)
    parser.add_argument("-m", "--mask", required=False, type=str, dest='mask', help="Filter server files by mask")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='webdavcli [-h]')
    subparsers = parser.add_subparsers(title="Commands", metavar='')
    pull_commands(subparsers.add_parser("pull", help="Get file from webdav server"))
    push_commands(subparsers.add_parser("push", help="Put file on webdav server"))
    list_commands(subparsers.add_parser("list", help="List all files on webdav server"))
    args = parser.parse_args()
    if hasattr(args, 'func'):
        runner = args.func
        params = vars(args)
        params.pop('func')
        runner(**params)
    else:
        parser.print_help()
