from tkinter import Tk, Label, Scale, X, Menu, HORIZONTAL, BOTTOM, TOP, filedialog, messagebox, IntVar, WORD
from tkinter.scrolledtext import ScrolledText
import json
import os

user_cfg_fp = './user_cfg.json'
tmp_file_path = './tmp_file.txt'
win_alpha_cfg = 80
auto_load_tmp_file_cfg = False
tmp_file_content = None

# 载入用户配置文件
try:
    f = open(user_cfg_fp, 'r')
    content = json.load(f)
    win_alpha_cfg = content.get('win_alpha')
    auto_load_tmp_file_cfg = content.get('auto_load_tmp_file')
    f.close()
except Exception as e:
    print(e)
    init_cfg = json.dumps({'win_alpha': '80', 'auto_load_tmp_file': False})
    with open(user_cfg_fp, 'w') as init_f:
        init_f.write(init_cfg)


class YobiDesktopNote:
    def __init__(self):
        # 窗体大小
        self.win_size = [300, 400]
        # 窗体最小大小
        self.min_size = [int(self.win_size[0] / 4), int(self.win_size[1] / 4)]
        # 窗体偏移
        self.win_offset = [0, 0]
        # 鼠标位置
        self.position = [0, 0]
        # 色彩
        self.main_color = '#DCDCDE'
        self.notes_bg_color = '#e7e7e7'
        # 窗口置顶配置
        self.win_topmost = True
        # 窗口透明度配置
        self.win_alpha_cfg = win_alpha_cfg

        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.win_offset[0] = int((self.root.winfo_screenwidth() - self.win_size[0]) / 2)
        self.win_offset[1] = int((self.root.winfo_screenheight() - self.win_size[1]) / 2)

        self.root.title('YobiDesktopNote v0.0.2')
        self.root.geometry(f'{self.win_size[0]}x{self.win_size[1]}+{self.win_offset[0]}+{self.win_offset[1]}')
        self.root.minsize(width=self.min_size[0], height=self.min_size[1])
        # 删除标题栏
        # self.root.update_idletasks()
        self.root.overrideredirect(True)
        # 窗口置顶
        self.root.attributes('-topmost', self.win_topmost)
        # 窗体透明
        # self.root.attributes("-alpha", 0.5)
        # 设置窗体背景
        self.root.configure(bg=self.main_color)

        # 功能条
        self.func_label = Label(self.root, text='★' * 40, height=2)
        self.func_label.pack(fill=X)
        # 创建右键菜单
        self.right_menu = Menu(self.func_label, tearoff=False)
        self.right_menu_auto_load_tmp_var = IntVar()
        self.right_menu_auto_load_tmp_var.set(1 if auto_load_tmp_file_cfg else 0)
        self.right_menu.add_checkbutton(label='启动时自动加载上一次编辑的笔记', onvalue=1, offvalue=0,
                                        variable=self.right_menu_auto_load_tmp_var)
        self.right_menu.add_command(label='保存笔记为文本文件', command=self.save_note_text)
        self.right_menu.add_command(label='置顶/取消置顶', command=self.win_set_topmost)
        self.right_menu.add_command(label="关闭", command=self.on_close)
        # self.right_menu.add_command(label='最小化', command=self.win_iconify)
        self.func_label.bind("<Button-3>", self.popup)
        # 拖动功能
        self.func_label.bind("<ButtonPress-1>", self.move_start)
        self.func_label.bind("<B1-Motion>", self.move)
        self.func_label.bind("<ButtonRelease-1>", self.move_end)
        # 笔记编辑区域
        self.notes_area = ScrolledText(self.root, autoseparators=False, undo=True, wrap=WORD)
        self.notes_area.pack(fill=X, expand=True, side=TOP)
        # 绑定键盘事件，插入分隔符
        self.notes_area.bind('<Key>', self.notes_area_add_separator)
        # 窗体透明度条
        self.win_transparent_scale = Scale(self.root, from_=100.0, to=20.0, resolution=1,
                                           sliderlength=20, orient=HORIZONTAL, command=self.set_win_alpha)
        self.win_transparent_scale.set(self.win_alpha_cfg)
        self.win_transparent_scale.pack(fill=X, side=BOTTOM)

        self.win_set_color()
        self.load_tmp_file()
        self.root.mainloop()

    def notes_area_add_separator(self, event):
        self.notes_area.edit_separator()

    def load_tmp_file(self):
        if not auto_load_tmp_file_cfg:
            return

        global tmp_file_content
        # 载入临时笔记文件
        if not os.path.exists(tmp_file_path):
            return
        with open(tmp_file_path, 'r', encoding='utf-8') as tmp_f:
            tmp_file_content = tmp_f.read()
        if not tmp_file_content:
            return

        self.notes_area.insert('end', tmp_file_content)
        self.notes_area.edit_separator()

    def win_set_color(self):
        self.func_label.configure(bg=self.main_color)
        # self.info_label.configure(bg=self.main_color)
        self.win_transparent_scale.configure(bg=self.main_color)
        self.notes_area.configure(bg=self.notes_bg_color)

    def on_close(self):
        # 保存用户配置
        with open(user_cfg_fp, 'r+') as fp:
            data = json.load(fp)
            data['win_alpha'] = self.win_transparent_scale.get()
            data['auto_load_tmp_file'] = True if self.right_menu_auto_load_tmp_var.get() == 1 else False
            # 文件指针移动到文件头
            fp.seek(0)
            # 清空文件内容
            fp.truncate()
            fp.write(json.dumps(data))

        # 保存笔记内容到临时文件
        note_content = self.notes_area.get('1.0', 'end-1c')
        if note_content.strip():
            with open(tmp_file_path, 'w', encoding='utf-8') as tmp_fp:
                tmp_fp.write(note_content)

        self.root.quit()
        self.root.destroy()

    def save_note_text(self):
        save_path = filedialog.asksaveasfilename(title=u'保存笔记到文本文件',
                                                 filetypes=[('记事本文件', '.txt'), ('所有文件', '*.*')],
                                                 defaultextension='.txt')

        if not save_path:
            return
        with open(save_path, 'w', encoding='utf-8') as save_fp:
            save_fp.write(self.notes_area.get('1.0', 'end-1c'))
        # Dialog(None, {'title': '保存完成', 'text': '文件已保存至' + save_path,
        #               'bitmap': '', 'strings': ('确定',),
        #               'default': ''})
        messagebox.showinfo('保存成功！', '已保存至' + save_path)

    def win_set_topmost(self):
        self.win_topmost = not self.win_topmost
        self.root.attributes('-topmost', self.win_topmost)
        print(self.win_topmost)

    def win_iconify(self):
        # 因为设置了self.root.overrideredirect(True)，无法最小化
        # self.root.iconify()
        self.root.state('icon')

    # 右键菜单弹出方式
    def popup(self, event):
        try:
            self.right_menu.post(event.x_root, event.y_root)
        finally:
            self.right_menu.grab_release()

    # 鼠标左键移动：拖动窗口
    def move(self, event):
        self.win_offset[0] = event.x - self.position[0] + self.root.winfo_x()
        self.win_offset[1] = event.y - self.position[1] + self.root.winfo_y()
        size_str = f"+{self.win_offset[0]}+{self.win_offset[1]}"
        self.root.geometry(size_str)
        # print(size_str)

    # 鼠标左键按下
    def move_start(self, event):
        self.position[0] = event.x
        self.position[1] = event.y

    # 鼠标左键释放
    def move_end(self, event):
        self.position[0] = 0
        self.position[1] = 0

    def set_win_alpha(self, value):
        self.root.attributes("-alpha", int(value) / 100)


if __name__ == '__main__':
    YobiDesktopNote()
