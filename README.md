# pdf2bibtex

A program that takes as input an academic paper in PDF format, and spits out the BibTeX for that paper.

BibTeX is crudely generated from querying DBLP based on the extracted title of the PDF file.


This program was (quickly) written by [Micah Sherr](mailto:msherr@cs.georgetown.edu).  It has been tested on Mac OSX, and nothing else.  I suspect it'll run under Linux.

Use at your own risk.


## Installation

Just one step:

`pip install -r requirements.txt`

And optionally:  
* `pip install pyinstaller`
* `pyinstaller --onefile pdf2bibtex.py`
* `sudo cp dist/pdf2bibtex /usr/local/bin/`


## Usage:

```
usage: pdf2bibtex.py [-h] -p PDF_FILE [-t TITLE] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -p PDF_FILE, --pdf PDF_FILE
                        pdf file
  -t TITLE, --title TITLE
                        manually specify title
  -l, --log             enable logging
  ```

  e.g., `python pdf2bibtex.py -p sherr.pdf`

  