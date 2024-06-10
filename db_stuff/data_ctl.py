import argparse
import pathlib
import io
import os

from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def read_dict(file_path: str) -> str:
    print(f"reading data from {file_path}", flush=True)
    langs = ""
    with open(os.path.join(
                pathlib.Path(__file__).parent.resolve(),
                "data", "languages.txt")) as f:
        langs = f.read()
    langs = "+".join(langs.splitlines()[1:])
    langs = "+".join(["rus", "eng", "pol", "Greek", "fra", "pol",
                      "urk", "uzb", "tur", "uzb_cyrl"]) # TODO: delete this line
    print(f"using languages from languages.txt:\n{langs}", flush=True)
    
    images = convert_from_path(file_path)

    for page_num, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang=langs)
        print(f"Page {page_num + 1}\n{text}\n", flush=True)
    

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str,
                        choices=["read_dict"])
    args = parser.parse_args()

    match args.action:
        case "read_dict":
            read_dict(os.path.join(
                pathlib.Path(__file__).parent.resolve(),
                "data", "Магомедова_П_Т_Чамалинско_русский_словарь_Институт_языка,_литературы.pdf"
            ))

if __name__ == "__main__":
    main()