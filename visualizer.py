import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def create_sector_heatmap(sector_data, output_path="sector_heatmap.png"):
    """섹터별 평균 수익률 히트맵 생성"""
    data = []
    for sec, (label, stocks) in sector_data.items():
        avg_change = sum(s.change_pct for s in stocks) / len(stocks) if stocks else 0
        data.append({"Sector": label, "Change": avg_change})
    
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 2))
    sns.heatmap(df.set_index("Sector").T, annot=True, cmap="RdYlGn", center=0, cbar=False, fmt=".2f")
    plt.title("Daily Sector Performance (%)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path

def create_stock_chart(ticker, hist_data, output_path=None):
    """개별 종목 5일 주가 차트 생성"""
    if output_path is None:
        output_path = f"{ticker}_chart.png"
    
    plt.figure(figsize=(4, 2))
    plt.plot(hist_data.index, hist_data['Close'], color='blue', linewidth=2)
    plt.fill_between(hist_data.index, hist_data['Close'], alpha=0.1)
    plt.axis('off')
    plt.savefig(output_path, transparent=True)
    plt.close()
    return output_path
