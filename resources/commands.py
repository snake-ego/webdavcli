import os
from os import path as op
from .config import ConfigFromJSON
from gnupg import GPG
from easywebdav import connect


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


def pull(filepath, target=None, decrypt=None):
    target = target if isinstance(target, str) else './'
    if not op.exists(target):
        os.makedirs(target)

    cfg = ConfigFromJSON(section='webdav')
    webdav = connect(cfg.address,
                     username=cfg.get('user'),
                     password=cfg.get('password'),
                     protocol=cfg.get('protocol', 'http'))

    filename = op.basename(filepath)
    targetpath = op.join(target, filename)
    response = webdav.download(filepath, targetpath)
    if decrypt:
        targetpath = decrypt_file(targetpath, remove_source=True)

    return targetpath


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
