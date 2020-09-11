#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################################
# FILE: (PH(p)y)create
# AUTHOR: R-Logik, Deutschland. https://github.com/RLogik/phpytex
# CREATED: 27.07.2020
# LAST CHANGED: 10.09.2020
# VERSION: 1·1·4
# NOTES:
#
#     Installation:
#     ~~~~~~~~~~~~~
#     1. modify the first 2 lines of this script if necessary.
#     2. place this in a folder, which is in the PATH variable (or extend this)
#     3. remove the .py-extension
#     4. run
#            sudo chmod +x phpycreate
#        in bash. The command is now available everywhere on your system.
#     5. Call
#            phpycreate --help
#     to see the instructions for usage
#     or https://github.com/RLogik/phpytex >> consult README.md
#
##############################################################################

import sys;
sys.tracebacklimit = 0; ## disables traceback.
import os;
import re;
from yaml import add_constructor;
from yaml import load;
from yaml import Loader;
from yaml import FullLoader;
from typing import Any;
from typing import Dict;
from typing import List;
from typing import Tuple;
from typing import Union;
from subprocess import Popen;
from gitignore_parser import parse_gitignore;

console_quiet = False;
PHPYCREATE_VERSION = '1·1·4';
FILE_EXT_PPTSTRUCT = r'\.phpycreate\.(yml|yaml)';
FILE_EXT_PPTIGNORE = r'\.phpycreate\.ignore';

# --------------------------------------------------------------------------------
# PRIMARY METHOD
# --------------------------------------------------------------------------------

def main():
    global FILE_EXT_PPTSTRUCT;
    global console_quiet;

    tokens, _ = parse_cli_args(sys.argv[1:]);
    show_version = ('version' in tokens) or ('v' in tokens);
    show_help = ('help' in tokens) or ('man' in tokens);
    console_quiet = ('q' in tokens);
    accept_current_directory = ('d' in tokens);
    recursive_creation = ('r' in tokens);

    if show_version:
        display_version();
        return;

    if show_help:
        display_help();
        return;

    message_to_console('');
    message_to_console('----------------------');
    message_to_console('|   \033[32;1m(PH(p)y)create\033[0m   |');
    message_to_console('----------------------');

    path_current = os.getcwd();
    try:
        if not accept_current_directory:
            success = set_wk_dir();

        path_wd = os.getcwd();
        setup_yaml_reader();
        success, obj = get_structure_yamls(path_wd, recursive_creation);
        if not success:
            raise FileExistsError('Could not find \'{}\' file in the project directory!'.format(FILE_EXT_PPTSTRUCT));

        message_to_console('');
        message_to_console('Generating project structure...');
        for path, struct in obj:
            crunch_structure_yaml(path, struct, path == path_wd);
        message_to_console('...project structure created.');
    except BaseException as e:
        os.chdir(path_current);
        raise e;
    finally:
        os.chdir(path_current);

    message_to_console('');
    return;

# --------------------------------------------------------------------------------
# SECONDARY METHODS
# --------------------------------------------------------------------------------

def display_version():
    message = [
        '''''',
        '''You are using \033[32m\033[1m(Ph(P)y)create\033[0m version \033[96m\033[1m{}\033[0m.'''.format(PHPYCREATE_VERSION),
        '''Created by \033[91mRLogik\033[0m, 27.07.2020.''',
        '''''',
    ];
    print('\n'.join(message));
    return;

def display_help():
    message = [
        '''''',
        '''\033[32m\033[1m(Ph(P)y)create\033[0m: usage''',
        '''---------------------''',
        '''''',
        '''This script complements the \033[32m\033[1m(Ph(P)y)TeX\033[0m compiler/transpiler. Its purpose is to enable users to generate latex/phpytex project structures rapidly using a single, manageable configuration file.''',
        '''To use it, first add the following files to your project folder:''',
        '''''',
        '''    \033[96mproject folder''',
        '''      |''',
        '''      ·''',
        '''      ·''',
        '''      |____ .phpycreate.yml''',
        '''      |____ .phpycreate.ignore\033[0m''',
        '''''',
        '''In \033[1mphpycreate.yml\033[0m you may add for example the following parts:''',
        '''''',
        '''    -------- example of ./\033[1mphpycreate.yml\033[0m ----''',
        '''    | \033[94mignore: \033[93mbackwards \033[32m# alternative - true, false (default if empty)\033[0m''',
        '''    | \033[94mstamp\033[0m:\033[93m\033[0m''',
        '''    |   \033[94mfile\033[0m: \033[93mstamp.tex\033[0m''',
        '''    |   \033[94moverwrite\033[0m: \033[93mtrue\033[0m''',
        '''    |   \033[94moptions\033[0m:\033[93m\033[0m''',
        '''    |     \033[94mauthor\033[0m: \033[93m<author> or [<list of authors>]\033[0m''',
        '''    |     \033[94mcreated\033[0m: \033[93m<date as string>\033[0m''',
        '''    |     \033[94mtitle\033[0m: \033[93m<title of document>\033[0m''',
        '''    |     \033[32m#... these attributes can be arbitrarily chosen, but are limited to a single level.\033[0m''',
        '''    | \033[94mcompile\033[0m: \033[93m\033[32m# will only be parsed if .yml file is at the root level\033[0m''',
        '''    |   \033[94mfile\033[0m: \033[93mstart.sh\033[0m''',
        '''    |   \033[94moverwrite\033[0m: \033[93mtrue\033[0m''',
        '''    |   \033[94moptions\033[0m:\033[93m\033[0m''',
        '''    |     \033[94minput\033[0m: \033[93mroot.tex\033[0m''',
        '''    |     \033[94moutput\033[0m: \033[93mmain.tex\033[0m''',
        '''    |     \033[94mdebug\033[0m: \033[93mfalse\033[0m''',
        '''    |     \033[94mcompile-latex\033[0m: \033[93mTRUE\033[0m''',
        '''    |     \033[94minsert-bib\033[0m: \033[93mtrue\033[0m''',
        '''    |     \033[94mcomments\033[0m: \033[93mauto\033[0m \033[32m# alternative - true, false\033[0m''',
        '''    |     \033[94mshow-structure\033[0m: \033[93mtrue\033[0m''',
        '''    |     \033[94mtabs\033[0m: \033[93mfalse\033[0m''',
        '''    |     \033[94mspaces\033[0m: \033[93m4\033[0m''',
        '''    |     \033[94mseed\033[0m: \033[93m<some seed for random number generation>\033[0m''',
        '''    | \033[94mfiles\033[0m: \033[93m[root.tex]\033[0m''',
        '''    | \033[94mfolders\033[0m:\033[93m\033[0m''',
        '''    |   \033[94msrc\033[0m:\033[93m\033[0m''',
        '''    |   \033[94mimg\033[0m:\033[93m\033[0m''',
        '''    |   \033[94mfront\033[0m:\033[93m\033[0m''',
        '''    |   \033[94mbody\033[0m:\033[93m\033[0m''',
        '''    |     \033[94mfolders\033[0m:\033[93m\033[0m''',
        '''    |       \033[94mintroduction\033[0m:\033[93m\033[0m''',
        '''    |       \033[94mliterature-review\033[0m:\033[93m\033[0m''',
        '''    |           \033[94mname\033[0m: \033[93mlit-review \033[32m# by default the key is used, unless a 'name:' attrbute is given.\033[0m''',
        '''    |           \033[94mfolders\033[0m: \033[93m\033[32m# you can nest under 'folders' as much as you like.\033[0m''',
        '''    |             \033[94mclassical-results:\033[0m:\033[93m\033[0m''',
        '''    |             \033[94mnon-classical-results\033[0m:\033[93m\033[0m''',
        '''    |       \033[94manalysis\033[0m:\033[93m\033[0m''',
        '''    |   \033[94mback\033[0m:\033[93m\033[0m''',
        '''    |   \033[94mappendix\033[0m:\033[93m\033[0m''',
        '''    |     \033[94mfiles\033[0m: \033[93m[references.bib]\033[0m''',
        '''    -------- end of example file ------------''',
        '''''',
        '''Now, in bash in your project folder simply call''',
        '''''',
        '''    \033[1mphpycreate [--version] [--help] [-d] [-q] [-r]\033[0m''',
        '''''',
        '''to generate the project structure. The arguments are as follows:''',
        '''''',
        '''     \033[1m--version\033[0m ⟹  show the version of (Ph(P)y)create.''',
        '''     \033[1m--help\033[0m ⟹  show this help file.''',
        '''     \033[1m-d\033[0m ⟹  skip the prompt which verifies the working directory.''',
        '''     \033[1m-q\033[0m ⟹  silent mode.''',
        '''     \033[1m-r\033[0m ⟹  recursively parse all phpycreate.yml files in project.''',
        '''''',
        '''\033[92mNote 1\033[0m) that the instructions in the generating file are 'safe', that is''',
        '''    no existing files will be overwritten or recreated.''',
        '''''',
        '''\033[92mNote 2\033[0m) You can add phpycreate.yaml files to subfolders. If the argument \033[1m-r\033[0m is used, then all of them will be interpreted with respect to their locations.''',
        '''''',
        '''    \033[1mExceptions:\033[0m''',
        '''    ~~~~~~~~~~~''',
        '''      - files in phpycreate.ignore;''',
        '''      - .yml files with the 'ignore: true' attribute.''',
        '''      - .yml files with the 'ignore: backwards' attribute,''',
        '''         provided this is not in the root folder.''',
        '''''',
        '''    \033[1mNote:\033[0m although redundant in your project, you should add 'ignore: backwards to the root phpycreate.yml file, if you want to prevent others from parsing your create-file when they integrate your project in a subfolder of theirs.''',
        '''''',
        '''\033[92mNote 2a\033[0m) the 3rd party package we use for parsing .ignore is not very robust. In our experience the negation commands (!) are not parsed correctly, as .gitignore does. Until this is fixed, we recommend using very simple exclusion-only rules.''',
        '''''',
        '''\033[92mNote 3\033[0m) The 'compile' part of the yaml file creates an otherwise cumbersome phpytex-command, custom designed for your project. Calling this one script, allows you to compile your project easier with phpytex.''',
        '''''',
        '''\033[92mNote 3a\033[0m) The exceptions to this are the file generated by the 'compile' and 'stamp' part of the yaml. If the user provides the 'overwrite: true' aspect respectively, then these files will be overwrittem. By default no value is intrepretted as 'overwrite: false'.''',
        '''''',
        '''Thank you for using \033[32m\033[1m(Ph(P)y)create\033[0m! Enjoy!.''',
        '''    ~~~~ \033[91mRLogik\033[0m, 2020''',
        '''''',
        '''P.S: A better version of \033[32m\033[1m(Ph(P)y)TeX\033[0m is in the works!''',
        '''''',
    ];
    print('\n'.join(message));
    return;

def set_wk_dir():
    message_to_console('\nSetting project directory...', force=True);
    path = os.getcwd();
    while True:
        message_to_console('  The director of the project is\n    \'{}\''.format(path), force=True);
        answer = False;
        while True:
            confirm = input('  Is this correct? y/n\n    > ');
            # accept empty response (enter key) as yes:
            if re.match(r'^(?:|1|y|yes|j|ja)$', confirm, re.IGNORECASE):
                answer = True;
                break;
            elif re.match(r'^(?:0|n|no|nein)$', confirm, re.IGNORECASE):
                answer = False;
                break;
        if answer:
            break;
        while True:
            path = input('  Please enter the correct path:\n    > ');
            if not (os.path.isdir(path) and os.path.exists(path)):
                message_to_console('  Path does not exist or is not a path to a folder!', force=True);
                continue;
            try:
                path = os.path.abspath(path);
                break;
            except:
                message_to_console('  Bad format! Try again!', force=True);
    os.chdir(path);
    message_to_console('...project directory confirmed.', force=True);
    return;

# adds special constructors to yaml
def setup_yaml_reader():
    def join_constructor(loader: Loader, node):
        values = loader.construct_sequence(node, deep=True);
        try:
            sep   = str(values[0]);
            parts = [str(_) for _ in values[1]];
            # value = sep.join(parts);
            value = None;
            for part in parts:
                if value is None:
                    value = part;
                else:
                    value += sep + part;
            return value or '';
        except:
            return '';

    def eval_constructor(loader: Loader, node):
        value = loader.construct_sequence(node, deep=True);
        try:
            expr = value[0];
        except:
            expr = None;
        return EvalType(expr);

    add_constructor(u'!join', join_constructor);
    add_constructor(u'!eval', eval_constructor);
    return;

def get_structure_yamls(path: str, recursive: bool) -> Tuple[bool, List[Tuple[str, Dict[str, Any]]]]:
    global FILE_EXT_PPTSTRUCT;
    global FILE_EXT_PPTIGNORE;

    pattern_create = FILE_EXT_PPTSTRUCT;
    regex_create = re.compile(pattern_create);
    pattern_ignore = FILE_EXT_PPTIGNORE;
    regex_ignore = re.compile(pattern_ignore);

    match_ignore = None;
    # extract ignore file (if one exists)
    for fname in os.listdir(path):
        if regex_ignore.match(fname):
            match_ignore = parse_gitignore(fname, base_dir=path);
            break;

    structures = [];
    for subpath, _, files in os.walk(path):
        if not recursive and not (subpath == path):
            continue;
        if not(match_ignore is None) and match_ignore(subpath):
            continue;
        files = [fname for fname in files if regex_create.match(fname)];
        if len(files) == 0:
            if subpath == path:
                raise FileNotFoundError('No file matching the pattern \'{}\' could be found in the project directory!'.format(pattern_create));
        else:
            fname = files[0];
            # extract instruction for structure from yml file:
            fname_full = fname;
            try:
                fname_full = os.path.join(subpath, fname);
                with open(fname_full, 'r') as fp:
                    struct = load(fp, Loader=FullLoader);
            except:
                raise FileExistsError('Could not open file `{}`.'.format(fname_full));
            force_ignore = get_dict_value(struct, 'ignore', typ=bool, default=False);
            if force_ignore == True or (not subpath == path and force_ignore == 'backwards'):
                continue;
            structures.append((subpath, struct));
        if not recursive and (subpath == path):
            break;

    return True, structures;

def crunch_structure_yaml(path: str, struct: Dict[str, Any], is_root: bool):
    # create files:
    files = get_dict_value(struct, 'files', typ=[list, dict], default=[]);
    for _, fname, _ in get_names(files):
        make_file_if_not_exists(fname, path);

    # create folders recursively:
    folders = get_dict_value(struct, ['folders', 'components'], typ=dict, default={});
    for _, dir_name, struct_ in get_names(folders):
        make_dir_if_not_exists(dir_name, path);
        create_folders(dir_name, struct_ or {}, path=path);

    # if the instructions exist, create and fill the stamp file:
    fname      = get_dict_value(struct, 'stamp', 'file', typ=str, default=None);
    file_stamp = fname;
    if isinstance(fname, str):
        fexists   = make_file_if_not_exists(fname, path);
        overwrite = get_dict_value(struct, 'stamp', 'overwrite', typ=bool, default=False);
        if not fexists or overwrite:
            options = get_dict_value(struct, 'stamp', 'options', typ=dict, default={});
            lines   = create_stamp(options);
            write_lines(lines, fname, path);

    # if the instructions exist, create and fill the parameters file:
    fname = get_dict_value(struct, 'parameters', 'file', typ=str, default=None);
    if isinstance(fname, str):
        fexists   = make_file_if_not_exists(fname, path);
        overwrite = get_dict_value(struct, 'parameters', 'overwrite', typ=bool, default=False);
        if not fexists or overwrite:
            options = get_dict_value(struct, 'parameters', 'options', typ=dict, default={});
            lines   = create_parameters(options);
            write_lines(lines, fname, path);

    if not is_root:
        return;

    # ONLY if at root level: create and fill compile-script:
    options     = get_dict_value(struct, 'compile', 'options', default=None);
    fname       = get_dict_value(struct, 'compile', 'file', typ=str, default=None);
    to_stdout   = get_dict_value(struct, 'compile', 'stdout', typ=bool, default=False);
    file_input  = get_dict_value(options, ['input', 'root'], typ=str, default=None);
    file_output = get_dict_value(options, 'output', typ=str, default=None);
    overwrite   = get_dict_value(struct, 'compile', 'overwrite', default=False);
    if (to_stdout or isinstance(fname, str)) and isinstance(file_input, str) and isinstance(file_output, str):
        command = create_startscript(
            input          = file_input,
            stamp          = file_stamp,
            output         = file_output,
            show_python    = get_dict_value(options, ['debug', 'show-python'],        typ=bool,                  default=False),
            compile_latex  = get_dict_value(options, ['latex', 'compile-latex'],      typ=bool,                  default=True),
            insert_bib     = get_dict_value(options, ['insert-bib'],                  typ=bool,                  default=False),
            latex_comments = get_dict_value(options, ['latex-comments', 'comments'],  typ=[True, False, 'auto'], default='auto'),
            silent         = not
                             get_dict_value(options, ['show-tree', 'show-structure'], typ=bool,                  default=True),
            seed           = get_dict_value(options, ['seed'],                        typ=int,                   default=None),
            tabs           = get_dict_value(options, ['tabs'],                        typ=bool,                  default=False),
            spaces         = get_dict_value(options, ['spaces'],                      typ=int,                   default=4),
            max_length     = get_dict_value(options, ['max-length', 'maxlength'],     typ=int,                   default=10000),
        );
        if isinstance(fname, str):
            fexists = make_file_if_not_exists(fname, path);
            if not fexists or overwrite:
                write_lines([r'#!/bin/bash', '', command +';'], fname);
        if to_stdout:
            print(command);
    return;

def create_stamp(options: dict) -> List[str]:
    lines = [];
    border = r'%% ' + '*'*80;

    max_tag_length = max([0] + [len(key) for key in options]);
    for key in options:
        value = options[key];
        tag = key.upper();
        line = r'%% ' + tag + r':';
        if isinstance(value, str):
            value = re.split('\n', str(value));
        elif isinstance(value, (int, float, bool)):
            value = [str(value)];
        if isinstance(value, list) and len(value) == 1:
            line += ' '*(1 + max_tag_length - len(tag)) + str(value[0]);
        elif isinstance(value, list) and len(value) > 1:
            indent = '\n' + r'%% ' + ' '*4;
            line_ = [''];
            line_ += [u for u in value if isinstance(u, str)];
            line += indent.join(line_);
        else:
            line += ' '*(1 + max_tag_length - len(tag)) + r'—';
        lines.append(line);
    if len(lines) > 0:
        lines = [border] + lines + [border];

    return lines;

def create_parameters(options: dict) -> List[str]:
    lines = [];
    for key in options:
        value = to_python_string(options[key]);
        if not isinstance(value, str):
            continue;
        lines += ['<<< set {} = {}; >>>'.format(key, value)];
    return lines;

def create_startscript(
    input: str,
    stamp: Union[str, None],
    output: str,
    show_python: bool,
    compile_latex: bool,
    insert_bib: bool,
    latex_comments: Union[str, bool],
    silent: bool,
    seed: Union[str, int, None],
    tabs: bool,
    spaces: int,
    max_length: int
) -> str:
    # CREATE PHPYTEX COMMAND:
    command = ['phpytex'];
    command += ['-i', input];
    # add stamp file?
    if isinstance(stamp, str):
        command += ['-head', stamp];
    command += ['-o', output];
    # debug? compile latex?
    if show_python:
        command += ['-debug'];
    elif not compile_latex:
        command += ['-no-compile'];
    # insert .bib contents into output file?
    if insert_bib:
        command += ['-insert-bib'];
    # handling of latex_comments:
    if latex_comments == 'auto':
        command += ['-no-comm-auto'];
    elif latex_comments == False:
        command += ['-no-comm'];
    # show tree structure in output?
    if silent:
        command += ['-silent'];
    # add seed?
    if isinstance(seed, (int, str)):
        command += ['-seed', str(seed)];
    # add max length?
    if max_length > 0:
        command += ['-max-length', str(max_length)];
    # tabs or spaces
    if tabs:
        command += ['-tabs'];
    else:
        command += ['-spaces', str(spaces)];
    return ' '.join(command);

def create_folders(dir_name: str, struct: dict, path: str):
    subpath = os.path.join(path, dir_name);

    # add any files demanded:
    files = get_dict_value(struct, 'files', typ=[list, dict], default={});
    for _, fname, _ in get_names(files):
        make_file_if_not_exists(fname, subpath);

    # add any subfolders demanded:
    folders = get_dict_value(struct, 'folders', typ=dict, default={});
    for _, dir_name_, struct_ in get_names(folders):
        make_dir_if_not_exists(dir_name_, subpath);
        create_folders(dir_name_, struct_ or {}, subpath);
    return;

# --------------------------------------------------------------------------------
# LOCAL CLASSES
# --------------------------------------------------------------------------------

class EvalMetaType(type):
    __name__ = 'evaluation';

    @classmethod
    def __instancecheck__(cls, o) -> bool:
        try:
            return type(o).__name__ == cls.__name__;
        except:
            return False;

class EvalType(metaclass=EvalMetaType):
    __expr: str = str(None);

    def __init__(self, expr):
        if isinstance(expr, str):
            self.__expr = expr;
        return;

    @property
    def expr(self):
        return self.__expr;

    def __str__(self) -> str:
        return self.expr;

# --------------------------------------------------------------------------------
# AUXILIARY FUNCTIONS
# --------------------------------------------------------------------------------

def parse_cli_args(args):
    tokens = [];
    kwargs = {};
    for arg in args:
        m = re.match(r'^(.*?)\=(.*)$', arg);
        if not m:
            arg = re.sub(r'^\-*', '', arg);
            arg = arg.lower();
            tokens.append(arg);
        else:
            key = m.group(1);
            value = m.group(2);
            kwargs[key] = value;
    return tokens, kwargs;

# extracts name of attribute --- either the key itself, or the 'name' attribute, if defined.
def get_name(key: str, struct: Union[dict, None]) -> str:
    return get_dict_value(struct, ['name'], typ=str, default=key);

def get_names(struct: Union[dict, List[str]]) -> List[Tuple[str, str, Any]]:
    if isinstance(struct, list):
        return [(key, key, {}) for key in struct];
    return [(key, get_name(key, struct[key]), struct[key]) for key in struct];

def make_file_if_not_exists(fname: str, path: str = None) -> bool:
    path = path or os.getcwd();
    fexists = os.path.isfile(os.path.join(path, fname));
    if fexists:
        message_to_console('  \033[33mSkipping creation of file\033[0m \033[96;1m{}\033[0m ⟶ already exists!'.format(fname));
    else:
        message_to_console('  File \033[96;1m{}\033[0m will be created.'.format(fname));
        Popen(['touch', fname], cwd=path).wait();
    return fexists;

def make_dir_if_not_exists(dir_name: str, path: str = None) -> bool:
    path = path or os.getcwd();
    fexists = os.path.isdir(os.path.join(path, dir_name));
    if fexists:
        message_to_console('  \033[33mSkipping creation of folder\033[0m \033[96;1m{}\033[0m ⟶ already exists!'.format(dir_name));
    else:
        message_to_console('  Folder \033[96;1m{}\033[0m will be created.'.format(dir_name));
        Popen(['mkdir', '-p', dir_name], cwd=path).wait();
    return fexists;

def write_lines(lines: List[str], fname: str, path: str = None):
    try:
        path = path or os.getcwd();
        fp = open(os.path.join(path, fname), 'w');
        for line in lines:
            fp.write(line + '\n');
        fp.close();
    except:
        pass;
    return;

def matchestype(o, t: Union[type, str, bool, int, float, None, list]):
    if t is None:
        return True;
    elif isinstance(t, type):
        return type(o) == t;
    elif isinstance(t, (str, bool, int, float)):
        return o == t;
    else:
        return True in [matchestype(o, tt) for tt in t];

def get_dict_value(obj, key: Union[str,List[str]], *keys: Union[str,List[str]], typ=None, default=None):
    if not isinstance(obj, dict):
        return default;
    if not isinstance(key, list):
        key = [key];
    key_ = None;
    for _ in key:
        if _ in obj:
            key_ = _;
            break;
    if key_ is None:
        return default;
    obj_ = obj[key_];
    if len(keys) > 0:
        return get_dict_value(obj_, *keys, typ=typ, default=default);
    if obj_ is None or not matchestype(obj_, typ):
        return default;
    return obj_;

def to_python_string(value) -> Union[str, None]:
    if isinstance(value, str):
        return "r'{}'".format(value);
    elif isinstance(value, (int, float, bool, EvalType)) or value is None:
        return str(value);
    elif isinstance(value, list):
        values = [to_python_string(_) for _ in value];
        if None in values:
            return None;
        return '[' + ', '.join([x for x in values if isinstance(x, str)]) + ']';
    elif isinstance(value, dict):
        values = [(_, to_python_string(value[_])) for _ in value];
        for _, __ in values:
            if __ is None:
                return None;
        return '{' + ', '.join(["'{}': {}".format(_, __) for _, __ in values]) + '}';
        # return 'dict(' + ', '.join(["'{}': {}".format(_, __) for _, __ in values]) + ')';
    return None;

def message_to_console(message: str, force=False):
    global console_quiet;
    if force or not console_quiet:
        print(message);
    return;

# --------------------------------------------------------------------------------
# EXECUTION
# --------------------------------------------------------------------------------

if __name__ == '__main__':
    main();
