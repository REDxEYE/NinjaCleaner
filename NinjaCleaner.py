import os.path, sys
from PIL import Image

from DDS_reader import DDSFile

try:
    import PIL
except:
    try:
        from pip._internal import main
    except:
        from pip import main
    print('MISIING PIL LIBRARY - INSTALLING IT')
    main(['install', 'PIL'])
    print('PLEASE RESTART SCRIPT')
try:
    import flags
except:
    try:
        from pip._internal import main
    except:
        from pip import main
    print('MISIING flags LIBRARY - INSTALLING IT')
    main(['install', 'py-flags'])
    print('PLEASE RESTART SCRIPT')


class NinjaCleaner:

    def __init__(self, folder=''):
        self.folder = folder
        self.files = []
        self.to_remove = []
        self.to_keep = []

    def get_all_files(self, folder=None):
        if not folder:
            folder = self.folder
        print('Scanning ', folder, 'for files')
        for path in os.listdir(folder):
            path = os.path.join(folder, path)
            if os.path.isdir(path):
                self.get_all_files(path)
            if path.endswith('.dds'):
                self.files.append(path)

    def process_files(self):
        for file in self.files:
            im = DDSFile(file)
            im.read_header()
            w, h = im.size
            if w < h:
                w, h = h, w
            if w == 0 or h == 0:
                print('Zero dimension texture, skipping')
                self.to_remove.append(file)
                continue
            print(w%h)
            if w % h:
                # print('File is probably buffer,', file)
                self.to_remove.append(file)
            else:
                self.to_keep.append(file)


if __name__ == '__main__':
    c = NinjaCleaner(r'E:\PYTHON_STUFF\NinjaCleaner\test_data')
    c.get_all_files()
    c.process_files()
    # pprint(c.files)
