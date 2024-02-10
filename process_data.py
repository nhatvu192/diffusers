import argparse
import os
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image
from tqdm import tqdm


def kanjivg_to_svg(root):
    paths = root.findall(".//path")

    svg_elements = []
    for path in paths:
        path_data = path.attrib["d"]
        svg_elements.append(f'<path d="{path_data}" stroke="black" fill="none"/>')

    svg_body = "\n".join(svg_elements)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">\n{svg_body}\n</svg>'

    return svg


def svg_to_png(svg, output_file: str) -> None:
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=output_file)


def hex_to_kanji(hex_number: str) -> str:
    return chr(int(hex_number, 16))


def transparent_to_white_background(image: np.ndarray) -> np.ndarray:
    image = np.where(image[..., -1] == 0, 255, 0).astype(np.uint8)
    image = np.repeat(image.reshape(*(image.shape), 1), 3, axis=2)
    return image


def get_kanji_to_meanings(kanjidic2_dir: str) -> dict:

    root = ET.parse(kanjidic2_dir).getroot()
    result = {}
    for character in root.findall("character"):
        # Get the literal kanji
        kanji = character.find("literal").text
        # Get the meanings
        meanings = []
        for meaning in character.findall("reading_meaning/rmgroup/meaning"):
            # Check if the meaning tag doesn't have 'm_lang' attribute (which means it's in English)
            if "m_lang" not in meaning.attrib:
                meanings.append(meaning.text)

        if meanings:
            result[kanji] = meanings

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script for creating a dataset of raster images of kanji characters and their meanings as captions"
    )

    parser.add_argument(
        "--output_dir", type=str, required=True, help="Path to the output folder"
    )

    parser.add_argument(
        "--kanjidic2_dir",
        type=str,
        default="../kanjidic2.xml",
        help="Path to the kanjidic2.xml file that contains the meanings of kanji characters",
    )

    parser.add_argument(
        "--kanjivg_dir",
        type=str,
        default="../kanjivg-20220427.xml",
        help="Path to the kanjivg.xml file that contain the strokes of the kanji characters in vector format",
    )

    args = parser.parse_args()

    kanjivg_root = ET.parse(args.kanjivg_dir).getroot()

    kanji_to_meanings = get_kanji_to_meanings(args.kanjidic2_dir)

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "transparent"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "white_background"), exist_ok=True)

    with open(os.path.join(args.output_dir, "metadata.jsonl"), "w") as output_metadata:
        for root in tqdm(kanjivg_root):
            kanji_character = hex_to_kanji(root.attrib["id"].split("_")[-1])
            if kanji_character in kanji_to_meanings:
                transparent_path = os.path.join(
                    args.output_dir, "transparent", f"{kanji_character}.png"
                )
                svg_to_png(kanjivg_to_svg(root), transparent_path)

                with Image.open(transparent_path) as image:
                    image = transparent_to_white_background(np.array(image))
                    image = Image.fromarray(image)
                    image.save(
                        os.path.join(
                            args.output_dir,
                            "white_background",
                            f"{kanji_character}.png",
                        )
                    )
