import requests
from config import FILE_CONFIG


class VoiceService:
    def __init__(self):
        self.api_key = FILE_CONFIG.get('baidu_api_key')
        self.secret_key = FILE_CONFIG.get('baidu_secret_key')

    def get_token(self):
        """获取百度语音识别token"""
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        try:
            response = requests.get(url)
            return response.json().get('access_token')
        except:
            return None

    def speech_to_text(self, audio_file):
        """语音转文字"""
        token = self.get_token()
        if not token:
            return None

        url = f"http://vop.baidu.com/server_api?dev_pid=1537&cuid=interview_system&token={token}"

        with open(audio_file, 'rb') as f:
            audio_data = f.read()

        try:
            response = requests.post(url, data=audio_data, headers={
                'Content-Type': 'audio/wav; rate=16000'
            })
            result = response.json()
            if result.get('err_no') == 0:
                return result.get('result')[0]
            return None
        except:
            return None