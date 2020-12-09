import argparse
import os
from pathlib import Path
import requests
import subprocess
import sys
import time
import shutil

import flickrapi
from bing_image_downloader import downloader

import tqdm

def main():
    parser = argparse.ArgumentParser(description='download some images')
    parser.add_argument('search_term', help='the query string')
    parser.add_argument('limit', type=int, help='the number of images to download')
    parser.add_argument('--only_yandex', type=str, default='False')
    args = parser.parse_args()
    search_phrase = args.search_term
    only_yandex = args.only_yandex
    only_yandex = False if only_yandex == 'False' else True
    limit = args.limit

    if 'FLICKR_API_KEY' in os.environ:
        api_key = os.environ['FLICKR_API_KEY']
    else:
        print("Set the FLICKR_API_KEY environment variable.")
        sys.exit()

    if 'FLICKR_API_SECRET' in os.environ:
        api_secret = os.environ['FLICKR_API_SECRET']
    else:
        print("Set the FLICKR_API_SECRET_KEY")
        sys.exit()

    if 'WEBLY_DOWNLOAD_DIR' in os.environ:
        webly_download_dir = Path(os.environ['WEBLY_DOWNLOAD_DIR'])
    else:
        print("Set the WEBLY_DOWNLOAD_DIR")
        sys.exit()

    # Create download folder.
    search_dir = Path(webly_download_dir / search_phrase.replace(' ', '_'))
    if not search_dir.exists():
        search_dir.mkdir()


    if not only_yandex:
        print('Downloading bing images!')
        downloader.download(search_phrase, limit=limit, adult_filter_off=True, force_replace=False, timeout=60)

        # Move bing files.
        bing_download_dir = Path(f'./dataset/{search_phrase}')
        for b in bing_download_dir.iterdir():
            shutil.move(b, Path(search_dir / b.name))

        if bing_download_dir.exists():
            bing_download_dir.rmdir()

        if Path('./dataset').exists():
            Path('./dataset').rmdir()

        print('Downloading flickr images!')
        download_flickr_images(api_key, api_secret, webly_download_dir, search_phrase, max_dl=limit)

    print('Launching yandex script.')
    subprocess.call(['yandex-images-download', 'Chrome', '--keywords', f'"{search_phrase}"',
        '--limit', f'{limit}', '-o', f'{str(webly_download_dir.resolve())}'])

    yandex_dir = Path(webly_download_dir / f'"{search_phrase}"')
    for p in yandex_dir.iterdir():
        shutil.move(p, Path(search_dir / p.name))

    if yandex_dir.exists():
        yandex_dir.rmdir()


def download_flickr_images(api_key, api_secret, flickr_dir, search_text, max_dl=500):
    search_dir = Path(flickr_dir / search_text.replace(' ', '_'))
    if not search_dir.exists():
        search_dir.mkdir()


    flickr = flickrapi.FlickrAPI(api_key, api_secret)

    photos = flickr.walk(
        text=search_text,
        extras='url_z,url_sq,url_q,url_t,url_s,url_n',
        sort='relevance'
    )

    count = 0
    with tqdm.tqdm(total=max_dl) as progress:
        for photo in photos:
            if count >= max_dl:
                break

            url = photo.get('url_z')

            if url is None:
                url = photo.get('url_q')

            if url is None:
                url = photo.get('url_t')

            if url is None:
                url = photo.get('url_s')

            if url is None:
                url = photo.get('url_n')

            if url is None:
                continue

            title = url.split('/')[-1]
            img_path = Path(search_dir / title)
            if not img_path.exists():
                response = requests.get(url, stream=True)

                with open(img_path, 'wb') as outfile:
                    outfile.write(response.content)
                    
            count += 1
            progress.update(1)
            time.sleep(0.5)


if __name__ == '__main__':
    main()
