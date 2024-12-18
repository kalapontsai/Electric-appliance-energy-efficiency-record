#rev6 使用sampo_test.ini 來控制輸出參數
#rev7 x軸以時間格式讀入, 加入RH POWER子圖是否顯示參數, 修復圖例
#rev8 檢查csv內是否有足夠的頻道資料
#rev9 顯示數據統計值,電力能耗值在標題
#0_1 新增統計數據指定範圍
#0_2 自動合併日期與時間欄位 from VM7000 記錄檔
#0_2 以中文字型顯示標題
# ***************************************************************
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import numpy as np
import configparser
import sys

def make_patch_spines_invisible(ax):
    ax.set_frame_on(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)

def is_datetime(string, format=None):
    try:
        pd.to_datetime(string, format=format)
        return True
    except ValueError:
        return False

# 創建 ConfigParser 物件
config = configparser.ConfigParser()
# 讀取配置文件
try:
	with open('config.ini', 'r', encoding='utf-8') as f:
	    config.read_file(f)
except FileNotFoundError:
	print("找不到sampo_test.ini !!")
	print()
	input("按Enter後結束程式...")
	sys.exit()

# 獲取整數值
Csv_file = config.get('FILE', 'filename')
Title = config.get('FILE', 'title')
Fontsize = config.getint('PLT', 'fontsize')
Stat = config.getint('PLT', 'statistics')
Stat_range = config.getint('PLT', 'stat_range')
Stat_start = config.getint('PLT', 'stat_start')
Stat_stop = config.getint('PLT', 'stat_stop')
Xticks = config.getint('PLT', 'xticks')
Dt_combine = config.getint('CHANNEL', 'DT')
Channel_str = config.get('CHANNEL', 'temp')
OutputChannel_list = Channel_str.split(',')
Stat_str = config.get('CHANNEL', 'stats')
StatChannel_list = Stat_str.split(',')
RHskip = config.get('CHANNEL', 'RH_skip')
POWERskip = config.get('CHANNEL', 'POWER_skip')

# 讀取 CSV, 並指定日期時間格式的欄位
# rev 0_2 判斷config內變數[DT] 自動合併日期與時間欄位
try:
	if Dt_combine == 0:
		data = pd.read_csv(config['FILE']['filename'], parse_dates=['DateTime'])
	else:
		data = pd.read_csv(config['FILE']['filename'])
		data['DateTime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
		#print(data['DateTime'])
except FileNotFoundError:
    print("csv檔案不存在")
    print("")
    input("按Enter後結束程式...")
    sys.exit()

#檢查csv內是否有INI設定的temp欄位,RH,Volt,I,W
Channel_check_list = OutputChannel_list + ["RH","Volt","I","W"]
# 部分項目若不顯示,刪除頻道檢查項目
if POWERskip == "1":
	fig, ax1 = plt.subplots()
	Channel_check_list.remove("Volt") #新增檢查csv項目
	Channel_check_list.remove("I")
	Channel_check_list.remove("W")
	Channel_check_list.remove("RH")
elif RHskip == "1":
	fig, (ax1, ax3) = plt.subplots(nrows=2, sharex=True, figsize=(10, 6))
	plt.subplots_adjust(left=0.15, right=0.85, bottom=0.15, top=0.85, hspace=0.1)
	Channel_check_list.remove("RH")
else:
	fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, sharex=True, figsize=(10, 6))
	plt.subplots_adjust(left=0.15, right=0.85, bottom=0.15, top=0.85, hspace=0.1)

#檢查頻道資料是否存在
for c in Channel_check_list:
	if not c in data.columns:
		print("檔案名稱:",Csv_file)
		print()
		print("設定顯示頻道",Channel_check_list)
		print("頻道不存在",c)
		print()
		input("按Enter後結束程式...")
		sys.exit()

#計算統計數據,電耗累積值,並放入標題
if Stat == 1 and Stat_range != 1:
	Title += "\n[℃]  AVG  Max   Min"
	for c in StatChannel_list:
		if c in Channel_check_list:
			Title += "\n[" + c + "]  " + str(data[c].mean().round(1)) 
			Title += "  " + str(data[c].max().round(1)) 
			Title += "  " + str(data[c].min().round(1))
if Stat == 1 and Stat_range == 1:
	if isinstance(Stat_start, int) and isinstance(Stat_stop, int) and Stat_start > 0 and ((Stat_stop - 1) <= len(data)) : 
		Title += "\n[℃]  AVG  Max   Min (" + str(data["DateTime"][Stat_start-1].strftime('%m/%d %H:%M')) + "~" + str(data["DateTime"][Stat_stop-1].strftime('%m/%d %H:%M')) + ")"
		for c in StatChannel_list:
			if c in Channel_check_list:
				#print(c,Stat_start-1,Stat_stop-1,data[c].iloc[Stat_start-1:Stat_stop-1].mean())
				Title += "\n[" + c + "]  " + str(data[c].iloc[Stat_start-1:Stat_stop-1].mean().round(1)) 
				Title += "  " + str(data[c].iloc[Stat_start-1:Stat_stop-1].max().round(1)) 
				Title += "  " + str(data[c].iloc[Stat_start-1:Stat_stop-1].min().round(1))
	else:
		print("已開啟統計範圍設定,但範圍與資料筆數不符 !!")
		print("")
		input("按Enter後繼續...")
#print(Title)

if POWERskip != "1" and Stat == 1:
	WH_p = int(data["WH"].max() - data["WH"].min())
	WH_t = data["DateTime"].iloc[-1] - data["DateTime"].iloc[0]
	print(WH_p,data["DateTime"].iloc[-1])
	WH_tmin = int(WH_t.total_seconds() // 60)
	Title += "\n"
	Title += str(WH_p) + "W/" + str(WH_tmin) + " min"
	EF = int((WH_p / WH_tmin) * 1440)
	Title += " (" + str(EF) + "W/24H)"

#強制 Matplotlib 使用系統默認的減號符號，而不是從字體中查找
plt.rcParams['axes.unicode_minus'] = False

plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 指定中文字體正黑體
# 指定字體路徑和名稱
#font_path = 'C:/Windows/Fonts/msjh.ttc'  # 替換為你電腦上的微軟正黑體路徑
#font_prop = fm.FontProperties(fname=font_path)

plt.rcParams['font.size'] = Fontsize
fig.suptitle(Title,horizontalalignment='left')
# ---------- 計算統計數據 ----------------

#以日期時間格式作為X軸
if is_datetime(data["DateTime"]):
	data.set_index('DateTime', inplace=True)
else:
#若非以日期時間格式當作X軸
#每隔 100 個數據點顯示一個X刻度。旋转 x 轴标籤
	plt.xticks(np.arange(0, len(data['DateTime']), Xticks), rotation=45)

# 繪製溫度的子圖
ax1.set_ylabel('Temp')
ax1.grid(True, linestyle='dashdot')
ax1.tick_params(labelcolor='black', labelsize='small', width=1)

ax1.yaxis.set_major_locator(plt.MultipleLocator(5))  # y 轴主刻度间隔
#ax1.yaxis.set_minor_locator(plt.MultipleLocator(1))

#print(OutputChannel_list,len(OutputChannel_list))
for i in OutputChannel_list:
	ax1.plot(data[i], label = i)
ax1.legend(ncol= len(OutputChannel_list),loc='lower left',fontsize = 6)

# 在第二个子图中绘制 RH
if(RHskip != "1"):
	ax2.set_ylabel('RH%')
	ax2.grid(True, linestyle='dashdot')
	ax2.tick_params(labelcolor='black', labelsize='small', width=1)
	ax2.yaxis.set_major_locator(plt.MultipleLocator(5))  # y 轴主刻度间隔
	ax2.set_ylim(70, 80)
	ax2.plot(data['RH'])
#ax2.yaxis.set_minor_locator(plt.MultipleLocator(1))
#ax2.legend()

# 在第3个子图中绘制 電力
if(POWERskip != "1"):
	ax3.set_ylabel('Watt')
	ax3.grid(True, linestyle='dashdot')
	ax3.tick_params(labelcolor='black', labelsize='small', width=1)
	ax3.yaxis.set_major_locator(plt.MultipleLocator(50))  # y 轴主刻度间隔为 0.5
	ax3.yaxis.set_minor_locator(plt.MultipleLocator(10))
	ax3.plot(data['W'])

	# 創建第二个和第三个Axes对象，并将其放置在第一个Axes对象之上
	ax31 = ax3.twinx()
	ax32 = ax3.twinx()

	# 調整第二个Axes的位置，避免標籤重疊
	ax31.spines['right'].set_position(('axes', 1.0))
	make_patch_spines_invisible(ax31)
	ax31.spines['right'].set_visible(True)

	# 在第二个和第三个Axes中绘制線
	ax31.set_ylabel('Current', color='green')
	ax31.set_ylim(0, 3)
	ax31.plot(data['I'], label='I', color='green')

	#ax31.tick_params(axis='y', color='green')
	ax32.plot(data['Volt'], label='V', color='orange')
	ax32.spines['right'].set_position(('axes', 1.06))
	make_patch_spines_invisible(ax32)
	ax32.spines['right'].set_visible(True)
	ax32.set_ylabel('Volt', color='orange')
	ax32.set_ylim(0, 120)



# 显示图形
plt.show()

