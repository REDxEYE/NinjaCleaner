import struct
from enum import IntEnum
from flags import Flags

DDS_MAGIC = b'DDS '
DDS_MAGIC_I = 542327876
DDS_HEADER_SIZE = 124
DDS_PIXEL_HEADER_SIZE = 32


class DDSFlags(Flags):
    DDSD_CAPS = 0x1  # Required in every.dds file
    DDSD_HEIGHT = 0x2  # Required in every .dds file
    DDSD_WIDTH = 0x4  # Required in every .dds file
    DDSD_PITCH = 0x8  # Required when pitch is provided for an uncompressed texture
    DDSD_PIXELFORMAT = 0x1000  # Required in every .dds file
    DDSD_MIPMAPCOUNT = 0x20000  # Required in a mipmapped texture
    DDSD_LINEARSIZE = 0x80000  # Required when pitch is provided for a compressed texture
    DDSD_DEPTH = 0x800000  # Required in a depth texture


class DDSPixelFlags(Flags):
    DDPF_ALPHAPIXELS = 0x1  # Texture contains alpha data; dwRGBAlphaBitMask contains valid data.
    DDPF_ALPHA = 0x2  # Used in some older DDS files for alpha channel only uncompressed data (dwRGBBitCount contains the alpha channel bitcount; dwABitMask contains valid data)
    DDPF_FOURCC = 0x4  # Texture contains uncompressed RGB data; dwRGBBitCount and the RGB masks (dwRBitMask, dwGBitMask, dwBBitMask) contain valid data.
    DDPF_RGB = 0x40  # Texture contains uncompressed RGB data; dwRGBBitCount and the RGB masks (dwRBitMask, dwGBitMask, dwBBitMask) contain valid data.
    DDPF_YUV = 0x200  # Used in some older DDS files for YUV uncompressed data (dwRGBBitCount contains the YUV bit count; dwRBitMask contains the Y mask, dwGBitMask contains the U mask, dwBBitMask contains the V mask)
    DDPF_LUMINANCE = 0x20000  # Used in some older DDS files for single channel color uncompressed data (dwRGBBitCount contains the luminance channel bit count; dwRBitMask contains the channel mask). Can be combined with DDPF_ALPHAPIXELS for a two channel DDS file.


class DDSFile:
    # struct DDS_HEADER{
    #   DWORD           dwSize;
    #   DWORD           dwFlags;
    #   DWORD           dwHeight;
    #   DWORD           dwWidth;
    #   DWORD           dwPitchOrLinearSize;
    #   DWORD           dwDepth;
    #   DWORD           dwMipMapCount;
    #   DWORD           dwReserved1[11];
    #   DDS_PIXELFORMAT ddspf;
    #   DWORD           dwCaps;
    #   DWORD           dwCaps2;
    #   DWORD           dwCaps3;
    #   DWORD           dwCaps4;
    #   DWORD           dwReserved2;
    # } ;

    # struct DDS_PIXELFORMAT {
    #   DWORD dwSize;
    #   DWORD dwFlags;
    #   DWORD dwFourCC;
    #   DWORD dwRGBBitCount;
    #   DWORD dwRBitMask;
    #   DWORD dwGBitMask;
    #   DWORD dwBBitMask;
    #   DWORD dwABitMask;
    # };

    def __init__(self, path: str):
        self.path = path
        self.file = open(path, 'rb')
        self.read = lambda size: self.file.read(size)
        self.size = (0, 0)
        self.flags = None  # type:DDSFlags
        self.pixel_flags = None  # type:DDSPixelFlags
        self.no_mipmaps = True
        self.bytes_per_channel = 0
        self.pixel_fourcc = ''
        self.data_start = 0

    def read_header(self):
        self.file.seek(0, 2)
        size = self.file.tell()
        self.file.seek(0)
        fourcc, header_size = struct.unpack('II', self.read(8))
        assert fourcc == DDS_MAGIC_I
        if header_size > DDS_HEADER_SIZE:
            raise NotImplementedError('Unknown DDS header format')
        flags, height, width, _, depth, mipmap_count = struct.unpack('IIIIII', self.read(6 * 4))
        # print(height,width)
        self.size = (width, height)
        self.flags = DDSFlags(flags)
        self.file.seek(11 * 4, 1)  # skip DWORD dwReserved1[11];
        p_size = struct.unpack('I', self.read(4))[0]
        if p_size > DDS_PIXEL_HEADER_SIZE:
            raise NotImplementedError('Unknown pixel header format')
        p_flags, p_fourcc, rgb_bits = struct.unpack('III', self.read(4 * 3))
        self.bytes_per_channel = rgb_bits // 8
        self.pixel_fourcc = b''.join(struct.unpack("cccc", struct.pack('I', p_fourcc))).decode()
        self.pixel_flags = DDSPixelFlags(p_flags)
        r_bits, g_bits, b_bits, a_bits = struct.unpack('IIII', self.read(4 * 4))
        self.file.seek(4 * 4, 1)
        self.data_start = self.file.tell()
        if DDSFlags.DDSD_MIPMAPCOUNT in self.flags:
            self.no_mipmaps = False

    def get_image(self):
        from PIL import Image
        self.file.seek(self.data_start)
        w, h = self.size
        if DDSPixelFlags.DDPF_RGB in self.pixel_flags:
            return Image.frombytes('RGBA', self.size, self.read(w * h * self.bytes_per_channel))
        elif DDSPixelFlags.DDPF_FOURCC in self.pixel_flags:
            return Image.open(self.path)
        else:
            print(self.pixel_flags)
            print(self.flags)
            raise NotImplementedError('This format is not currently supported')


if __name__ == '__main__':
    dds = DDSFile(r'E:\PYTHON_STUFF\NinjaCleaner\test_data\palma_1\2018.04.22_17.56.26_Sniper_x86.exe\Tex_0003_0.dds')
    dds.read_header()
    from PIL import Image

    print(dds.get_image())
    a = dds.get_image()
    a.save(r'./test_data/test.png')
