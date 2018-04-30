import os.path, sys
from PIL import Image



try:
    import PIL
except:
    from pip._internal import main
    main(['install','PIL'])
try:
    import flags
except:
    from pip._internal import main
    main(['install','flags'])

class NinjaCleaner:

    def __init__(self, folder=''):
        self.folder = folder
        self.files = []
        self.to_remove = []
        self.to_keep = []

    def get_all_files(self, folder=None):
        if not folder:
            folder = self.folder
        print('Scanning ',folder,'for files')
        for path in os.listdir(folder):
            path = os.path.join(folder, path)
            if os.path.isdir(path):
                self.get_all_files(path)
            if path.endswith('.dds'):
                self.files.append(path)

    def process_files(self):
        for file in self.files:
            im = Image.open(file)  # type:Image.Image
            w, h = im.size
            if w < h:
                w, h = h, w

            if w % h:
                # print('File is probably buffer,', file)
                self.to_remove.append(file)
            else:
                self.to_keep.append(file)


if __name__ == '__main__':
    folder = r'E:\PYTHON_STUFF\NinjaCleaner\test_data'
    c = NinjaCleaner(folder)
    c.get_all_files()
    c.process_files()
    # pprint(c.files)
