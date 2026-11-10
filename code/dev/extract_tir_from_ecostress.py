import os
import numpy as np
import pandas as pd

# ========== 配置 ==========
# 请将这里的路径替换为你解压 ecostress.zip 后的实际文件夹路径
splib_dir = r"D:\A_MineralProspecting\raw\ecostress" 
out_dir = r"D:\A_MineralProspecting\processed\spectra"
os.makedirs(out_dir, exist_ok=True)

# 目标矿物关键词匹配规则
targets = {
    "Quartz": ["Quartz"],
    "Feldspar": ["Feldspar", "Albite", "Anorthite", "Microcline", "Orthoclase", "Adularia"],
    "Clay": ["Kaolinite", "Montmorillonite", "Illite", "Smectite", "Chlorite"],
    "Calcite": ["Calcite"],
    "Dolomite": ["Dolomite"],
}

TIR_MIN, TIR_MAX = 8.0, 14.0
MAX_PER_CLASS = 5  # 每类最多提取5个样本

# ========== 智能解析函数 ==========
def read_spectrum_file(filepath):
    """自动识别波长或波数，并提取光谱数据"""
    try:
        # 尝试读取文本文件
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # 寻找数据起始行（跳过表头/注释）
        data_start = 0
        for i, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    float(parts[0]); float(parts[1])
                    data_start = i
                    break
                except ValueError:
                    continue
        
        # 提取前两列数据（通常第一列是 X 轴，第二列是 Y 轴）
        x_vals, y_vals = [], []
        for line in lines[data_start:]:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    x_vals.append(float(parts[0]))
                    y_vals.append(float(parts[1]))
                except ValueError:
                    continue
                    
        x_vals = np.array(x_vals)
        y_vals = np.array(y_vals)
        
        if len(x_vals) == 0:
            return None, None

        # ========== 智能判断单位并转换为微米 ==========
        if x_vals[0] > 100: 
            # 如果 X 轴数值很大，说明是波数 (cm^-1)
            wavelengths = 10000.0 / x_vals
        else:
            # 否则已经是微米 (μm)
            wavelengths = x_vals
            
        # 确保波长升序排列
        sort_idx = np.argsort(wavelengths)
        wavelengths = wavelengths[sort_idx]
        y_vals = y_vals[sort_idx]
        
        # 过滤掉 NoData 或异常值
        valid = np.isfinite(y_vals) & (y_vals > -1e30)
        return wavelengths[valid], y_vals[valid]
        
    except Exception as e:
        return None, None

# ========== 主流程 ==========
print(f"扫描目录: {splib_dir}")
if not os.path.exists(splib_dir):
    print("❌ 找不到文件夹，请检查路径！")
    exit()

# 递归收集所有 txt 文件
all_files = []
for root, dirs, files in os.walk(splib_dir):
    for file in files:
        if file.endswith((".txt", ".TXT")):
            all_files.append(os.path.join(root, file))
            
print(f"共找到 {len(all_files)} 个光谱文本文件\n")

for mineral_type, keywords in targets.items():
    print(f"处理: {mineral_type}")
    spectra = []
    
    for fpath in all_files:
        fname = os.path.basename(fpath).lower()
        if any(kw.lower() in fname for kw in keywords):
            wl, rf = read_spectrum_file(fpath)
            if wl is None or len(wl) < 10:
                continue
                
            # 截取 8-14 μm 范围
            mask = (wl >= TIR_MIN) & (wl <= TIR_MAX)
            if np.sum(mask) < 10:
                continue
                
            wl_tir = wl[mask]
            rf_tir = rf[mask]
            
            spectra.append((os.path.basename(fpath), wl_tir, rf_tir))
            if len(spectra) >= MAX_PER_CLASS:
                break
                
    if not spectra:
        print(f"  ⚠️ 未找到 {mineral_type} 的 TIR 光谱")
        continue

    # 统一插值到 200 个波长点
    common_wl = np.linspace(TIR_MIN, TIR_MAX, 200)
    interp_spectra = []
    for _, wl, rf in spectra:
        # 归一化到 0-1 范围（如果光谱是反射率）
        rf_norm = np.clip(rf, 0, 1) 
        interp_spectra.append(np.interp(common_wl, wl, rf_norm))
        
    interp_spectra = np.array(interp_spectra)
    
    # 保存为 .npy 和 .csv
    np.save(os.path.join(out_dir, f"{mineral_type}_TIR.npy"), interp_spectra)
    
    df = pd.DataFrame(interp_spectra.T, columns=[s[0][:30] for s in spectra])
    df.insert(0, "wavelength_um", common_wl)
    df.to_csv(os.path.join(out_dir, f"{mineral_type}_TIR.csv"), index=False)
    
    print(f"  ✅ 成功提取 {len(spectra)} 条光谱，已保存到 {mineral_type}_TIR.npy")

print(f"\n全部完成！文件已保存至: {out_dir}")