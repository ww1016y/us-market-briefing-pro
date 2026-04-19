import os
import yfinance as yf
import google.generativeai as genai
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from tickers import SECTOR_TICKERS, INDICES, KST, THEMES
from visualizer import create_sector_heatmap, create_stock_chart

load_dotenv()

# Gemini 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_summary(ticker, news):
    """Gemini를 이용한 주가 변동 원인 요약"""
    if not news: return "관련 뉴스 없음"
    
    titles = [n['title'] for n in news[:3]]
    prompt = f"Analyze the following news titles for {ticker} and summarize why the stock might be moving in Korean (one short sentence): {titles}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"요약 실패: {str(e)}"

def fetch_data():
    results = {}
    for sec, (label, tickers) in SECTOR_TICKERS.items():
        stocks = []
        for t, en, ko in tickers:
            ticker_obj = yf.Ticker(t)
            hist = ticker_obj.history(period="10d")
            if hist.empty: continue
            
            close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change = (close - prev_close) / prev_close * 100
            
            # 간단한 HeatScore (5일 거래량 트렌드 반영)
            vol_avg = hist['Volume'].iloc[:-1].mean()
            vol_ratio = hist['Volume'].iloc[-1] / vol_avg if vol_avg > 0 else 1
            heat = vol_ratio + (change / 2)
            
            stocks.append({
                "ticker": t, "name": ko, "close": close, "change_pct": change, 
                "heat": heat, "hist": hist, "news": ticker_obj.news
            })
        stocks.sort(key=lambda x: x['heat'], reverse=True)
        results[sec] = (label, stocks[:5])
    return results

def send_email(html_content, images):
    msg = MIMEMultipart('related')
    msg['Subject'] = f"🚀 [AI 브리핑] 미 증시 섹터 & 테마 분석 ({datetime.now(KST).strftime('%m/%d')})"
    msg['From'] = os.getenv("GMAIL_USER")
    msg['To'] = os.getenv("TO_EMAIL")

    msg.attach(MIMEText(html_content, 'html'))

    for cid, path in images.items():
        with open(path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', f'<{cid}>')
            msg.attach(img)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD").replace(" ",""))
        server.send_message(msg)

def main():
    print("데이터 수집 중...")
    data = fetch_data()
    
    # 히트맵 생성
    heatmap_path = create_sector_heatmap(data)
    images = {"sector_heatmap": heatmap_path}
    
    # HTML 구성
    html = f"<h2>🔥 오늘의 미국 주식 섹터 브리핑</h2>"
    html += f"<p><img src='cid:sector_heatmap' style='width:100%; max-width:800px;'></p>"
    
    for sec, (label, stocks) in data.items():
        html += f"<h3>{label}</h3><table border='1' style='border-collapse: collapse; width: 100%;'>"
        html += "<tr><th>종목</th><th>종가</th><th>등락</th><th>AI 한줄분석</th></tr>"
        for s in stocks:
            color = "red" if s['change_pct'] > 0 else "blue"
            ai_summary = get_ai_summary(s['ticker'], s['news'])
            html += f"<tr><td><b>{s['name']}</b> ({s['ticker']})</td>"
            html += f"<td>${s['close']:.2f}</td>"
            html += f"<td style='color:{color}'>{s['change_pct']:+.2f}%</td>"
            html += f"<td>{ai_summary}</td></tr>"
        html += "</table>"
    
    print("메일 발송 중...")
    send_email(html, images)
    print("완료!")

if __name__ == "__main__":
    main()
