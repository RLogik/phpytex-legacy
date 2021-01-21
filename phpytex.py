#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#############################################################################
# ENTITÄT: (PH(p)y)TeX                                                      #
# AUTOR: R-Logik, Deutschland. https://github.com/RLogik/phpytex            #
# ERSTELLUNGSDATUM: 27.11.2018                                              #
# ZULETZT VERÄNDERT: 20.1.2021                                              #
# VERSION: 3·2·0                                                            #
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
import numpy;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN METHOD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    phpytexTranspiler().run();
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
        self.start = 1;
        self.last  = 1;

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
    GLOBALVARS:         Dict[str, Any]   = {'__ROOT__':'.', '__DIR__':'.'};
    INCLUDES:           List[str]        = [];
    CURRDIR:            str              = os.path.abspath('');
    ROOTDIR:            str              = CURRDIR;
    INSERTBIB:          bool             = False;
    ERROR:              bool             = False;
    PYERROR:            bool             = False;
    STAMPDATEI:         str;
    HAUPTDATEI:         str;
    OUTPUTDATEI:        str;
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
    INDENTCODE:         int              = 1;
    INDENTCHARACTER:    str              = '    ';
    INDENTCHARACTER_re: str              = r'    ';
    INDENTATION: phpytexIndentation;

    def __init__(self):
        self.INDENTATION = phpytexIndentation(self.INDENTCHARACTER_re);
        pass;

    ## HAUPTVORGANG
    def run(self):
        params = self.____getarguments(sys.argv);

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
        if 'path' in params:
            self.ROOTDIR = str(params['path']);
            self.GLOBALVARS['__ROOT__'] = self.ROOTDIR;

        self.HAUPTDATEI, _, _  = self.____extractfilename(path=self.HAUPTDATEI, relative=True);
        self.OUTPUTDATEI, _, _ = self.____extractfilename(path=self.OUTPUTDATEI, relative=True, ext='');
        if self.HAUPTDATEI == self.OUTPUTDATEI:
            display_message('''\n    ACHTUNG! Die Namen der py-tex-Datei und Outputdatei dürfen nicht übereinstimmen!\n''');
            return;
        hauptfile, _, _ = self.____extractfilename(path=self.OUTPUTDATEI, relative=False, ext='tex');

        if 'head' in params:
            self.STAMPDATEI, _, _ = self.____extractfilename(path=str(params['head']), relative=True);

        debug = params['debug'];
        cmpl = not params['no-compile'];
        silent = params['silent'];
        # anon = params['anon']; # <— funktioniert nicht richtig
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
        lines = [];
        struct = [];
        numpy.random.seed(self.SEED); ## nur ein Mal ausführen!
        erfolg = self.____knit(filecontents=lines, verbatim=self.PRECOMPILELINES, struct=struct, mute=False, silent=silent, filename={'src':self.HAUPTDATEI, 'main':self.OUTPUTDATEI+'.tex'}, params=params);
        if not erfolg:
            return;
        lines, erfolg = self.____addpreamble(silent=silent, lines=lines, struct=struct, params=params);
        if not erfolg:
            return;

        display_message('''\n...Dokumentteile erfolgreich kombiniert.\n''');
        self.____execmetacode(lines=lines, fname=hauptfile, debug=debug, cmpl=cmpl);
        display_message('''\n\033[92;1m(PH(p)y)TeX\033[0m fertig!\n''');
        return;


    ## METHODEN
    def ____getarguments(self, sysargs) -> Dict[str, Union[str, bool]]:
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

    def ____createmetacode(self, lines=[], fname='', cmpl=False):
        fname_rel, _, _ = self.____extractfilename(path=fname, relative=True, ext='');
        tab = self.INDENTCHARACTER;
        lines_pre = string_long(
            r'''
            import sys;
            import os;
            import re;
            import subprocess;
            import numpy;
            import numpy as np;
            from typing import Any;

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

            def ____reset_indentation():
                global ____indentation____;
                ____indentation____ = '';
                pass;

            def ____set_indentation(s: str):
                global ____indentation____;
                ____indentation____ = s;
                pass;

            ## expand: quickpython —> prä-eval-Ausdruckâ
            def ____qp(linenr=None, expr='', params={{}}):
                if ____ignore('get'):
                    return "''";

                global ____error_eval____;
                global ____last_latex____;
                global __LINENR__;
                ____error_eval____ = True;
                ____last_latex____ = expr;
                __LINENR__ = linenr;

                re_meta = r'(\<{{3}}(?![\<|\`])(?:(?!(?:\<{{3}}|\>{{3}})).)*\>{{3}})';
                has_subs = True;
                while has_subs:
                    meta = "''";
                    has_subs = False;
                    for i,u in enumerate(re.split(re_meta, expr)):
                        m = re.match(r'^\<{{3}}((?![\<|\`])(?:(?!(?:\<{{3}}|\>{{3}})).)*)\>{{3}}$', u);
                        if m:
                            # has_subs = True;
                            # has_subs = False; # <— erlaube nur eine Auflösungsstufe.
                            u = m.group(1);
                            u = re.sub(r'^[\s\?\=]+|[\s\;]+$', '', u);
                            if u == '':
                                continue;
                            u = 'str('+u+')';
                            meta += '+'+u;
                        else:
                            mm = re.split(r'(\'+)', u);
                            for uu in mm:
                                if re.match(r'\'+', uu):
                                    uu = '"'+uu+'"';
                                else:
                                    uu = "'"+uu+"'";
                                meta += '+'+uu;
                        continue;
                    expr = meta;
                    continue;

                return expr;

            ## record + print-to-latex
            def ____print(s: Any, keep_indent=True, anon=False):
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

                ____forceprint(s, keep_indent=keep_indent, anon=anon);
                pass;

            def ____forceprint(s: str, keep_indent=True, anon=False):
                global ____filetex____;
                global ____lines____;

                n = len(____lines____['post-compile']);
                for _s in re.split(r'\n', s):
                    if keep_indent:
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
                line = indent + r'\bibliography{{'+nom+'}}';
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

            ## PDFLATEX:
            def ____compilelatex():
                print('\n\nPDFLATEX WIRD AUSGEFÜHRT:');
                outfile, _ = os.path.splitext(____filetex_name____);
                proc = subprocess.Popen(['pdflatex', outfile], cwd=____rootdir____);
                proc.wait();
                print('\n\nBIBTEX WIRD AUSGEFÜHRT:');
                for src in ____lines____['bib']:
                    src, _ = os.path.splitext(src);
                    proc = subprocess.Popen(['bibtex', src], cwd=____rootdir____);
                    proc.wait();
                print('\n\nDOKUMENT \033[1m{{fname}}.pdf\033[0m WURDE FERTIGGESTELLT.'.format(fname=____filetex_name_rel____));
                pass;

            ## ERSETZUNG VON \bibliography-Befehlen durch Inhalte + Anonymisierung:
            def ____cleanlatex():
                global ____filetex____;

                with open(____filetex_name____, 'w+') as ____filetex____:
                    bibindex = [];
                    bibtext = {{}};
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
                            print('ACHTUNG! Bib-Datei \033[1m{{fname}}\033[0m konnte nicht gefunden werden'.format(fname=src));
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
                global ____filetex____;
                global ____lines____;
                global ____reseed;
                global ____print;
                global ____qp;
                global ____ignore;
                global __ROOT__;
                global __DIR__;
                global __FNAME__;
                global __LINENR__;

                ____ignore('init');
            '''.format(
                indentchar   = self.INDENTCHARACTER_re,
                fname        = fname,
                fname_rel    = fname_rel,
                maxlength    = self.MAXLENGTH,
                insertbib    = self.INSERTBIB,
                compilelatex = cmpl,
                rootdir      = self.ROOTDIR,
                seed         = self.SEED,
            ),
            indent='''
            '''
        );
        self.LENPRECODE = len(lines_pre);
        lines = lines_pre + lines + string_long(
            r'''
                ____reset_indentation();
                pass;

            try:
                ____filetex____ = open(____filetex_name____, 'w+');
                ____compilephpytex();
                ____filetex____.close();
                if ____compilelatex____:
                    ____compilelatex();
                else:
                    print('\nPDFLATEX WIRD NICHT AUSGEFÜHRT.');
                ____cleanlatex();
            except Exception as e:
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
                    print(sys.exc_info())
                    print(e)
                    print("-----------------------------------------------------------------");

            ''',
            indent='''
            '''
        );
        return lines;

    def ____execmetacode(self, lines=[], fname='', debug=False, cmpl=False):
        lines = self.____createmetacode(lines=lines, fname=fname, cmpl=cmpl);
        fname_rel, _, _ = self.____extractfilename(path=fname, relative=True, ext='');
        ____filetex____ = open(fname, 'w+');
        ____filetex____.write('\n'.join(lines));
        ____filetex____.close();

        if debug:
            display_message('''Siehe Outputdatei: \033[1m{fname}.tex\033[0m'''.format(fname_rel));
            return;

        try:
            ## Former method: Removed---avoid usage of 'exec'!!
            # code = compile('\n'.join(lines), '<string>', mode='exec');
            # exec(code);
            proc = subprocess.Popen(['python3', fname_rel+'.tex']);
            proc.wait();
        except:
            self.ERROR = True;
            self.PYERROR = True;
            typ, err, tb = sys.exc_info();

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
                    display_message(*[line for k, ignore, line in precompilelines if k < n and not ignore is True], file=fp);
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
                display_error(err);

        return;

    def ____addpreamble(self, silent=False, lines=[], struct=[], params={}):
        preamble = [];
        verbatim = [];
        params['no-comm'] = False;
        params['no-comm-auto'] = True;
        erfolg = True;
        if not self.STAMPDATEI is None:
            erfolg = self.____knit(filecontents=preamble, verbatim=verbatim, struct=[], mute=True, filename={'src':self.STAMPDATEI, 'main':None}, params=params, dateityp='head');
            if not self.ERROR:
                self.____addpytexline(lines=preamble, verbatim=verbatim, expr=[''], mode='meta');

        if not erfolg:
            return lines, False;

        if not silent:
            self.____addpytexline(lines=preamble, verbatim=verbatim, expr=[
                '%% ********************************************************************************',
                '%% DOCUMENT STRUCTURE:',
                '%% ~~~~~~~~~~~~~~~~~~~',
                '%%',
            ] + struct + [
                '%%',
                '%% DOCUMENT-RANDOM-SEED: '+str(self.SEED),
                '%% ********************************************************************************',
            ], mode='meta');

        lines = preamble + lines;
        self.PRECOMPILELINES = verbatim + self.PRECOMPILELINES;

        return lines, erfolg;

    def ____knit(
        self,
        filecontents                         = [],
        verbatim: List[Tuple[int, Any, str]] = [],
        struct                               = [],
        filename                             = Dict[str, str],
        anon                                 = False,
        mute                                 = False,
        silent                               = False,
        indent                               = None,
        params                               = {},
        dateityp                             = None,
        chain                                = []
    ):
        if self.ERROR:
            return False;
        if dateityp is None:
            dateityp = 'tex';
        if indent is None:
            indent = dict(tex=0, struct=0);

        ## Bestimme Dateiquelle und neuen Root:
        root         = self.ROOTDIR;
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
            src, root, _ = self.____extractfilename(path=fname_src, root=self.ROOTDIR, relative=True, split=True);
            fname_curr = src;
            ## Prüfe, ob Dateiquelle existiert:
            if not(src in chain):
                try:
                    with open(src, 'r') as fp:
                        lines = fp.readlines();
                    bool_getfile = True;
                except:
                    pass;

        ## Anonymise file name:
        if anon:
            fname_curr = self.____censorpath(path=fname_curr);

        ## Prüfe, ob Datei schon inkludiert wurde (entlang aktueller input-Kette):
        if src in chain:
            msg = r'''{branch} [∞] {fname}; (∞-Schleife! Datei wird nicht hinzugefügt!)'''.format(
                branch = '    '*indent['struct'] + ('-' if indent['struct'] == 0 else '-'*4),
                fname  =  fname_curr,
            );
            display_message(msg);
            struct.append('%%' + msg);
            return True;

        ## Falls Dateiquelle nicht existiert oder sich nicht öffnen lässt:
        if not bool_getfile:
            self.ERROR = True;
            if not dateityp == 'head':
                msg = r'''{branch} [x] {fname};'''.format(
                    branch = '    '*indent['struct'] + ('-' if indent['struct'] == 0 else '-'*4),
                    fname  =  fname_curr,
                );
                display_message(msg);
                struct.append('%%' + msg);
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
        heretoorigin, _, _ = self.____extractfilename(path='.', root=self.ROOTDIR, relative=True, relative_to=root);
        origintohere, _, _ = self.____extractfilename(path='.', root=root,         relative=True, relative_to=self.ROOTDIR);
        origintoorigin = '.'; # os.path.normpath(os.path.join(origintohere, heretoorigin));
        self.GLOBALVARS['__ROOT__'] = heretoorigin;
        self.GLOBALVARS['__DIR__'] = '.';
        orientation = [];
        orientation += self.____postcompile(key='__ROOT__',  val=origintoorigin, symbolic=False);
        orientation += self.____postcompile(key='__DIR__',   val=origintohere,   symbolic=False);
        orientation += self.____postcompile(key='__FNAME__', val=src,            symbolic=False);
        self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=orientation, mode='direkt');
        lines_ = self.____postcompile(key='__LINENR__', val=None, symbolic=False);
        self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=lines_, mode='direkt');
        self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
            self.INDENTCHARACTER*self.INDENTCODE + r"____ignore('add');",
        ], mode='direkt');

        ## Output für Hauptdatei:
        if not mute:
            msg = r'''{branch} {fname};'''.format(
                branch = '    '*indent['struct'] + ('-' if indent['struct'] == 0 else '-'*4),
                fname  = fname_curr,
            );
            display_message(msg);
            struct.append('%%' + msg);
            if not silent:
                self.____addpytexline(lines=filecontents, verbatim=verbatim, expr=[
                    '',
                    '%% ********************************************************************************',
                    '%% FILE: {name}'.format(name=fname_curr),
                    '%% ********************************************************************************',
                    '',
                ], indent=self.INDENTATION.last, mode='meta');

        ## Zeilen einlesen und interpretieren:
        erfolg = True;
        chain_ = chain[::];
        bool_insidecode = False;
        code_language = '';
        code_flags = [];
        code_options: Dict[str, Any] = dict();
        code_option_print: bool = False;
        pre_characters: str = '';

        for linenr, line in enumerate(lines):
            if self.ERROR:
                break;

            # Entferne alle whitespaces am Ende.
            line = re.sub(r'[\s\n]+$', '', line);

            # Dokumentart ist Python:
            if dateityp == 'py':
                line = self.INDENTCHARACTER*self.INDENTCODE + line;
                line = line.rstrip();
                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                continue;

            # Dokumentart ist tex und Zeile: Kommentar -> entscheide, ob Zeile übersprungen werden soll:
            m = re.match(r'^\s*(\%+).*', line);
            if not bool_insidecode and m:
                n_zeichen = len(m.group(1));
                if params['no-comm'] or (params['no-comm-auto'] and n_zeichen == 1):
                    ## <continue: i. e. remove line>
                    continue;

            # Zeile: Quick-Python SET
            m = re.match(r'^\s*\<{3}\s*set\s+(.*)\>{3}', line);
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
                lines_ = self.____postcompile(key=nom, val=val, indent=self.INDENTATION.last, symbolic=True, set_precompile=True);
                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, verbexpr=[
                    '<<< set {}; >>>'.format(e.lstrip()) for e in line
                ], mode='direkt');
                continue;

            # Zeile: Quick-Python ESCAPE_ONCE
            m = re.match(r'^\s*\<{3}\s*escape_once(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.decrOffset();
                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    self.INDENTCHARACTER*self.INDENTATION.last + "pass;",
                ], verbexpr=['<<< esape_once; >>>'], mode='direkt');
                continue;

            # Zeile: Quick-Python ESCAPE
            m = re.match(r'^\s*\<{3}\s*escape(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.reset();
                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    self.INDENTCHARACTER*self.INDENTATION.last + "pass;",
                ], verbexpr=['<<< escape; >>>'], mode='direkt');
                continue;

            # Zeile: Quick-Python IGNORE
            m = re.match(r'^\s*\<{3}\s*ignore(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.reset();
                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    self.INDENTCHARACTER*self.INDENTATION.last + r"____ignore('set', True);",
                ], verbexpr=['<<< ignore; >>>'], mode='direkt');
                continue;

            # Zeile: Quick-Python UNIGNORE
            m = re.match(r'^\s*\<{3}\s*unignore(;|)\s*\>{3}', line);
            if not bool_insidecode and m:
                if mute:
                    continue;
                self.INDENTATION.reset()
                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                    self.INDENTCHARACTER*self.INDENTATION.last + r"____ignore('set', False);",
                ], verbexpr=['<<< unignore; >>>'], mode='direkt');
                continue;

            #  --- unter Arbeit (Problem mit der Indentation-Logik) --- #
            # # Zeile: Quick-Python Python-Controlstatement (<<< ... : >>>)
            # # Indentation wie beim letzten Zustand von python-Code.
            # m = re.match(r'^\s*(?:\<{3}|\`{3})\s*((?![\<\`]).*\:)\s*(?:\>{3}|\`{3}).*$', line);
            # if not bool_insidecode and m:
            # 	self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
            # 		self.INDENTCHARACTER*self.INDENTATION.last + m.group(1)
            # 	], mode='direkt');
            # 	continue;

            # Zeile: Start eines Codeblocks
            m = re.match(r'^(\s*)(.*)(?:\<{3}|\`{3})\s*((?![\<\`]).*\S|)\s*$', line);
            m_bad = re.match(r'^\s*(?:\<{4}|\`{4})', line);
            m_inline = re.match(r'^\s*(.*)(?:\<{3}|\`{3}).*(?:\>{3}|\`{3})', line);
            if m and not m_bad and not m_inline:
                if mute:
                    continue;
                inline_indentation = m.group(1);
                pre_characters     = m.group(2);
                code_language, code_flags, code_options = self.____get_code_language_and_options(m.group(3));
                code_option_print = ('print' in code_options and code_options['print'] is True);
                bool_insidecode = True;
                ## Set indentation level. If within print=true set, use previous indentation level:
                if code_option_print:
                    self.INDENTATION.reference = self.INDENTATION.computeIndentations(inline_indentation) - self.INDENTATION.last;
                    self.INDENTATION.start = self.INDENTATION.last;
                    self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        self.INDENTCHARACTER*self.INDENTATION.last + "____set_indentation('{}');".format(inline_indentation),
                        self.INDENTCHARACTER*self.INDENTATION.last + '____temp_value____ = \\',
                    ], mode='direkt');
                else:
                    self.INDENTATION.initOffset(inline_indentation);
                self.____addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['{}<<< {}'.format(pre_characters, code_language)], mode='direkt');
                continue;

            # Zeile: Ende eines Codeblocks
            m = re.match(r'^\s*(?:\>{3}|\`{3})(.*)$', line);
            m_bad = re.match(r'^\s*(?:\>{4}|\`{4})', line);
            m_inline = re.match(r'^\s*(.*)(?:\<{3}|\`{3}).*(?:\>{3}|\`{3})', line);
            if m and not m_bad and not m_inline:
                if mute:
                    continue;
                post_characters = m.group(1);
                bool_insidecode = False;
                if code_option_print:
                    self.INDENTATION.last = self.INDENTATION.start;
                    self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=None, indent=self.INDENTATION.last, expr=[
                        '''{}<<< ____temp_value____; >>>{}'''.format(pre_characters, post_characters),
                    ], anon=anon, keep_indent=True, mode='meta');
                    self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        self.INDENTCHARACTER*self.INDENTATION.last + 'del ____temp_value____;',
                    ], anon=anon, mode='direkt');
                else:
                    inline_indentation = self.INDENTCHARACTER*self.INDENTATION.last;
                    self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        self.INDENTCHARACTER*self.INDENTATION.last + "____set_indentation('{}');".format(inline_indentation),
                    ], mode='direkt');
                self.____addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['>>>{}'.format(post_characters)], mode='direkt');
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

                    # Zeile: Python-Kommentar aber mit evtl. falschem Zeichen (LaTeX, Javascript, etc.).
                    m = re.match(r'^\s*(?:\#|\%|\/\/)(.*)$', line);
                    if m:
                        line = self.INDENTCHARACTER*indent_last + '#'+m.group(1);
                        self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                        continue;

                    # wenn nicht leer od. Kommentarzeile, dann python-Indent updaten.
                    self.INDENTATION.last = indent_last;

                    # Zeile: ignore / unignore.
                    m = re.match(r'^\s*(ignore|unignore)(?:\;|$|\s*\#.*)', line);
                    if m:
                        control = m.group(1);
                        self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
                            self.INDENTCHARACTER*self.INDENTATION.last + r"____ignore('set', "+str(control == 'ignore')+r");",
                        ], mode='direkt');
                        continue;

                    # Zeile: Kopf eines Indent-Blocks
                    m = re.match(r'^\s*.*:(?:\s*\#.*|\s*)$', line);
                    if m:
                        self.INDENTATION.incrOffset();
                        self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                        continue;

                    # Zeile: sonstiger python Code.
                    self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
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
                nom_sub, is_bad = self.____expandquickpython(expr=nom);

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

                nom, _, _ = self.____extractfilename(path=nom_sub, root=root, relative=False);
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
                nom, _, _  = self.____extractfilename(path=nom_sub, root=root);
                _, ext = os.path.splitext(nom);
                if ext == '':
                    nom += '.tex';
                    ext = 'tex';
                if ext == '.py':
                    ext = 'py';
                else:
                    ext = 'tex';

                filename_ = filename.copy();
                filename_['src'] = nom;
                indent_ = {};
                for key in indent:
                    if (key == 'tex' and ext == 'tex') or key == 'struct':
                        indent_[key] = indent[key] + 1;
                    else:
                        indent_[key] = self.INDENTCODE;

                msg = r'''{branch}'''.format(branch = '    '*indent['struct'] + '    |');
                display_message(msg);
                struct.append('%%' + msg);
                erfolg_ = self.____knit(filecontents=filecontents, verbatim=verbatim, struct=struct, filename=filename_, anon=anon_, mute=mute, silent=silent, indent=indent_, params=params, dateityp=ext, chain=chain_[::]);
                erfolg = erfolg and erfolg_;

                self.GLOBALVARS['__ROOT__'] = heretoorigin;
                self.GLOBALVARS['__DIR__'] = '.';
                self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, linenr=linenr, expr=orientation, mode='direkt');
                lines_ = self.____postcompile(key='__LINENR__', val=linenr, symbolic=False);
                self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, mode='direkt');
                continue;

            # Zeile: <<< bibliography... >>>
            m = re.match(r'^(\s*)\<{3}\s*(bibliography(?:_once|_anon|_anon_once|_once_anon|))\s+(.*\S|)\s*\>{3}', line);
            nom = None;
            if m:
                tex_indent = m.group(1);
                typ = m.group(2);
                nom = m.group(3);
                nom = re.sub(r'^[\s]+|[\s\;]+$', '', nom);
                nom_sub, is_bad = self.____expandquickpython(expr=nom);

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

                nom, _, _  = self.____extractfilename(path=nom_sub, root=root, relative=False, ext='bib');

                ## prüfe, ob Datei schon inkludiert wurde:
                if re.search(r'once', typ) and nom in self.INCLUDES:
                    continue;
                self.INCLUDES.append(nom);

                ## prüfe ob anonymisiert werden soll:
                anon_ = anon;
                if re.search(r'anon', typ):
                    anon_ = True;

                ## nested Call für neue Dateiquelle:
                nom, _, _  = self.____extractfilename(path=nom_sub, root=root, ext='bib');
                # nom, root, fname = self.____extractfilename(path=fname_src, root=root, split=True, ext='bib');
                src, _, _ = self.____extractfilename(path=fname_main, ext='bbl');
                indent_ = {};
                for key in indent:
                    val = self.INDENTCODE;
                    if key == 'tex' or key == 'struct':
                        val = indent[key] + 1;
                    indent_[key] = val;

                line = self.INDENTCHARACTER*self.INDENTATION.last + '''____insertbib(fname="'''+nom+'''", src="'''+src+'''", indent="'''+tex_indent+'''", anon='''+str(anon_)+''')''';

                if not mute:
                    if anon:
                        nom = self.____censorpath(path=nom);
                    msg = r'''{branch}'''.format(branch = '    '*indent['struct'] + '    |');
                    display_message(msg);
                    struct.append('%%' + msg);
                    msg = r'''{branch} {fname};'''.format(
                        branch = '    '*indent['struct'] + ('-' if indent['struct'] == 0 else '-'*4),
                        fname  = nom,
                    );
                    display_message(msg);
                    struct.append('%%' + msg);

                    if not silent:
                        self.____addpytexline(lines=filecontents, verbatim=verbatim, expr=[
                            '',
                            '%% ********************************************************************************',
                            '%% FILE: {name}'.format(name=nom),
                            '%% ********************************************************************************',
                            '',
                        ], indent=self.INDENTATION.last, mode='meta');

                self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
                continue;

            # Zeile: normaler LaTeX (Kommentare am Ende einer Zeile werden nicht gelöscht)
            # ## indent line by current tex-indentation level:
            # line = self.INDENTCHARACTER*indent['tex'] + line;
            # m = re.match(r'^(|.*?(?!\\).)(\%.*)$', line);
            # if m:
            #     line = m.group(1).rstrip();

            self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, indent=self.INDENTATION.last, expr=[line], anon=anon, mode='meta');
            continue;

        self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
            self.INDENTCHARACTER*self.INDENTCODE + r"____ignore('rem');",
        ], mode='direkt');
        return erfolg;

    def ____addpytexline(
        self,
        lines: List[str]                     = [],
        verbatim: List[Tuple[int, Any, str]] = [],
        linenr                               = None,
        expr: List[str]                      = [],
        verbexpr                             = None,
        indent                               = None,
        keep_indent: bool                    = False,
        anon: bool                           = False,
        mode: str                            = 'direkt',
        ignore: Any                          = False
    ):
        if mode == 'meta':
            for e in expr:
                lines += self.____metaprint(linenr=linenr, expr=e, indent=indent, keep_indent=keep_indent, anon=anon);
        elif mode == 'none':
            pass;
        else:
            lines += expr;
        if isinstance(verbexpr, list):
            verbatim += [(linenr, ignore, line) for line in verbexpr];
        else:
            verbatim += [(linenr, ignore, line) for line in expr];
        return;

    def ____extractfilename(
        self,
        path: str,
        root=None,
        split=False,
        relative=None,
        relative_to=None,
        ext=None
    ) -> Tuple[str, str, str]:
        if not isinstance(root, str):
            root = self.ROOTDIR;

        root = os.path.abspath(os.path.normpath(root));
        if re.match(r'\:|^[\/\\]', path):
            relative = relative if isinstance(relative, bool) else False;
            path = os.path.abspath(os.path.normpath(path));
        else:
            relative = relative if isinstance(relative, bool) else True;
            path = os.path.join(root, path);
            path = os.path.abspath(os.path.normpath(path));

        if relative:
            root = relative_to if isinstance(relative_to, str) else self.ROOTDIR;
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

    def ____expandquickpython(self, expr='', contains_latex=False, evaluate=True) -> Tuple[Any, bool]:
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
                    u = m.group(1);
                    u = re.sub(r'^[\s\?\=]+|[\s\;]+$', '', u);
                    if u == '':
                        continue;
                    if u in self.GLOBALVARS:
                        ## Wert substituieren:
                        u = self.GLOBALVARS[u];
                        if isinstance(u, str):
                            meta += self.____escapecharacters(u);
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

    # def ____compilenestedstring(self, s): # <--- unter Arbeit
    # 	is_bad = True;
    # 	return s, is_bad;

    def ____postcompile(self, key=None, val='', indent=None, symbolic=True, set_precompile=False) -> List[str]:
        if len(key) == 0:
            return [];

        if indent is None:
            indent = self.INDENTCODE;

        is_bad = False;
        if symbolic:
            if len(val) == 0:
                val = None;
            if isinstance(val, str):
                val, is_bad = self.____expandquickpython(expr=val);

        if set_precompile and not is_bad:
            self.GLOBALVARS[key] = val;

        if is_bad:
            val = "eval('" + str(val) + "')";
        elif isinstance(val, str):
            val = "'" + self.____escapecharacters(val) + "'";
        else:
            val = str(val);

        line = self.INDENTCHARACTER*indent + key + ' = ' + val + ';';

        return [line];

    def ____remove_quotes(self, s: str) -> str:
        return re.sub(r'^[\'\"]+|[\'\"]+$', '', s);

    def ____escapecharacters(self, s: str) -> str:
        s = re.sub(r'(\\+)', r'\1\1', s);
        s = re.sub(r'\n', r'\\n', s);
        s = re.sub(r'\t', r'\\t', s);
        s = re.sub(r'\"', r'\\u0022', s);
        s = re.sub(r'\'', r'\\u0027', s);
        # s = re.sub(r'\%', slash+'u0025', s);
        return s;

    ## verwandelt Strings in starke Metastrings:
    def ____metastring(self, s: str) -> str:
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

    def ____metaprint(self, indent=None, linenr=None, expr='', keep_indent=False, anon=False) -> List[str]:
        if indent is None or indent < self.INDENTCODE:
            indent = self.INDENTCODE;
        expr = self.____metastring(expr);
        args = dict(keep_indent=keep_indent, anon=anon);
        if anon:
            line = "____print(eval(____qp("+str(linenr)+", "+expr+"), locals()), keep_indent={keep_indent}, anon={anon});".format(**args);
        else:
            line = "____print(eval(____qp("+str(linenr)+", "+expr+"), locals()), keep_indent={keep_indent});".format(**args);
        lines = [self.INDENTCHARACTER*indent + line];
        return lines;

    def ____censorpath(self, path: str) -> str:
        # return '#'*len(path);
        return '#'*self.CENSORLENGTH;

    def ____get_inline_arguments(self, s: str) -> Tuple[List[str], Dict[str, Any]]:
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

    def ____get_code_language_and_options(self, s: str) -> Tuple[str, List[str], Dict[str, Any]]:
        flags, parameters = self.____get_inline_arguments(s);
        language = flags[0] if len(flags) > 0 else '';
        return language, flags[1:], parameters;
    pass;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MISCELLANEOUS METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXECUTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main();
