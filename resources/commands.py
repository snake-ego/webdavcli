import os
from os import path as op
from .config import ConfigFromJSON
from gnupg import GPG
from easywebdav import connect
from fnmatch import fnmatch

__all__ = ['pull', 'push', 'list']


def push(filepath, encrypt=None):
    cfg = ConfigFromJSON(section='webdav')
    webdav = connect(cfg.address,
                     username=cfg.get('user'),
                     password=cfg.get('password'),
                     protocol=cfg.get('protocol', 'http'))
    if encrypt:
        filepath = encrypt_file(filepath)

    filename = op.basename(filepath)
    response = webdav.upload(filepath, op.join(cfg.get("root", "."), filename))
    if 199 < response.status_code < 300 and encrypt:
        os.remove(filepath)

    return response


def pull(filename, target=None, decrypt=None, remove=None):
    target = target if isinstance(target, str) else './'
    cfg = ConfigFromJSON(section='webdav')
    webdav = connect(cfg.address,
                     username=cfg.get('user'),
                     password=cfg.get('password'),
                     protocol=cfg.get('protocol', 'http'))

    if not op.exists(target):
        os.makedirs(target)

    filepath = op.join(cfg.get('root', '.'), filename)
    targetpath = op.join(target, op.basename(filepath))
    response = webdav.download(filepath, targetpath)
    if decrypt:
        targetpath = decrypt_file(targetpath, remove_source=True)
    if remove:
        webdav.delete(filepath)
    return targetpath


def ls(mask=None):
    cfg = ConfigFromJSON(section='webdav')
    webdav = connect(cfg.address,
                     username=cfg.get('user'),
                     password=cfg.get('password'),
                     protocol=cfg.get('protocol', 'http'))
    files = webdav.ls(remote_path=cfg.get('root', '.'))
    alldata = list(filter(lambda f: f, [i.name.lstrip(cfg.get('root', '.')) for i in files]))
    if isinstance(mask, str):
        out = list(filter(lambda f: fnmatch(f, mask), alldata))
    else:
        out = alldata

    return [print(i) for i in out] or out


def encrypt_file(filename):
    cfg = ConfigFromJSON(section='gpg')

    if not op.exists(filename):
        raise ValueError(f'File {filename} not exisit')

    gpg = GPG()
    target = ".".join([filename, 'gpg'])
    with open(filename, 'rb') as f:
        enc = gpg.encrypt_file(f, None, symmetric=True, passphrase=cfg.passphrase, output=target)
    if not enc.ok:
        raise RuntimeError(enc.status)

    return target


def decrypt_file(filename, remove_source=None):
    cfg = ConfigFromJSON(section='gpg')

    if not op.exists(filename):
        raise ValueError(f'File {filename} not exisit')

    gpg = GPG()
    target = filename.rstrip('.gpg')
    with open(filename, 'rb') as f:
        dec = gpg.decrypt_file(f, passphrase=cfg.passphrase, output=target)
    if not dec.ok:
        raise RuntimeError(dec.status)

    if remove_source:
        os.remove(filename)

    return target
