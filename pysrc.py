#!/usr/bin/env python

# to enable tab completion, add (and uncomment) the next line to .bashrc
# complete -C 'pysrc --get-bash-completion' pysrc


import hashlib
import inspect
import os
import sys

from subprocess import check_output


h = hashlib.md5(os.path.realpath(sys.executable)).hexdigest()
module_cache_location = os.path.join(os.path.expanduser('~/.pysrc/'), h)


def ensure_dir():
    if not os.path.isdir(os.path.expanduser('~/.pysrc')):
        os.mkdir(os.path.expanduser('~/.pysrc'))


def update_module_cache():
    try:
        from bpython import importcompletion
    except:
        return False
    while importcompletion.find_coroutine():
        pass
    ensure_dir()
    with open(module_cache_location, 'w') as f:
        for mod in sorted(importcompletion.modules):
            f.write(mod)
            f.write('\n')


def log(*args):
    sys.stderr.write('\n')
    for arg in args:
        sys.stderr.write(repr(arg))
        sys.stderr.write(' ')
    sys.stderr.write('\n')
    sys.stderr.flush()


def complete(base, word, prev):
    if not os.path.exists(module_cache_location):
        msg = 'discovering modules...'
        sys.stderr.write(msg)
        sys.stderr.flush()
        update_module_cache()
        sys.stderr.write('\x1b[%dD' % len(msg) + ' '*len(msg) +
                         '\x1b[%dD' % len(msg))
        sys.stderr.flush()

    modules = set(open(module_cache_location).read().split('\n'))
    if word == '':
        for mod in sorted(set(m.split('.')[0] for m in modules)):
            print(mod)
        return
    matches = [m for m in modules if m.startswith(word)]
    if matches:
        for mod in matches:
            print(mod)
        return
    parts = word.split('.')

    mods = {}
    try:
        exec("import %s" % (parts[0],), mods)
    except ImportError:
        return
    for i, part in enumerate(parts[1:], start=1):
        modulename = '.'.join(parts[:i])
        if part == '':
            break
        try:
            exec("from %s import %s" % (modulename, part), mods)
        except ImportError:
            pass #log('could not import', part, 'from', modulename)
        else:
            pass #log('successfully imported', part, 'from', modulename)

    for name in dir(mods[parts[i-1]]):
        if name.startswith(part):
            print(modulename+'.'+name)


def un_pyc(filename):
    if filename.endswith('.pyc'):
        new = filename.replace('.pyc', '.py')
        if os.path.exists(new):
            return new
        else:
            raise ValueError("no source file found")
    return filename


def find(obj):
    x = None
    if '.' in obj:
        while obj.endswith('.'):
            obj = obj[:-1]
        root, last = obj.rsplit('.', 1)
        if sys.version_info[0] > 2:
            d = {}
            exec('from %s import %s as x' % (root, last), globals(), d)
            x= d['x']
        else:
            exec('from %s import %s as x' % (root, last))
    else:
        x = __import__(obj)
    return un_pyc(inspect.getfile(x))


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == []:
        print('usage: vimdiff $(pysource -p python3)')
        sys.exit()
    versions = []
    if '--update-cache' in args:
        update_module_cache()
        sys.exit()
    if args[0] == '--get-bash-completion':
        complete(*args[1:])
        sys.exit()
    while '-p' in args:
        spot = args.index('-p')
        version = args[spot + 1]
        args = args[:spot] + args[spot+2:]
        versions.append(version)
    if versions:
        for version in versions:
            sys.stdout.write(check_output([version, os.path.realpath(__file__)] + args))
    else:
        obj, = args
        print(find(obj))
