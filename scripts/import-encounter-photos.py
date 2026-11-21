import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageOps


PLATES = {
    'relay': ('image16.jpeg', 'image15.png'),
    'drum': ('image18.jpeg', 'image17.png'),
    'cuju': ('image19.jpeg', 'image20.jpeg'),
    'hammer': ('image21.png', 'image22.png'),
    'mime': ('image23.png', 'image24.png'),
    'treasure': ('image26.png', 'image25.png'),
    'mugwort': ('image28.png', 'image27.png'),
    'candy': ('image29.png', 'image30.png'),
    'constable': ('image31.png', 'image32.png'),
    'ranger': ('image33.png', 'image34.png'),
    'escort': ('image36.jpeg', 'image35.png'),
    'magistrate': ('image38.png', 'image37.png'),
    'trader': ('image39.png',),
    'masked': ('image40.png', 'image41.png', 'image42.png'),
}


def main():
    parser = argparse.ArgumentParser(description='Import the encounter plates from the v1119 PPTX.')
    parser.add_argument('deck', type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1] / 'public/art/encounters'
    output.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.deck) as deck:
        for entry, images in PLATES.items():
            for number, name in enumerate(images, start=1):
                with Image.open(BytesIO(deck.read(f'ppt/media/{name}'))) as source:
                    photo = ImageOps.exif_transpose(source).convert('RGB')
                    photo.thumbnail((920, 820), Image.Resampling.LANCZOS)
                    photo.save(output / f'{entry}-{number}.webp', quality=80, method=6)
                    if number == 1:
                        thumb = ImageOps.fit(photo, (128, 128), centering=(0.5, 0.3))
                        thumb.save(output / f'{entry}-thumb.webp', quality=75, method=6)


if __name__ == '__main__':
    main()
