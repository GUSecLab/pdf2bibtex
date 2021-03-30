"""
pdf2bibtex

A program that takes as input an academic paper in PDF format,
and spits out the BibTeX for that paper.

BibTeX is crudely generated from querying DBLP based on the extracted
title of the PDF file.


This program was (quickly) written by Micah Sherr <msherr@cs.georgetown.edu>.

Use at your own risk.
"""


import argparse
import pdftitle
import logging
import requests
import json
import sys
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( '-p', '--pdf', dest="pdf_file", required=True, help='pdf file')
    parser.add_argument( '-t', '--title', dest="title", help='manually specify title')
    parser.add_argument( '-l', '--log', dest="log", action='store_true', help='enable logging')
    args = parser.parse_args()
    return args


def query_dblp( title ):
    global logger
    logger.info( "grabbing records from dblp" )
    payload = {
        'q' : title,
        'format' : 'json',
    }
    r = requests.get( "https://dblp.org/search/publ/api", params=payload )
    logger.info( f'request submitted via {r.url}')
    j = r.json()
    if j["result"]["status"]["@code"] != "200":
        logger.error( "DBLP search did not complete successfully" )
        return None
    else:
        logger.info( "dblp search succeeded" )

    # dump the DBLP results
    logger.debug( f'raw DBLP result: {json.dumps(j)}' )
    
    return j


def main():
    global logger

    args = parse_args()

    logger = logging.getLogger("pdf2bibtex")
    if args.log:
        # set up logging
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        ch.setFormatter(formatter)

    if args.title is not None:
        title = args.title
    else:
        try:
            title = pdftitle.get_title_from_file(args.pdf_file)
        except FileNotFoundError as e:
            logger.error( f"cannot find file: {e}")
            return 1
        except Exception as e:
            logger.error( f"cannot find title; maybe try -t option?: {e}")
            return 1
        logger.info( f'extracted title from pdf: "{title}"' )

    j = query_dblp( title )
    if j is None:  return 1

    db = BibDatabase()
    db.entries = []

    for hit in j["result"]["hits"]["hit"]:
        logger.info( f'processing result with id {hit["info"]["key"]}' )

        # first, parse the authors
        authors = []
        first_author = None
        for author in hit["info"]["authors"]["author"]:
            authors += [ author["text"] ]
            if first_author is None:
                first_author = author["text"].split(" ")[1]
        authors = " and ".join(authors)
        
        # next, figure out the type of publicaton
        pubtype = "misc"
        venuetype = "howpublished"
        ptype = hit["info"]["type"]
        if ptype == "Conference and Workshop Papers":
            pubtype = "inproceedings"
            venuetype = "booktitle"
        elif ptype == "Journal Articles":
            pubtype = "article"
            venuetype = "journal"
        else:
            logger.warning( f"unsupported pub type: {ptype}" ) 
        
        # generate a key for this bibtex entry
        year = hit["info"]['year']
        key = f'{first_author}{year}'

        logger.debug( f'processing entry {key}, type {pubtype}')

        # add the entry to the bibtex DB
        entry = {
            'title' : hit["info"]['title'],
            'year' : year,
            'author' : authors,
            'ENTRYTYPE' : pubtype,
            'ID' : key,
            venuetype : hit["info"]["venue"]
        } 
        if "volume" in hit["info"]:  entry["volume"] = hit["info"]["volume"]
        if "number" in hit["info"]:  entry["number"] = hit["info"]["number"]
        db.entries.append( entry )

    # write the bibtex!
    writer = BibTexWriter()
    print(writer.write(db))

    return 0            # all's well that ends well


if __name__ == "__main__":
    sys.exit(main())
