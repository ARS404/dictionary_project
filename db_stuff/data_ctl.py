import argparse
import pathlib
import io
import os

import fitz
import pytesseract
from PIL import Image

def read_dict(file_path: str) -> str:
    print(f"reading data from {file_path}")

    document = fitz.open(file_path)
    
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes(output="png")))
        
        text += pytesseract.image_to_string(img)
        print(len(text))
    

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