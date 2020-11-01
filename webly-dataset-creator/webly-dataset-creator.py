import argparse
import os
from pathlib import Path
import requests
import subprocess
import sys
import time

import flickrapi
from bing_image_downloader import downloader

import tqdm

def main():
    parser = argparse.ArgumentParser(description='download some images')
    parser.add_argument('search_term', help='the query string')
    parser.add_argument('limit', type=int, help='the number of images to download')
    args = parser.parse_args()
    search_phrase = args.search_term
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

    # Create Flickr folder.
    flickr_dir = Path(webly_download_dir / 'flickr')
    if not flickr_dir.exists():
        flickr_dir.mkdir()

    bing_dir = Path(webly_download_dir / 'bing')
    if not bing_dir.exists():
        bing_dir.mkdir()

    bing_search_dir = Path(bing_dir / search_phrase.replace(' ', '_'))
    if not bing_search_dir.exists():
        bing_search_dir.mkdir()

    yandex_dir = Path(webly_download_dir / 'yandex')
    if not yandex_dir.exists():
        yandex_dir.mkdir()


    print('Downloading bing images!')
    downloader.download(search_phrase, limit=limit,  output_dir=str(bing_dir.resolve()), adult_filter_off=True, force_replace=False, timeout=60)

    print('Downloading flickr images!')
    download_flickr_images(api_key, api_secret, flickr_dir, search_phrase, max_dl=limit)

    print('Launching yandex script.')
    subprocess.call(['yandex-images-download', 'Chrome', '--keywords', f'"{search_phrase}"',
        '--limit', f'{limit}', '-o', f'{str(yandex_dir.resolve())}'])

    # Rename yandex folder to remove quotes
    yandex_search_dir = Path(yandex_dir / f'"{search_phrase}"')
    _yandex_search_dir = Path(yandex_dir / search_phrase.replace(' ', '_'))
    yandex_search_dir.rename(_yandex_search_dir)




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
