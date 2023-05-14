from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog,messagebox
import pickle
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pymysql
import time_series_analysis
import history_rank
import accident_type_analysis
import accident_zone_analysis
import accident_rate_analysis
import work_day_and_rest_day_analysis
import os


f = Figure(figsize=(1, 1), dpi=100)#figsize定义图像大小，dpi定义像素
f_plot = f.add_subplot(111)


class Exe(Tk):
    def __init__(self):
        super().__init__()
        self._set_window_()
        self._login_()


    #设置窗口的基本属性
    def _set_window_(self):
        self.title('事故数据自动分析系统登录界面')
        scn_width, scn_height = self.maxsize()
        self.wm_val = '750x450+{}+{}'.format((scn_width - 750) // 2, (scn_height - 450) // 2)
        self.geometry(self.wm_val)
        # print(self.wm_val)
        self.iconbitmap('titles.ico')
        self.protocol('WM_DELETE_WINDOW', self.exit_editor)

    def _login_(self):
        global image_file
        canvas = Canvas(self, width=750, height=150)
        image_file = PhotoImage(file='校徽logo.png')
        image = canvas.create_image(377, 2, anchor='n', image=image_file)
        canvas.pack(side='top')
        Label(self, text='身份验证', font=('Miscrosoft YaHei', 24)).pack(padx = 10,pady = 20)
        frame = Frame(self)
        Label(frame, text='账号：', font=('Arial', 16)).grid(row=0, column=0)
        Label(frame, text='密码：', font=('Arial', 16)).grid(row=1, column=0)
        self.var_user_name = StringVar()
        self.var_user_name.set('admin')
        entry_user_name = Entry(frame, textvariable=self.var_user_name, font=('Arial', 16))
        entry_user_name.grid(row=0, column=1, padx=10, pady=15)
        self.var_user_pwd = StringVar()
        entry_user_pwd = Entry(frame, textvariable=self.var_user_pwd, font=('Arial', 16), show='*')
        entry_user_pwd.grid(row=1, column=1, padx=10, pady=15)
        frame.pack()

        btn_login = Button(frame, text='登录', command =self.user_login)
        # btn_login.bind('<Enter>',lambda event: self.user_login(event)) #监听回车登录
        btn_login.grid(row = 2, column = 1,padx = 10, pady = 10,sticky = 'w')
        btn_sign_up = Button(frame, text='注册', command = self.usr_sign_up)
        btn_sign_up.grid(row = 2, column = 1,padx = 10, pady = 10,sticky = 'e')


    def user_login(self):
        user_name = self.var_user_name.get()
        user_pwd = self.var_user_pwd.get()

        try:
            with open('users_info.pickle', 'rb') as user_file:
                users_info = pickle.load(user_file)
        except FileNotFoundError:
            # 账号密码初始化，即用户名为`admin`密码为`admin`。
            with open('users_info.pickle', 'wb') as user_file:
                users_info = {'admin': 'admin'}
                pickle.dump(users_info, user_file)
                user_file.close()

        if user_name in users_info:
            if user_pwd == users_info[user_name]:
                messagebox.showinfo(title='登录成功', message='尊敬的 ' + user_name +'，欢迎使用事故数据自动分析系统！')
                self.open_new_frame()
            else:
                messagebox.showerror(message='抱歉，您的密码错误，请重新输入')
        else:
            is_sign_up = messagebox.askyesno('欢迎 ', '您还没有注册，现在进行注册？')
            if is_sign_up:
                self.usr_sign_up()


    def usr_sign_up(self):
        def sign_to_website():
            np = new_pwd.get()
            npf = new_pwd_confirm.get()
            nn = new_name.get()

            with open('users_info.pickle', 'rb') as usr_file:
                exist_usr_info = pickle.load(usr_file)
            if np != npf:
                messagebox.showerror('警告', '密码需要输入一致!')
            elif nn in exist_usr_info:
                messagebox.showerror('警告', '用户名已经被注册!')
            else:
                exist_usr_info[nn] = np
                with open('users_info.pickle', 'wb') as usr_file:
                    pickle.dump(exist_usr_info, usr_file)
                messagebox.showinfo('欢迎', '您已经成功注册!')
                window_sign_up.destroy()

        window_sign_up = Toplevel(self)
        window_sign_up.geometry('300x200+850+500')
        window_sign_up.title('注册窗口')
        window_sign_up.iconbitmap('titles.ico')

        new_name = StringVar()
        Label(window_sign_up, text='账户: ',  font=('Arial', 16)).place(x=10, y=10)
        entry_new_name = Entry(window_sign_up, textvariable=new_name)
        entry_new_name.place(x=130, y=20)

        new_pwd = StringVar()
        Label(window_sign_up, text='密码: ', font=('Arial', 16)).place(x=10, y=50)
        entry_usr_pwd = Entry(window_sign_up, textvariable=new_pwd, show='*')
        entry_usr_pwd.place(x=130, y=60)

        new_pwd_confirm = StringVar()
        Label(window_sign_up, text='核实密码: ', font=('Arial', 16)).place(x=10, y=90)
        entry_usr_pwd_confirm = Entry(window_sign_up, textvariable=new_pwd_confirm, show='*')
        entry_usr_pwd_confirm.place(x=130, y=100)

        btn_comfirm_sign_up = Button(window_sign_up, text='注册', command=sign_to_website)
        btn_comfirm_sign_up.place(x=180, y=150)


    def open_new_frame(self):
        self.withdraw()
        self.newframe =Toplevel(self)
        self.newframe.iconbitmap('titles.ico')
        screen_height =self.newframe.winfo_screenheight()
        screen_width = self.newframe.winfo_screenwidth()
        # 窗体的大小
        win_width = 0.8 * screen_width
        win_height = 0.8 * screen_height
        # 窗体出现的位置：控制的是左上角的坐标
        show_width = (screen_width - win_width) / 2
        show_height = (screen_height - win_height) / 2
        self.newframe.geometry(f'{win_width:.0f}x{win_height:.0f}+{show_width:.0f}+{show_height:.0f}')
        self.newframe.title("事故数据自动分析系统")
        self.newframe.protocol('WM_DELETE_WINDOW', self.exit_editor)

        #设置新窗口的布局
        self.create_tab_zone()


    def create_tab_zone(self):
        self.data_load_frame = LabelFrame(self.newframe, text = '数据加载')
        Button(self.data_load_frame,text = '加载本地文件',command = lambda : self.data_select('本地文件',self.data_glimpse_frame)).pack(padx = 5,pady = 10,fill = 'x', expand = 1)
        Button(self.data_load_frame, text='加载数据库文件', command = lambda : self.data_select('数据库文件',self.data_glimpse_frame)).pack(padx = 5,pady = 10,fill = 'x', expand = 1)
        self.data_load_frame.place(relx = 0.005,rely = 0.005, relwidth=0.15, relheight=0.2)

        self.data_option_frame = LabelFrame(self.newframe, text = '功能选项')
        # self.data_option_items = ['事故时间序列分析','事故类型占比分析','事故与工作日关联度分析','事故热点区域分析','事故发生省份分析','事故与节假日关联度分析','事故增长率分析']
        self.set_option_content()
        self.data_option_frame.place(relx=0.005, rely=0.22, relwidth=0.15, relheight=0.77)

        self.data_glimpse_frame = LabelFrame(self.newframe, text = '数据查看')
        demo_data = pd.read_excel('demo.xlsx')
        self.data_select(demo_data,self.data_glimpse_frame)
        self.data_glimpse_frame.place(relx=0.16, rely=0.005, relwidth=0.35, relheight=0.47)

        self.data_filter_conditions = LabelFrame(self.newframe)
        label_data_filter = Label(self.data_filter_conditions, text='请输入筛选条件:')
        label_data_filter.place(relx=0.01, rely=0.00, relwidth=0.2, relheight=0.87)
        self.entry_data_filter = Entry(self.data_filter_conditions)
        self.entry_data_filter.place(relx=0.2, rely=0.00, relwidth=0.12, relheight=0.87)

        Button(self.data_filter_conditions, text='确定', command=self.filter_data).place(relx=0.33,rely=0.00,relwidth=0.12,relheight=0.97)
        # Button(self.data_filter_conditions, text='筛选数据绘图', command=self.draw_picture).place(relx=0.63, rely=0.00,relwidth=0.22, relheight=0.97)
        Button(self.data_filter_conditions, text='保存数据', command=self.save_filter_data).place(relx=0.86, rely=0.00,relwidth=0.12, relheight=0.97)
        self.data_filter_conditions.place(relx=0.16, rely=0.477, relwidth=0.35, relheight=0.06)

        self.data_filter_frame = LabelFrame(self.newframe, text='数据筛选')
        self.data_filter_frame.place(relx=0.16, rely=0.54, relwidth=0.35, relheight=0.46)

        self.plot_params_frame = LabelFrame(self.newframe, text='绘图参数')
        Label(self.plot_params_frame, text='绘图类型:').place(relx = 0.01, rely =0.12)
        plot_type = ['饼图','折线图','散点图','条状图','横向条状图']
        self.combo = Combobox(self.plot_params_frame, width=12, values=plot_type)
        self.combo.set(plot_type[1])
        self.combo.place(relx = 0.11, rely = 0.1,relwidth = 0.1, relheight = 0.15)
        Label(self.plot_params_frame, text='提取数据条数:').place(relx=0.24, rely=0.12)
        self.data_num_params = Entry(self.plot_params_frame)
        self.data_num_params.place(relx=0.36, rely=0.11,relwidth = 0.1, relheight = 0.15)
        Label(self.plot_params_frame, text='指定x轴数据:').place(relx=0.5, rely=0.12)
        self.x_axis_params = Entry(self.plot_params_frame)
        self.x_axis_params.place(relx=0.62, rely=0.11, relwidth=0.1, relheight=0.15)
        Label(self.plot_params_frame, text='指定y轴数据:').place(relx=0.74, rely=0.12)
        self.y_axis_params = Entry(self.plot_params_frame)
        self.y_axis_params.place(relx=0.86, rely=0.11, relwidth=0.1, relheight=0.15)

        Label(self.plot_params_frame, text='绘制颜色:').place(relx=0.01, rely=0.42)
        self.color_params = Entry(self.plot_params_frame)
        self.color_params.place(relx= 0.11, rely=0.42, relwidth=0.1, relheight=0.15)
        Label(self.plot_params_frame, text='添加图形标记:').place(relx=0.24, rely=0.42)
        self.mark_params = Entry(self.plot_params_frame)
        self.mark_params.place(relx=0.36, rely=0.42, relwidth=0.1, relheight=0.15)
        Label(self.plot_params_frame, text='输入x轴标题:').place(relx=0.5, rely=0.42)
        self.x_title_params = Entry(self.plot_params_frame)
        self.x_title_params.place(relx=0.62, rely=0.42,relwidth = 0.1, relheight = 0.15)
        Label(self.plot_params_frame, text='输入y轴标题:').place(relx=0.74, rely=0.42)
        self.y_title_params = Entry(self.plot_params_frame)
        self.y_title_params.place(relx=0.86, rely=0.42, relwidth=0.1, relheight=0.15)

        self.str_val = StringVar()
        Radiobutton(self.plot_params_frame, text = '原生数据',value = '原生数据', variable = self.str_val, command = self.checkbotton_click).place(relx =0.3,rely = 0.65 ,relheight = 0.21, relwidth = 0.3)
        Radiobutton(self.plot_params_frame, text = '筛选数据',value = '筛选数据', variable =  self.str_val, command = self.checkbotton_click).place(relx =0.3,rely = 0.85 ,relheight = 0.15, relwidth = 0.3)

        Button(self.plot_params_frame,text = '提交参数', command = self.draw_picture).place(relx =0.45,rely = 0.75 ,relheight = 0.2, relwidth = 0.3)
        self.plot_params_frame.place(relx = 0.52, rely = 0.01, relwidth = 0.485, relheight = 0.23)

        self.data_plot_frame = LabelFrame(self.newframe, text = '数据绘图')
        self.canvs = FigureCanvasTkAgg(f, self.data_plot_frame)  # f是定义的图像，root是tkinter中画布的定义位置
        self.canvs.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        # Button(self.data_plot_frame, text='pic', command=self.draw_picture).pack(side = 'left')
        self.data_plot_frame.place(relx=0.52, rely=0.25, relwidth=0.485, relheight=0.73)

    def checkbotton_click(self):
        print(self.str_val.get())
        self.data_type =  self.str_val.get()

    def draw_picture(self):
        f_plot.clear()

        data_num = int(self.data_num_params.get())
        x = self.x_axis_params.get()
        y = self.y_axis_params.get().split('|')
        color = self.color_params.get().split('|')
        marker = self.mark_params.get().split('|')
        x_label = self.x_title_params.get()
        y_label = self.y_title_params.get()

        if self.data_type == '原生数据':
            data = self.data
        elif self.data_type == '筛选数据':
            data = self.filtered_data

        if self.combo.get() == '折线图':
            kind = 'line'
            data[y] = data[y].astype(float)
            for i in range(len(marker)):
                data[:data_num].plot(kind=kind, x=x, y=y[i], color=color[i], marker=marker[i], ax=f_plot)
            f_plot.set_xlabel(x_label)
            f_plot.set_ylabel(y_label)
        elif self.combo.get() == '散点图':
            kind = 'scatter'
            data[y] = data[y].astype(float)
            for i in range(len(marker)):
                data[:data_num].plot(kind=kind,x = x, y=y[i], color=color[i], marker=marker[i], ax=f_plot)
            f_plot.set_xlabel(x_label)
            f_plot.set_ylabel(y_label)
        elif self.combo.get() == '饼图':
            kind = 'pie'
            data[y] = data[y].astype(float)
            data = pd.Series(data[y[0]].values, index = data[x])
            data[:data_num].plot(kind=kind, y = y[0],autopct='%.1f%%',legend = True, ax = f_plot)
            f_plot.set_xlabel(x_label)
            f_plot.set_ylabel(y_label)
        elif self.combo.get() == '条状图':

            kind = 'bar'
            if marker[0] == '1':
                marker = True
            else:
                marker = False
            data = data.set_index(data[x])
            del data[x]
            print(data)
            data[:data_num].plot(kind=kind, stacked =marker,legend=True,rot = 0, ax=f_plot)
            f_plot.set_xlabel(x_label)
            f_plot.set_ylabel(y_label)
        elif self.combo.get() == '横向条状图':
            kind = 'barh'
            if marker[0] == '1':
                marker = True
            else:
                marker = False
            data.set_index(data[x],inplace=True)
            data_copy = data.copy()
            del data_copy[x]
            data_copy[:data_num].plot(kind=kind, stacked=marker, legend=True, rot = 0,ax=f_plot)
            f_plot.set_xlabel(x_label)
            f_plot.set_ylabel(y_label)

        self.canvs.draw()


    def set_option_content(self):
        time_series_ls = ['按年统计','按季度统计','按月统计']
        Label(self.data_option_frame , text='事故时间序列分析：').place(relx = 0.01,rely =0.05)
        self.combo_1 = Combobox(self.data_option_frame , width = 12,values=time_series_ls)
        self.combo_1.current(2)
        self.combo_1.place(relx = 0.01,rely =0.09,relwidth = 0.6 ,relheight = 0.04)
        Button(self.data_option_frame , text='确定',width = 6, command=self.time_series_command).place(relx = 0.62,rely =0.09,relwidth = 0.3 ,relheight = 0.04)

        accident_type_ls = ['按月统计','按季度统计','汇总']
        Label(self.data_option_frame, text='事故类型分析：').place(relx = 0.01,rely =0.21,relwidth = 0.6 ,relheight = 0.03)
        self.combo_2 = Combobox(self.data_option_frame, width=12, values=accident_type_ls)
        self.combo_2.current(2)
        self.combo_2.place(relx = 0.01,rely =0.25,relwidth = 0.6 ,relheight = 0.04)
        Button(self.data_option_frame, text='确定', width=6, command=self.accident_type_command).place(relx = 0.62,rely =0.25,relwidth = 0.3 ,relheight = 0.04)

        accident_zone_ls = ['各年份的事故数量', '事故死亡人数与GDP关联']
        Label(self.data_option_frame, text='事故发生省份分析：').place(relx = 0.01,rely =0.36,relwidth = 0.6 ,relheight = 0.03)
        self.combo_3 = Combobox(self.data_option_frame, width=20, values=accident_zone_ls)
        self.combo_3.current(0)
        self.combo_3.place(relx = 0.01,rely =0.39,relwidth = 0.6 ,relheight = 0.04)
        Button(self.data_option_frame, text='确定', width=6, command=self.accident_zone_command).place(relx = 0.62,rely =0.39,relwidth = 0.3 ,relheight = 0.04)

        accident_rate_ls = ['同比增长率','环比增长率']
        Label(self.data_option_frame, text='事故增长率分析：').place(relx = 0.01,rely =0.51,relwidth = 0.6 ,relheight = 0.03)
        self.combo_4 = Combobox(self.data_option_frame, width=12, values=accident_rate_ls)
        self.combo_4.current(0)
        self.combo_4.place(relx = 0.01,rely =0.54,relwidth = 0.6 ,relheight = 0.04)
        Button(self.data_option_frame, text='确定', width=6, command=self.accident_rate_command).place(relx = 0.62,rely =0.54,relwidth = 0.3 ,relheight = 0.04)

        accident_day_ls = ['数据汇总','加班期间发生的事故','正常周末发生的事故','节假日发生的事故']
        Label(self.data_option_frame, text='事故工作日、休息日关联分析：').place(relx = 0.01,rely =0.66,relwidth = 0.8 ,relheight = 0.03)
        self.combo_5 = Combobox(self.data_option_frame, width=20, values=accident_day_ls)
        self.combo_5.current(1)
        self.combo_5.place(relx = 0.01,rely =0.69,relwidth = 0.6 ,relheight = 0.04)
        Button(self.data_option_frame, text='确定', width=6, command=self.accident_day_command).place(relx = 0.62,rely =0.69,relwidth = 0.3 ,relheight = 0.04)

        history_ls = ['各省市双月','各省市汇总']
        Label(self.data_option_frame, text='事故数量历史动态变化分析：').place(relx=0.01, rely=0.81, relwidth=0.8, relheight=0.03)
        self.combo_6 = Combobox(self.data_option_frame, width=20, values=history_ls)
        self.combo_6.current(1)
        self.combo_6.place(relx=0.01, rely=0.84, relwidth=0.6, relheight=0.04)
        Button(self.data_option_frame, text='确定', width=6, command=self.accident_history_command).place(relx=0.62,rely=0.84,relwidth=0.3,relheight=0.04)


    def accident_history_command(self):
        if self.combo_6.get() == '各省市双月':
            data = history_rank.history_rank_month()
            self.data_select(data, self.data_glimpse_frame)

        else:
            data = history_rank.history_rank_acc()
            self.data_select(data, self.data_glimpse_frame)

    def accident_day_command(self):
        if self.combo_5.get() == '数据汇总':
            data = work_day_and_rest_day_analysis.get_data()
            self.data_select(data, self.data_glimpse_frame)
        elif self.combo_5.get() == '加班期间发生的事故':
            data = work_day_and_rest_day_analysis.get_data_add_work()
            self.data_select(data, self.data_glimpse_frame)
        elif self.combo_5.get() == '正常周末发生的事故':
            data = work_day_and_rest_day_analysis.get_data_weekend()
            self.data_select(data, self.data_glimpse_frame)
        else:
            data = work_day_and_rest_day_analysis.get_data_holidays()
            self.data_select(data, self.data_glimpse_frame)

    def accident_rate_command(self):
        if self.combo_4.get() == '同比增长率':
            data = accident_rate_analysis.accident_same_rate()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)
        else:
            data = accident_rate_analysis.accident_ring_rate()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)

    def accident_zone_command(self):

        if self.combo_3.get() == '各年份的事故数量':
            data = accident_zone_analysis.get_zone_data()
            data.columns = data.columns.astype(str)
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)
        elif self.combo_3.get() == '事故死亡人数与GDP关联':
            data = accident_zone_analysis.get_finial_data()
            self.data_select(data, self.data_glimpse_frame)


    def accident_type_command(self):
        if  self.combo_2.get() == '按月统计':
            data = accident_type_analysis.data_type_month()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)
        elif self.combo_2.get() == '按季度统计':
            data = accident_type_analysis.data_type_season()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)
        else:
            data = accident_type_analysis.data_type_acc()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)


    def time_series_command(self):
        if self.combo_1.get() == '按年统计':
            data = time_series_analysis.data_year()[0]
            data.set_index('年份',inplace= True)
            data.reset_index(inplace = True)
            self.data_select(data, self.data_glimpse_frame)

        elif self.combo_1.get() == '按季度统计':
            data = time_series_analysis.data_season_detail()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)

        else:
            data = time_series_analysis.data_month_detail()
            data.reset_index(inplace=True)
            self.data_select(data, self.data_glimpse_frame)

    def filter_data(self):
        conditions = self.entry_data_filter.get()
        print(conditions,type(conditions))
        if len(conditions) == 0:
            messagebox.showerror(message='抱歉，您的筛选条件错误，请重新输入')
        elif '|' not in conditions:
            if conditions in self.data.columns.tolist():
                self.filtered_data = pd.DataFrame(self.data[conditions])
                self.set_content(self.filtered_data, self.data_filter_frame)
            else:
                self.filtered_data = self.find_df_row(conditions)
                self.set_content(self.filtered_data, self.data_filter_frame)
        elif '|' in conditions:
            items = conditions.split('|')
            if set(items) <= set(self.data.columns.tolist()):
                self.filtered_data = self.data[items]
                self.set_content(self.filtered_data, self.data_filter_frame)
            else:
                self.filtered_data = self.find_df_row(conditions)
                self.set_content(self.filtered_data, self.data_filter_frame)

    def find_df_row(self,items):
        #第一种方式，太耗时间了
        # index_ls = []
        # # print(self.data)
        # for indexs in self.data.index:
        #     for i in range(len(self.data.loc[indexs].values)):
        #         if (str(self.data.loc[indexs].values[i]) in items) or (str(self.data.loc[indexs].values[i]) == items):
        #             # print(self.data.loc[indexs].values[i])
        #             index_ls.append(indexs)
        # self.df_row_data =  self.data.iloc[index_ls]

        # #第二种方式
        self.data = self.data.astype(str)
        df = pd.DataFrame()
        for column in self.data.columns:
            df_ = self.data[self.data[column].str.contains(items)]
            df = pd.concat([df,df_])
        self.df_row_data = df
        self.df_row_data.drop_duplicates(inplace = True)
        return self.df_row_data


    def save_filter_data(self):
        path = os.getcwd()
        file_name = filedialog.asksaveasfilename(
            title='打开我的文件', initialdir=path,
            filetype=[('xlsx', 'xlsx'), ('csv', 'csv'),('xls','xls')]
        )
        if '.xls' in file_name:
            self.df_row_data.to_excel(file_name,index = False)
        elif '.csv' in file_name:
            self.df_row_data.to_csv(file_name,index = False)
        else:
            self.df_row_data.to_excel(f'{file_name}.xlsx',index = False)

    def data_select(self,flag,set_frame):
        if type(flag) == str and flag == '本地文件':
            self.data = self.get_data()
        elif type(flag) == str and flag ==  '数据库文件':
            self.data = self.get_sql_data()
        else:
            self.data = flag
        self.set_content(self.data,set_frame)

    def set_content(self,data,set_frame):
        columns = data.columns.tolist()
        self.tree = Treeview(set_frame, show='headings', columns=columns)

        # 设置表头名称，根据上面的columns的顺序进行排序
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor='center')

        for i in range(len(data)):
            # 用“end”表示父节点的最后一个位置插入
            item = self.tree.insert('', 'end', values=tuple(data.iloc[i].tolist()))
        # 放置控件，rel*表示使用相对定位，相对于父容器的定位
        self.tree.place(relx=0.004, rely=0.028, relwidth=0.964, relheight=0.95)
        self.VScroll1 = Scrollbar(set_frame, orient='vertical', command=self.tree.yview)
        self.VScroll2 = Scrollbar(set_frame, orient='horizontal', command=self.tree.xview)
        self.VScroll1.place(relx=0.971, rely=0.028, relwidth=0.024, relheight=0.958)
        self.VScroll2.place(relx=0.028, rely=0.971, relwidth=0.958, relheight=0.024)
        # 给treeview添加配置

        self.tree.configure(yscrollcommand=self.VScroll1.set)
        self.tree.configure(xscrollcommand=self.VScroll2.set)

    def get_data(self):
        path = os.getcwd()
        file_name = filedialog.askopenfilename(
            title='打开我的文件', initialdir=path,
            filetype=[('xlsx', 'xlsx'), ('xls', 'xls')]
        )
        data = pd.read_excel(file_name)
        return data

    def get_sql_data(self):
        conn = pymysql.connect(host='127.0.0.1', user='root', passwd='lx520828', db='test')
        data = pd.read_sql('select * from accident_data', conn)
        return data

    def exit_editor(self):
        if messagebox.askokcancel('退出?', '确定退出吗?'):
            self.destroy()

if __name__ == '__main__':
    root = Exe()
    root.mainloop()