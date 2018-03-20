# Human 3.6M dataset fetcher

[Human 3.6M](http://vision.imar.ro/human3.6m/description.php) is a 3D
human pose dataset containing 3.6 million human poses and corresponding
images. The scripts in this repository make it easy to download,
extract, and preprocess the images and annotations from Human 3.6M.

## Requirements

* Python 3
* `axel`
* CDF

## Usage

1. Firstly, you will need to create an account at
   http://vision.imar.ro/human3.6m/ to gain access to the dataset.
2. Once your account has been approved, log in and inspect your cookies
   to find your PHPSESSID.
3. Copy the configuration file `config.ini.example` to `config.ini`
   and fill in your PHPSESSID.
4. Use the `download_all.py` script to download the dataset,
   `extract_all.py` to extract the downloaded archives, and
   `process_all.py` to preprocess the dataset into an easier to use
   format.

## License

The code in this repository is licensed under the terms of the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

Please read the
[license agreement](http://vision.imar.ro/human3.6m/eula.php) for the
Human 3.6M dataset itself, which specifies citations you must make when
using the data in your own research.
