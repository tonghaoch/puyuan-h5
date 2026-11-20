"""Encode a browser raster and its preview, rejecting an unpainted landmark frame."""
import argparse
import sys

from PIL import Image


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source'); parser.add_argument('asset'); parser.add_argument('preview')
    parser.add_argument('width',type=int); parser.add_argument('height',type=int)
    parser.add_argument('--landmark',action='store_true'); args = parser.parse_args()
    with Image.open(args.source) as image:
        if args.landmark and 'A' in image.getbands() and not image.getchannel('A').getbbox():
            print(f'Unpainted landmark frame: {args.source}',file=sys.stderr)
            sys.exit(3)
        image.save(args.asset,quality=92,method=4)
        image.resize((args.width,args.height),Image.Resampling.LANCZOS).save(args.preview,quality=85,method=4)
