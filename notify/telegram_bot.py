import requests

def send_bark(title, content, api_url):
    """
    发送Bark推送
    :param title: 推送标题
    :param content: 推送内容
    :param api_url: Bark推送API地址（如 https://api.day.app/xxx/ ）
    :return: True/False
    """
    url = f"{api_url}{title}/{content}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            print(f"推送成功: {resp.text}")
            return True
        else:
            print(f"推送失败: {resp.text}")
            return False
    except Exception as e:
        print(f"推送异常: {e}")
        return False

if __name__ == '__main__':
    # 示例
    api = 'https://api.day.app/CiBwcJFtZJqN2oDeRx3RK7/'
    send_bark('测试推送','BTC暴涨10%', api) 