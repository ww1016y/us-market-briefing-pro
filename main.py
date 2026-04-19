import os
import yfinance as yf
from google import genai  # 최신 SDK v2 적용
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from tickers import SECTOR_TICKERS, INDICES, KST, THEMES
from visualizer import create_sector_heatmap

load_dotenv()

# 최신 Gemini SDK 설정
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_ai_summary(ticker, news):
    """최신 SDK v2를 이용한 주가 변동 원인 요약"""
    if not news: return "관련 뉴스 없음"
    
    # 뉴스 제목 추출
    titles = []
    for n in news[:3]:
        title = n.get('title') or n.get('content', {}).get('title') or ""
        if title: titles.append(title)
        
    if not titles: return "뉴스 제목 없음"
    
    prompt = f"Analyze these news titles for {ticker} and summarize why the stock is moving in Korean (one short sentence): {titles}"
    
    try:
        # 최신 SDK v2 호출 방식
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"요약 실패: {str(e)}"

def fetch_data():
    results = {}
    for sec, (label, tickers) in SECTOR_TICKERS.items():
        stocks = []
        for t, en, ko in tickers:
            try:
                ticker_obj = yf.Ticker(t)
                hist = ticker_obj.history(period="10d")
                if hist.empty: continue
                
                close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change = (close - prev_close) / prev_close * 100
                
                vol_avg = hist['Volume'].iloc[:-1].mean()
                vol_ratio = hist['Volume'].iloc[-1] / vol_avg if vol_avg > 0 else 1
                heat = vol_ratio + (change / 2)
                
                stocks.append({
                    "ticker": t, "name": ko, "close": close, "change_pct": change, 
                    "heat": heat, "hist": hist, "news": ticker_obj.news
                })
            except Exception as e:
                print(f"[ERROR] {t} 데이터 수집 실패: {e}")
                continue
                
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
        if os.path.exists(path):
            with open(path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<{cid}>')
                msg.attach(img)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD").replace(" ",""))
        server.send_message(msg)

def main():
    print("데이터 수집 시작...")
    data = fetch_data()
    
    print("히트맵 생성 중...")
    heatmap_path = "sector_heatmap.png"
    create_sector_heatmap(data, output_path=heatmap_path)
    images = {"sector_heatmap": heatmap_path}
    
    # HTML 구성
    html = f"<h2>🔥 오늘의 미국 주식 섹터 브리핑</h2>"
    html += f"<p><img src='cid:sector_heatmap' style='width:100%; max-width:800px;'></p>"
    
    for sec, (label, stocks) in data.items():
        html += f"<h3>{label}</h3><table border='1' style='border-collapse: collapse; width: 100%; font-size: 14px;'>"
        html += "<tr style='background-color: #f2f2f2;'><th>종목</th><th>종가</th><th>등락</th><th>AI 한줄분석</th></tr>"
        for s in stocks:
            color = "red" if s['change_pct'] > 0 else "blue"
            ai_summary = get_ai_summary(s['ticker'], s['news'])
            html += f"<tr><td style='padding: 8px;'><b>{s['name']}</b> ({s['ticker']})</td>"
            html += f"<td style='padding: 8px;'>${s['close']:.2f}</td>"
            html += f"<td style='padding: 8px; color:{color};'><b>{s['change_pct']:+.2f}%</b></td>"
            html += f"<td style='padding: 8px;'>{ai_summary}</td></tr>"
        html += "</table>"
    
    print("이메일 발송 중...")
    try:
        send_email(html, images)
        print("모든 작업 완료!")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")

if __name__ == "__main__":
    main()
