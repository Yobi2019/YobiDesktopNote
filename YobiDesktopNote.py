from tkinter import Tk, Label, Button, Scale, X, Menu, HORIZONTAL, BOTTOM, TOP, \
    Text, NONE, Scrollbar, RIGHT, filedialog, dialog, messagebox
from tkinter.scrolledtext import ScrolledText
import json

user_cfg_fp = './user_cfg.json'
win_alpha_cfg = 0

try:
    f = open(user_cfg_fp, 'r')
    content = json.load(f)
    win_alpha_cfg = content.get('win_alpha')
    f.close()
except Exception as e:
    print(e)
    init_cfg = json.dumps({'win_alpha': '80'})
    with open(user_cfg_fp, 'w') as init_f:
        init_f.write(init_cfg)
    win_alpha_cfg = 80


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
        self.right_menu.add_command(label='保存笔记为文本文件', command=self.save_note_text)
        self.right_menu.add_command(label='置顶/取消置顶', command=self.win_set_topmost)
        self.right_menu.add_command(label="关闭", command=self.on_close)
        # self.right_menu.add_command(label='最小化', command=self.win_iconify)
        self.func_label.bind("<Button-3>", self.popup)
        # 拖动功能
        self.func_label.bind("<ButtonPress-1>", self.move_start)
        self.func_label.bind("<B1-Motion>", self.move)
        self.func_label.bind("<ButtonRelease-1>", self.move_end)
        # 显示有关信息
        # self.info_label = Label(self.root, text='')
        # self.info_label.pack(fill=X)
        # 笔记编辑区域
        self.notes_area = ScrolledText(self.root)
        # 滚动条
        # self.h_scrollbar = Scrollbar(self.root)
        # self.h_scrollbar.pack(side=RIGHT, fill='y')
        # self.notes_area = Text(self.root, yscrollcommand=self.h_scrollbar.set)
        self.notes_area.pack(fill=X, expand=True, side=TOP)
        # 窗体透明度条
        self.win_transparent_scale = Scale(self.root, from_=100.0, to=20.0, resolution=1,
                                           sliderlength=20, orient=HORIZONTAL, command=self.set_win_alpha)
        self.win_transparent_scale.set(self.win_alpha_cfg)
        self.win_transparent_scale.pack(fill=X, side=BOTTOM)
        # 占位
        # Label(self.root, text='').pack(fill=X)
        # 关闭按钮
        # self.quit_btn = Button(self.root, text='退出', command=self.on_close)
        # self.quit_btn.pack(fill=X, side=BOTTOM)

        self.win_set_color()
        self.root.mainloop()

    def win_set_color(self):
        self.func_label.configure(bg=self.main_color)
        # self.info_label.configure(bg=self.main_color)
        self.win_transparent_scale.configure(bg=self.main_color)
        self.notes_area.configure(bg=self.notes_bg_color)

    def on_close(self):
        with open(user_cfg_fp, 'r+') as fp:
            data = json.load(fp)
            data['win_alpha'] = self.win_transparent_scale.get()
            # 文件指针移动到文件头
            fp.seek(0)
            # 清空文件内容
            fp.truncate()
            fp.write(json.dumps(data))

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
        # dialog.Dialog(None, {'title': '保存完成', 'text': '文件已保存至' + save_path,
        #                      'bitmap': '', 'strings': ('确定', ),
        #                      'default': ''})
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
        self.right_menu.post(event.x_root, event.y_root)

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
