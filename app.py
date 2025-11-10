from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 접수 데이터 저장 (메모리)
applications = []

# 🎨 로고 및 정적 파일 제공 (이 부분이 핵심!)
@app.route('/logo.png')
def serve_logo():
    """로고 파일 제공"""
    return send_from_directory('.', 'logo.png')

@app.route('/<path:filename>')
def serve_static(filename):
    """기타 정적 파일 제공 (이미지, CSS, JS 등)"""
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    return "File not found", 404

@app.route('/')
def home():
    """메인 페이지 - 신청 페이지 표시"""
    try:
        with open('sinchon_project.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "신청 페이지를 찾을 수 없습니다.", 404

@app.route('/admin')
def admin():
    """관리자 대시보드"""
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>신촌 프로젝트 관리자</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #4A90E2 0%, #5BA3E8 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #7f8c8d;
                margin-bottom: 30px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #4A90E2 0%, #5BA3E8 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
            }}
            .stat-card h3 {{
                font-size: 14px;
                opacity: 0.9;
                margin-bottom: 10px;
            }}
            .stat-card .number {{
                font-size: 36px;
                font-weight: 700;
            }}
            .applications {{
                margin-top: 30px;
            }}
            .applications h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 24px;
            }}
            .application-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
                border-left: 4px solid #4A90E2;
            }}
            .application-card .header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
                align-items: center;
            }}
            .application-card .name {{
                font-size: 18px;
                font-weight: 600;
                color: #2c3e50;
            }}
            .application-card .time {{
                font-size: 13px;
                color: #7f8c8d;
            }}
            .application-card .info {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-bottom: 10px;
            }}
            .application-card .info-item {{
                font-size: 14px;
                color: #555;
            }}
            .application-card .info-item strong {{
                color: #2c3e50;
                display: inline-block;
                width: 80px;
            }}
            .application-card .message {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                font-size: 14px;
                color: #555;
                line-height: 1.6;
            }}
            .badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }}
            .badge.consult {{
                background: #e3f2fd;
                color: #1976d2;
            }}
            .badge.trial {{
                background: #f3e5f5;
                color: #7b1fa2;
            }}
            .badge.register {{
                background: #e8f5e9;
                color: #388e3c;
            }}
            .empty {{
                text-align: center;
                padding: 60px 20px;
                color: #95a5a6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐋 신촌 프로젝트 관리자</h1>
            <p class="subtitle">영어 말하기 커뮤니티 신청 관리</p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>총 신청 건수</h3>
                    <div class="number">{len(applications)}</div>
                </div>
            </div>
            
            <div class="applications">
                <h2>최근 신청 내역 (최근 10건)</h2>
    """
    
    if applications:
        for app_data in reversed(applications[-10:]):
            app_type = app_data.get('applicationType', '')
            badge_class = 'consult' if '상담' in app_type else 'trial' if '맛보기' in app_type else 'register'
            
            html += f"""
                <div class="application-card">
                    <div class="header">
                        <div class="name">{app_data.get('name', 'N/A')}</div>
                        <div class="time">{app_data.get('timestamp', 'N/A')}</div>
                    </div>
                    <div class="info">
                        <div class="info-item">
                            <strong>연락처:</strong> {app_data.get('contact', 'N/A')}
                        </div>
                        <div class="info-item">
                            <strong>신청:</strong> <span class="badge {badge_class}">{app_type}</span>
                        </div>
                    </div>
            """
            
            if app_data.get('message'):
                html += f"""
                    <div class="message">
                        <strong>남기신 말:</strong><br>
                        {app_data.get('message')}
                    </div>
                """
            
            html += "</div>"
    else:
        html += """
            <div class="empty">
                <h3>아직 신청 내역이 없습니다</h3>
                <p>첫 신청을 기다리고 있습니다!</p>
            </div>
        """
    
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/api/application', methods=['POST'])
def submit_application():
    """신청 접수 처리"""
    try:
        data = request.json
        
        # 타임스탬프 추가
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 데이터 저장
        applications.append(data)
        
        # 텔레그램 알림 전송
        send_telegram_notification(data)
        
        return jsonify({
            'success': True,
            'message': '신청이 성공적으로 접수되었습니다!'
        }), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'message': '접수 중 오류가 발생했습니다.'
        }), 500

def send_telegram_notification(data):
    """텔레그램 알림 전송"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 설정이 없습니다.")
        return
    
    message = f"""
🐋 <b>신촌 프로젝트 - 신규 신청</b>

👤 <b>이름:</b> {data.get('name', 'N/A')}
📱 <b>연락처:</b> {data.get('contact', 'N/A')}
📝 <b>신청 종류:</b> {data.get('applicationType', 'N/A')}

💬 <b>남기신 말:</b>
{data.get('message', '없음')}

⏰ <b>접수 시간:</b> {data.get('timestamp', 'N/A')}
    """
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("텔레그램 알림 전송 성공")
        else:
            print(f"텔레그램 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"텔레그램 전송 오류: {e}")

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """전체 신청 내역 조회"""
    return jsonify(applications)

@app.route('/api/test-telegram', methods=['GET'])
def test_telegram():
    """텔레그램 알림 테스트"""
    test_data = {
        'name': '테스트',
        'contact': '010-0000-0000',
        'applicationType': '상담+레벨테스트',
        'message': '텔레그램 알림 테스트입니다.',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    send_telegram_notification(test_data)
    
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>텔레그램 테스트</title>
    </head>
    <body style="font-family: Arial; padding: 50px; text-align: center;">
        <h1>📱 텔레그램 알림 테스트 완료</h1>
        <p>텔레그램으로 테스트 메시지가 전송되었습니다.</p>
        <p>메시지가 도착했는지 확인해주세요!</p>
        <br>
        <a href="/" style="color: #4A90E2; text-decoration: none; font-weight: bold;">← 메인으로 돌아가기</a>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """헬스체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'sinchon-project',
        'applications_count': len(applications)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
