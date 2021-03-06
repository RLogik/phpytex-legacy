#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#############################################################################
# ENTITÄT: (PH(p)y)TeX                                                      #
# AUTOR: R-Logik, Deutschland. https://github.com/RLogik/phpytex            #
# ERSTELLUNGSDATUM: 27.11.2018                                              #
# ZULETZT VERÄNDERT: 06.03.2021                                             #
# VERSION: 3·3·3                                                            #
# HINWEISE:                                                                 #
#                                                                           #
#    Installation:                                                          #
#    ~~~~~~~~~~~~~                                                          #
#    1. Evtl. die ersten 2 Zeilen dieser Dateie an deinem System anpassen.  #
#    2. In einen Ordner legen, der im PATH liegt.                           #
#    3. Die .py-Extension entfernen                                         #
#    4. Mac OSX / Linux:                                                    #
#    sudo chmod 755 phpytex                                                 #
#    in Terminal ausführen.                                                 #
#    (Oder den äquivalenten Befehl für Windows.)                            #
#    5. Befehl ist jetzt überall verfügbar.                                 #
#    6. Mit                                                                 #
#        phpytex -help                                                      #
#        phpytex -man                                                       #
#    die Anleitungen aufrufen.                                              #
#    oder https://github.com/RLogik/phpytex >> README.md konsultieren.      #
#                                                                           #
#############################################################################

import sys;
import os;
import re;
import subprocess;

from types import TracebackType;
from typing import Dict;
from typing import List;
from typing import Tuple;
from typing import Union;
from typing import Any;
from pathlib import Path;
import numpy;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ROOTDIR: str = os.path.abspath('');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN METHOD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    phpytexTranspiler();
    return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SECONDARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS phpytexIndentation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class phpytexIndentation(object):
    pattern: str = r'    ';
    reference: int = 0;
    start: int = 1;
    last: int = 1;

    def __init__(self, pattern = None):
        if isinstance(pattern, str):
            self.pattern = pattern;
        return;

    def reset(self):
        self.reference = 0;
        self.start     = 1;
        self.last      = 1;

    def computeIndentations(self, s: str, pattern = None) -> int:
        pattern = pattern if isinstance(pattern, str) else self.pattern;
        return len(re.findall(pattern, s));

    def initOffset(self, s: str):
        self.reset();
        self.reference = self.computeIndentations(s);

    def computeOffset(self, s: str):
        return max(self.computeIndentations(s) - self.reference, 1);

    def setOffset(self, s: str):
        self.last = self.computeOffset(s);

    def decrOffset(self):
        self.last = max(self.last - 1, 1);

    def incrOffset(self):
        self.last = self.last + 1;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS phpytexTranspiler
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class phpytexTranspiler(object):
    ## GLOBALE VARIABLE
    GLOBALVARS:         Dict[str, Any]   = dict(__ROOT__='.', __DIR__='.');
    EXPORTVARS:         Dict[str, Any]   = dict();
    INCLUDES:           List[str]        = [];
    INSERTBIB:          bool             = False;
    ERROR:              bool             = False;
    PYERROR:            bool             = False;
    STAMPDATEI:         str;
    HAUPTDATEI:         str;
    OUTPUTDATEI:        str;
    EXPORTPARAMS:       bool             = False;
    PARAMDATEI:         str;
    PARAM_PY_IMPORT:    str;
    PARAM_MODULE_NAME:  str              = 'MODULE_GLOBAL_PARAMS';
    LENPRECODE:         int              = 0;
    LENGTHOFOUTPUT:     int              = 0; ## <-- Anzahl der Zeilen.
    MAXLENGTH:          int              = 10000; ## verhindere, dass die Datei zu groß wird.
    TOOLONG:            bool             = False;
    # SEED:               int            = numpy.random.get_state()[1][0];
    SEED:               int              = numpy.random.choice(100000000);
    PRECOMPILELINES:    List[Tuple[int, Any, str]] \
                                         = [];
    CENSORLENGTH:       int              = 8;

    ## Hier kann man optional den Defaulttabcharakter bestimmen:
    INDENTCHARACTER:    str              = '    ';
    INDENTCHARACTER_re: str              = r'    ';

    STRUCTURE:   List[str];
    INDENTATION: phpytexIndentation;

    def __init__(self):
        global ROOTDIR;

        # must initialise arrays!
        self.INCLUDES = [];
        self.PRECOMPILELINES = [];
        self.STRUCTURE = [];

        self.INDENTATION = phpytexIndentation(self.INDENTCHARACTER_re);
        params = get_cli_arguments(*sys.argv);

        if params['man'] or params['usage'] or params['guide']:
            display_message(r'''Siehe https://github.com/RLogik/phpytex/blob/master/README.md''');
            return;

        if params['help'] or not 'i' in params or not 'o' in params:
            display_message(
                '''
                    Zum Gebrauch dieses Befehls entweder:

                        phpytex -help
                        phpytex --help

                    um diese Hilfe aufzurufen, oder:

                        phpytex -man
                        phpytex -guide
                        phpytex -usage

                    um die Gebrauchsanleitung aufzurufen, oder:

                        phpytex
                            -i DATEI              Inputdatei relativ zum aktuellen Ordner.
                            -o DATEI              Outputdatei relativ zum aktuellen Ordner.
                            ___________________
                            | optionale Flags |
                            ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
                            -path PFAD            Pfad des lokalen Ordners.
                            -head DATEI           Datei mit Latex-Kommentar als Kopfteil.
                            -export-params        Pfad zu einer Datei, in die globale Parameter exportiert werden.
                                                  !! Als python Import-Pfad angeben. !!
                                                  Z. B.
                                                        `src/params.py` -> `\033[1msrc.params\033[0m`
                            -insert-bib           Inhalte von .bbl-Datei(en) werden eingesetzt anstelle von \\bibliography{...}.

                            -debug                Präkompiliertes Pythonskript wird zu Outputdatei geschrieben.
                            -no-compile           Latex-Datei wird generiert, aber nicht kompiliert.
                            -silent               Dateiaufbau in Outputdatei NICHT zeigen.

                            -no-comm              Entferne sämtliche LaTex-Kommentare
                            -no-comm-auto         Entferne rauskommentierte Zeilen (% ...) aber nicht Kommentare (%%...).
                            -max-length [0-9]+    Setze maximale Länge des Dokuments auf n Zeilen: verhindert endlose schleifen.
                                                (Defaultwert 10000.)

                            -tabs / -tab          Benutze \t als Einheit für Einrückung (Default).
                            -spaces [0-9]+        Benutze n x Leerzeichen als Einheit für Einrückung.

                            -seed [0-9]+          Seed für Pythons np.random.

                ''',
                indent='''
                '''
            );
            return;

        self.HAUPTDATEI = str(params['i']);
        self.OUTPUTDATEI = str(params['o']);
        if 'export-params' in params:
            mod = str(params['export-params']);
            if not re.match(r'^(\S+\.)*\S+$', mod):
                raise Exception('-export-params option MUST by a python-like import path (relative to the root of the project).');
            self.EXPORTPARAMS = True;
            self.PARAM_PY_IMPORT   = mod;
            self.PARAMDATEI        = re.sub(r'\.', '/', self.PARAM_PY_IMPORT);
            self.PARAMDATEI, _, _  = extractfilename(path=self.PARAMDATEI, relative=True);

        self.HAUPTDATEI, _, _  = extractfilename(path=self.HAUPTDATEI, relative=True);
        self.OUTPUTDATEI, _, _ = extractfilename(path=self.OUTPUTDATEI, relative=True, ext='');
        if self.HAUPTDATEI == self.OUTPUTDATEI:
            display_message('''\n    ACHTUNG! Die Namen der py-tex-Datei und Outputdatei dürfen nicht übereinstimmen!\n''');
            return;
        hauptfile, _, _ = extractfilename(path=self.OUTPUTDATEI, relative=False, ext='tex');

        if 'head' in params:
            self.STAMPDATEI, _, _ = extractfilename(path=str(params['head']), relative=True);

        debug  = force_bool(params['debug'], default=False);
        cmpl   = force_bool(not params['no-compile'], default=False);
        silent = force_bool(params['silent'], default=False);
        # anon   = force_bool(params['anon'], default=False); # <— funktioniert nicht richtig
        if 'seed' in params:
            self.SEED = int(params['seed']);
        if 'max-length' in params:
            self.MAXLENGTH = int(params['max-length']);
        if params['tab'] or params['tabs']:
            self.INDENTCHARACTER = '\t';
            self.INDENTCHARACTER_re = r'\t';
        elif 'spaces' in params:
            n = int(params['spaces']);
            self.INDENTCHARACTER = ' '*n;
            self.INDENTCHARACTER_re = ' '*n;

        if params['insert-bib']:
            self.INSERTBIB = True;

        display_message(
            '''
            ---------------------
            |    \033[32;1m(PH(p)y)TeX\033[0m    |
            ---------------------

            Dokumentteile werden kombiniert...

            ''',
            indent='''
            ''',
        );

        self.INCLUDES = [];
        self.PRECOMPILELINES = [];
        lines      = [];
        imports    = [];
        self.STRUCTURE = [];
        numpy.random.seed(self.SEED); ## nur ein Mal ausführen!
        erfolg = self.knit(
            filecontents = lines,
            imports      = imports,
            verbatim     = self.PRECOMPILELINES,
            mute         = False,
            silent       = silent,
            filename     = dict(
                src      = self.HAUPTDATEI,
                main     = self.OUTPUTDATEI+'.tex',
            ),
            params       = params
        );
        if not erfolg:
            return;
        lines, erfolg = self.addpreamble(silent=silent, lines=lines, params=params);
        if not erfolg:
            return;

        display_message('''\n...Dokumentteile erfolgreich kombiniert.\n''');
        globalvars = [];
        if self.EXPORTPARAMS:
            fname_params, _, _ = extractfilename(path=self.PARAMDATEI, relative=True, ext='py');
            self.export_parameters(fname=fname_params, globalvars=globalvars);
        self.execmetacode(lines=lines, imports=imports, globalvars=globalvars, fname=hauptfile, debug=debug, cmpl=cmpl);
        display_message('''\n\033[92;1m(PH(p)y)TeX\033[0m fertig!\n''');
        return;

    def createmetacode(
        self,
        lines:      List[str] = [],
        imports:    List[str] = [],
        globalvars: List[str] = [],
        fname:      str       = '',
        cmpl:       bool      = False
    ):
        fname_rel, _, _ = extractfilename(path=fname, relative=True, ext='');
        lines_pre = string_long(
            r'''
            from __future__ import annotations;
            import sys;
            import os;
            import re;
            import subprocess;
            import numpy;
            import numpy as np;
            from typing import Any;{import_params}

            ____lines____            = {{'post-compile':[], 'anon':[], 'bib':{{}}}};
            ____len_empty_block____  = 0;
            ____indent____           = '{indentchar}';
            ____indentation____      = '';
            ____filetex_name____     = '{fname}';
            ____filetex_name_rel____ = '{fname_rel}';
            ____filetex____          = None;
            ____error_toolong____    = False;
            ____outputlength____     = 0;
            ____maxlength____        = {maxlength};
            ____insertbib____        = {insertbib};
            ____compilelatex____     = {compilelatex};
            ____last_latex____       = None;
            ____rootdir____          = '{rootdir}';
            ____seed____             = {seed};
            __ROOT__                 = None;
            __DIR__                  = None;
            __SKIP__                 = None;
            __FNAME__                = None;
            __LINENR__               = None;
            ____error_eval____       = False;

            '''.format(
                import_params = '\nimport {} as {};\n'.format(self.PARAM_PY_IMPORT, self.PARAM_MODULE_NAME) if self.EXPORTPARAMS else '',
                indentchar    = self.INDENTCHARACTER_re,
                fname         = fname,
                fname_rel     = fname_rel,
                maxlength     = self.MAXLENGTH,
                insertbib     = self.INSERTBIB,
                compilelatex  = cmpl,
                rootdir       = ROOTDIR,
                seed          = self.SEED,
            ),
            indent='''
            '''
        ) \
        + string_long(
            r'''
            ## reseed-funktion:
            def ____reseed():
                global ____seed____;
                np.random.seed(____seed____);
                return True;

            class ____skipclass:
                def __init__(self):
                    self.len = 0;
                    self.chain = [];
                    self.status = False;
                    pass;

                def get(self):
                    self.status = (True in self.chain);
                    return self.status;

                def set(self, val):
                    if self.len == 0:
                        return False;
                    self.chain[self.len-1] = val;
                    self.get();
                    return True;

                def add(self, val):
                    self.chain.append(val);
                    self.len += 1;
                    self.get();
                    pass;

                def rem(self):
                    self.chain = self.chain[:-1];
                    self.len -= 1;
                    self.get();
                    pass;

                pass;

            def ____ignore(opt, val=None):
                global __SKIP__;
                global ____skipclass;

                if opt == 'get':
                    return __SKIP__.get();
                elif opt == 'add':
                    __SKIP__.add(False);
                elif opt == 'set':
                    __SKIP__.set(val);
                elif opt == 'rem':
                    __SKIP__.rem();
                elif opt == 'init':
                    __SKIP__ = ____skipclass();
                pass;

            ## expand: quickpython —> prä-eval-Ausdruck
            def ____qp(linenr=None, expr='', update_indentation=False):
                if ____ignore('get'):
                    return "''";

                global ____indentation____;
                global ____error_eval____;
                global ____last_latex____;
                global __LINENR__;
                ____error_eval____ = True;
                ____last_latex____ = expr;
                __LINENR__ = linenr;

                m = re.match(r'^((?:\s|\\t)*)(.*)$', expr);
                lmargin = re.sub(r'\\t', r'\t', m.group(1));
                expr    = m.group(2);
                re_meta = r'(\<{3}(?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*\>{3})';

                has_subs = True;
                while has_subs:
                    meta = "''";
                    has_subs = False;
                    for i,u in enumerate(re.split(re_meta, expr)):
                        m = re.match(r'^\<{3}((?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*)\>{3}$', u);
                        if m:
                            # has_subs = True;
                            # has_subs = False; # <— erlaube nur eine Auflösungsstufe.
                            u = m.group(1);
                            u = re.sub(r'^[\s\?\=]+|[\s\;]+$', '', u);
                            if u == '':
                                continue;
                            u = 'str(' + u + ')';
                            meta += '+'+u;
                        else:
                            mm = re.split(r'(\'+)', u);
                            for uu in mm:
                                if re.match(r'\'+', uu):
                                    uu = '"'+uu+'"';
                                else:
                                    uu = "'"+uu+"'";
                                meta += '+'+uu;
                    expr = meta;

                if update_indentation:
                    ____indentation____ = lmargin;
                else:
                    expr = "'{}' + ".format(lmargin) + expr;

                return expr;

            ## record + print-to-latex
            def ____print(s: Any, use_indent=True, anon=False):
                if ____ignore('get'):
                    return;

                global ____len_empty_block____;
                global ____error_eval____;
                global ____error_toolong____;
                global ____outputlength____;

                ## reduces blocks of empty lines to single empty lines:
                s = str(s);
                ____len_empty_block____ = (____len_empty_block____ + 1) if re.match(r'^\s*$', s) else 0;
                if ____len_empty_block____ > 1:
                    return;

                ____error_eval____ = False;
                if ____error_toolong____:
                    return;
                ____outputlength____ += 1;
                if ____outputlength____ > ____maxlength____:
                    ____error_toolong____ = True;

                ____forceprint(s, use_indent=use_indent, anon=anon);
                pass;

            def ____forceprint(s: str, use_indent=True, anon=False):
                global ____filetex____;
                global ____lines____;

                n = len(____lines____['post-compile']);
                for _s in re.split(r'\n', s):
                    if use_indent:
                        _s = ____indentation____ + _s;
                    print(_s, file=____filetex____);
                    ____lines____['post-compile'].append(_s);
                    if anon:
                        ____lines____['anon'].append(n);
                    n += 1;

                pass;

            def ____insertbib(fname='', src='', indent='', anon=False):
                global ____filetex____;
                global ____lines____;
                global ____insertbib____;

                nom, _ = os.path.splitext(fname);
                line = indent + r'\bibliography{'+nom+'}';
                print(line, file=____filetex____);
                ## lies Datei ein und füge Inhalte hinzu.
                ____lines____['post-compile'].append(line);
                if not src in ____lines____['bib']:
                    ____lines____['bib'][src] = [];
                n = len(____lines____['post-compile']);
                if anon:
                    ____lines____['anon'].append(n-1);
                elif ____insertbib____:
                    ____lines____['bib'][src].append(n-1);
                pass;

            def pipeCall(*_args, cwd = None):
                args = [_ for _ in _args];
                cmd = ' '.join(args);
                if not isinstance(cwd, str):
                    cwd = ____rootdir____;
                pipe = subprocess.Popen(args, cwd=cwd);
                pipe.wait();
                if pipe.returncode == 0:
                    return;
                raise Exception('Shell command < \033[94;1m{}\033[0m > failed.'.format(cmd));

            ## PDFLATEX:
            def ____compilelatex():
                print('\n\nPDFLATEX WIRD AUSGEFÜHRT:');
                outfile, _ = os.path.splitext(____filetex_name____);
                # pipeCall('pdflatex', '-interaction=scrollmode', outfile);
                # pipeCall('pdflatex', '-interaction=batchmode', outfile);
                pipeCall('pdflatex', '-interaction=errorstopmode', outfile);
                # pipeCall('pdflatex', '-interaction=nonstopmode', outfile);
                print('\n\nBIBTEX WIRD AUSGEFÜHRT:');
                for src in ____lines____['bib']:
                    src, _ = os.path.splitext(src);
                    pipeCall('bibtex', src);
                print('\n\nDOKUMENT \033[1m{fname}.pdf\033[0m WURDE FERTIGGESTELLT.'.format(fname=____filetex_name_rel____));
                pass;

            ## ERSETZUNG VON \bibliography-Befehlen durch Inhalte + Anonymisierung:
            def ____cleanlatex():
                global ____filetex____;

                with open(____filetex_name____, 'w+') as ____filetex____:
                    bibindex = [];
                    bibtext = {};
                    for src in ____lines____['bib']:
                        bibindex += ____lines____['bib'][src];
                        n = len(____lines____['bib'][src]);
                        biblines = [];
                        try:
                            fp = open(src, 'r');
                            lines = fp.readlines();
                            fp.close();
                            for bibline in lines:
                                bibline = re.sub(r'[\s\n]+$', '', bibline);
                                bibline = re.sub(r'^(.*)\%(.*)', r'\1', bibline);
                                if re.match(r'^\s*\%.*', bibline):
                                    continue;
                                biblines.append(bibline);
                                pass;
                        except:
                            biblines = None;
                            print('ACHTUNG! Bib-Datei \033[1m{fname}\033[0m konnte nicht gefunden werden'.format(fname=src));
                        bibtext[src] = biblines;
                        pass;

                    nr_lines = len(____lines____['post-compile']);
                    for n, line in enumerate(____lines____['post-compile']):
                        if n in ____lines____['anon']:
                            continue;
                        if n in bibindex:
                            src = None
                            for src_ in ____lines____['bib']:
                                if n in ____lines____['bib'][src_]:
                                    src = src_;
                                    break;
                                continue;
                            try:
                                if not src is None and not bibtext[src] is None:
                                    indent = re.sub(r'^(\s*)(\S|).*', r'\1', line);
                                    for bibline in bibtext[src]:
                                        print(indent + bibline, file=____filetex____);
                                        pass;
                                    continue;
                            except:
                                pass;
                        if n == nr_lines-1 and line == '':
                            continue;
                        print(line, file=____filetex____);
                pass;

            def ____compilephpytex():
                global ____reseed;
                global ____print;
                global ____qp;
                global ____ignore;
                global ____indentation____;
                global __ROOT__;
                global __DIR__;
                global __FNAME__;
                global __LINENR__;

                ____ignore('init');
            ''',
            indent='''
            '''
        ) \
        + string_long(
            r'''

                ################################
                # USER IMPORTS

            ''',
            indent='''
            '''
        ) + \
        (imports if len(imports) > 0 else ['# no imports']) + \
        string_long(
            r'''

                # END OF USER IMPORTS
                ################################

                ################################
                # USER 'GLOBAL'VARIABLES

            ''',
            indent='''
            '''
        ) + \
        (globalvars if len(globalvars) > 0 else ['    # no global vars']) + \
        string_long(
            r'''

                # END OF USER 'GLOBAL'VARIABLES
                ################################

            ''',
            indent='''
            '''
        );
        self.LENPRECODE = len(lines_pre);
        lines = lines_pre + lines + string_long(
            r'''
                ____indentation____ = '';
                pass;

            try:
                with open(____filetex_name____, 'w+') as ____filetex____:
                    ____compilephpytex();
                if ____compilelatex____:
                    ____compilelatex();
                else:
                    print('\nPDFLATEX WIRD NICHT AUSGEFÜHRT.');
                ____cleanlatex();
            except Exception as e:
                ## Provide information, then exit with status 1.
                print("-----------------------------------------------------------------");
                print("!!! (PH(p)y)TeX Kompilationsfehler !!!");
                if ____error_eval____:
                    ____last_latex____ = eval("'"+____last_latex____+"'");
                    print("  DATEI: "+str(__FNAME__));
                    print("  ZEILE: "+str(__LINENR__ + 1)+" (lokale Position innerhalb Datei).");
                    print("!!! Zeile konnte nicht evaluiert werden !!!");
                    print("-----------------------------------------------------------------");
                    print(____last_latex____);
                    print("-----------------------------------------------------------------");
                    ____forceprint("-----------------------------------------------------------------");
                    ____forceprint("!!! (PH(p)y)TeX-FEHLER !!!");
                    ____forceprint("  DATEI: "+str(__FNAME__));
                    ____forceprint("  ZEILE: "+str(__LINENR__ + 1)+" (lokale Position innerhalb Datei).");
                    ____forceprint("!!! Zeile konnte nicht evaluiert werden !!!");
                    ____forceprint("-----------------------------------------------------------------");
                    ____forceprint(____last_latex____);
                    ____forceprint("-----------------------------------------------------------------");
                else:
                    print("-----------------------------------------------------------------");
                    # print(sys.exc_info());
                    print(e);
                    print("-----------------------------------------------------------------");
                exit(1);

            ''',
            indent='''
            '''
        );
        return lines;

    def execmetacode(
        self,
        lines:      List[str] = [],
        imports:    List[str] = [],
        globalvars: List[str] = [],
        fname:      str       = '',
        debug:      bool      = False,
        cmpl:       bool      = False
    ):
        fname_rel, _, _ = extractfilename(path=fname, relative=True, ext='');
        lines = self.createmetacode(lines=lines, imports=imports, globalvars=globalvars, fname=fname, cmpl=cmpl);
        write_file(fname, lines);

        if debug:
            display_message('''Siehe Outputdatei: \033[1m{fname}.tex\033[0m'''.format(fname=fname_rel));
            return;

        try:
            pipeCall('python3', fname_rel+'.tex', errormsg='Phpytex transpilation/compilation error.');
        except:
            self.ERROR = True;
            self.PYERROR = True;
            _, err, tb = sys.exc_info();

            try:
                n = tb.tb_lineno - 1 if isinstance(err, TracebackType) else 0;
                line_err = lines[n];
                n -= self.LENPRECODE;
                linenr = -1; ## globale Zeilennummer
                precompilelines = [];
                __LINENR__ = -1;
                __FNAME__ = '???';
                for k, ignore, line in self.PRECOMPILELINES:
                    if ignore is True:
                        m = re.match(r'^\s*__FNAME__\s*=\s*[\'\"](.*)[\'\"](?:;|)\s*$', line);
                        if m:
                            __FNAME__ = m.group(1);
                        linenr += 1;
                    elif ignore is False:
                        linenr += 1;
                    precompilelines.append((linenr, ignore, line));
                    if linenr >= n:
                        __LINENR__ = int(k); ## lokale Zeilennummer innerhalb Datei
                        break;
                    continue;

                display_message(
                    r'''
                    -----------------------------------------------------------------
                    !!! (PH(p)y)TeX Kompilation hat versagt !!!
                      DATEI: {fname}
                      ZEILE: {lineno} (lokale Position innerhalb Datei).
                    !!! Syntaxfehler !!!
                    -----------------------------------------------------------------
                    '''.format(
                        fname  = __FNAME__,
                        lineno = __LINENR__ + 1,
                    ),
                    indent='''
                    '''
                );
                display_message(line_err);
                display_message(r'''-----------------------------------------------------------------''');
                display_message(r'''    (siehe Outputdatei)''');

                ## print to main tex file:
                with open(fname, 'w+') as fp:
                    display_message(*[line for k, ignore, line in precompilelines if k < n and not (ignore is True)], file=fp);
                    display_message(
                        r'''
                        -----------------------------------------------------------------
                        !!! (PH(p)y)TeX Kompilation hat versagt !!!
                        DATEI: {fname}
                        ZEILE: {lineno} (lokale Position innerhalb Datei).
                        !!! Syntaxfehler !!!
                        -----------------------------------------------------------------
                        '''.format(
                            fname  = __FNAME__,
                            lineno = __LINENR__ + 1,
                        ),
                        indent='''
                        ''',
                        file=fp
                    );
                    display_message('', *[line for k, ignore, line in precompilelines if k == n and ignore is False], file=fp);
                    display_message(r'''-----------------------------------------------------------------''', file=fp);
            except:
                ## Provide information, then exit with status 1.
                display_error(err);
                exit(1);

        return;

    def export_parameters(self, fname: str, globalvars: List[str]):
        lines = [];
        for key in self.EXPORTVARS:
            value = self.EXPORTVARS[key];
            if isinstance(value, str):
                value = "r'" + value + "'";
            else:
                # value = json.dumps(value);
                value = str(value);
            lines.append('{name} = {val};'.format(name=key, val=value));
            # globalvars.append('{indent}from {importpath} import {name};'.format(
            #     indent     = self.INDENTCHARACTER*1,
            #     importpath = self.PARAM_PY_IMPORT,
            #     name       = key,
            # ));
            globalvars.append('{indent}{name} = {mod}.{name};'.format(
                indent = self.INDENTCHARACTER*1,
                name   = key,
                mod    = self.PARAM_MODULE_NAME,
            ));
        if len(lines) > 0:
            lines = ['#!/usr/bin/env python3', '# -*- coding: utf-8 -*-', ''] + lines;
        else:
            lines = ['#!/usr/bin/env python3', '# -*- coding: utf-8 -*-'];
        write_file(fname, lines, force_create_path=True);
        return;

    def addpreamble(self, silent=False, lines=[], params={}):
        preamble = [];
        verbatim = [];
        params['no-comm'] = False;
        params['no-comm-auto'] = True;
        erfolg = True;
        if not self.STAMPDATEI is None:
            struct = self.STRUCTURE[:]
            self.STRUCTURE = [];
            erfolg = self.knit(
                filecontents = preamble,
                verbatim     = verbatim,
                mute         = True,
                filename     = dict(
                    src      =  self.STAMPDATEI,
                    main     =  'main',
                ),
                params       = params,
                dateityp     = 'head'
            );
            self.STRUCTURE = struct[:];

        if not erfolg:
            return lines, False;

        if not silent:
            self.addpytexline(lines=preamble, verbatim=verbatim, expr=[
                '%% ********************************************************************************',
                '%% DOCUMENT STRUCTURE:',
                '%% ~~~~~~~~~~~~~~~~~~~',
                '%%',
            ] + self.STRUCTURE + [
                '%%',
                '%% DOCUMENT-RANDOM-SEED: '+str(self.SEED),
                '%% ********************************************************************************',
            ], anon=False, mode='meta');

        lines = preamble + lines;
        self.PRECOMPILELINES = verbatim + self.PRECOMPILELINES;

        return lines, erfolg;

    def knit(
        self,
        filecontents: List[str]                  = [],
        imports:      List[str]                  = [],
        verbatim:     List[Tuple[int, Any, str]] = [],
        filename:     Dict[str, str]             = dict(),
        anon:         bool                       = False,
        mute:         bool                       = False,
        silent:       bool                       = False,
        indent:       Dict[str, int]             = dict(tex=0, struct=0),
        params:       Dict[str, Any]             = {},
        dateityp:     str                        = 'tex',
        chain:        List[str]                  = []
    ):
        if self.ERROR:
            return False;

        ## Bestimme Dateiquelle und neuen Root:
        root         = ROOTDIR;
        fname_src    = filename['src'];
        fname_main   = filename['main'];
        fname_curr   = fname_src;
        bool_getfile = False;
        src          = fname_src;
        lines        = [];
        if dateityp in ['head', 'tex', 'py']:
            if dateityp in ['head', 'tex']:
                _, ext = os.path.splitext(fname_src);
                if ext == '':
                    fname_src += '.tex';
            src, root, _ = extractfilename(path=fname_src, root=ROOTDIR, relative=True, split=True);
            fname_curr = src;
            bool_getfile, lines = (False, []) if (src in chain) else read_file(src);

        ## Anonymise file name:
        if anon:
            fname_curr = self.censorpath(path=fname_curr);

        ## Prüfe, ob Datei schon inkludiert wurde (entlang aktueller input-Kette):
        if src in chain:
            self.display_state_of_tree(
                r'''{branch} [∞] {fname}; (∞-Schleife! Datei wird nicht hinzugefügt!)'''.format(
                    branch = '    '*indent['struct'] + ('   -' if indent['struct'] == 0 else '-'*4),
                    fname  =  fname_curr,
                )
            );
            return True;

        ## Falls Dateiquelle nicht existiert oder sich nicht öffnen lässt:
        if not bool_getfile:
            self.ERROR = True;
            if not dateityp == 'head':
                self.display_state_of_tree(
                    r'''{branch} [x] {fname};'''.format(
                        branch = '    '*indent['struct'] + ('   -' if indent['struct'] == 0 else '-'*4),
                        fname  =  fname_curr,
                    )
                );
            display_message(
                r'''
                -----------------------------------------------------------------
                !!! (PH(p)y)TeX Kompilationsfehler !!!
                !!! Folgende Datei existiert nicht / ließ sich nicht öffnen:
                -----------------------------------------------------------------
                {fname}
                -----------------------------------------------------------------
                '''.format(fname=src),
                indent='''
                '''
            );
            return False;

        ## Berechne relative Pfade:
        heretoorigin, _, _ = extractfilename(path='.', root=ROOTDIR, relative=True, relative_to=root);
        origintohere, _, _ = extractfilename(path='.', root=root,         relative=True, relative_to=ROOTDIR);
        origintoorigin = '.'; # os.path.normpath(os.path.join(origintohere, heretoorigin));
        self.GLOBALVARS['__ROOT__'] = heretoorigin;
        self.GLOBALVARS['__DIR__'] = '.';
        orientation = [];
        orientation += self.postcompile(key='__ROOT__',  val=origintoorigin, symbolic=False);
        orientation += self.postcompile(key='__DIR__',   val=origintohere,   symbolic=False);
        orientation += self.postcompile(key='__FNAME__', val=src,            symbolic=False);
        self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=orientation, mode='direkt');
        lines_ = self.postcompile(key='__LINENR__', val=None, symbolic=False);
        self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=lines_, mode='direkt');
        self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
            '''{indent_py}____ignore('add');'''.format(indent_py=self.INDENTCHARACTER),
        ], mode='direkt');

        ## Output für Hauptdatei:
        if not mute:
            self.display_state_of_tree(
                r'''{branch} {fname};'''.format(
                    branch = '    '*indent['struct'] + ('   -' if indent['struct'] == 0 else '-'*4),
                    fname  = fname_curr,
                )
            );
            if not silent:
                self.addpytexline(lines=filecontents, verbatim=verbatim, expr=[
                    '',
                    '%% ********************************************************************************',
                    '%% FILE: {name}'.format(name=fname_curr),
                    '%% ********************************************************************************',
                    '',
                ], indent=self.INDENTATION.last, anon=anon, mode='meta');

        ## Zeilen einlesen und interpretieren:
        erfolg = True;
        chain_ = chain[::];
        bool_insidecode = False;
        code_language = '';
        code_flags = [];
        code_options: Dict[str, Any] = dict();
        code_option_print: bool = False;
        code_option_import: bool = False;
        pre_characters: str = '';

        for linenr, line in enumerate(lines + ['']):
            if self.ERROR:
                break;

            # Entferne alle whitespaces am Ende.
            line = re.sub(r'[\s\n]+$', '', line);

            # Dokumentart ist Python:
            if dateityp == 'py':
                line = self.INDENTCHARACTER*1 + line;
                line = line.rstrip();
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                continue;

            # Dokumentart ist tex und Zeile: Kommentar -> entscheide, ob Zeile übersprungen werden soll:
            m = re.match(r'^\s*(\%+).*', line);
            if not bool_insidecode and m:
                n_zeichen = len(m.group(1));
                if params['no-comm'] or (params['no-comm-auto'] and n_zeichen == 1):
                    ## <continue: i. e. remove line>
                    continue;

            # Zeile: Quick-Python SET GLOBAL
            m = re.match(r'^\s*\<{3}\s*set\s+global\s+(\S+\s*\=\s*.*)\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                line = m.group(1);
                m = re.match(r'((?!\d)[\w|\_]+)\s*\=\s*(.*)', line);
                if not m:
                    continue;
                nom = m.group(1);
                val = m.group(2);
                val = re.sub(r'^[\s]+|[\s\;]+$', '', val);
                # port directly to EXPORTVARS+GLOBALVARS Array:
                lines_ = self.postcompile(key=nom, val=val, indent=self.INDENTATION.last, symbolic=True, set_precompile=True, export=True);
                # do not write locally:
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, verbexpr=[
                    '<<< set global {}; >>>'.format(e.lstrip()) for e in line
                ], mode='direkt');
                continue;

            # Zeile: Quick-Python SET (= set local)
            m = re.match(r'^\s*\<{3}\s*(?:set\s+local|set)\s+(\S+\s*\=\s*.*)\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                line = m.group(1);
                m = re.match(r'((?!\d)[\w|\_]+)\s*\=\s*(.*)', line);
                if not m:
                    continue;
                nom = m.group(1);
                val = m.group(2);
                val = re.sub(r'^[\s]+|[\s\;]+$', '', val);
                # port directly to EXPORTVARS+GLOBALVARS Array:
                lines_ = self.postcompile(key=nom, val=val, indent=self.INDENTATION.last, symbolic=True, set_precompile=True, export=False);
                # do not write locally:
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, verbexpr=[
                    '<<< set {}; >>>'.format(e.lstrip()) for e in line
                ], mode='direkt');
                continue;

            # Zeile: Quick-Python ESCAPE_ONCE
            m = re.match(r'^\s*\<{3}\s*escape_once(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.decrOffset();
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    '''{indent_py}pass;'''.format(indent_py=self.INDENTCHARACTER*self.INDENTATION.last),
                ], verbexpr=['<<< esape_once; >>>'], mode='direkt');
                continue;

            # Zeile: Quick-Python ESCAPE
            m = re.match(r'^\s*\<{3}\s*escape(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.reset();
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    '''{indent_py}pass;'''.format(indent_py=self.INDENTCHARACTER*self.INDENTATION.last),
                ], verbexpr=['<<< escape; >>>'], mode='direkt');
                continue;

            # Zeile: Quick-Python IGNORE
            m = re.match(r'^\s*\<{3}\s*ignore(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.reset();
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    '''{indent_py}____ignore('set', True);'''.format(indent_py=self.INDENTCHARACTER*self.INDENTATION.last),
                ], verbexpr=['<<< ignore; >>>'], mode='direkt');
                continue;

            # Zeile: Quick-Python UNIGNORE
            m = re.match(r'^\s*\<{3}\s*unignore(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.reset()
                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    '''{indent_py}____ignore('set', False);'''.format(indent_py=self.INDENTCHARACTER*self.INDENTATION.last),
                ], verbexpr=['<<< unignore; >>>'], mode='direkt');
                continue;

            # Zeile: Start eines Codeblocks
            m        = re.match(r'^(\s*)(.*)(?:\<{3}|\`{3})\s*((?![\<\`]).*\S|)\s*$', line);
            m_bad    = re.match(r'^\s*(?:\<{4}|\`{4})', line);
            m_inline = re.match(r'^\s*(.*)(?:\<{3}|\`{3}).*(?:\>{3}|\`{3})', line);
            if m and not m_bad and not m_inline:
                if mute:
                    continue;
                inline_indentation = m.group(1);
                pre_characters     = m.group(1) + m.group(2);
                code_language, code_flags, code_options = get_code_language_and_options(m.group(3));
                bool_insidecode    = True;
                code_option_import = ('import' in code_flags);
                code_option_print  = ('print' in code_options and code_options['print'] is True);
                # If line is `<<< python, import`, then port subsequent lines to imports array:
                if code_option_import:
                    self.INDENTATION.initOffset(inline_indentation);
                # If line is `<<< python, print=true`, then use previous indentation level:
                elif code_option_print:
                    self.INDENTATION.reference = self.INDENTATION.computeIndentations(inline_indentation) - self.INDENTATION.last;
                    self.INDENTATION.start     = self.INDENTATION.last;
                    self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        '''{indent_py}____temp_value____ = \\'''.format(
                            indent_py  = self.INDENTCHARACTER*self.INDENTATION.last
                        ),
                    ], mode='direkt');
                else:
                    ## TODO: need to update tex-indentation at start of python blocks, avoiding conflicting python-indentation within e.g. if/else.
                    ##       The current solution works, but is not tidy.
                    self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        '''{indent_py}____indentation____ = '{indent_tex}';'''.format(
                            indent_py = self.INDENTCHARACTER*self.INDENTATION.last,
                            indent_tex = inline_indentation,
                        ),
                    ], mode='direkt');
                    self.INDENTATION.initOffset(inline_indentation);
                self.addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['{}<<< {}'.format(pre_characters, code_language)], mode='direkt');
                continue;

            # Zeile: Ende eines Codeblocks
            m        = re.match(r'^\s*(?:\>{3}|\`{3})(.*)$', line);
            m_bad    = re.match(r'^\s*(?:\>{4}|\`{4})', line);
            m_inline = re.match(r'^\s*(.*)(?:\<{3}|\`{3}).*(?:\>{3}|\`{3})', line);
            if m and not m_bad and not m_inline:
                if mute:
                    continue;
                post_characters = m.group(1);
                bool_insidecode = False;
                if code_option_print:
                    self.INDENTATION.last = self.INDENTATION.start;
                    self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=None, indent=self.INDENTATION.last, expr=[
                        '''{pre}<<< ____temp_value____; >>>{post}'''.format(
                            pre  = pre_characters,
                            post = post_characters
                        ),
                    ], anon=anon, mode='meta');
                    self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        '''{indent_py}del ____temp_value____;'''.format(
                            indent_py = self.INDENTCHARACTER*self.INDENTATION.last
                        ),
                    ], anon=anon, mode='direkt');
                self.addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['>>>{}'.format(post_characters)], mode='direkt');
                continue;

            # Zeile: Inside Code
            if bool_insidecode:
                if code_language == 'python':
                    if mute:
                        continue;
                    # Einrückung berechnen:
                    m = re.match(r'^(\s*)(.*)$', line);
                    indent_last = self.INDENTATION.computeOffset(m.group(1));
                    line = self.INDENTCHARACTER*indent_last + m.group(2);

                    # If within `<<< python, import` block, port lines to imports Array:
                    if code_option_import:
                        imports.append(line);
                        continue;

                    # Zeile: Python-Kommentar aber mit evtl. falschem Zeichen (LaTeX, Javascript, etc.).
                    m = re.match(r'^\s*(?:\#|\%|\/\/)(.*)$', line);
                    if m:
                        line = self.INDENTCHARACTER*indent_last + '#'+m.group(1);
                        self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                        continue;

                    # wenn nicht leer od. Kommentarzeile, dann python-Indent updaten.
                    self.INDENTATION.last = indent_last;

                    # Zeile: ignore / unignore.
                    m = re.match(r'^\s*(ignore|unignore)(?:\;|$|\s*\#.*)', line);
                    if m:
                        control = m.group(1);
                        self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                            '''{indent_py}____ignore('set', {ignore});'''.format(
                                indent_py = self.INDENTCHARACTER*self.INDENTATION.last,
                                ignore = (control == 'ignore'),
                            ),
                        ], mode='direkt');
                        continue;

                    # Zeile: Kopf eines Indent-Blocks
                    m = re.match(r'^\s*.*:(?:\s*\#.*|\s*)$', line);
                    if m:
                        self.INDENTATION.incrOffset();
                        self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                        continue;

                    # Zeile: sonstiger python Code.
                    self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                    continue;
                else:
                    # aktuell wird nur py unterstützt
                    continue;

            # Zeile: <<< input... >>>
            m = re.match(r'^(\s*)\<{3}\s*(input(?:_once|_anon|_anon_once|_once_anon|))\s+(.*\S|)\s*\>{3}', line);
            nom = None;
            if m:
                tex_indent = m.group(1);
                typ = m.group(2);
                nom = m.group(3);
                nom = re.sub(r'^[\s]+|[\s\;]+$', '', nom);
                nom_sub, is_bad = self.expandquickpython(expr=nom);

                if is_bad:
                    self.ERROR = True;
                    erfolg = False;
                    display_message(
                        r'''
                        -----------------------------------------------------------------
                        !!! (PH(p)y)TeX Kompilationsfehler !!!
                          DATEI: {fname}
                          ZEILE: {lineno} (lokale Position innerhalb Datei).
                        !!! <<< input >>>-Befehle konnte nicht evaluiert werden !!!
                        -----------------------------------------------------------------
                        '''.format(
                            fname  = fname_curr,
                            lineno = linenr+1,
                        ),
                        indent='''
                        '''
                    );
                    display_message(line);
                    display_message(r'''-----------------------------------------------------------------''');
                    continue;

                nom, _, _ = extractfilename(path=nom_sub, root=root, relative=False);
                _, ext = os.path.splitext(nom);
                if ext == '':
                    nom += '.tex';

                ## prüfe, ob Datei schon inkludiert wurde:
                if re.search(r'once', typ) and nom in self.INCLUDES:
                    continue;
                self.INCLUDES.append(nom);

                ## prüfe ob anonymisiert werden soll:
                anon_ = anon;
                if re.search(r'anon', typ):
                    anon_ = True;

                ## nested Call für neue Dateiquelle:
                nom, _, _  = extractfilename(path=nom_sub, root=root);
                _, ext = os.path.splitext(nom);
                if ext == '':
                    nom += '.tex';
                    ext = '.tex';
                ext = re.sub(r'^\.', '', ext);

                self.display_state_of_tree(r'''{branch}'''.format(branch = '    '*indent['struct'] + '    |'));
                erfolg_ = self.knit(
                    filecontents = filecontents,
                    imports      = imports,
                    verbatim     = verbatim,
                    filename     = dict(
                        src      = nom,
                        main     = filename['main'],
                    ),
                    anon         = anon_,
                    mute         = mute,
                    silent       = silent,
                    indent       = dict(
                        struct   = indent['struct'] + 1,
                        tex      = indent['tex']    + 1 if ext == 'tex' else 0,
                        py       = 1,
                    ),
                    params       = params,
                    dateityp     = ext,
                    chain        = chain_[::]
                );
                erfolg = erfolg and erfolg_;
                self.GLOBALVARS['__ROOT__'] = heretoorigin;
                self.GLOBALVARS['__DIR__'] = '.';
                self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, linenr=linenr, expr=orientation, mode='direkt');
                lines_ = self.postcompile(key='__LINENR__', val=linenr, symbolic=False);
                self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, mode='direkt');
                continue;

            # Zeile: <<< bibliography... >>>
            m   = re.match(r'^(\s*)\<{3}\s*(bibliography(?:_once|_anon|_anon_once|_once_anon|))\s+(.*\S|)\s*\>{3}', line);
            nom = None;
            if m:
                tex_indent = m.group(1);
                typ = m.group(2);
                nom = m.group(3);
                nom = re.sub(r'^[\s]+|[\s\;]+$', '', nom);
                nom_sub, is_bad = self.expandquickpython(expr=nom);

                ## prüfe, ob es möglich ist, die Inputdatei präkompiliert zu laden:
                if is_bad:
                    self.ERROR = True;
                    erfolg = False;
                    display_message(
                        r'''
                        -----------------------------------------------------------------
                        !!! (PH(p)y)TeX Kompilationsfehler !!!
                          DATEI: {fname}
                          ZEILE: {lineno} (lokale Position innerhalb Datei).
                        !!! <<< bibliography >>>-Befehl konnte nicht evaluiert werden !!!
                        -----------------------------------------------------------------
                        '''.format(
                            fname  = fname_curr,
                            lineno = linenr+1,
                        ),
                        indent='''
                        '''
                    );
                    display_message(line);
                    display_message(r'''-----------------------------------------------------------------''');
                    continue;

                nom, _, _  = extractfilename(path=nom_sub, root=root, relative=False, ext='bib');

                ## prüfe, ob Datei schon inkludiert wurde:
                if re.search(r'once', typ) and nom in self.INCLUDES:
                    continue;
                self.INCLUDES.append(nom);

                ## prüfe ob anonymisiert werden soll:
                anon_ = anon;
                if re.search(r'anon', typ):
                    anon_ = True;

                ## nested Call für neue Dateiquelle:
                nom, _, _  = extractfilename(path=nom_sub, root=root, ext='bib');
                # nom, root, fname = extractfilename(path=fname_src, root=root, split=True, ext='bib');
                src, _, _ = extractfilename(path=fname_main, ext='bbl');
                line = r'''{indent_py}____insertbib(fname='{fname}', src='{src}', indent='{indent_tex}', anon={anon})'''.format(
                    indent_py=self.INDENTCHARACTER*self.INDENTATION.last,
                    fname=nom,
                    src=src,
                    indent_tex=tex_indent,
                    anon=anon,
                );

                if not mute:
                    if anon_:
                        nom = self.censorpath(path=nom);
                    self.display_state_of_tree(r'''{branch}'''.format(branch = '    '*indent['struct'] + '    |'));
                    self.display_state_of_tree(
                        r'''{branch} {fname};'''.format(
                            branch = '    '*(indent['struct'] + 1) + ('   -' if indent['struct'] == 0 else '-'*4),
                            fname  = nom,
                        )
                    );

                    if not silent:
                        self.addpytexline(lines=filecontents, verbatim=verbatim, expr=[
                            '',
                            '%% ********************************************************************************',
                            '%% FILE: {name}'.format(name=nom),
                            '%% ********************************************************************************',
                            '',
                        ], indent=self.INDENTATION.last, anon=anon, mode='meta');

                self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                continue;

            # Zeile: normaler LaTeX (Kommentare am Ende einer Zeile werden nicht gelöscht)
            # ## indent line by current tex-indentation level:
            # line = self.INDENTCHARACTER*indent['tex'] + line;
            # m = re.match(r'^(|.*?(?!\\).)(\%.*)$', line);
            # if m:
            #     line = m.group(1).rstrip();

            self.addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, indent=self.INDENTATION.last, expr=[line], anon=anon, mode='meta');
            continue;

        self.addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
            '''{indent_py}____ignore('rem');'''.format(indent_py=self.INDENTCHARACTER),
        ], mode='direkt');
        return erfolg;

    def display_state_of_tree(self, msg: str):
        display_message(msg);
        self.STRUCTURE.append('%%' + msg);
        pass;

    def addpytexline(
        self,
        lines: List[str]                     = [],
        verbatim: List[Tuple[int, Any, str]] = [],
        linenr                               = None,
        expr: List[str]                      = [],
        verbexpr                             = None,
        indent                               = 1,
        anon: bool                           = True,
        mode: str                            = 'direkt',
        ignore: Any                          = False
    ):
        if mode == 'meta':
            indent = max(indent, 1);
            for e in expr:
                e = metastring(e);
                lines += [
                    '''{indent_py}____print(eval(____qp({lineno}, {expr}, True), locals()), True, {anon});'''.format(
                        indent_py   = self.INDENTCHARACTER*indent,
                        lineno      = linenr,
                        expr        = e,
                        anon        = anon,
                    ),
                ];
        elif mode == 'none':
            pass;
        else:
            lines += expr;
        if isinstance(verbexpr, list):
            verbatim += [(linenr, ignore, line) for line in verbexpr];
        else:
            verbatim += [(linenr, ignore, line) for line in expr];
        return;

    def expandquickpython(self, expr: str, contains_latex: bool = False, evaluate: bool = True) -> Tuple[Any, bool]:
        # re_meta = r'(\<{3}(?:(?![<>]).)*\>{3})'; # <— problematisch!
        re_meta = r'(\<{3}(?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*\>{3})';
        is_bad = False;
        has_subs = True;
        while has_subs:
            meta = '';
            has_subs = False;
            for _, u in enumerate(re.split(re_meta, expr)):
                # m = re.match(r'^\<{3}((?:(?!>).)*)\>{3}$', u); # <— problematisch!
                m = re.match(r'^\<{3}((?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*)\>{3}$', u);
                if m:
                    has_subs = True;
                    u = str(m.group(1));
                    u = re.sub(r'^[\s\?\=]+|[\s\;]+$', '', u);
                    if u == '':
                        continue;
                    if u in self.GLOBALVARS:
                        ## Wert substituieren:
                        u = self.GLOBALVARS[u];
                        if isinstance(u, str):
                            meta += escapecharacters(u);
                        else:
                            meta += str(u);
                    else:
                        meta += u;
                else:
                    meta += u;
            expr = meta;

        if not contains_latex:
            ## Bad <--- LaTeX Macros drin enthalten:
            ## (erkennbar als ungerade Anzahl an \'s hintereinander irgendwo im String)
            for u in enumerate(re.split(r'(\\+)', expr)):
                if len(u) % 2 == 1:
                    is_bad = True;
                    break;

        if not is_bad:
            ## Bad <--- ex. eine im pre-compile unauflösbare Variable.
            try:
                meta = eval(expr, self.GLOBALVARS);
                if evaluate:
                    expr = meta;
            except:
                is_bad = True;

        return expr, is_bad;

    def postcompile(self,
        key:            str,
        val:            Any,
        indent:         int  = 1,
        symbolic:       bool = True,
        set_precompile: bool = False,
        export:         bool = False,
    )-> List[str]:
        if len(key) == 0:
            return [];

        is_bad = False;
        if symbolic:
            if isinstance(val, str) and len(val) == 0:
                val = None;
            if isinstance(val, str):
                val, is_bad = self.expandquickpython(expr=val);

        if set_precompile and not is_bad:
            self.GLOBALVARS[key] = val;

        # only save the first definition:
        if export and self.EXPORTPARAMS and not (key in self.EXPORTVARS):
            self.EXPORTVARS[key] = None if is_bad else val;

        if is_bad:
            val = "eval('" + str(val) + "')";
        elif isinstance(val, str):
            val = "'" + escapecharacters(val) + "'";
        else:
            val = str(val);

        lines = [ '{indent}{key} = {value};'.format(indent = self.INDENTCHARACTER*indent, key = key, value = val), ];
        if export and self.EXPORTPARAMS:
            lines += [ '{indent}{mod}.{key} = {key}'.format(indent = self.INDENTCHARACTER*indent, mod=self.PARAM_MODULE_NAME, key=key) ];
        return lines;

    def censorpath(self, path: str) -> str:
        # return '#'*len(path);
        return '#'*self.CENSORLENGTH;
    pass;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MISCELLANEOUS METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def pipeCall(*_args, cwd = None, errormsg: str):
    args = [_ for _ in _args];
    if not isinstance(cwd, str):
        cwd = os.getcwd();
    pipe = subprocess.Popen(args, cwd=cwd);
    pipe.wait();
    if pipe.returncode == 0:
        return;
    raise Exception(errormsg);

def display_error(*x: Any, file=sys.stderr):
    print(*x, file=file);

def string_long(*text: str, indent: str = '') -> List[str]:
    lines = [];
    if indent == '':
        for _ in text:
            for line in _.split('\n')[1:][:-1]:
                lines.append(line);
    else:
        indent = ([_ for _ in indent.split('\n') if  not _ == ''] + [''])[0];
        n = len(indent);
        for _ in text:
            for line in _.split('\n')[1:][:-1]:
                if line.startswith(indent):
                    line = line[n:];
                lines.append(line);
    return lines;

def display_message(*text: Any, indent = None, file = sys.stdout):
    lines = [str(_) for _ in text];
    if isinstance(indent, str):
        lines = string_long(*lines, indent=indent);
    for line in lines:
        print(line, file=file);
    pass;

## EXTRACT CLI ARGUMENTS
def get_cli_arguments(*sysargs: str) -> Dict[str, Union[str, bool]]:
    params = {};
    flags_bool = ['anon','silent','man','usage','guide','help','no-comm','no-comm-auto','insert-bib','debug','tab','tabs','no-compile'];
    for key in flags_bool:
        params[key] = False;
    key = None;
    for i,arg in enumerate(sysargs):
        m = re.match(r'^\s*\-\s*(.*\S|)\s*', arg);
        if m:
            key = m.group(1);
            if re.match(r'.*help.*', key, re.IGNORECASE):
                key = 'help';
            if key in flags_bool:
                params[key] = True;
                key = None;
        else:
            if key is None:
                continue;
            m = re.match(r'^\s*(?:\'|\")(.*)(?:\'|\")\s*$', arg);
            if m:
                arg = m.group(1);
            params[key] = arg;
            key = None;
            continue;
    return params;

## FILE METHODS
def read_file(fname: str) -> Tuple[bool, List[str]]:
    try:
        with open(fname, 'r') as fp:
            lines = fp.readlines();
        return True, lines;
    except:
        return False, [];

def create_path(path: str):
    if not os.path.exists(path):
        Path(path).mkdir(parents=True, exist_ok=True);
    if not os.path.exists(path):
        raise FileExistsError('Could not create or find path \033[93;1m{}\033[0m!'.format(path));
    return;

def write_file(fname: str, lines: List[str], force_create_path: bool = False, force_create_empty_line: bool = True):
    if force_create_path:
        create_path(os.path.dirname(fname));
    while len(lines) > 0:
        if not re.match(r'^\s*$', lines[-1]):
            break;
        lines = lines[:-1];
    if force_create_empty_line:
        lines = lines + [''];
    with open(fname, 'w+') as fp:
        fp.writelines('\n'.join(lines));
    return;

def extractfilename(path: str, root=None, split=False, relative=None, relative_to=None, ext=None) -> Tuple[str, str, str]:
    if not isinstance(root, str):
        root = ROOTDIR;

    root = os.path.abspath(os.path.normpath(root));
    if re.match(r'\:|^[\/\\]', path):
        relative = relative if isinstance(relative, bool) else False;
        path = os.path.abspath(os.path.normpath(path));
    else:
        relative = relative if isinstance(relative, bool) else True;
        path = os.path.join(root, path);
        path = os.path.abspath(os.path.normpath(path));

    if relative:
        root = relative_to;
        if not isinstance(root, str):
            root = ROOTDIR;
        root = os.path.abspath(os.path.normpath(root));
        root_parts = re.split(r'/+', re.sub('^/+', '', root));
        path_parts = re.split(r'/+', re.sub('^/+', '', path));
        back = len(root_parts);
        while len(root_parts) > 0 and len(path_parts) > 0:
            if root_parts[0] == path_parts[0]:
                back -= 1;
                root_parts = root_parts[1:];
                path_parts = path_parts[1:];
                continue;
            break;
        path = os.path.join(*(['.'] + ['..']*back + path_parts));

    if isinstance(ext, str):
        path, _ = os.path.splitext(path);
        if not ext == '':
            path = path + '.' + ext;

    if split:
        root, fname = os.path.split(path);
        path = os.path.normpath('/'.join([root, fname]));
        return path, root, fname;
    return path, '', '';

## READ INLINE ARGUMENTS FROM HEAD OF CODE BLOCKS:
def get_inline_arguments(s: str) -> Tuple[List[str], Dict[str, Any]]:
    letters      = [_ for _ in s];
    i            = 0;
    slashes      = False;
    inside_quote = False
    open_quote   = '';
    parts        = [];
    for j, u in enumerate(letters):
        if re.match(r'\\', u):
            slashes = True;
        elif re.match(r'[\"\']', u):
            if not slashes:
                if inside_quote:
                    if u == open_quote:
                        inside_quote = False;
                else:
                    inside_quote = True;
                    open_quote = u;
            slashes = False;
        elif not inside_quote and re.match(r'[\s\,]', u):
            parts.append(s[i:j].strip());
            slashes = False;
            inside_quote = False;
            open_quote = '';
            i = j;
    parts.append(s[i:].strip());

    flags = [];
    parameters: Dict[str, Any] = dict();
    for part in parts:
        if re.match(r'^\s*$', part):
            continue;
        m = re.match(r'([\w\_\-]+)=(.*)', part);
        if not m:
            flags.append(part);
        else:
            key = m.group(1).strip();
            value = m.group(2).strip();
            if value == '':
                parameters[key] = None;
            elif re.match('^true$', value, re.IGNORECASE):
                parameters[key] = True;
            elif re.match('^false$', value, re.IGNORECASE):
                parameters[key] = False;
            else:
                try:
                    parameters[key] = eval(value);
                except:
                    parameters[key] = value;
    return flags, parameters;

def get_code_language_and_options(s: str) -> Tuple[str, List[str], Dict[str, Any]]:
    flags, parameters = get_inline_arguments(s);
    language = flags[0] if len(flags) > 0 else '';
    return language, flags[1:], parameters;

## STRING METHODS
def escapecharacters(s: str) -> str:
    s = re.sub(r'(\\+)', r'\1\1', s);
    s = re.sub(r'\n', r'\\n', s);
    s = re.sub(r'\t', r'\\t', s);
    s = re.sub(r'\"', r'\\u0022', s);
    s = re.sub(r'\'', r'\\u0027', s);
    # s = re.sub(r'\%', slash+'u0025', s);
    return s;

# verwandelt Strings in starke Metastrings:
def metastring(s: str) -> str:
    meta = "r''";
    s = re.sub(r'(\\+)', r'\1\1', s);
    s = re.sub(r'\n', r'\\n', s);
    s = re.sub(r'\t', r'\\t', s);
    m = re.split(r'(\'+)', s);
    for u in m:
        if re.match(r'\'+', u):
            u = 'r"'+u+'"';
        else:
            u = "r'"+u+"'";
        meta += '+'+u;
    if len(meta) > 3:
        meta = meta[4:]
    return meta;

def remove_quotes(s: str) -> str:
    return re.sub(r'^[\'\"]+|[\'\"]+$', '', s);

## FORCE TYPE
def force_bool(x: Any, default: bool = False) -> bool:
    return x if isinstance(x, bool) else default;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXECUTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    sys.tracebacklimit = 4;
    main();
