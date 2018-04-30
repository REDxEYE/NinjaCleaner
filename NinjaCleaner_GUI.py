from tkinter import Tk
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askdirectory
import os.path
from PIL import ImageTk
from PIL import Image
from DDS_reader import DDSFile
from NinjaCleaner import NinjaCleaner
from tkinter import messagebox

class NinjaCleanderGui(Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.file_path = ''
        self.ninja_cleaner = NinjaCleaner(self.file_path)
        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)

        self.filemenu.add_command(label="Open folder", command=self.select_folder)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.delete_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Delete", menu = self.delete_menu)
        self.delete_menu.add_command(label="Delete unnecessary files", command=self.delete)

        self.master = master
        master.config(menu=self.menubar)
        master.title("NinjaCleaner gui")
        self.current_img = ''
        list_frame = Frame(self)
        list_frame.pack(side= LEFT)
        to_keep_frame = Frame(list_frame)
        to_keep_frame.pack()
        Label(to_keep_frame, text='To keep').pack(fill=Y)
        self.to_keep = Listbox(to_keep_frame, width=100)
        self.to_keep.pack(fill=Y, anchor=S)
        self.to_keep.bind('<<ListboxSelect>>', self.on_select)
        to_remove_frame = Frame(list_frame)
        to_remove_frame.pack()
        Label(to_remove_frame, text='To remove').pack(fill=Y)
        self.to_remove_files = Listbox(to_remove_frame, width=100)
        self.to_remove_files.pack(fill=Y, anchor=S)
        self.to_remove_files.bind('<<ListboxSelect>>', self.on_select)
        self.image = Image.new('RGB', (512, 512))
        self.img = ImageTk.PhotoImage(image=self.image)
        self.img_label = Label(self)
        self.img_label.configure(image=self.img)
        self.img_label._image_cache = self.img
        self.img_label.pack(side=RIGHT)

    def resize(self,img:Image.Image):
        w,h = img.size
        if w<h:
            w,h = h,w
        k = h / w
        width,height = (int(512 * (k if w<h else 1)), int(512 * (k if h<w else 1)))
        # print(k,width,height)
        return img.resize((width,height))

    def on_select(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        if not w.curselection():
            return
        index = int(w.curselection()[0])
        value = w.get(index)
        self.current_img = value
        dds_file = DDSFile(value)
        dds_file.read_header()
        print('Loaded {} {}'.format(os.path.basename(value), dds_file.size))
        print(dds_file.get_image())
        self.img.paste(Image.new('RGBA',(512,512)))
        self.img.paste(self.resize(dds_file.get_image()))
        dds_file.file.close()

    def delete(self):
        ans = messagebox.askyesno(title='Are you sure?',message = 'Remove all files from \'to remove\' list?')
        if not ans:
            return
        for file in self.ninja_cleaner.to_remove:
            # print(file)
            os.remove(file)

    def select_folder(self):
        self.to_keep.delete(0, END)
        self.to_remove_files.delete(0, END)
        self.file_path = askdirectory()
        self.ninja_cleaner.folder = self.file_path
        self.ninja_cleaner.get_all_files()
        self.ninja_cleaner.process_files()
        for to_keep in self.ninja_cleaner.to_keep:
            self.to_keep.insert(END, to_keep)

        for to_remove in self.ninja_cleaner.to_remove:
            self.to_remove_files.insert(END, to_remove)


if __name__ == '__main__':
    root = Tk()
    my_gui = NinjaCleanderGui(root)
    my_gui.pack()
    root.mainloop()
