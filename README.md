# (PH(p)y)TeX #

## Inhaltsverzeichnis ##
- [Installation](#setup)
- [Gebrauchsanleitung (kurz)](#usage-short)
- [Gebrauchsanleitung (lang)](#usage-long)
  - [Python-Befehle](#py-cmd)
    - Python
    - „Quick-Python“
  - [Python-Variable in LaTeX](#py-var)
  - [Beispiele](#bsp)
  - [Sonderbefehle/-variable in Python](#bes-var)
  - [Der (p(p)y)tex Compiler](#compiler)
    - [Compilationsvorgang](#compile-zyklus)
    - [\input und \bibliography](#input-bib)
    - [Indentation (inkl. Beispiele)](#indentation)
    - [Auflösung von py/PHP-Ausdrücken (inkl. Beispiele)](#ersetzung-variable)

## <a name="setup">INSTALLATION</a> ##

1. Die ersten 2 Zeilen der `phptex.py`-Datei an deinem System anpassen.
2. In einen Ordner legen, der im PATH liegt.
3. Die `.py`-Extension entfernen
4. Mac OSX / Linux:
  ```
  sudo chmod 755 phpytex
  ```
  in Terminal ausführen. (Oder den äquivalenten Befehl für Windows.)
5. Befehl ist jetzt überall verfügbar.
6. Mit
  ```
  phpytex -help
  phpytex -man
  ```
  die Anleitungen aufrufen.



## <a name="usage-short">GEBRAUCHSANLEITUNG</a> ##
Zum Gebrauch dieses Befehls entweder:

```
phpytex -help
phpytex --help
```

um diese Hilfe aufzurufen, oder:

```
phpytex -man
phpytex -guide
phpytex -usage
```

um die Gebrauchsanleitung aufzurufen, oder:

```
phpytex
  -i DATEI        Inputdatei relativ zum path.
  -o DATEI        Outputdatei relativ zum path.
  ___________________
  | optionale Flags |
  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
  -path PFAD      Pfad des lokalen Ordners.
  -share PFAD       Pfad zum geteilten Ordner (PDF-Output kommt dahin).
  -head DATEI       Datei mit Latex-Kommentar als Kopfteil.
  -insert-bib       Inhalte von .bbl-Datei(en) werden eingesetzt anstelle von \bibliography{...}.

  -debug        Präkompiliertes Pythonskript wird zu Outputdatei geschrieben.
  -no-compile       Latex-Datei wird generiert, aber nicht kompiliert.

  -no-comm        Entferne sämtliche LaTex-Kommentare
  -no-comm-auto     Entferne rauskommentierte Zeilen (% ...) aber nicht Kommentare (%%...).
  -max-length [0-9]+  Setze maximale Länge des Dokuments auf n Zeilen: verhindert endlose schleifen.
              (Defaultwert 10000.)

  -tabs / -tab      Benutze \t als Einheit für Einrückung (Default).
  -spaces [0-9]+    Benutze n x Leerzeichen als Einheit für Einrückung.

  -seed [0-9]+      Seed für Pythons np.random.
```

## <a name="usage-long">VOLLE GEBRAUCHSANLEITUNG</a> ##

*„Wie PHP zu HTML, so (PH(p)y)TeX to LaTeX!“*

Im Grunde könnte man diesen Compiler **php-latex** oder **meta-tex** benennen. Der langweilige Name **pylatex** wäre genauer, ist aber leider schon besetzt. Da unser Compiler auf python augmentiert mit durch durch PHP inspirierten Konzepten basiert, ist der Name **(PH(p)y)TeX** das Richtige.

*Doch was macht er?*

Mit **(PH(p)y)TeX** kannst du LaTeX-Dokumente ordentlich programmieren und insbesondere die Vielfalt von Variablentypen und Methoden, die **Python 3.X** zur Verfügung stellt, ausnutzen. Mit LaTeX kannst du nur mit großem Umstand Schleifen schreiben, auf Variable beziehen, und Werte von Variablen anzeigen. LaTeX augmentiert mit python hingegen macht einem das alles einfacher.

### <a name="py-cmd">PYTHON BEFEHLE</a> ###

#### Python-Blöcke ####

```
<<< python
  ...DEIN CODE...
>>>
```

um Code-Blocks zu verwenden. Beachte, dass *relativ zu der ersten Instanz* von `<<<` Code-Zeilen **immer um ≥ 1 Tab eingerückt** werden sollen. Alternativ kann man die **3-Tick** Konvention


  ``` python
    ...DEIN CODE...
  ```

verwenden. Dem Compiler ist es egal, ob die Datei **.tex** oder **.md** lautet. Insofern (v. a. wegen Syntax-Highlight) kann es vom Vorteil sein, die 3-Tick Konvention und Markdown-Dateien zu verwenden. By **Quick-Python** (siehe folgenden Abschnitt) hingegen wird nur die `<<< ··· >>>`-Schreibweise akzeptiert.

#### „Quick-Python“ ####

Variablendefinition können schnell mittels

```
<<< set VARIABLE = AUSDRUCK; >>>
```

auf leeren Zeilen ausgeführt werden. Der set-Befehl stellt außerdem dem Compiler diese Variable während Compilation zur Verfügung. Die aktuelle Indentationsebene kann mittels

```
<<< escape_once; >>>
<<< escape; >>>
```

*um 1* bzw. *auf 0* reduziert werden, z. B. um den Scope einer for-Schleifen zu begrenzen. Die Befehle

```
<<< input FILENAME; >>>
<<< input_once FILENAME; >>>
<<< input_anon FILENAME; >>>
<<< input_anon_once FILENAME; >>>
<<< bibliography FILENAME; >>>
```

ist analog zu den LaTeX-Befehlen `\input{FILENAME}` und `\bibliography{FILENAME}`. Die `_anon`-Versionen zensieren die Pfadnamen und das TeX in der Outputdatei. **ACHTUNG!** Der Ausdruck, `FILENAME`, *muss ein String sein* oder *einen String ergeben*. Ein `FILENAME`, der mit `/` (Linux/Mac) oder `\` (Windows) anfängt, wird als absoluter Pfad benhandelt. Alle andere Werte für `FILENAME` inkl. derer, die mit `./`, `../`, `.\` oder `..\` anfangen, werden relativ zum Ort der aktuellen Datei gesucht. Für den Path kann man **quick-Python**-definierte Variable verwenden. Z. B. kann man die **quick-Python**-Variable

- `__ROOT__`
- `__DIR__`

verwenden (z. B. `<<< input __ROOT__ + '/chapters/analysis/result.tex'; >>>` oder `<<< input __DIR__ + '/../../chapters/analysis/result.tex'; >>>`), um den Pfad des Hauptordners bzw. den des aktuellen zu verwenden. Solange der Ausdrück während Compilation definierbar ist (siehe unten), wird der Inhalt der verlinkten Datei direkt eingesetzt und mit **(PH(p)y)TeX** rekursiv geparsed. Der Gebrauch von `input_once` bedeutet: die Datei wird höchstens 1 Mal eingebettet.

**Beachte:** in allen Befehlen sind weder Leerzeichen noch anschließendes `;` nötig.

#### DATEITYPEN ###

Wenn die Dateiextension (ob **.tex** oder **.bib** oder **.md**) nicht explizit angegeben wird, dann nimmt der Kompiler an, für `<<< input ···>>>` sei die Extension **.tex** und für `<<< bibliography ···>>>` die Extension **.bib**.

Man kann ganze Python-Skript direkt mit `<<< input (PATH/)FILENAME.py>>>` inkludieren. Beachte, dass die **.py** Extension dabei ist, ansonsten wird das Skript als **.tex** interpretiert. Beachte, dass der Code aus einem Python-Skript *nicht* in einem `<<<` Block `>>>>` geschrieben werden muss. Schreibe dein Code ganz normal und mach dir keine Sorgen um die Indentation.


### <a name="py-var">PYTHON-VARIABLE IN LATEX AUSSPIELEN</a> ###

Wenn in Code-Blöcken Variable definiert werden, so lassen sich diese mittels

```
<<< VARIABLENAME >>>
```

im normalen **LaTeX** ausspielen.
Zum Kompilieren des Codes, siehe

```
phpytex -help
```

### <a name="bsp">BEISPIELE</a> ###

Was diese Beispiele erzeugen sollten selbstverständlich sein.
Man kann die selber austesten.

#### BEISPIEL 0. ####

```
\begin{document}
  ·
  ·
  ·

  <<< python
    n = numpy.random.choice(1,8);
  >>>

  Definition $X^{n}=\underbrace{X\cdot X\cdot \cdots \cdot X}_{n~\text{Mal}}$.
  Z. B. $X^{<<< n >>>} = X<<<'\cdot X'*(n-1)>>>$.

  ·
  ·
  ·
\end{document}
```

#### BEISPIEL 1. ####

```
<<< python
  ht = ['eine Katze', 'einen Hund'];
  choice = int(2*numpy.random.rand());
>>>

Als Haustier hätte ich am liebsten <<< ht[choice];>>>.
```

#### BEISPIEL 2. ####

```
<<< python
  dimx = 25;
  dimy = 38.4;
>>>

Der Flächeninhalt beträgt <<< dimx*dimy >>>$m^{2}$.
```

#### BEISPIEL 3. ####

```
<<< python
  n = 10;
  dna = [];
  sim = [];
  for i in range(0,n):
    dna_ = ''.join(numpy.random.choice(['G','C','A','T'], 15, replace=True));
    dna.append(dna_);
  pass;
>>>

\begin{tabular}[t]{ll}
  Gen &Struktur\\
  \hline
  <<< python
    for i in range(0,n):
  >>>
  Gen<<<i>>> &<<<dna[i];>>>\\
  <<< escape; >>>
\end{tabular}
```

Mit **(PH(p)y)TeX** verfügst du also über viele der mächtigen python-Methoden und kannst damit ohne zu viel Frust LaTeX-Dokumente erstellen.


### <a name="bes-var">SONDERBEFEHLE/VARIABLE IN PYTHON:</a> ###

- `__ROOT__` = Pfad zum Hauptordner.
- `__DIR__` = Pfad zum aktuellen Ordner.
- `____filetex____` = der File-Pointer zur Outputdatei.
- `____print(string, anon=False)` = Print-Befehl (in Outputdatei) analog dem echo(·) und print_r(·) für PHP. Das optionale Argument bestimmt, ob der String nur für die Kompilation erscheinen und dann zensiert (in der Outputdatei) werden soll.
- `____maxlength____` = Oberschranke der Outputlänge.

### <a name="compiler">WIE FUNKTIONIERT (PH(p)y)TeX?</a> ###

**(PH(p)y)TeX** scannt die Zeile deines Dokumentes ein prüft, ob die Zeile

- ein **quick-Python**-Befehl ist; oder
- der Anfang/dasEnde/innerhalb eines (Python)-Codeblocks ist; oder
- eine (Python/Latex)-Kommentarzeile oder gar leer ist; oder
- eine normale LaTeX-Zeile ist.

und für **LaTeX**-Zeilen wird zusätzlich geprüft, ob `<<< VARIABLE >>>`-Befehle vorkommen.

Aus diesen wird eine Funktion erzeugt, die aus deinem **Python**-Code und Print-Befehlen für deinen **LaTeX**-Code untereinander, geordnet wie im Dokument.

#### <a name="compule-zyklus">COMPILATIONSVORGANG</a> ####

1. **(PH(p)y)TeX** scannt das Dokument wie oben und und erzeugt ein **Python**-Skript, das aus deinem Python-Code und Printbefehlen für deinen **LaTeX**-Code besteht.
2. Das Python-Skript wird ausgeführt, wobei die print-Befehle Output in die durch den `-i` Flag festgelegte Datei erzeugen.
3. Dieses Dokument wird dann mit pdflatex kompiliert.
4. Falls der `-insert-bib` Flag verwendet wurde, werden nochmals 1–3 ausgeführt, wobei bei 1 die Inhalte von gefundenen .bbl-Dateien eingesetzt werden.

#### <a name="input-bib">ERSETZUNG VON \input und \bibliography</a> ####
Betrachte folgende Situation:

- du kannst nur eine .tex-Datei abgeben
- du willst dennoch strukturiert und damit mit mehreren Dateien und Ordnern arbeiten

Dies kommt vor allem bei Abgaben bei akademischen Journals vor. Zum Teil ist aus diesem Grund **(PH(p)y)TeX** ursprünglich entstanden. Das ist der 2. Zweck von **(PH(p)y)TeX**. Deshalb, wird bei `<<< input|input_once ··· >>>`-Befehlen das verlinkte Dokument eingebetet und auch mit **(PH(p)y)TeX** kompiliert. Am Ende erhält man ein einziges Dokument. Die Abhängigkeiten werden als Baumstruktur am Anfang des Dokuments (ggf. nach dem Kopf-Teil) dargestellt. Hingegen signalisiert der Gebrauch von `\input{···}`, dass **(PH(p)y)TeX** das verlinkte Dokument nicht einbetten soll. In diesem Falle wird das verlinkte Dokument ebenfalls nicht mit **(PH(p)y)TeX** kompiliert.

Analog verhält es sich bei `<<< bibliography >>>` bzw. `\bibliography{···}`.

**Beachte:** Vermeide `\LaTeX`-Macros innerhalb `<<< input ··· >>>` und `<<< bibliography ··· >>>` Befehlen, denn **(PH(p)y)TeX** verfolgt die LaTeX-Macros (noch) nicht. Die durch **quick-Python** definierten Variablen können LaTeX-Macros aber schon verwendet werden. Z. B. anstelle von

```
\def\ordner{/User/Me/Project}
<<< input '\ordner/head1'; >>>
<<< input '\ordner/head2'; >>>
```

benutze die python-artigen pre-compile Befehle

```
<<< set ordner = '/User/Me/Project'; >>>
<<< input ordner + '/head1'; >>>
<<< input ordner + '/head2'; >>>
```

oder die PHP-artigen pre-compile Befehle

```
<<< input '<<< ordner >>>/head1'; >>>
<<< input '<<< ordner /head2'; >>>
```

Solange die Variablen dem **(PH(p)y)TeX**-Compiler zur Verfügung stehen, wird dies klappen.

##### Warum ist dies nur mit dem **set**-Befehl möglich ist? #####

Eine **Python**-Variable, die NICHT mit `<<< set ··· >>>` erstellt wurde, steht dem Compiler beim ersten Durchlauf noch nicht zur Verfügung. Der `set`-Befehl ist in dieser Hinsicht sehr beschränkt: er stellt dem Compiler *nur den Ausdruck* zur Verfügung. Falls im Ausruck weitere Variable vorkommen, so werden diese *nicht* durch ihre Werte ersetzt.

#### <a name="indentation">INDENTATION</a> ####

Die Einrückung wird immer strikt durch die **Python**-Blöcke bestimmt. „Null“-Indentation = 1 Tabstop relativ zur Position von

```
<<< python
```

im Dokument. Einrückungen in **LaTeX**-Zeilen werden nur as Teil des Strings im Print-Befehl verwendet, dessen Einrückung als Befehl in der Funktion wird alleine durch den letzten Zustand in den Python-Blöcken. Einrückung von **quick-Python**-Befehlen, wird ebenfalls durch die Python-Blöcke bestimmt.

Beachte deshalb, die Python-Blöcke ordentlich abzuschließen um unerwartetes Verhalten zu vermeiden. Zum Beispiel kann man mithilfe von

```
<<< python
  pass;
>>>
```

oder

```
<<< python
    pass;
>>>
```

*etc.* das Indentation-Level erzwingen. Stelle insbesondere bei Schleifen und anderen Control-Statements sicher, dass der Scope ebenfalls durch solche blöcke abgeschlossen sind. Hierfür eignen sich die folgenden **quick-Python** Befehle:

- `<<< escape; >>>` fügt ein `pass` Statement auf der aktuellen Indentation, dann setzt die Indentation auf Level-1 zurück.
- `<<< escape_once; >>>` fügt ein `pass` Statement auf der aktuellen Indentation, dann rückt die Indentation eine Stufe zurück.

##### BEISPIELE #####

Der folgende **(PH(p)y)TeX** Code

```
<<< python
  x = [];
  for i in range(3):
    x.append([]);
    for j in range(2):
      x[i].append(i*i + j);
>>>

Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{<<<i>>>}$ unvollständig.
```

ist äquivalent zu

```
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{0}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{0}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{1}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{1}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{2}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{2}$ unvollständig.
```

Hingegen ist

```
<<< python
  x = [];
  for i in range(3):
    x.append([]);
    for j in range(2):
      x[i].append(i*i + j);
      pass;
>>>

Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{<<<i>>>}$ unvollständig.
```

äquivalent zu

```
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{0}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{1}$ unvollständig.
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T_{2}$ unvollständig.
```

und

```
<<< python
  x = [];
  for i in range(3):
    x.append([]);
    for j in range(2):
      x[i].append(i*i + j);
>>>

<<< escape; >>>

Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T$ unvollständig.
```

erzeugt

```
Laut des Gödel'schen Unvollständigkeits-Theorems ist die Theorie $T$ unvollständig.
```

#### <a name="ersetzung-variable">AUFLÖSUNG VON AUSDRÜCKEN</a> ####

Es gibt zwei Arten der Auflösung: **python-artige** und **PHP-artige** auflösung. Python-artige Auflösung bedeutet, dass Teilausdrücke direkt als Variablen interpretiert und so typifiziert werden. PHP-artige Auflösung bedeutet, dass Teilausdrücke zunächst durch ihren stringifizierten Wert ersetzt werden, bevor der ganze Ausdruck aufgelöst wird. PHP-artige Ausdrücke können im Gegensatz zu python-artigen verschachtelte .

##### BEISPIELE #####

Angenommen, folgende Variable entweder global oder lokal definiert sind:

```python
__ROOT__ = './../..';
__DIR__ = './chapters/sections';
farbe = 'Rot';
Rot = 'Blau';
frequenz = 13.57e-8;
anzahl = 3;
key1 = 'key2';
attr = {'key1':'Lila', 'key2':19};
energy = [78.12e-6, 1.87e-3];
term = '<<< farbe >>>';
```

Dann wird der folgende Audruck (wenn er im normalen LaTeX-Text erscheint) pytho-artig interpretiert:

```
<<< 'dunkles ' + farbe >>>
```

und der folgende PHP-artig:

```
<<< 'dunkles <<< farbe >>>' >>>
```

interpretiert, und beide ergeben (in der python-Umgebung) den Wert

```python
'dunkles Rot'
```

und im LaTeX-Text sieht man nur

```
dunkles Rot
```

Hier eine Tabelle von weiteren Beispielen:

| Ausdruck | Interpetation (in der python-Umgebung) |
| :------- | :------------------------------------- |
| `<<< 'dunkles ' + farbe >>>` | `dunkles Rot` |
| `<<< 'dunkles farbe' >>>` | `dunkles farbe` (Compiler sieht keine Variable) |
| `<<< 'dunkles <<< farbe >>>' >>>` | `dunkles Rot` |
| `<<< __ROOT__ + '/vorwort.tex' >>>` | `'./../../vorwort.tex'` |
| `<<< '__ROOT__/vorwort.tex' >>>` | `'__ROOT__/vorwort.tex'` (Compiler sieht keine Variable) |
| `<<< '<<< __ROOT__ >>>/vorwort.tex' >>>` | `'./../../vorwort.tex'` |
| `<<< (farbe + '-') * anzahl >>>` | `'Rot-Rot-Rot'` |
| `<<< ('<<< farbe >>>-') * anzahl >>>` | `'Rot-Rot-Rot'` |
| `<<< (<<< farbe >>> + '-') * anzahl >>>` | `'Blau-Blau-Blau'` |
| `<<< sum(energy) >>>` | `0.00194812` |
| `<<< str(sum(energy)) + ' J' >>>` | `'0.00194812 J'` |
| `<<< attr['key1'] >>>` | `'Lila'` |
| `<<< attr['key2'] >>>` | `19` |
| `<<< attr['<<< key1 >>>'] >>>` | `19` |
| `<<< attr[<<< key1 >>>] >>>` | Fehler: `attr[key2]` nicht evaluierbar! |

Man beachte u. a. wie PHP-artige Ausdrücke direkt als durch neue Teilausdrücke ersetzt werden, während python-artige Ausdrücke ganz normal als Variablen interpretiert werden.

Beachte, dass **(PH(p)y)tex**-Interpretation wie folgt ausgeführt wird:

1. `<<< ··· >>>` von innen nach außen in einem Ausdruck auflösen;
2. der `eval(···)`-Befehl von Python auf den aus aufgelösten Ausdruck ausführen

Schritt **1** wird nie nach Schritt **2** wiederholt, d. h.

```<<< term + ' ist meine Lieblingsfarbe' >>>```

wird als 

```'<<< farbe >>> ist meine Lieblingsfarbe'```

und **nicht** als

```'Rot ist meine Lieblingsfarbe'```

interpretiert, weil in Schritt 1 der Wert '<<< farbe >>>' gar nicht vorkommt, weil `term` nie aufgelöst wird. Nur wenn man PHP-artig vorgeht, wird

```<<< '<<< term >>> ist meine Lieblingsfarbe' >>>```

als

```'Rot ist meine Lieblingsfarbe'```

interpretiert.