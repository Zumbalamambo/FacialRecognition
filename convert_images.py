IMAGES_DIR = {
    'train': './Images/train',
    'test': './Images/test'
}


def _has_path(path):
    import os

    return os.path.exists(path)


def _make_list(sampling):
    import os
    import random
    import numpy as np

    set_type_list = list(IMAGES_DIR.keys())
    set_type_list.sort()

    # list of class name
    class_list = []
    for class_name in os.listdir(IMAGES_DIR['train']):
        if not class_name.startswith('.'):
            class_list.append(class_name)
    class_list.sort()

    datasets = {}
    for set_type in set_type_list:
        datasets[set_type] = {}
        for class_ in class_list:
            # list of image file name
            image_list = []
            for image_name in os.listdir('{0}/{1}'.format(IMAGES_DIR[set_type], class_)):
                if image_name.endswith('.jpg') or image_name.endswith('.png'):
                    image_list.append(image_name)
            image_list.sort()

            datasets[set_type][class_] = image_list

    if not sampling:
        return datasets
    else:
        train_count = []
        for class_ in class_list:
            train_count.append(len(datasets['train'][class_]))

        test_count = []
        for class_ in class_list:
            test_count.append(len(datasets['test'][class_]))

        if sampling == 'over':
            min_ = min(train_count)
            max_ = max(train_count)
            idx = np.argmin(train_count)

            temp = []
            for _ in range(int(max_ / min_)):
                temp += datasets['train'][class_list[idx]]
            datasets['train'][class_list[idx]] = temp

            min_ = min(test_count)
            max_ = max(test_count)
            idx = np.argmin(test_count)

            temp = []
            for _ in range(int(max_ / min_)):
                temp += datasets['test'][class_list[idx]]
            datasets['test'][class_list[idx]] = temp
        elif sampling == 'under':
            idx = min(train_count)
            for class_ in class_list:
                random.shuffle(datasets['train'][class_])
                datasets['train'][class_] = datasets['train'][class_][:idx]

            idx = min(test_count)
            for class_ in class_list:
                random.shuffle(datasets['test'][class_])
                datasets['test'][class_] = datasets['test'][class_][:idx]

    return datasets


def _read_dataset(data_list, add_transpose):
    import random
    from PIL import Image

    set_type_list = list(data_list.keys())
    set_type_list.sort()

    class_list = list(data_list[set_type_list[0]].keys())
    class_list.sort()
    class_num = len(class_list)

    datasets = {}
    for set_type in set_type_list:
        dataset = []
        for (i, class_) in enumerate(class_list):
            image_list = data_list[set_type][class_]
            for image_name in image_list:
                image_path = '{0}/{1}/{2}'.format(IMAGES_DIR[set_type], class_, image_name)
                opened_image = Image.open(image_path).convert(mode='L')
                width, height = opened_image.size

                image = []
                for y in range(height):
                    for x in range(width):
                        image.append(
                            opened_image.getpixel((x, y))
                        )

                label = [0 for _ in range(class_num)]
                label[i] = 1

                data = {
                    'image': image,
                    'label': label
                }

                dataset.append(data)

                if add_transpose:
                    flipped_image = opened_image.transpose(Image.FLIP_LEFT_RIGHT)
                    image = []
                    for y in range(height):
                        for x in range(width):
                            image.append(
                                flipped_image.getpixel((y, x))
                            )

                    data = {
                        'image': image,
                        'label': label
                    }

                    dataset.append(data)

                    flipped_image = opened_image.transpose(Image.FLIP_TOP_BOTTOM)
                    image = []
                    for y in range(height):
                        for x in range(width):
                            image.append(
                                flipped_image.getpixel((y, x))
                            )

                    data = {
                        'image': image,
                        'label': label
                    }

                    dataset.append(data)

                opened_image.close()

        random.shuffle(dataset)
        datasets[set_type] = dataset

    return datasets


def _save_dataset(dataset, save_dir):
    import json
    import os
    import zipfile

    if not _has_path(save_dir):
        os.makedirs(save_dir)

    set_type_list = list(dataset.keys())
    set_type_list.sort()

    for set_type in set_type_list:
        if str(set_type).lower() == 'train':
            with open('{0}/{1}'.format(save_dir, 'train.json'), 'w', encoding='utf-8') as f:
                json.dump(dataset[set_type], f)
        elif str(set_type).lower() == 'test':
            with open('{0}/{1}'.format(save_dir, 'test.json'), 'w', encoding='utf-8') as f:
                json.dump(dataset[set_type], f)

    datasets_zip = zipfile.ZipFile('{0}/{1}'.format(save_dir, 'Datasets.zip'), 'w')

    for folder, subfolders, files in os.walk(save_dir):
        for f in files:
            if f.endswith('.json'):
                datasets_zip.write(
                    os.path.join(folder, f),
                    compress_type=zipfile.ZIP_DEFLATED
                )

    datasets_zip.close()

    os.remove('{0}/{1}'.format(save_dir, 'train.json'))
    os.remove('{0}/{1}'.format(save_dir, 'test.json'))


def convert(sampling=None, add_transpose=False, save_dir='./Datasets'):
    """
    Parameters
    ===========
    sampling : str
        sampling mode
    add_transpose : bool
        whether to add transpose
    save_dir : str
        the directory in which to store the dataset
    """
    data_list = _make_list(sampling)
    datasets = _read_dataset(data_list, add_transpose)
    _save_dataset(datasets, save_dir)

    print('Convert Dataset complete!')
