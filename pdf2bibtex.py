import argparse
import pdftitle


def main():

    filename = 'Singh2020.pdf'
    title = pdftitle.get_title_from_file(filename)
    print(title)

    return 0


if __name__ == "__main__":
    # execute only if run as a script
    exit(main())