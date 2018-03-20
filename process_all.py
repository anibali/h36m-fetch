#!/usr/bin/env python3

from os import path, makedirs, listdir
from shutil import move
from spacepy import pycdf
import numpy as np
import h5py
from subprocess import call
from tempfile import TemporaryDirectory
from itertools import product
from tqdm import tqdm


# subjects = ['S1', 'S5', 'S6', 'S7', 'S8', 'S9', 'S11']
subjects = ['S1']
actions = {
    'Directions': 1,
    'Discussion': 2,
    'Eating': 3,
    'Greeting': 4,
    'Phoning': 5,
    'Posing': 6,
    'Purchases': 7,
    'Sitting': 8,
    'SittingDown': 9,
    'Smoking': 10,
    'TakingPhoto': 11,
    'Waiting': 12,
    'Walking': 13,
    'WalkingDog': 14,
    'WalkTogether': 15,
}
cameras = {
    '54138969': 0,
    '55011271': 1,
    '58860488': 2,
    '60457274': 3,
}


def process_view(subject, action, camera):
    subj_dir = path.join('extracted', subject)
    if action == 'Sitting':
        act_cam = '.'.join([action + ' 1', camera])
    else:
        act_cam = '.'.join([action, camera])

    with pycdf.CDF(path.join(subj_dir, 'Poses_D2_Positions', act_cam + '.cdf')) as cdf:
        poses_2d = np.array(cdf['Pose'])
        poses_2d = poses_2d.reshape(poses_2d.shape[1], 32, 2)
    with pycdf.CDF(path.join(subj_dir, 'Poses_D3_Positions_mono_universal', act_cam + '.cdf')) as cdf:
        poses_3d = np.array(cdf['Pose'])
        poses_3d = poses_3d.reshape(poses_3d.shape[1], 32, 3)

    # Infer camera intrinsics
    pose2d = poses_2d.reshape(len(poses_2d) * 32, 2)
    pose3d = poses_3d.reshape(len(poses_3d) * 32, 3)
    x3d = np.stack([pose3d[:, 0], pose3d[:, 2]], axis=-1)
    x2d = (pose2d[:, 0] * pose3d[:, 2])
    alpha_x, x_0 = list(np.linalg.lstsq(x3d, x2d, rcond=-1)[0].flatten())
    y3d = np.stack([pose3d[:, 1], pose3d[:, 2]], axis=-1)
    y2d = (pose2d[:, 1] * pose3d[:, 2])
    alpha_y, y_0 = list(np.linalg.lstsq(y3d, y2d, rcond=-1)[0].flatten())

    frames = np.arange(0, len(poses_3d), 5) + 1
    video_file = path.join(subj_dir, 'Videos', act_cam + '.mp4')
    frames_dir = path.join('processed', subject, action, 'imageSequence', camera)
    makedirs(frames_dir, exist_ok=True)

    existing_files = {f for f in listdir(frames_dir)}
    skip = True
    for i in frames:
        filename = 'img_%06d.jpg' % i
        if filename not in existing_files:
            skip = False
            break

    if not skip:
        with TemporaryDirectory() as tmp_dir:
            call([
                'ffmpeg',
                '-nostats', '-loglevel', '0',
                '-i', video_file,
                '-qscale:v', '3',
                path.join(tmp_dir, 'img_%06d.jpg')
            ])

            for i in frames:
                filename = 'img_%06d.jpg' % i
                move(
                    path.join(tmp_dir, filename),
                    path.join(frames_dir, filename)
                )

    return {
        'pose/2d': poses_2d,
        'pose/3d-univ': poses_3d,
        'intrinsics/' + camera: np.array([alpha_x, x_0, alpha_y, y_0]),
        'camera': np.array(int(camera)).repeat(len(poses_3d), axis=0),
        'frame': frames,
    }


def process_sequence(subject, action):
    datasets = {}

    for camera in tqdm(list(sorted(cameras.keys())), ascii=True, leave=False):
        annots = process_view(subject, action, camera)
        for k, v in annots.items():
            if k in datasets:
                datasets[k] = np.concatenate([datasets[k], v])
            else:
                datasets[k] = v

    out_dir = path.join('processed', subject, action)
    makedirs(out_dir, exist_ok=True)
    with h5py.File(path.join(out_dir, 'annot.h5'), 'w') as f:
        for name, data in datasets.items():
            f.create_dataset(name, data=data)


def process_all():
    for subject, action in tqdm(list(product(subjects, actions)), ascii=True, leave=False):
        process_sequence(subject, action)


if __name__ == '__main__':
  process_all()
