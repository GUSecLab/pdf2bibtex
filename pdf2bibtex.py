import argparse
import pdftitle
import logging
import scholarly


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( '-p', '--pdf', dest="pdf_file", required=True, help='pdf file')
    parser.add_argument( '-t', '--title', dest="title", help='manually specify title')
    parser.add_argument( '-T', '--tor', dest="tor", help='path to Tor')
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

    if args.tor is not None:
        logger.info( f'using Tor as a proxy' )
        pg = scholarly.ProxyGenerator()
        pg.Tor_Internal(tor_cmd = args.tor)
        scholarly.scholarly.use_proxy(pg)
    logger.info( 'querying Google Scholar...')
    search_query = scholarly.scholarly.search_pubs(title)
    pub = next(search_query)
    print( scholarly.bibtex(pub) )
    
    return 0            # all's well that ends well


if __name__ == "__main__":
    exit(main())
