#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#############################################################################
# ENTITÄT: (PH(p)y)TeX                                                      #
# AUTOR: R-Logik, Deutschland. https://github.com/RLogik/phpytex            #
# ERSTELLUNGSDATUM: 27.11.2018                                              #
# ZULETZT VERÄNDERT: 1.10.2020                                              #
# VERSION: 3·1·7                                                            #
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
    PRECOMPILELINES:    List[Tuple[int, bool, str]] \
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
            print(r'''Siehe https://github.com/RLogik/phpytex/blob/master/README.md''');
            return;

        if params['help'] or not 'i' in params or not 'o' in params:
            print(r'''\

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
            -share PFAD           Pfad zum geteilten Ordner (PDF-Output kommt dahin).
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

''');
            return;

        self.HAUPTDATEI = str(params['i']);
        self.OUTPUTDATEI = str(params['o']);
        if 'path' in params:
            self.ROOTDIR = str(params['path']);
            self.GLOBALVARS['__ROOT__'] = self.ROOTDIR;

        self.HAUPTDATEI, _, _  = self.____extractfilename(path=self.HAUPTDATEI, relative=True);
        self.OUTPUTDATEI, _, _ = self.____extractfilename(path=self.OUTPUTDATEI, relative=True, ext='');
        if self.HAUPTDATEI == self.OUTPUTDATEI:
            print('\n\tACHTUNG! Die Namen der py-tex-Datei und Outputdatei dürfen nicht übereinstimmen!\n');
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

        print('----------------------');
        print('|    \033[32;1m(PH(p)y)TeX\033[0m    |');
        print('----------------------');
        print('\nDokumentteile werden kombiniert...\n');

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

        print('\n...Dokumentteile erfolgreich kombiniert.\n');
        self.____execmetacode(lines=lines, fname=hauptfile, debug=debug, cmpl=cmpl);
        print('');
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
        lines_pre = [
            r'''import sys;''',
            r'''import os;''',
            r'''import re;''',
            r'''import subprocess;''',
            r'''import numpy;''',
            r'''import numpy as np;''',
            r'''from typing import Any;''',
            r'''''',
            r'''____lines____            = {'post-compile':[], 'anon':[], 'bib':{}};''',
            r'''____len_empty_block____  = 0;''',
            r'''____indent____           = ''' + "'" + self.INDENTCHARACTER_re + "'" + ''';''',
            r'''____indentation____      = '';''',
            r'''____filetex_name____     = "'''+fname+'''";''',
            r'''____filetex_name_rel____ = "'''+fname_rel+'''";''',
            r'''____filetex____          = None;''',
            r'''____error_toolong____    = False;''',
            r'''____outputlength____     = 0;''',
            r'''____maxlength____        = '''+str(self.MAXLENGTH)+''';''',
            r'''____insertbib____        = '''+str(self.INSERTBIB)+''';''',
            r'''____compilelatex____     = '''+str(cmpl)+''';''',
            r'''____last_latex____       = None;''',
            r'''____rootdir____          = "'''+self.ROOTDIR+'''";''',
            r'''____seed____             = '''+str(self.SEED)+''';''',
            r'''__ROOT__                 = None;''',
            r'''__DIR__                  = None;''',
            r'''__SKIP__                 = None;''',
            r'''__FNAME__                = None;''',
            r'''__LINENR__               = None;''',
            r'''____error_eval____       = False;''',
            r'''''',
            r'''## reseed-funktion:''',
            r'''def ____reseed():''',
            tab+r'''global ____seed____;''',
            tab+r'''np.random.seed(____seed____);''',
            tab+r'''return True;''',
            r'''''',
            r'''class ____skipclass:''',
            tab+r'''def __init__(self):''',
            tab+tab+r'''self.len = 0;''',
            tab+tab+r'''self.chain = [];''',
            tab+tab+r'''self.status = False;''',
            tab+tab+r'''pass;''',
            tab+r'''''',
            tab+r'''def get(self):''',
            tab+tab+r'''self.status = (True in self.chain);''',
            tab+tab+r'''return self.status;''',
            tab+r'''''',
            tab+r'''def set(self, val):''',
            tab+tab+r'''if self.len == 0:''',
            tab+tab+tab+r'''return False;''',
            tab+tab+r'''self.chain[self.len-1] = val;''',
            tab+tab+r'''self.get();''',
            tab+tab+r'''return True;''',
            tab+r'''''',
            tab+r'''def add(self, val):''',
            tab+tab+r'''self.chain.append(val);''',
            tab+tab+r'''self.len += 1;''',
            tab+tab+r'''self.get();''',
            tab+tab+r'''pass;''',
            tab+r'''''',
            tab+r'''def rem(self):''',
            tab+tab+r'''self.chain = self.chain[:-1];''',
            tab+tab+r'''self.len -= 1;''',
            tab+tab+r'''self.get();''',
            tab+tab+r'''pass;''',
            tab+r'''''',
            tab+r'''pass;''',
            r'''''',
            r'''def ____ignore(opt, val=None):''',
            tab+r'''global __SKIP__;''',
            tab+r'''global ____skipclass;''',
            tab+r'''''',
            tab+r'''if opt == 'get':''',
            tab+tab+r'''return __SKIP__.get();''',
            tab+r'''elif opt == 'add':''',
            tab+tab+r'''__SKIP__.add(False);''',
            tab+r'''elif opt == 'set':''',
            tab+tab+r'''__SKIP__.set(val);''',
            tab+r'''elif opt == 'rem':''',
            tab+tab+r'''__SKIP__.rem();''',
            tab+r'''elif opt == 'init':''',
            tab+tab+r'''__SKIP__ = ____skipclass();''',
            tab+r'''pass;''',
            r'''''',
            r'''def ____reset_indentation():''',
            tab+r'''global ____indentation____;''',
            tab+r'''____indentation____ = '';''',
            tab+r'''pass;''',
            r'''''',
            r'''def ____set_indentation(s: str):''',
            tab+r'''global ____indentation____;''',
            tab+r'''____indentation____ = s;''',
            tab+r'''pass;''',
            r'''''',
            r'''## expand: quickpython —> prä-eval-Ausdruck''',
            r'''def ____qp(linenr=None, expr='', params={}):''',
            tab+r'''if ____ignore('get'):''',
            tab+tab+r'''return "''";''',
            tab+r'''''',
            tab+r'''global ____error_eval____;''',
            tab+r'''global ____last_latex____;''',
            tab+r'''global __LINENR__;''',
            tab+r'''____error_eval____ = True;''',
            tab+r'''____last_latex____ = expr;''',
            tab+r'''__LINENR__ = linenr;''',
            tab+r'''''',
            # tab+r'''re_meta = r'(\<{3}(?:(?![<>]).)*\>{3})';''', # <— problematisch!
            tab+r'''re_meta = r'(\<{3}(?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*\>{3})';''',
            tab+r'''has_subs = True;''',
            tab+r'''while has_subs:''',
            tab+tab+r'''meta = "''";''',
            tab+tab+r'''has_subs = False;''',
            tab+tab+r'''for i,u in enumerate(re.split(re_meta, expr)):''',
            # tab+tab+tab+r'''m = re.match(r'^\<{3}((?:(?!>).)*)\>{3}$', u);''', # <— problematisch!
            tab+tab+tab+r'''m = re.match(r'^\<{3}((?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*)\>{3}$', u);''',
            tab+tab+tab+r'''if m:''',
            tab+tab+tab+tab+r'''# has_subs = True;''',
            tab+tab+tab+tab+r'''# has_subs = False; # <— erlaube nur eine Auflösungsstufe.''',
            tab+tab+tab+tab+r'''u = m.group(1);''',
            tab+tab+tab+tab+r'''u = re.sub(r'^[\s\?\=]+|[\s\;]+$', '', u);''',
            tab+tab+tab+tab+r'''if u == '':''',
            tab+tab+tab+tab+tab+r'''continue;''',
            tab+tab+tab+tab+r'''u = 'str('+u+')';''',
            tab+tab+tab+tab+r'''meta += '+'+u;''',
            tab+tab+tab+r'''else:''',
            tab+tab+tab+tab+r'''mm = re.split(r'(\'+)', u);''',
            tab+tab+tab+tab+r'''for uu in mm:''',
            tab+tab+tab+tab+tab+r'''if re.match(r'\'+', uu):''',
            tab+tab+tab+tab+tab+tab+r'''uu = '"'+uu+'"';''',
            tab+tab+tab+tab+tab+r'''else:''',
            tab+tab+tab+tab+tab+tab+r'''uu = "'"+uu+"'";''',
            tab+tab+tab+tab+tab+r'''meta += '+'+uu;''',
            tab+tab+tab+r'''continue;''',
            tab+tab+r'''expr = meta;''',
            tab+tab+r'''continue;''',
            tab+r'''''',
            tab+r'''return expr;''',
            r'''''',
            r'''## record + print-to-latex''',
            r'''def ____print(s: Any, keep_indent=True, anon=False):''',
            tab+r'''if ____ignore('get'):''',
            tab+tab+r'''return;''',
            tab+r'''''',
            tab+r'''global ____len_empty_block____;''',
            tab+r'''global ____error_eval____;''',
            tab+r'''global ____error_toolong____;''',
            tab+r'''global ____outputlength____;''',
            tab+r'''''',
            tab+r'''## reduces blocks of empty lines to single empty lines:''',
            tab+r'''s = str(s);''',
            tab+r'''____len_empty_block____ = (____len_empty_block____ + 1) if re.match(r'^\s*$', s) else 0;''',
            tab+r'''if ____len_empty_block____ > 1:''',
            tab+tab+r'''return;''',
            tab+r'''''',
            tab+r'''____error_eval____ = False;''',
            tab+r'''if ____error_toolong____:''',
            tab+tab+r'''return;''',
            tab+r'''____outputlength____ += 1;''',
            tab+r'''if ____outputlength____ > ____maxlength____:''',
            tab+tab+r'''____error_toolong____ = True;''',
            tab+r'''''',
            tab+r'''____forceprint(s, keep_indent=keep_indent, anon=anon);''',
            tab+r'''pass;''',
            r'''''',
            r'''def ____forceprint(s: str, keep_indent=True, anon=False):''',
            tab+r'''global ____filetex____;''',
            tab+r'''global ____lines____;''',
            tab+r'''''',
            tab+r'''n = len(____lines____['post-compile']);''',
            tab+r'''for _s in re.split(r'\n', s):''',
            tab+tab+r'''if keep_indent:''',
            tab+tab+tab+r'''_s = ____indentation____ + _s;''',
            tab+tab+r'''print(_s, file=____filetex____);''',
            tab+tab+r'''____lines____['post-compile'].append(_s);''',
            tab+tab+r'''if anon:''',
            tab+tab+tab+r'''____lines____['anon'].append(n);''',
            tab+tab+r'''n += 1;''',
            tab+r'''''',
            tab+r'''pass;''',
            r'''''',
            r'''def ____insertbib(fname='', src='', indent='', anon=False):''',
            tab+r'''global ____filetex____;''',
            tab+r'''global ____lines____;''',
            tab+r'''global ____insertbib____;''',
            r'''''',
            tab+r'''nom, _ = os.path.splitext(fname);''',
            tab+r'''line = indent + r'\bibliography{'+nom+'}';''',
            tab+r'''print(line, file=____filetex____);''',
            tab+r'''## lies Datei ein und füge Inhalte hinzu.''',
            tab+r'''____lines____['post-compile'].append(line);''',
            tab+r'''if not src in ____lines____['bib']:''',
            tab+tab+r'''____lines____['bib'][src] = [];''',
            tab+r'''n = len(____lines____['post-compile']);''',
            tab+r'''if anon:''',
            tab+tab+r'''____lines____['anon'].append(n-1);''',
            tab+r'''elif ____insertbib____:''',
            tab+tab+r'''____lines____['bib'][src].append(n-1);''',
            tab+r'''pass;''',
            r'''''',
            r'''## PDFLATEX:''',
            r'''def ____compilelatex():''',
            tab+r'''global ____rootdir____;''',
            tab+r'''global ____filetex_name____;''',
            tab+r'''global ____filetex_name_rel____;''',
            tab+r'''global ____lines____;''',
            tab+r'''''',
            tab+r'''print('\n\nPDFLATEX WIRD AUSGEFÜHRT:');''',
            tab+r'''outfile, _ = os.path.splitext(____filetex_name____);''',
            tab+r'''proc = subprocess.Popen(['pdflatex', outfile], cwd=____rootdir____);''',
            tab+r'''proc.wait();''',
            tab+r'''print('\n\nBIBTEX WIRD AUSGEFÜHRT:');''',
            tab+r'''for src in ____lines____['bib']:''',
            tab+tab+r'''src, _ = os.path.splitext(src);''',
            tab+tab+r'''proc = subprocess.Popen(['bibtex', src], cwd=____rootdir____);''',
            tab+tab+r'''proc.wait();''',
            tab+r'''print('\n\nDOKUMENT {'+____filetex_name_rel____+'.pdf} WURDE FERTIGGESTELLT.');''',
            tab+r'''pass;''',
            r'''''',
            r'''## ERSETZUNG VON \bibliography-Befehlen durch Inhalte + Anonymisierung:''',
            r'''def ____cleanlatex():''',
            tab+r'''global ____filetex____;''',
            tab+r'''global ____filetex_name____;''',
            tab+r'''global ____lines____;''',
            tab+r'''global ____insertbib;''',
            tab+r'''''',
            tab+r'''____filetex____ = open(____filetex_name____, 'w+');''',
            tab+r'''''',
            tab+r'''bibindex = [];''',
            tab+r'''bibtext = {};''',
            tab+r'''for src in ____lines____['bib']:''',
            tab+tab+r'''bibindex += ____lines____['bib'][src];''',
            tab+tab+r'''n = len(____lines____['bib'][src]);''',
            tab+tab+r'''biblines = [];''',
            tab+tab+r'''try:''',
            tab+tab+tab+r'''fp = open(src, 'r');''',
            tab+tab+tab+r'''lines = fp.readlines();''',
            tab+tab+tab+r'''fp.close();''',
            tab+tab+tab+r'''for bibline in lines:''',
            tab+tab+tab+tab+r'''bibline = re.sub(r'[\s\n]+$', '', bibline);''',
            tab+tab+tab+tab+r'''bibline = re.sub(r'^(.*)\%(.*)', r'\1', bibline);''',
            tab+tab+tab+tab+r'''if re.match(r'^\s*\%.*', bibline):''',
            tab+tab+tab+tab+tab+r'''continue;''',
            tab+tab+tab+tab+r'''biblines.append(bibline);''',
            tab+tab+tab+tab+r'''pass;''',
            tab+tab+r'''except:''',
            tab+tab+tab+r'''biblines = None;''',
            tab+tab+tab+r'''print('ACHTUNG! Bib-Datei {'+src+'} konnte nicht gefunden werden');''',
            tab+tab+r'''bibtext[src] = biblines;''',
            tab+tab+r'''pass;''',
            tab+r'''''',
            tab+r'''nr_lines = len(____lines____['post-compile']);''',
            tab+r'''for n, line in enumerate(____lines____['post-compile']):''',
            tab+tab+r'''if n in ____lines____['anon']:''',
            tab+tab+tab+r'''continue;''',
            tab+tab+r'''if n in bibindex:''',
            tab+tab+tab+r'''src = None''',
            tab+tab+tab+r'''for src_ in ____lines____['bib']:''',
            tab+tab+tab+tab+r'''if n in ____lines____['bib'][src_]:''',
            tab+tab+tab+tab+tab+r'''src = src_;''',
            tab+tab+tab+tab+tab+r'''break;''',
            tab+tab+tab+tab+r'''continue;''',
            tab+tab+tab+r'''try:''',
            tab+tab+tab+tab+r'''if not src is None and not bibtext[src] is None:''',
            tab+tab+tab+tab+tab+r'''indent = re.sub(r'^(\s*)(\S|).*', r'\1', line);''',
            tab+tab+tab+tab+tab+r'''for bibline in bibtext[src]:''',
            tab+tab+tab+tab+tab+tab+r'''print(indent + bibline, file=____filetex____);''',
            tab+tab+tab+tab+tab+tab+r'''pass;''',
            tab+tab+tab+tab+tab+r'''continue;''',
            tab+tab+tab+r'''except:''',
            tab+tab+tab+tab+r'''pass;''',
            tab+tab+r'''if n == nr_lines-1 and line == '':''',
            tab+tab+tab+r'''continue;''',
            tab+tab+r'''print(line, file=____filetex____);''',
            tab+tab+r'''pass;''',
            tab+r'''''',
            tab+r'''____filetex____.close();''',
            tab+r'''pass;''',
            r'''''',
            r'''def ____compilephpytex():''',
            tab+r'''global ____filetex____;''',
            tab+r'''global ____lines____;''',
            tab+r'''global ____reseed;''',
            tab+r'''global ____print;''',
            tab+r'''global ____qp;''',
            tab+r'''global ____ignore;''',
            tab+r'''global __ROOT__;''',
            tab+r'''global __DIR__;''',
            tab+r'''global __FNAME__;''',
            tab+r'''global __LINENR__;''',
            tab+r'''''',
            tab+r'''____ignore('init');''',
            r'''''',
        ];
        self.LENPRECODE = len(lines_pre);
        lines = lines_pre + lines + [
            tab+r'''____reset_indentation();''',
            tab+r'''pass;''',
            r'''''',
            r'''try:''',
            tab+r'''____filetex____ = open(____filetex_name____, 'w+');''',
            tab+r'''____compilephpytex();''',
            tab+r'''____filetex____.close();''',
            tab+r'''if ____compilelatex____:''',
            tab+tab+r'''____compilelatex();''',
            tab+r'''else:''',
            tab+tab+r'''print('\nPDFLATEX WIRD NICHT AUSGEFÜHRT.');''',
            tab+r'''____cleanlatex();''',
            r'''except Exception as e:''',
            tab+r'''print("----------------------------------------------------------------");''',
            tab+r'''print("!!! (PH(p)y)TeX Kompilationsfehler !!!");''',
            tab+r'''if ____error_eval____:''',
            tab+tab+r'''____last_latex____ = eval("'"+____last_latex____+"'");''',
            tab+tab+r'''print("  DATEI: "+str(__FNAME__));''',
            tab+tab+r'''print("  ZEILE: "+str(__LINENR__ + 1)+" (lokale Position innerhalb Datei).");''',
            tab+tab+r'''print("!!! Zeile konnte nicht evaluiert werden !!!");''',
            tab+tab+r'''print("----------------------------------------------------------------");''',
            tab+tab+r'''print(____last_latex____);''',
            tab+tab+r'''print("----------------------------------------------------------------");''',
            tab+tab+r'''____forceprint("----------------------------------------------------------------");''',
            tab+tab+r'''____forceprint("!!! (PH(p)y)TeX-FEHLER !!!");''',
            tab+tab+r'''____forceprint("  DATEI: "+str(__FNAME__));''',
            tab+tab+r'''____forceprint("  ZEILE: "+str(__LINENR__ + 1)+" (lokale Position innerhalb Datei).");''',
            tab+tab+r'''____forceprint("!!! Zeile konnte nicht evaluiert werden !!!");''',
            tab+tab+r'''____forceprint("----------------------------------------------------------------");''',
            tab+tab+r'''____forceprint(____last_latex____);''',
            tab+tab+r'''____forceprint("----------------------------------------------------------------");''',
            tab+r'''else:''',
            tab+tab+r'''print("----------------------------------------------------------------");''',
            tab+tab+r'''print(sys.exc_info())''',
            tab+tab+r'''print(e)''',
            tab+tab+r'''print("----------------------------------------------------------------");''',
            r'''''',
        ];
        return lines;


    def ____execmetacode(self, lines=[], fname='', debug=False, cmpl=False):
        lines = self.____createmetacode(lines=lines, fname=fname, cmpl=cmpl);
        fname_rel, _, _ = self.____extractfilename(path=fname, relative=True, ext='');
        ____filetex____ = open(fname, 'w+');
        ____filetex____.write('\n'.join(lines));
        ____filetex____.close();

        if debug:
            print('\nSiehe Outputdatei: {'+fname_rel+'.tex}.');
            print('\n(PH(p)y)TeX FERTIG.');
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

                print("----------------------------------------------------------------");
                print("!!! (PH(p)y)TeX Kompilation hat versagt !!!");
                print("  DATEI: "+__FNAME__);
                print("  ZEILE: "+str(__LINENR__ + 1)+" (lokale Position innerhalb Datei).");
                print("!!! Syntaxfehler !!!");
                print("----------------------------------------------------------------");
                print(line_err);
                print("----------------------------------------------------------------");
                print("(siehe Outputdatei)");

                ____filetex____ = open(fname, 'w+');
                print('\n'.join([line for k, ignore, line in precompilelines if k < n and not ignore is True]), file=____filetex____);
                print("----------------------------------------------------------------", file=____filetex____);
                print("!!! (PH(p)y)TeX Kompilation hat versagt !!!", file=____filetex____);
                print("  DATEI: "+__FNAME__, file=____filetex____);
                print("  ZEILE: "+str(__LINENR__ + 1)+" (lokale Position innerhalb Datei).", file=____filetex____);
                print("!!! Syntaxfehler !!!", file=____filetex____);
                print("----------------------------------------------------------------", file=____filetex____);
                print('\n'.join([line for k, ignore, line in precompilelines if k == n and ignore is False]), file=____filetex____);
                print("----------------------------------------------------------------", file=____filetex____);
                ____filetex____.close();
            except:
                print(err);

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
        filecontents                          = [],
        verbatim: List[Tuple[int, bool, str]] = [],
        struct                                = [],
        filename                              = Dict[str, str],
        anon                                  = False,
        mute                                  = False,
        silent                                = False,
        indent                                = None,
        params                                = {},
        dateityp                              = None,
        chain                                 = []
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
            print('    '*(indent['struct']+1)+'— [∞] '+fname_curr+'; (∞-Schleife! Datei wird nicht hinzugefügt!)');
            struct.append('%%'+'    '*(indent['struct']+1)+'— [∞] '+fname_curr+'; (∞-Schleife! Datei wird nicht hinzugefügt!)');
            return True;

        ## Falls Dateiquelle nicht existiert oder sich nicht öffnen lässt:
        if not bool_getfile:
            self.ERROR = True;
            if not dateityp == 'head':
                print('    '*(indent['struct']+1)+'— [x] '+fname_curr+';');
                struct.append('%%'+'    '*(indent['struct']+1)+'— [x] '+fname_curr+';');
            print("----------------------------------------------------------------");
            print("!!! (PH(p)y)TeX Kompilationsfehler !!!");
            print("!!! Folgende Datei existiert nicht / ließ sich nicht öffnen:");
            print("----------------------------------------------------------------");
            print(src);
            print("----------------------------------------------------------------");
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
            print('    '*(indent['struct'] + 1)+'— '+fname_curr+';');
            struct.append('%%'+'    '*(indent['struct'] + 1)+'— '+fname_curr+';');
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
            m = re.match(r'^(\s*)(?:\<{3}|\`{3})\s*((?![\<\`]).*\S|)\s*$', line);
            m_inline = re.match(r'^\s*(?:\<{3}|\`{3}).*(?:\>{3}|\`{3})', line);
            if m and not m_inline:
                if mute:
                    continue;
                inline_indentation = m.group(1);
                code_language, code_flags, code_options = self.____get_code_language_and_options(m.group(2));
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
                    # self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                    #     self.INDENTCHARACTER*self.INDENTATION.start + "____set_indentation('{}');".format(inline_indentation),
                    # ], mode='direkt');
                self.____addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['<<< '+code_language], mode='direkt');
                continue;

            # Zeile: Ende eines Codeblocks
            m = re.match(r'^\s*(?:\>{3}|\`{3})\s*$', line);
            if m:
                if mute:
                    continue;
                bool_insidecode = False;
                if code_option_print:
                    self.INDENTATION.last = self.INDENTATION.start;
                    self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
                        self.INDENTCHARACTER*self.INDENTATION.last + '____print(____temp_value____);',
                        self.INDENTCHARACTER*self.INDENTATION.last + 'del ____temp_value____;',
                    ], mode='direkt');
                self.____addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['>>>'], mode='direkt');
                continue;

            # Zeile: Python-Code
            if bool_insidecode and code_language == 'python':
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

            if bool_insidecode: # aktuell wird nur py unterstützt
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
                    print("----------------------------------------------------------------");
                    print("!!! (PH(p)y)TeX Kompilationsfehler !!!");
                    print("  DATEI: "+fname_curr);
                    print("  ZEILE: "+str(linenr+1)+" (lokale Position innerhalb Datei).");
                    print("!!! <<< input >>>-Befehle konnte nicht evaluiert werden !!!");
                    print("----------------------------------------------------------------");
                    print(line);
                    print("----------------------------------------------------------------");
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

                print('    '*(indent_['struct']+1)+'|');
                struct.append('%%'+'    '*(indent_['struct']+1)+'|');
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
                    print("----------------------------------------------------------------");
                    print("!!! (PH(p)y)TeX Kompilationsfehler !!!");
                    print("  DATEI: "+fname_curr);
                    print("  ZEILE: "+str(linenr+1)+" (lokale Position innerhalb Datei).");
                    print("!!! <<< bibliography >>>-Befehl konnte nicht evaluiert werden !!!");
                    print("----------------------------------------------------------------");
                    print(line);
                    print("----------------------------------------------------------------");
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
                    print('    '*(indent_['struct']+1)+'|');
                    print('    '*(indent_['struct']+1)+'— '+nom+';');
                    struct.append('%%'+'    '*(indent_['struct']+1)+'|');
                    struct.append('%%'+'    '*(indent_['struct']+1)+'— '+nom+';');
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

            # Zeile: Kommentar -> entscheide, ob Zeile übersprungen werden soll:
            m = re.match(r'^\s*(\%+).*', line);
            if m:
                n_zeichen = len(m.group(1));
                if params['no-comm'] or (params['no-comm-auto'] and n_zeichen == 1):
                    ## <continue: i. e. remove line>
                    continue;
                ## otherwise display line...

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
        lines=[],
        verbatim: List[Tuple[int, bool, str]] = [],
        linenr=None,
        expr=[],
        verbexpr=None,
        indent=None,
        anon=False,
        mode='direkt',
        ignore=False
    ):
        if mode == 'meta':
            for e in expr:
                lines += self.____metaprint(linenr=linenr, expr=e, indent=indent, anon=anon);
        elif mode == 'none':
            pass;
        else:
            lines += expr;
        if isinstance(verbexpr, list):
            verbatim += [(linenr, ignore, line) for line in verbexpr];
        else:
            verbatim += [(linenr, ignore, line) for line in expr];
        return;

    def ____extractfilename(self, path: str, root=None, split=False, relative=None, relative_to=None, ext=None) -> Tuple[str, str, str]:
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

    def ____expandquickpython(self, expr='', contains_latex=False, evaluate=True):
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

    def ____postcompile(self, key=None, val='', indent=None, symbolic=True, set_precompile=False):
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

    def ____remove_quotes(self, s: str):
        return re.sub(r'^[\'\"]+|[\'\"]+$', '', s);

    def ____escapecharacters(self, s: str):
        s = re.sub(r'(\\+)', r'\1\1', s);
        s = re.sub(r'\n', r'\\n', s);
        s = re.sub(r'\t', r'\\t', s);
        s = re.sub(r'\"', r'\\u0022', s);
        s = re.sub(r'\'', r'\\u0027', s);
        # s = re.sub(r'\%', slash+'u0025', s);
        return s;

    ## verwandelt Strings in starke Metastrings:
    def ____metastring(self, s: str):
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

    def ____metaprint(self, indent=None, linenr=None, expr='', anon=False):
        if indent is None or indent < self.INDENTCODE:
            indent = self.INDENTCODE;
        expr = self.____metastring(expr);
        if anon:
            line = "____print(eval(____qp("+str(linenr)+", "+expr+"), locals()), keep_indent=False, anon=True);";
        else:
            line = "____print(eval(____qp("+str(linenr)+", "+expr+"), locals()), keep_indent=False);";
        lines = [self.INDENTCHARACTER*indent + line];
        return lines;

    def ____countindents(self, s: str, pattern = None):
        pattern = pattern if isinstance(pattern, str) else self.INDENTCHARACTER_re;
        return len(re.findall(pattern, s));

    def ____censorpath(self, path: str):
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


phpytexTranspiler().run();
