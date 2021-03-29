import argparse
import pdftitle
import logging
import requests
import json
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( '-p', '--pdf', dest="pdf_file", required=True, help='pdf file')
    parser.add_argument( '-t', '--title', dest="title", help='manually specify title')
    args = parser.parse_args()
    return args


def main():
    logger = logging.getLogger("pdf2bibtex")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    ch.setFormatter(formatter)

    args = parse_args()

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
        return 1
    else:
        logger.info( "dblp search succeeded" )

    db = BibDatabase()
    db.entries = []

    for hit in j["result"]["hits"]["hit"]:
        logger.info( f'processing result with id {hit["info"]["key"]}' )
        authors = []
        for author in hit["info"]["authors"]["author"]:
            authors += [ author["text"] ]
        authors = " and ".join(authors)
        pubtype = "misc"
        venuetype = "howpublished"

        ptype = hit["info"]["type"]
        if ptype == "Conference and Workshop Papers":
            pubtype = "inproceedings"
            venuetype = "booktitle"       
        
        entry = {
            'title' : hit["info"]['title'],
            'year' : hit["info"]['year'],
            'author' : authors,
            'type' : pubtype,
            'id' : hit["info"]['key'],
            venuetype : hit["info"]["venue"]
        }
        db.entries += [entry]

    #json_formatted_str = json.dumps(j, indent=2)
    #logger.debug(json_formatted_str)

    writer = BibTexWriter()
    writer.write(db)

    return 0            # all's well that ends well


if __name__ == "__main__":
    exit(main())
