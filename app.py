from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 텔레그램 설정 (환경 변수에서 가져오기)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 메모리에 신청 내역 저장 (간단한 구현)
applications = []

def send_telegram_message(message):
    """텔레그램으로 메시지 전송"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ 텔레그램 설정이 없습니다.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")
        return False

@app.route('/')
def index():
    """관리자 대시보드"""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>신촌 프로젝트 - 관리자</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #5B9BD5 0%, #4A8BC2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{
                color: #5B9BD5;
                margin-bottom: 10px;
                font-size: 32px;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #5B9BD5 0%, #4A8BC2 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
            }}
            .stat-number {{
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            .applications {{
                margin-top: 30px;
            }}
            .applications h2 {{
                color: #333;
                margin-bottom: 20px;
                font-size: 24px;
            }}
            .application-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
                border-left: 4px solid #5B9BD5;
            }}
            .application-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .application-name {{
                font-weight: bold;
                color: #333;
                font-size: 18px;
            }}
            .application-time {{
                color: #666;
                font-size: 13px;
            }}
            .application-details {{
                color: #555;
                line-height: 1.6;
            }}
            .application-details div {{
                margin: 5px 0;
            }}
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #999;
            }}
            .test-btn {{
                display: inline-block;
                padding: 12px 24px;
                background: #5B9BD5;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin-top: 20px;
                font-weight: 600;
                transition: all 0.2s;
            }}
            .test-btn:hover {{
                background: #4A8BC2;
                transform: translateY(-2px);
            }}
            .status {{
                margin-top: 30px;
                padding: 20px;
                background: #e8f5e9;
                border-radius: 10px;
                border-left: 4px solid #4caf50;
            }}
            .status.warning {{
                background: #fff3cd;
                border-left-color: #ffc107;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 신촌 프로젝트 관리자</h1>
            <p class="subtitle">영어 말하기 커뮤니티 신청 관리 시스템</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(applications)}</div>
                    <div class="stat-label">총 신청 건수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">✓</div>
                    <div class="stat-label">시스템 정상 작동</div>
                </div>
            </div>
            
            <div class="status {'warning' if not TELEGRAM_BOT_TOKEN else ''}">
                <strong>📱 텔레그램 연동 상태:</strong> 
                {'✅ 정상 연결됨' if TELEGRAM_BOT_TOKEN else '⚠️ 설정 필요 (환경 변수 확인)'}
            </div>
            
            <a href="/api/test-telegram" class="test-btn">텔레그램 테스트</a>
            
            <div class="applications">
                <h2>📋 최근 신청 내역 (최근 10건)</h2>
                {''.join([f'''
                <div class="application-card">
                    <div class="application-header">
                        <span class="application-name">{app['name']}</span>
                        <span class="application-time">{app['timestamp']}</span>
                    </div>
                    <div class="application-details">
                        <div><strong>연락처:</strong> {app['phone']}</div>
                        <div><strong>신청:</strong> {app['applicationType']}</div>
                        {f"<div><strong>메시지:</strong> {app['message']}</div>" if app.get('message') else ''}
                    </div>
                </div>
                ''' for app in reversed(applications[-10:])]) if applications else '<div class="empty-state">아직 신청 내역이 없습니다.</div>'}
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/sinchon')
def sinchon_page():
    """신청 페이지 제공"""
    return send_file('sinchon_project.html')

@app.route('/api/application', methods=['POST'])
def submit_application():
    """신청 접수 처리"""
    try:
        data = request.json
        
        # 필수 항목 검증
        required_fields = ['name', 'phone', 'applicationType', 'timestamp']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # 신청 내역 저장
        applications.append(data)
        
        # 텔레그램 알림 메시지 생성
        message = f"""
🎓 <b>신촌 프로젝트 신청 접수</b>

👤 <b>이름:</b> {data['name']}
📱 <b>연락처:</b> {data['phone']}
📝 <b>신청:</b> {data['applicationType']}
💬 <b>메시지:</b> {data.get('message', '없음')}
🕐 <b>시간:</b> {data['timestamp']}
        """
        
        # 텔레그램 전송
        telegram_sent = send_telegram_message(message.strip())
        
        print(f"✅ 신청 접수: {data['name']} - {data['applicationType']}")
        print(f"📱 텔레그램 전송: {'성공' if telegram_sent else '실패'}")
        
        return jsonify({
            'success': True,
            'message': '신청이 접수되었습니다.',
            'telegram_sent': telegram_sent
        }), 200
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    """전체 신청 내역 조회 (JSON)"""
    return jsonify(applications), 200

@app.route('/api/test-telegram', methods=['GET'])
def test_telegram():
    """텔레그램 알림 테스트"""
    test_message = """
🧪 <b>신촌 프로젝트 테스트 메시지</b>

텔레그램 알림이 정상적으로 작동하고 있습니다! ✅

📅 테스트 시간: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    success = send_telegram_message(test_message)
    
    if success:
        return """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { 
                    font-family: Arial; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #5B9BD5 0%, #4A8BC2 100%);
                    color: white;
                }
                .box {
                    background: white;
                    color: #333;
                    padding: 40px;
                    border-radius: 20px;
                    max-width: 500px;
                    margin: 0 auto;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                h1 { color: #4caf50; margin-bottom: 20px; }
                a { 
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #5B9BD5;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>✅ 성공!</h1>
                <p>텔레그램 메시지가 전송되었습니다.</p>
                <p>텔레그램 앱에서 확인해주세요.</p>
                <a href="/">대시보드로 돌아가기</a>
            </div>
        </body>
        </html>
        """
    else:
        return """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { 
                    font-family: Arial; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #5B9BD5 0%, #4A8BC2 100%);
                    color: white;
                }
                .box {
                    background: white;
                    color: #333;
                    padding: 40px;
                    border-radius: 20px;
                    max-width: 500px;
                    margin: 0 auto;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                h1 { color: #f44336; margin-bottom: 20px; }
                a { 
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #5B9BD5;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>❌ 실패</h1>
                <p>텔레그램 설정을 확인해주세요.</p>
                <p>환경 변수: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID</p>
                <a href="/">대시보드로 돌아가기</a>
            </div>
        </body>
        </html>
        """, 500

@app.route('/health')
def health():
    """헬스 체크"""
    return jsonify({'status': 'healthy', 'applications': len(applications)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
