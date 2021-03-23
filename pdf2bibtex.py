import argparse
import pdftitle
import logging
import scholarly


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( '-p', '--pdf', dest="pdf_file", required=True, help='pdf file')
    args = parser.parse_args()
    return args


def main():
    logger = logging.getLogger("pdf2bibtex")
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    ch.setFormatter(formatter)

    args = parse_args()
    try:
        title = pdftitle.get_title_from_file(args.pdf_file)
    except FileNotFoundError as e:
        logger.error( f"cannot find file: {e}")
        exit(1)
    logger.info( f'extracted title from pdf: {title}' )

    logger.info( 'querying Google Scholar...')
    try:
        search_query = scholarly.scholarly.search_pubs(title)
        pub = next(search_query)
        print( scholarly.bibtex(pub) )
    except Exception as e:
        logger.error( f'scholarly lookup failed: {e}')
        return 1
    return 0


if __name__ == "__main__":
    # execute only if run as a script
    main()
