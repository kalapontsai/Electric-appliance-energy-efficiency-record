#test chart tool / Author:Kadela
#rev 0.7 : 2025/2/6 : GUI mode config edit
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.ticker import AutoLocator
import numpy as np
from scipy import stats
import configparser
import argparse
import sys,os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# 初始化組態設定
config = configparser.ConfigParser()

class show_chart:
    def __init__():
        global modified_data

    def read_csv():
        # 讀取 CSV, 需手動新增csv檔內[Date][Time]欄位名稱
        # rev 0_2 判斷config內變數[DT] 自動合併日期與時間欄位
        try:
            if entry_dt.get() == "0":
                data = pd.read_csv(entry_tempfile.get(), parse_dates=['DateTime'])
            else:
                data = pd.read_csv(entry_tempfile.get())
                data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])

        #讀取HIOKI PW3335 PC版軟體PWCommunicatorV170zh csv.log
        #前兩行為儀器序號等無用資料,須排除skiprows=2
            if entry_dt.get() == "0" and entry_power_skip.get() == "0":
                Power_data = pd.read_csv(entry_powerfile.get(), parse_dates=['DateTime'], skiprows=2)
            elif entry_dt.get() == "1" and entry_power_skip.get() == "0":
                Power_data = pd.read_csv(entry_powerfile.get(), skiprows=2)
                Power_data['DateTime'] = pd.to_datetime(Power_data['Date'] + ' ' + Power_data['Time'])
            else:
                Power_data = pd.DataFrame()
            
            data = data.sort_values(by='DateTime').reset_index(drop=True)
            if entry_power_skip.get() == "0":
                Power_data = Power_data.sort_values(by='DateTime').reset_index(drop=True)
        except KeyError as e:
            print("日期時間的欄位名稱不正確:",e)
            return
        except FileNotFoundError:
            print("檔案不存在")
            return
        return data,Power_data

    def plot(df,legend_list):
        # 部分項目若不顯示,刪除頻道檢查項目
        if entry_power_skip.get() == "1" and entry_rh_skip.get() == "1":
            fig, ax1 = plt.subplots()
        elif entry_rh_skip.get() == "0" and entry_power_skip.get() == "1":
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(10, 6))
            plt.subplots_adjust(left=0.15, right=0.85, bottom=0.15, top=0.85, hspace=0.1)
        elif entry_rh_skip.get() == "1" and entry_power_skip.get() == "0":
            fig, (ax1, ax3) = plt.subplots(nrows=2, sharex=True, figsize=(10, 6))
            plt.subplots_adjust(left=0.15, right=0.85, bottom=0.15, top=0.85, hspace=0.1)
        else:
            fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, sharex=True, figsize=(10, 6))
            plt.subplots_adjust(left=0.15, right=0.85, bottom=0.15, top=0.85, hspace=0.1)

        #強制 Matplotlib 使用系統默認的減號符號，而不是從字體中查找
        plt.rcParams['axes.unicode_minus'] = False

        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 指定中文字體正黑體
        # 指定字體路徑和名稱
        #font_path = 'C:/Windows/Fonts/msjh.ttc'  # 替換為你電腦上的微軟正黑體路徑
        #font_prop = fm.FontProperties(fname=font_path)

        plt.rcParams['font.size'] = entry_fontsize.get()
        fig.suptitle(entry_title.get(),horizontalalignment='left')

        #以日期時間格式作為X軸
        try:
            pd.to_datetime(df["DateTime"], format=format)
            df.set_index('DateTime', inplace=True)
            plt.xticks(rotation=45)
            #print("X軸格式為datetime")
        except ValueError:
            plt.xticks(np.arange(0, len(df['DateTime']), int(entry_xticks.get())), rotation=45)
            print("X軸格式非datetime")

        # 繪製溫度的子圖
        ax1.set_ylabel('Temp')
        ax1.grid(True, linestyle='dashdot')
        ax1.tick_params(labelcolor='black', labelsize='small', width=1)
        #判定是否自動設定 Y 軸範圍
        if entry_y_limit_auto.get() != "1":
            # 計算欄位的最大值和最小值
            max_value = max(df[col].max() for col in columns if col in df)
            min_value = min(df[col].min() for col in columns if col in df)
            print(f"設定Y軸最大值: {max_value}, 最小值: {min_value}")

            # 根據設定的比例調整上下限
            if min_value < 0:
                ax1.set_ylim(min_value * float(entry_y_limit_min.get()), max_value * float(entry_y_limit_max.get()))
            else:
                ax1.set_ylim(min_value / float(entry_y_limit_min.get()), max_value * float(entry_y_limit_max.get()))

        for i in legend_list:
            ax1.plot(df[i], label=i)

        ax1.legend(ncol=len(legend_list), loc='lower left', fontsize=6)
        ax1.yaxis.set_major_locator(plt.MultipleLocator(float(entry_yaxis_major_locator.get())))  # y 轴主刻度间隔
        if int(entry_yaxis_minor_locator.get()) > 0 :
            ax1.yaxis.set_minor_locator(plt.MultipleLocator(int(entry_yaxis_minor_locator.get())))

        # 在第二个子图中绘制 RH
        if entry_rh_skip.get() != "1":
            ax2.set_ylabel('RH%')
            ax2.grid(True, linestyle='dashdot')
            ax2.tick_params(labelcolor='black', labelsize='small', width=1)
            ax2.yaxis.set_major_locator(plt.MultipleLocator(5))  # y 轴主刻度间隔
            ax2.set_ylim(70, 90)
            ax2.plot(df['RH'])
        #ax2.yaxis.set_minor_locator(plt.MultipleLocator(1))
        #ax2.legend()

        # 在第3个子图中绘制 電力
        if entry_power_skip.get() != "1":
            ax3.set_ylabel('Watt')
            ax3.grid(True, linestyle='dashdot')
            ax3.tick_params(labelcolor='black', labelsize='small', width=1)
            ax3.yaxis.set_major_locator(plt.MultipleLocator(50))  # y 轴主刻度间隔为 0.5
            ax3.yaxis.set_minor_locator(plt.MultipleLocator(10))
            #ax3.set_ylim(0, 200)
            ax3.plot(df['W'])

            # 創建第二个和第三个Axes对象，并将其放置在第一个Axes对象之上
            ax31 = ax3.twinx()
            ax32 = ax3.twinx()

            # 調整第二个Axes的位置，避免標籤重疊
            ax31.spines['right'].set_position(('axes', 1.0))
            ax31.set_frame_on(False)
            ax31.get_xaxis().set_visible(False)
            ax31.get_yaxis().set_visible(True)
            #self.make_patch_spines_invisible(ax31)
            ax31.spines['right'].set_visible(True)

            # 在第二个和第三个Axes中绘制線
            ax31.set_ylabel('Current', color='green')
            #ax31.set_ylim(0, 10)
            ax31.plot(df['I'], label='I', color='green')

            #ax31.tick_params(axis='y', color='green')
            ax32.spines['right'].set_position(('axes', 1.06))
            ax32.set_frame_on(False)
            ax32.get_xaxis().set_visible(False)
            ax32.get_yaxis().set_visible(True)
            #self.make_patch_spines_invisible(ax32)
            ax32.spines['right'].set_visible(True)
            ax32.set_ylabel('Volt', color='orange')
            ax32.set_ylim(-5, 120)
            ax32.plot(df['Volt'], label='V', color='orange')
        # 显示图形
        plt.show()

    def run(action = 0):
        data, Power_data = show_chart.read_csv()

        Channel_check_list = entry_temp.get().split(',')
        #檢查csv內是否有INI設定的temp欄位,RH
        # 部分項目若不顯示,刪除頻道檢查項目
        print(f"資料欄位 : {list(data)}")
        if entry_rh_skip.get() == "0" and "RH" not in data.columns:
            print(f"頻道 [RH] ... 未找到 !!")
            entry_rh_skip.delete(0, tk.END)
            entry_rh_skip.insert(0, "1")
        #檢查頻道資料是否存在
        for i in Channel_check_list:
            if i in data.columns:
                print(f"頻道 [{i}] ... 確認OK")
            else:
                print(f"頻道 [{i}] ... 未找到 !!")
                Channel_check_list.remove(i)

        #0_6_1 刪除異常值
        # 將結果儲存為一個新的 DataFrame
        filtered_data = data.copy()
        show_chart.modified_data = pd.DataFrame(columns=data.columns)  # 儲存被修改的數據

        # 處理需要檢查的欄位
        for col in Channel_check_list:
            if col in data.columns:
                filtered_data[col] = show_chart.process_column(data[col], col)

        # 確保 modified_data 的索引與原始 DataFrame 一致
        show_chart.modified_data = show_chart.modified_data.reindex(data.index)

        # 輸出結果
        #print("過濾後的數據：")
        #print(filtered_data)
        if not show_chart.modified_data.dropna(how='all').empty :
            print("\n溫度異常,已修正的數據：")
            #print(show_chart.modified_data)
            print(show_chart.modified_data.dropna(how='all'))

        data = filtered_data.copy()

        #使用 merge_asof 將最近的時間對應欄位合併進 data
        Unmatched_power = False
        if entry_power_skip.get() == "0":
            merged_data = pd.merge_asof(
                data,
                Power_data,
                on='DateTime',
                direction='nearest',
                tolerance=pd.Timedelta(seconds=60)
            )
            # 檢查未能匹配的情況
            unmatched_rows = merged_data[merged_data['U(V)'].isna()]
            if not unmatched_rows.empty:
                Unmatched_power = True
                print("以下目標時間未能找到一分鐘以內的電力值：")
                print(unmatched_rows['DateTime'])

            # 將合併的結果分配回 data
            data['Volt'] = merged_data['U(V)']
            data['I'] = merged_data['I(A)']
            data['W'] = merged_data['P(W)']
            data['WH'] = merged_data['WP(Wh)']
        else:
            Unmatched_power = False
        print(f"\n電力檔合併，筆數: {len(data)}")
        #print(data)
        if action == 1:
            return data
        else:
            show_chart.plot(data,Channel_check_list)

    def process_column(column, col_name):
        threshold = 100
        # 將欄位轉換為數值
        column = pd.to_numeric(column, errors='coerce')

        # 計算差異
        diff = column.diff().abs()

        # 篩選數據，將超過閾值的數據用前一筆取代
        modified_rows = []
        for i in range(1, len(column)):
            if diff[i] > threshold:
                modified_rows.append((i, column[i]))  # 記錄修改前的值
                column[i] = column[i - 1]

        # 將被修改的數據儲存到 modified_data
        for row, old_value in modified_rows:
            show_chart.modified_data.loc[row, col_name] = old_value

        return column

    def stat():
        data = show_chart.run(1)
        data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
        #print(f"已收到data")
        #print(data)
        txt_Result = ""
        StatChannel_list = entry_stats.get().split(',')
        #Channel_check_list = entry_temp.get().split(',')
        err_check = False

        if entry_stat_range.get() != "1":

            txt_Result = "[℃]  AVG    Max     Min (" + str(data["DateTime"].iloc[0].strftime('%m/%d %H:%M')) + " ~ " \
                    + str(data["DateTime"].iloc[-1].strftime('%m/%d %H:%M')) + ")\n"
            
            for c in StatChannel_list:
                if c in data.columns:
                    stat_result = "\n[" + c + "]  " \
                    + str(data[c].mean().round(1)) \
                    + "  " + str(data[c].max().round(1)) \
                    + "  " + str(data[c].min().round(1))
                    txt_Result += stat_result
                else:
                    print(f"統計欄位 : {StatChannel_list}")
                    print(f"在資料欄位 {list(data)} 未找到 [{c}] !!")
                    StatChannel_list.remove(c)
        else:
            if isinstance(int(entry_stat_start.get()), int) and isinstance(int(entry_stat_stop.get()), int):
                Int_record_start = int(entry_stat_start.get())
                Int_record_stop = int(entry_stat_stop.get())
            else:
                messagebox.showwarning("警告", "區段位置須為整數 !!")
                err_check = True

            if Int_record_start > 0 and Int_record_stop <= len(data) : 
                txt_Result += "\n[℃]  AVG  Max   Min (" + \
                    str(data["DateTime"].iloc[Int_record_start - 1].strftime('%m/%d %H:%M')) + "~" \
                    + str(data["DateTime"].iloc[Int_record_stop - 1].strftime('%m/%d %H:%M')) + ")"
                for c in StatChannel_list:
                    if c in data.columns:
                        stat_result = "\n[" + c + "]  " + str(data[c].iloc[Int_record_start - 1:Int_record_stop - 1].mean().round(1)) \
                        + "  " + str(data[c].iloc[Int_record_start - 1:Int_record_stop - 1].max().round(1)) \
                        + "  " + str(data[c].iloc[Int_record_start - 1:Int_record_stop - 1].min().round(1))
                        txt_Result += stat_result
                    else:
                        print(f"統計欄位 : {StatChannel_list}")
                        print(f"在資料欄位 {list(data)} 未找到 [{c}] !!")
                        StatChannel_list.remove(c)
            else:
                messagebox.showwarning("警告", "已開啟統計範圍設定,但範圍與資料筆數不符 !!")
                err_check = True

        if entry_power_skip.get() == "0" and entry_stat_power.get() == "1":
            #判斷是否以區段做計算
            if entry_stat_range.get() == "1":
                r_begin = Int_record_start - 1
                r_end = Int_record_stop - 1
            else:
                r_begin = 0
                r_end = len(data) - 1
            #print(r_begin,r_end,data["WH"].iloc[r_begin],data["WH"].iloc[r_end])
            WH_p = int(data["WH"].iloc[r_end] - data["WH"].iloc[r_begin])
            WH_t = data["DateTime"].iloc[r_end] - data["DateTime"].iloc[r_begin]
            #print(data["DateTime"].iloc[r_begin],data["DateTime"].iloc[r_end])
            WH_tmin = int(WH_t.total_seconds() // 60)
            txt_Result += "\n\n能耗計算:\n"
            txt_Result += str(WH_p) + "W/" + str(WH_tmin) + " min"
            EF = int((WH_p / WH_tmin) * 1440)
            txt_Result += " (" + str(EF) + "W/24H)"

        if err_check == False:
            # 取得目前日期和時間
            now = datetime.datetime.now()
            # 將日期和時間格式化為字串
            filename = now.strftime("%m%d_%H%M%S") + ".txt"
            # 建立檔案並寫入內容
            with open(filename, "w") as f:
                f.write(txt_Result)
            messagebox.showinfo("成功", f"統計結果儲存為 {filename}")

def load_config():
    """讀取選擇的組態檔並填入 GUI"""
    global config
    filepath = filedialog.askopenfilename(filetypes=[("INI Files", "*.ini")])  # 讓使用者選擇 config.ini
    filepath = filepath.replace("/", "\\")
    if not filepath:
        messagebox.showwarning("警告", "未選擇組態檔，請手動輸入設定")
        return
    
    entry_configfile.delete(0, tk.END)
    entry_configfile.insert(0, filepath)
    
    config.read(filepath, encoding='utf-8')

    # 讀取 FILE 欄位
    entry_tempfile.delete(0, tk.END)
    entry_tempfile.insert(0, config.get('FILE', 'tempfile', fallback=""))

    entry_powerfile.delete(0, tk.END)
    entry_powerfile.insert(0, config.get('FILE', 'powerfile', fallback=""))

    # 讀取其他欄位 (舉例: 繪圖設定)
    entry_title.delete(0, tk.END)
    entry_title.insert(0, config.get('PLT', 'title', fallback=""))

    entry_fontsize.delete(0, tk.END)
    entry_fontsize.insert(0, config.get('PLT', 'fontsize', fallback=""))

    entry_yaxis_major_locator.delete(0, tk.END)
    entry_yaxis_major_locator.insert(0, config.get('PLT', 'yaxis_major_locator', fallback=""))

    entry_yaxis_minor_locator.delete(0, tk.END)
    entry_yaxis_minor_locator.insert(0, config.get('PLT', 'yaxis_minor_locator', fallback=""))

    entry_xticks.delete(0, tk.END)
    entry_xticks.insert(0, config.get('PLT', 'xticks', fallback=""))

    entry_y_limit_auto.delete(0, tk.END)
    entry_y_limit_auto.insert(0, config.get('PLT', 'y_limit_auto', fallback=""))

    entry_y_limit_max.delete(0, tk.END)
    entry_y_limit_max.insert(0, config.get('PLT', 'y_limit_max', fallback=""))

    entry_y_limit_min.delete(0, tk.END)
    entry_y_limit_min.insert(0, config.get('PLT', 'y_limit_min', fallback=""))

    entry_dt.delete(0, tk.END)
    entry_dt.insert(0, config.get('CHANNEL', 'dt', fallback=""))

    entry_temp.delete(0, tk.END)
    entry_temp.insert(0, config.get('CHANNEL', 'temp', fallback=""))

    entry_rh_skip.delete(0, tk.END)
    entry_rh_skip.insert(0, config.get('CHANNEL', 'rh_skip', fallback=""))

    entry_power_skip.delete(0, tk.END)
    entry_power_skip.insert(0, config.get('CHANNEL', 'power_skip', fallback=""))

    entry_stats.delete(0, tk.END)
    entry_stats.insert(0, config.get('STAT', 'stats', fallback=""))

    entry_stat_range.delete(0, tk.END)
    entry_stat_range.insert(0, config.get('STAT', 'stat_range', fallback=""))

    entry_stat_start.delete(0, tk.END)
    entry_stat_start.insert(0, config.get('STAT', 'stat_start', fallback=""))

    entry_stat_stop.delete(0, tk.END)
    entry_stat_stop.insert(0, config.get('STAT', 'stat_stop', fallback=""))

    entry_stat_power.delete(0, tk.END)   
    entry_stat_power.insert(0, config.get('STAT', 'stat_power', fallback=""))


def select_file(entry_widget):
    """讓使用者選擇檔案並將路徑填入對應的輸入框"""
    filepath = filedialog.askopenfilename(filetypes=[("log Files", "*.csv")])
    filepath = filepath.replace("/", "\\")
    if filepath:  # 確保使用者有選擇檔案
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filepath)

def save_config():

    # 獲取用戶輸入的內容
    config['FILE'] = {
        'configfile': entry_configfile.get(),
        'tempfile': entry_tempfile.get(),
        'powerfile': entry_powerfile.get()
    }

    config['PLT'] = {
        'title': entry_title.get(),
        'fontsize': entry_fontsize.get(),
        'yaxis_major_locator': entry_yaxis_major_locator.get(),
        'yaxis_minor_locator': entry_yaxis_minor_locator.get(),
        'xticks': entry_xticks.get(),
        'y_limit_auto': entry_y_limit_auto.get(),
        'y_limit_max': entry_y_limit_max.get(),
        'y_limit_min': entry_y_limit_min.get(),
    }

    config['CHANNEL'] = {
        'dt': entry_dt.get(),
        'temp': entry_temp.get(),
        'rh_skip': entry_rh_skip.get(),
        'power_skip': entry_power_skip.get()
    }

    config['STAT'] = {
        'stats': entry_stats.get(),
        'stat_range': entry_stat_range.get(),
        'stat_start': entry_stat_start.get(),
        'stat_stop': entry_stat_stop.get(),
        'stat_power': entry_stat_power.get()
    }

    # 獲取 configfile 的路徑
    configfile_path = entry_configfile.get()

    # 檢查路徑是否存在，如果不存在則創建目錄
    directory = os.path.dirname(configfile_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # 將配置寫入文件
    with open(configfile_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

    messagebox.showinfo("成功", f"組態檔已保存為 {configfile_path}")

# 創建主窗口
root = tk.Tk()
root.title("溫度/電力圖表工具 v0.7.2")

# 創建輸入框和標籤
# 創建保存按鈕
tk.Button(root, text="儲存組態檔", command=save_config).grid(row=0, column=0)

tk.Label(root, text="設定檔:").grid(row=11, column=0, sticky=tk.W, padx=5)
entry_configfile = tk.Entry(root, width=70)
entry_configfile.grid(row=11, column=1, columnspan=4)
btn_configfile = tk.Button(root, text="選擇檔案", command=lambda: load_config())
btn_configfile.grid(row=11, column=5, sticky=tk.E, padx=5)
entry_configfile.insert(0, "config.ini")

tk.Label(root, text="溫度資料:").grid(row=12, column=0, sticky=tk.W, padx=5)
entry_tempfile = tk.Entry(root, width=70)
entry_tempfile.grid(row=12, column=1, columnspan=4)
#entry_tempfile.insert(0, "D:\\071\\temp1.csv")
btn_tempfile = tk.Button(root, text="選擇檔案", command=lambda: select_file(entry_tempfile))
btn_tempfile.grid(row=12, column=5)

tk.Label(root, text="電力資料:").grid(row=13, column=0, sticky=tk.W, padx=5)
entry_powerfile = tk.Entry(root, width=70)
entry_powerfile.grid(row=13, column=1, columnspan=4)
#entry_powerfile.insert(0, "D:\\071\\power1.csv")
btn_powerfile = tk.Button(root, text="選擇檔案", command=lambda: select_file(entry_powerfile))
btn_powerfile.grid(row=13, column=5)

tk.Label(root, text=" ").grid(row=14, column=0, columnspan=4)

tk.Label(root, text="標題:").grid(row=21, column=0, sticky=tk.W, padx=5)
entry_title = tk.Entry(root, width=20)
entry_title.grid(row=21, column=1, sticky=tk.W)
entry_title.insert(0, "Title")

tk.Label(root, text="字體size:").grid(row=21, column=2, sticky=tk.W, padx=5)
entry_fontsize = tk.Entry(root, width=5)
entry_fontsize.grid(row=21, column=3, sticky=tk.W)
entry_fontsize.insert(0, "10")

tk.Label(root, text="Y軸主要刻度:").grid(row=22, column=0, sticky=tk.W, padx=5)
entry_yaxis_major_locator = tk.Entry(root, width=5)
entry_yaxis_major_locator.grid(row=22, column=1, sticky=tk.W)
entry_yaxis_major_locator.insert(0, "5")

tk.Label(root, text="Y軸次要刻度:").grid(row=22, column=2, sticky=tk.W, padx=5)
entry_yaxis_minor_locator = tk.Entry(root, width=5)
entry_yaxis_minor_locator.grid(row=22, column=3, sticky=tk.W)
entry_yaxis_minor_locator.insert(0, "0")

tk.Label(root, text="X軸刻度:").grid(row=23, column=0, sticky=tk.W, padx=5)
entry_xticks = tk.Entry(root, width=5)
entry_xticks.grid(row=23, column=1, sticky=tk.W)
entry_xticks.insert(0, "100")

tk.Label(root, text="Y軸上下限自動設定(0/1):").grid(row=23, column=2, sticky=tk.W, padx=5)
entry_y_limit_auto = tk.Entry(root, width=5)
entry_y_limit_auto.grid(row=23, column=3, sticky=tk.W)
entry_y_limit_auto.insert(0, "1")

tk.Label(root, text="Y軸上限:").grid(row=24, column=0, sticky=tk.W, padx=5)
entry_y_limit_max = tk.Entry(root, width=5)
entry_y_limit_max.grid(row=24, column=1, sticky=tk.W)
entry_y_limit_max.insert(0, "1.1")

tk.Label(root, text="Y軸下限:").grid(row=24, column=2, sticky=tk.W, padx=5)
entry_y_limit_min = tk.Entry(root, width=5)
entry_y_limit_min.grid(row=24, column=3, sticky=tk.W)
entry_y_limit_min.insert(0, "1.1")

tk.Label(root, text=" ").grid(row=8, column=25, columnspan=4, sticky=tk.W, padx=5)

tk.Label(root, text="日期時間欄位分開:").grid(row=26, column=0, sticky=tk.W, padx=5)
entry_dt = tk.Entry(root, width=5)
entry_dt.grid(row=26, column=1, sticky=tk.W)
entry_dt.insert(0, "1")

tk.Label(root, text="顯示溫度欄位:").grid(row=26, column=2, sticky=tk.W, padx=5)
entry_temp = tk.Entry(root, width=5)
entry_temp.grid(row=26, column=3, sticky=tk.W)
entry_temp.insert(0, "F,R")

tk.Label(root, text="不顯示濕度圖形(0/1):").grid(row=27, column=0, sticky=tk.W, padx=5)
entry_rh_skip = tk.Entry(root, width=5)
entry_rh_skip.grid(row=27, column=1, sticky=tk.W)
entry_rh_skip.insert(0, "1")

tk.Label(root, text="不顯示電力圖形(0/1):").grid(row=27, column=2, sticky=tk.W, padx=5)
entry_power_skip = tk.Entry(root, width=5)
entry_power_skip.grid(row=27, column=3, sticky=tk.W)
entry_power_skip.insert(0, "1")

tk.Button(root, text="產出圖表", command=show_chart.run).grid(row=27, column=5)

tk.Label(root, text=" ").grid(row=28, column=0, columnspan=6)

tk.Label(root, text="進行統計的欄位:").grid(row=40, column=0, sticky=tk.W, padx=5)
entry_stats = tk.Entry(root, width=10)
entry_stats.grid(row=40, column=1, sticky=tk.W)
entry_stats.insert(0, "F,R")

tk.Label(root, text="區段統計(0/1):").grid(row=40, column=2, sticky=tk.W, padx=5)
entry_stat_range = tk.Entry(root, width=5)
entry_stat_range.grid(row=40, column=3, sticky=tk.W)
entry_stat_range.insert(0, "0")

tk.Label(root, text="區段起點位置:").grid(row=41, column=0, sticky=tk.W, padx=5)
entry_stat_start = tk.Entry(root, width=5)
entry_stat_start.grid(row=41, column=1, sticky=tk.W)
entry_stat_start.insert(0, "1")

tk.Label(root, text="區段終點位置:").grid(row=41, column=2, sticky=tk.W, padx=5)
entry_stat_stop = tk.Entry(root, width=5)
entry_stat_stop.grid(row=41, column=3, sticky=tk.W)
entry_stat_stop.insert(0, "10")

tk.Label(root, text="計算耗能:").grid(row=42, column=0, sticky=tk.W, padx=5)
entry_stat_power = tk.Entry(root, width=5)
entry_stat_power.grid(row=42, column=1, sticky=tk.W)
entry_stat_power.insert(0, "0")

tk.Button(root, text="統計", command=show_chart.stat).grid(row=42, column=5)

tk.Label(root, text=" ").grid(row=43, column=0, columnspan=6)

# **自動執行 load_config() 以選擇組態檔**
root.after(500, load_config)

# 運行主循環
root.mainloop()
