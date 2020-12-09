# webly-dataset-creator

Wrapper around [bing-image-downloader](https://pypi.org/project/bing-image-downloader/), [flickrapi](https://pypi.org/project/flickrapi/), & [yandex-images-download](https://pypi.org/project/yandex-images-download/) for the creation of a webly dataset.


## Setup
The flickr library needs a registered api key.

System variables need to be set:

```
export FLICKR_API_KEY=
export FLICKR_API_SECRET=
export WEBLY_DOWNLOAD_DIR=
```

## Usage
```
python webly-dataset-creator/webly-dataset-creator.py "SEARCH TERM" NUM_ITMES
```
