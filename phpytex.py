#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#############################################################################
# ENTITÄT: (PH(p)y)TeX														#
# AUTOR: R-Logik, Deutschland. https://github.com/RLogik/phpytex			#
# ERSTELLUNGSDATUM: 27.11.2018												#
# ZULETZT VERÄNDERT: 30.05.2019												#
# VERSION: 3·1·5															#
# HINWEISE:																	#
#																			#
#	Installation:															#
# 	~~~~~~~~~~~~~															#
# 	1. Evtl. die ersten 2 Zeilen dieser Dateie an deinem System anpassen.	#
# 	2. In einen Ordner legen, der im PATH liegt.							#
# 	3. Die .py-Extension entfernen											#
# 	4. Mac OSX / Linux:														#
# 	sudo chmod 755 phpytex													#
# 	in Terminal ausführen.													#
# 	(Oder den äquivalenten Befehl für Windows.)								#
# 	5. Befehl ist jetzt überall verfügbar.									#
# 	6. Mit																	#
# 		phpytex -help														#
# 		phpytex -man														#
# 	die Anleitungen aufrufen.												#
#	oder https://github.com/RLogik/phpytex >> README.md konsultieren.		#
#																			#
#############################################################################


import sys;
import os;
import re;
import numpy;
import numpy as np;
import subprocess;

class ____phpytexcompiler:
	def __init__(self):
		## GLOBALE VARIABLE
		self.GLOBALVARS = {'__ROOT__':'.', '__DIR__':'.'};
		self.INCLUDES = [];
		self.CURRDIR = os.path.abspath('');
		self.ROOTDIR = self.CURRDIR;
		self.INSERTBIB = False;
		self.ERROR = False;
		self.PYERROR = False;
		self.STAMPDATEI = None;
		self.HAUPTDATEI = None;
		self.OUTPUTDATEI = None;
		self.GETEILTERORDNER = None;
		self.LENPRECODE = 0;
		self.LENGTHOFOUTPUT = 0; ## <-- Anzahl der Zeilen.
		self.MAXLENGTH = 10000; ## verhindere, dass die Datei zu groß wird.
		self.TOOLONG = False;
		# self.SEED = np.random.get_state()[1][0];
		self.SEED = np.random.choice(100000000);
		self.PRECOMPILELINES = [];

		## Hier kann man optional den Defaulttabcharakter bestimmen:
		self.INDENTCODE = 1;
		self.INDENTCHARACTER = '    ';
		self.INDENTCHARACTER_re = r'    ';
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

		self.HAUPTDATEI = params['i'];
		self.OUTPUTDATEI = params['o'];
		if 'path' in params:
			self.ROOTDIR = params['path'];
			self.GLOBALVARS['__ROOT__'] = self.ROOTDIR;

		self.HAUPTDATEI = self.____extractfilename(path=self.HAUPTDATEI, relative=True);
		self.OUTPUTDATEI = self.____extractfilename(path=self.OUTPUTDATEI, relative=True, ext='');
		if self.HAUPTDATEI == self.OUTPUTDATEI:
			print('\n\tACHTUNG! Die Namen der py-tex-Datei und Outputdatei dürfen nicht übereinstimmen!\n');
			return;
		hauptfile = self.____extractfilename(path=self.OUTPUTDATEI, relative=False, ext='tex');

		if 'head' in params:
			self.STAMPDATEI = params['head'];
			self.STAMPDATEI = self.____extractfilename(path=self.STAMPDATEI, relative=True);

		debug = params['debug'];
		cmpl = not params['no-compile'];
		silent = params['silent'];
		# anon = params['anon']; # <— funktioniert nicht richtig
		if 'share' in params:
			self.GETEILTERORDNER = params['share'];
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
		np.random.seed(self.SEED); ## nur ein Mal ausführen!
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
	def ____getarguments(self, sysargs):
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
		fname_rel = self.____extractfilename(path=fname, relative=True, ext='');
		tab = self.INDENTCHARACTER;
		share_folder = str(None);
		if not self.GETEILTERORDNER is None:
			share_folder = "'"+self.GETEILTERORDNER+"'";
		lines_pre = [
			r'''import sys;''',
			r'''import os;''',
			r'''import re;''',
			r'''import traceback;''',
			r'''import subprocess;''',
			r'''import numpy;''',
			r'''import numpy as np;''',
			r'''''',
			r'''''',
			r'''____lines____ = {'post-compile':[], 'anon':[], 'bib':{}};''',
			r'''____indent____ = ''' + "'" + self.INDENTCHARACTER_re + "'" + ''';''',
			r'''____filetex_name____ = "'''+fname+'''";''',
			r'''____filetex_name_rel____ = "'''+fname_rel+'''";''',
			r'''____filetex____ = None;''',
			r'''____sharefolder____ = '''+share_folder+''';''',
			r'''____error_toolong____ = False;''',
			r'''____outputlength____ = 0;''',
			r'''____maxlength____ = '''+str(self.MAXLENGTH)+''';''',
			r'''____insertbib____ = '''+str(self.INSERTBIB)+''';''',
			r'''____compilelatex____ = '''+str(cmpl)+''';''',
			r'''____last_latex____ = None;''',
			r'''____rootdir____ = "'''+self.ROOTDIR+'''";''',
			r'''____seed____ = '''+str(self.SEED)+''';''',
			r'''__ROOT__ = None;''',
			r'''__DIR__ = None;''',
			r'''__SKIP__ = None;''',
			r'''__FNAME__ = None;''',
			r'''__LINENR__ = None;''',
			r'''____error_eval____ = False;''',
			r'''''',
			r'''''',
			r'''## reseed-funktion:''',
			r'''def ____reseed():''',
			tab+r'''global ____seed____;''',
			tab+r'''np.random.seed(____seed____);''',
			tab+r'''return True;''',
			r'''''',
			r'''''',
			r'''class ____skipclass:''',
			tab+r'''def __init__(self):''',
			tab+tab+r'''self.len = 0;''',
			tab+tab+r'''self.chain = [];''',
			tab+tab+r'''self.status = False;''',
			tab+tab+r'''pass;''',
			r'''''',
			tab+r'''def get(self):''',
			tab+tab+r'''self.status = (True in self.chain);''',
			tab+tab+r'''return self.status;''',
			r'''''',
			tab+r'''def set(self, val):''',
			tab+tab+r'''if self.len == 0:''',
			tab+tab+tab+r'''return False;''',
			tab+tab+r'''self.chain[self.len-1] = val;''',
			tab+tab+r'''self.get();''',
			tab+tab+r'''return True;''',
			r'''''',
			tab+r'''def add(self, val):''',
			tab+tab+r'''self.chain.append(val);''',
			tab+tab+r'''self.len += 1;''',
			tab+tab+r'''self.get();''',
			tab+tab+r'''pass;''',
			r'''''',
			tab+r'''def rem(self):''',
			tab+tab+r'''self.chain = self.chain[:-1];''',
			tab+tab+r'''self.len -= 1;''',
			tab+tab+r'''self.get();''',
			tab+tab+r'''pass;''',
			r'''''',
			tab+r'''pass;''',
			r'''''',
			r'''''',
			r'''def ____ignore(opt, val=None):''',
			tab+r'''global __SKIP__;''',
			tab+r'''global ____skipclass;''',
			r'''''',
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
			r'''''',
			tab+r'''return expr;''',
			r'''''',
			r'''''',
			r'''# record+print-to-latex''',
			r'''def ____print(s, anon=False):''',
			tab+r'''if ____ignore('get'):''',
			tab+tab+r'''return;''',
			tab+r'''''',
			tab+r'''global ____filetex____;''',
			tab+r'''global ____lines____;''',
			tab+r'''global ____error_eval____;''',
			tab+r'''global ____error_toolong____;''',
			tab+r'''global ____outputlength____;''',
			tab+r'''global ____maxlength____;''',
			tab+r'''''',
			tab+r'''____error_eval____ = False;''',
			tab+r'''if ____error_toolong____:''',
			tab+tab+r'''return;''',
			tab+r'''____outputlength____ += 1;''',
			tab+r'''if ____outputlength____ > ____maxlength____:''',
			tab+tab+r'''____error_toolong____ = True; ''',
			tab+r'''print(s, file=____filetex____);''',
			tab+r'''____lines____['post-compile'].append(s);''',
			tab+r'''if anon:''',
			tab+tab+r'''n = len(____lines____['post-compile']);''',
			tab+tab+r'''____lines____['anon'].append(n-1);''',
			tab+r'''return;''',
			r'''''',
			r'''''',
			r'''def ____forceprint(s, anon=False):''',
			tab+r'''global ____filetex____;''',
			tab+r'''global ____lines____;''',
			tab+r'''''',
			tab+r'''print(s, file=____filetex____);''',
			tab+r'''____lines____['post-compile'].append(s);''',
			tab+r'''if anon:''',
			tab+tab+r'''n = len(____lines____['post-compile']);''',
			tab+tab+r'''____lines____['anon'].append(n-1);''',
			tab+r'''return;''',
			r'''''',
			r'''''',
			'''def ____insertbib(fname='', src='', indent='', anon=False):''',
			tab+r'''global ____filetex____;''',
			tab+r'''global ____lines____;''',
			tab+r'''global ____insertbib____;''',
			tab+r'''''',
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
			tab+r'''return;''',
			r'''''',
			r'''''',
			r'''## PDFLATEX:''',
			r'''def ____compilelatex():''',
			tab+r'''global ____rootdir____;''',
			tab+r'''global ____sharefolder____;''',
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
			tab+r'''if ____sharefolder____ is None:''',
			tab+tab+r'''return;''',
			tab+r'''print('\nOUTPUT WIRD IN GETEILTEN ORDNER VERLEGT.');''',
			tab+r'''_, nom = os.path.split(____filetex_name_rel____)''',
			tab+r'''print('\tzum "'+____sharefolder____+'/'+nom+'.pdf" kopieren...');''',
			tab+r'''os.system('cp "'+outfile+'.pdf" "'+____sharefolder____+'/'+nom+'.pdf"');''',
			tab+r'''print('\t... kopieren erfolgreich.');''',
			tab+r'''return;''',
			r'''''',
			r'''''',
			r'''## ERSETZUNG VON \bibliography-Befehlen durch Inhalte + Anonymisierung:''',
			r'''def ____cleanlatex():''',
			tab+r'''global ____filetex____;''',
			tab+r'''global ____filetex_name____;''',
			tab+r'''global ____lines____;''',
			tab+r'''global ____insertbib;''',
			r'''''',
			tab+r'''____filetex____ = open(____filetex_name____, 'w+');''',
			r'''''',
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
			r'''''',
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
			tab+tab+r'''print(line, file=____filetex____);''',
			tab+tab+r'''pass;''',
			r'''''',
			tab+r'''____filetex____.close();''',
			tab+r'''return;''',
			r'''''',
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
			r'''''',
			r'''''',
			tab+r'''____ignore('init');''',
			r'''''',
			r'''''',
		];
		self.LENPRECODE = len(lines_pre);
		lines = lines_pre + lines + [
			r'''''',
			r'''''',
			tab+r'''return;''',
			r'''''',
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
			r'''except:''',
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
			tab+tab+r'''print("----------------------------------------------------------------");''',
			r'''''',
		];
		return lines;

	def ____execmetacode(self, lines=[], fname='', debug=False, cmpl=False):
		lines = self.____createmetacode(lines=lines, fname=fname, cmpl=cmpl);

		if debug:
			fname_rel = self.____extractfilename(path=fname, relative=True, ext='');
			____filetex____ = open(fname, 'w+');
			____filetex____.write('\n'.join(lines));
			____filetex____.close();
			print('\nSiehe Outputdatei: {'+fname_rel+'.tex}.');
			print('\n(PH(p)y)TeX FERTIG.');
			return;

		try:
			code = compile('\n'.join(lines), '<string>', mode='exec');
			exec(code);
		except:
			self.ERROR = True;
			self.PYERROR = True;
			typ, err, tb = sys.exc_info();

			try:
				n = err.lineno - 1;
				line_err = lines[n];
				n -= self.LENPRECODE;
				linenr = -1; ## globale Zeilennummer
				precompilelines = [];
				__LINENR__ = '???';
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
						__LINENR__ = k; ## lokale Zeilennummer innerhalb Datei
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
				'%% ******************************************************************************',
				'%% DATEIAUFBAU:',
				'%% ~~~~~~~~~~~~',
				'%%',
			] + struct + [
				'%%',
				'%% Gebrauchter SEED: '+str(self.SEED),
				'%% [x] = Dokument fehlt.',
				'%% ******************************************************************************',
			], mode='meta');

		lines = preamble + lines;
		self.PRECOMPILELINES = verbatim + self.PRECOMPILELINES;

		return lines, erfolg;

	def ____knit(self, root=None, filecontents=[], verbatim=[], struct=[], filename={}, anon=False, mute=False, silent=False, indent=None, params={}, dateityp=None, chain=[]):
		if self.ERROR:
			return False;

		if root is None:
			root = self.ROOTDIR;
		if dateityp is None:
			dateityp = 'tex';
		if indent is None:
			indent = {'py':self.INDENTCODE, 'tex':0, 'struct':0};

		## Bestimme Dateiquelle und neuen Root:
		bool_getfile = True;
		fname_src = filename['src'];
		fname_main = filename['main'];
		if dateityp in ['head', 'tex', 'py']:
			if dateityp in ['head', 'tex']:
				_, ext = os.path.splitext(fname_src);
				if ext == '':
					fname_src += '.tex';
			nom, root, fname = self.____extractfilename(path=fname_src, root=root, split=True);
			src = nom;
		else:
			bool_getfile = False;

		fname_curr = nom;
		if anon:
			nom = self.____censorpath(path=nom);

		## Prüfe, ob Datei schon inkludiert wurde (entlang aktueller input-Kette):
		if src in chain:
			print('    '*(indent['struct']+1)+'— [∞] '+nom+'; (∞-Schleife! Datei wird nicht hinzugefügt!)');
			struct.append('%%'+'    '*(indent['struct']+1)+'— [∞] '+nom+'; (∞-Schleife! Datei wird nicht hinzugefügt!)');
			return True;
		else:
			chain.append(src);

		## Prüfe, ob Dateiquelle existiert:
		if bool_getfile:
			bool_getfile = os.path.isfile(src);
		## Versuche Dateiquelle zu öffnen:
		if bool_getfile:
			try:
				fp = open(src, 'r');
			except:
				bool_getfile = False;
		## Falls Dateiquelle nicht existiert oder sich nicht öffnen lässt:
		if not bool_getfile:
			self.ERROR = True;
			if not dateityp == 'head':
				print('    '*(indent['struct']+1)+'— [x] '+nom+';');
				struct.append('%%'+'    '*(indent['struct']+1)+'— [x] '+nom+';');
			print("----------------------------------------------------------------");
			print("!!! (PH(p)y)TeX Kompilationsfehler !!!");
			print("!!! Folgende Datei existiert nicht / ließ sich nicht öffnen:");
			print("----------------------------------------------------------------");
			print(src);
			print("----------------------------------------------------------------");
			return False;

		## Berechne relative Pfade:
		backtoorigin = self.____extractfilename(path='.', root=self.ROOTDIR, relative=True, relative_to=root);
		origintohere = self.____extractfilename(path='.', root=root, relative=True, relative_to=self.ROOTDIR);
		self.GLOBALVARS['__ROOT__'] = backtoorigin;
		self.GLOBALVARS['__DIR__'] = '.';
		orientation = [];
		orientation += self.____postcompile(key='__ROOT__', val=origintohere+'/'+backtoorigin, symbolic=False);
		orientation += self.____postcompile(key='__DIR__', val=origintohere, symbolic=False);
		orientation += self.____postcompile(key='__FNAME__', val=src, symbolic=False);
		self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=orientation, mode='direkt');
		lines_ = self.____postcompile(key='__LINENR__', val=None, symbolic=False);
		self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=lines_, mode='direkt');
		self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
			self.INDENTCHARACTER*self.INDENTCODE + r"____ignore('add');",
		], mode='direkt');

		## Output für Hauptdatei:
		if not mute:
			print('    '*(indent['struct']+1)+'— '+nom+';');
			struct.append('%%'+'    '*(indent['struct']+1)+'— '+nom+';');
			if not silent:
				self.____addpytexline(lines=filecontents, verbatim=verbatim, indent=indent['py'], expr=[
					'',
					self.INDENTCHARACTER*indent['struct']+'%% ******************************************************************************',
					self.INDENTCHARACTER*indent['struct']+'%% DATEI: '+nom,
					self.INDENTCHARACTER*indent['struct']+'%% ******************************************************************************',
					'',
				], mode='meta');

		## Zeilen einlesen und interpretieren:
		lines = fp.readlines();
		fp.close();
		erfolg = True;
		chain_ = chain[::];
		bool_belowcontent = False;
		bool_belowfile = False;
		bool_insidecomment = False;
		bool_insidecode = False;
		code_language = '';
		indent_code_offset = 0;
		len_comm = 0;
		len_empty = 0;

		for linenr, line in enumerate(lines):
			if self.ERROR:
				break;

			# Entferne alle whitespaces am Ende.
			line = re.sub(r'[\s\n]+$', '', line);

			# Dokumentart ist Python:
			if dateityp == 'py':
				line = self.INDENTCHARACTER*self.INDENTCODE + line;
				line = re.sub(r'\s+$', '', line);
				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
				continue;

			# Zeile: leer
			m = re.match(r'^\s*$', line);
			if m:
				if bool_insidecomment:
					len_comm += 1;
				if bool_insidecode and code_language == 'python':
					self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[''], mode='direkt');
					continue;
				if bool_insidecode and not re.match(r'tex',code_language):
					continue;
				if bool_belowfile:
					continue;
				if bool_belowcontent:
					if len_empty < 1: # 1 = maximale länge von einem leeren Block
						self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, indent=indent['py'], expr=[''], anon=anon, mode='meta');
					len_empty += 1;
					continue;
				if bool_insidecomment:
					continue;
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
				lines_ = self.____postcompile(key=nom, val=val, indent=indent['py'], symbolic=True, set_precompile=True);
				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, verbexpr=['<<< set '+re.sub(r'^\s+', '', e)+'; >>>' for e in line], mode='direkt');
				continue;

			# Zeile: Quick-Python ESCAPE_ONCE
			m = re.match(r'^\s*\<{3}\s*escape_once(;|)\s*\>{3}', line);
			if not bool_insidecode and m:
				if mute:
					continue;
				line = self.INDENTCHARACTER*indent['py'] + "pass;";
				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], verbexpr=['<<< esape_once; >>>'], mode='direkt');
				indent['py'] -= 1;
				if indent['py'] < self.INDENTCODE:
					indent['py'] = self.INDENTCODE;
				continue;

			# Zeile: Quick-Python ESCAPE
			m = re.match(r'^\s*\<{3}\s*escape(;|)\s*\>{3}', line);
			if not bool_insidecode and m:
				if mute:
					continue;
				line = self.INDENTCHARACTER*indent['py'] + "pass;";
				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], verbexpr=['<<< escape; >>>'], mode='direkt');
				indent['py'] = self.INDENTCODE;
				continue;

			# Zeile: Quick-Python IGNORE
			m = re.match(r'^\s*\<{3}\s*ignore(;|)\s*\>{3}', line);
			if not bool_insidecode and m:
				if mute:
					continue;
				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
					self.INDENTCHARACTER*indent['py'] + r"____ignore('set', True);",
				], verbexpr=['<<< ignore; >>>'], mode='direkt');
				indent['py'] = self.INDENTCODE;
				continue;

			# Zeile: Quick-Python UNIGNORE
			m = re.match(r'^\s*\<{3}\s*unignore(;|)\s*\>{3}', line);
			if not bool_insidecode and m:
				if mute:
					continue;
				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
					self.INDENTCHARACTER*indent['py'] + r"____ignore('set', False);",
				], verbexpr=['<<< unignore; >>>'], mode='direkt');
				indent['py'] = self.INDENTCODE;
				continue;

			#  --- unter Arbeit (Problem mit der Indentation-Logik) --- #
			# # Zeile: Quick-Python Python-Controlstatement (<<< ... : >>>)
			# # Indentation wie beim letzten Zustand von python-Code.
			# m = re.match(r'^\s*(?:\<{3}|\`{3})\s*((?![\<\`]).*\:)\s*(?:\>{3}|\`{3}).*$', line);
			# if not bool_insidecode and m:
			# 	self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
			# 		self.INDENTCHARACTER*indent['py'] + m.group(1)
			# 	], mode='direkt');
			# 	continue;

			# Zeile: Start eines Codeblocks
			m = re.match(r'^(\s*)(?:\<{3}|\`{3})\s*((?![\<\`]).*\S|)\s*$', line);
			m_inline = re.match(r'^\s*(?:\<{3}|\`{3}).*(?:\>{3}|\`{3})', line);
			if m and not m_inline:
				if mute:
					continue;
				indent_code_offset = self.____countindents(m.group(1));
				code_language = m.group(2);
				bool_insidecode = True;
				self.____addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['<<< '+code_language], mode='direkt');
				continue;

			# Zeile: Ende eines Codeblocks
			m = re.match(r'^\s*(?:\>{3}|\`{3})\s*$', line);
			if m:
				if mute:
					continue;
				indent_code_offset = 0;
				bool_insidecode = False;
				self.____addpytexline(ignore=-1, lines=[], verbatim=verbatim, linenr=linenr, expr=['>>>'], mode='direkt');
				continue;

			# Zeile: Python-Code
			if bool_insidecode and code_language == 'python':
				if mute:
					continue;
				# Einrückung berechnen:
				m = re.match(r'^(\s*)(.*)$', line);
				len_indent = self.____countindents(m.group(1)) - indent_code_offset
				if len_indent < self.INDENTCODE:
					len_indent = self.INDENTCODE;
				line = self.INDENTCHARACTER*len_indent + m.group(2);

				# Zeile: Python-Kommentar aber mit evtl. falschem Zeichen (LaTeX, Javascript, etc.).
				m = re.match(r'^\s*(?:\#|\%|\/\/)(.*)$', line);
				if m:
					line = self.INDENTCHARACTER*len_indent + '#'+m.group(1);
					self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');
					continue;

				# wenn nicht leer od. Kommentarzeile, dann python-Indent updaten.
				indent['py'] = len_indent;

				# Zeile: ignore / unignore.
				m = re.match(r'^\s*(ignore|unignore)(?:\;|$|\s*\#.*)', line);
				if m:
					control = m.group(1);
					self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[
						self.INDENTCHARACTER*indent['py'] + r"____ignore('set', "+str(control == 'ignore')+r");",
					], mode='direkt');
					continue;

				# Zeile: Kopf eines Indent-Blocks
				m = re.match(r'^\s*.*:(?:\s*\#.*|\s*)$', line);
				if m:
					indent['py'] += 1;
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
				nom_init = nom;
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

				nom = self.____extractfilename(path=nom_sub, root=root, relative=False);
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
				nom  = self.____extractfilename(path=nom_sub, root=root);
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
					val = self.INDENTCODE;
					if (key == 'tex' and ext == 'tex') or key == 'struct':
						val = indent[key] + 1;
					indent_[key] = val;

				print('    '*(indent_['struct']+1)+'|');
				struct.append('%%'+'    '*(indent_['struct']+1)+'|');
				erfolg_ = self.____knit(filecontents=filecontents, verbatim=verbatim, struct=struct, filename=filename_, anon=anon_, mute=mute, silent=silent, indent=indent_, params=params, dateityp=ext, chain=chain_[::]);
				erfolg = erfolg and erfolg_;

				self.GLOBALVARS['__ROOT__'] = backtoorigin;
				self.GLOBALVARS['__DIR__'] = '.';
				self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, linenr=linenr, expr=orientation, mode='direkt');
				lines_ = self.____postcompile(key='__LINENR__', val=linenr, symbolic=False);
				self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, linenr=linenr, expr=lines_, mode='direkt');

				bool_belowcontent = False;
				bool_belowfile = True;
				bool_insidecomment = False;
				len_empty = 0;
				len_comm = 0;
				continue;

			# Zeile: <<< bibliography... >>>
			m = re.match(r'^(\s*)\<{3}\s*(bibliography(?:_once|_anon|_anon_once|_once_anon|))\s+(.*\S|)\s*\>{3}', line);
			nom = None;
			if m:
				tex_indent = m.group(1);
				typ = m.group(2);
				nom = m.group(3);
				nom = re.sub(r'^[\s]+|[\s\;]+$', '', nom);
				nom_init = nom;
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
					continue;

				nom  = self.____extractfilename(path=nom_sub, root=root, relative=False, ext='bib');

				## prüfe, ob Datei schon inkludiert wurde:
				if re.search(r'once', typ) and nom in self.INCLUDES:
					continue;
				self.INCLUDES.append(nom);

				## prüfe ob anonymisiert werden soll:
				anon_ = anon;
				if re.search(r'anon', typ):
					anon_ = True;

				## nested Call für neue Dateiquelle:
				nom  = self.____extractfilename(path=nom_sub, root=root, ext='bib');
				# nom, root, fname = self.____extractfilename(path=fname_src, root=root, split=True, ext='bib');
				src = self.____extractfilename(path=fname_main, ext='bbl');
				indent_ = {};
				for key in indent:
					val = self.INDENTCODE;
					if key == 'tex' or key == 'struct':
						val = indent[key] + 1;
					indent_[key] = val;

				line = self.INDENTCHARACTER*indent['py'] + '''____insertbib(fname="'''+nom+'''", src="'''+src+'''", indent="'''+tex_indent+'''", anon='''+str(anon_)+''')''';

				if not mute:
					if anon:
						nom = self.____censorpath(path=nom);
					print('    '*(indent_['struct']+1)+'|');
					print('    '*(indent_['struct']+1)+'— '+nom+';');
					struct.append('%%'+'    '*(indent_['struct']+1)+'|');
					struct.append('%%'+'    '*(indent_['struct']+1)+'— '+nom+';');
					self.____addpytexline(lines=filecontents, verbatim=verbatim, expr=[
						'',
						self.INDENTCHARACTER*indent_['struct']+'%% ******************************************************************************',
						self.INDENTCHARACTER*indent_['struct']+'%% DATEI: '+nom,
						self.INDENTCHARACTER*indent_['struct']+'%% ******************************************************************************',
						'',
					], indent=indent['py'], mode='meta');

				self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, expr=[line], mode='direkt');

				bool_belowcontent = False;
				bool_belowfile = True;
				bool_insidecomment = False;

				len_empty = 0;
				len_comm = 0;
				continue;

			# Zeile: Kommentar
			if params['no-comm'] or params['no-comm-auto']:
				m = re.match(r'^\s*(\%+).*', line);
				if m:
					n_zeichen = len(m.group(1));
					if params['no-comm'] or (params['no-comm-auto'] and n_zeichen == 1):
						if not bool_insidecomment:
							len_comm = 0;
						bool_insidecomment = True;
						len_comm += 1;
						continue;

			# Zeile: normaler LaTeX (Kommentare am Ende einer Zeile werden nicht gelöscht)
			if bool_belowfile:
				self.____addpytexline(lines=filecontents, verbatim=verbatim, indent=indent['py'], expr=[''], anon=anon, mode='meta');
			line = self.INDENTCHARACTER*indent['tex']+line;
			# m = re.match(r'^(|.*?(?!\\).)(\%.*)$', line);
			# if m:
			#     line = m.group(1).rstrip();
			self.____addpytexline(lines=filecontents, verbatim=verbatim, linenr=linenr, indent=indent['py'], expr=[line], anon=anon, mode='meta');
			bool_belowcontent = True;
			bool_belowfile = False;
			bool_insidecomment = False;
			len_empty = 0;
			len_comm = 0;
			continue;


		self.____addpytexline(ignore=True, lines=filecontents, verbatim=verbatim, expr=[
			self.INDENTCHARACTER*self.INDENTCODE + r"____ignore('rem');",
		], mode='direkt');
		return erfolg;

	def ____addpytexline(self, lines=[], verbatim=[], linenr=None, expr=[], verbexpr=None, indent=None, anon=False, mode='direkt', ignore=False):
		if mode == 'meta':
			for e in expr:
				lines += self.____metaprint(linenr=linenr, expr=e, indent=indent, anon=anon);
		elif mode == 'none':
			pass;
		else:
			lines += expr;
		if verbexpr is None:
			verbatim += [(linenr, ignore, line) for line in expr];
		else:
			verbatim += [(linenr, ignore, line) for line in verbexpr];
		return;

	def ____extractfilename(self, path=None, root=None, split=False, relative=None, relative_to=None, ext=None):
		if path is None:
			return None;

		if root is None:
			root = self.ROOTDIR;

		root = os.path.abspath(os.path.normpath(root));
		if re.match(r'\:|^[\/\\]', path):
			if relative is None:
				relative = False;
			path = os.path.abspath(os.path.normpath(path));

		else:
			if relative is None:
				relative = True;
			path = '/'.join([root, path]);
			path = os.path.abspath(os.path.normpath(path));

		if relative:
			root = relative_to;
			if root is None:
				root = self.ROOTDIR;
			root = os.path.abspath(os.path.normpath(root));
			root = re.split(r'/+', re.sub('^/+', '', root));
			path = re.split(r'/+', re.sub('^/+', '', path));
			back = len(root);
			while len(root) > 0 and len(path) > 0:
				if root[0] == path[0]:
					back -= 1;
					root = root[1:];
					path = path[1:];
					continue;
				break;
			path = '/'.join(['.'] + ['..']*back + path);

		if split:
			root, fname = os.path.split(path);
		else:
			fname = path;

		if not ext is None:
			fname, _ = os.path.splitext(fname);
			if not ext == '':
				fname = fname + '.' + ext;

		if split:
			path = os.path.normpath('/'.join([root,fname]));
			return path, root, fname;
		return fname;

	def ____expandquickpython(self, expr='', no_latex=True, evaluate=True):
		# re_meta = r'(\<{3}(?:(?![<>]).)*\>{3})'; # <— problematisch!
		re_meta = r'(\<{3}(?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*\>{3})';
		is_bad = False;
		has_subs = True;
		while has_subs:
			meta = '';
			has_subs = False;
			for i,u in enumerate(re.split(re_meta, expr)):
				# m = re.match(r'^\<{3}((?:(?!>).)*)\>{3}$', u); # <— problematisch!
				m = re.match(r'^\<{3}((?![\<|\`])(?:(?!(?:\<{3}|\>{3})).)*)\>{3}$', u);
				if m:
					has_subs = True;
					u = m.group(1);
					u = re.sub(r'^[\s\?\=]+|[\s\;]+$', '', u);
					if u == '':
						continue;
					if u in self.GLOBALVARS:
						u = self.GLOBALVARS[u];
						if isinstance(u, str):
							u = self.____escapecharacters(u);
					meta += u;
				else:
					meta += u;
			expr = meta;

		if no_latex:
			## Bad <--- LaTeX Macros drin enthalten:
			## (erkennbar als ungerade Anzahl an \'s hintereinander irgendwo im String)
			for u in enumerate(re.split(r'(\\+)', meta)):
				if len(u) % 2 == 1:
					is_bad = True;
					break;

		if not is_bad:
			## Bad <--- ex. eine im pre-compile unauflösbare Variable.
			try:
				meta = eval(expr, self.GLOBALVARS);
			except:
				is_bad = True;

		if evaluate:
			expr = meta;

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
			val = "eval('"+val+"')";
		elif isinstance(val, str):
			val = "'" + self.____escapecharacters(val) + "'";
		else:
			val = str(val);

		line = self.INDENTCHARACTER*indent + key + ' = ' + val + ';';

		return [line];

	def ____remove_quotes(self, s):
		return re.sub(r'^[\'\"]+|[\'\"]+$', '', s);

	def ____escapecharacters(self, s):
		s = re.sub(r'(\\+)', r'\1\1', s);
		s = re.sub(r'\n', r'\\n', s);
		s = re.sub(r'\t', r'\\t', s);
		s = re.sub(r'\"', r'\\u0022', s);
		s = re.sub(r'\'', r'\\u0027', s);
		# s = re.sub(r'\%', slash+'u0025', s);
		return s;

	## verwandelt Strings in starke Metastrings:
	def ____metastring(self, s):
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
			line = "____print(eval(____qp("+str(linenr)+", "+expr+"), locals()), anon=True);";
		else:
			line = "____print(eval(____qp("+str(linenr)+", "+expr+"), locals()));";
		lines = [self.INDENTCHARACTER*indent + line];
		return lines;

	def ____countindents(self, s):
		return len(re.findall(self.INDENTCHARACTER_re, s));

	def ____censorpath(self, path):
		return '#'*len(path);

	pass;


____phpytexcompiler().run();
