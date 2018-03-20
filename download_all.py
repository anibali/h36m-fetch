from subprocess import call
from os import path, makedirs
import hashlib
from tqdm import tqdm
from configparser import ConfigParser


config = ConfigParser()
config.read('config.ini')
PHPSESSID = config['General']['PHPSESSID']

BASE_URL = 'http://vision.imar.ro/human3.6m/filebrowser.php'

subjects = [
    ('S1', 1),
    ('S5', 6),
    ('S6', 7),
    ('S7', 2),
    ('S8', 3),
    ('S9', 4),
    ('S11', 5),
]


def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download_file(url, dest_file):
    call(['axel',
          '-a',
          '-n', '24',
          '-H', 'COOKIE: PHPSESSID=' + PHPSESSID,
          '-o', dest_file,
          url])


def download_all():
    checksums = {}
    with open('checksums.txt', 'r') as f:
        for line in f.read().splitlines(keepends=False):
            v, k = line.split('  ')
            checksums[k] = v

    files = []
    for subject_id, id in subjects:
        files += [
            ('Poses_D2_Positions_{}.tgz'.format(subject_id),
             'download=1&filepath=Poses/D2_Positions&filename=SubjectSpecific_{}.tgz'.format(id)),
            ('Poses_D3_Positions_mono_universal_{}.tgz'.format(subject_id),
             'download=1&filepath=Poses/D3_Positions_mono_universal&filename=SubjectSpecific_{}.tgz'.format(id)),
            ('Videos_{}.tgz'.format(subject_id),
             'download=1&filepath=Videos&filename=SubjectSpecific_{}.tgz'.format(id)),
        ]

    out_dir = 'archives'
    makedirs(out_dir, exist_ok=True)

    for filename, query in tqdm(files, ascii=True):
        out_file = path.join(out_dir, filename)

        if path.isfile(out_file):
            checksum = md5(out_file)
            if checksums.get(out_file, None) == checksum:
                continue

        download_file(BASE_URL + '?' + query, out_file)

        checksums[out_file] = md5(out_file)
        with open('checksums.txt', 'w') as f:
            for k, v in checksums.items():
                f.write('{}  {}\n'.format(v, k))


if __name__ == '__main__':
    download_all()
