import smtplib
from email.mime.text import MIMEText
from email.header import Header

    
def send_email(receiver_email, body, sender_email = "736045262@qq.com", sender_password = "xnokteehqdfjbbbj", subject = "【乐游】完成通知"):
    if not receiver_email.strip():
        print("邮箱未设置")
        return
    # SMTP服务器配置，请根据您的邮件服务商进行修改
    smtp_server = 'smtp.qq.com'  # 示例服务器地址
    smtp_port = 587  # 示例端口号
    
    # 创建 MIMEText 对象，这代表了邮件本身
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = Header(sender_email)
    message['To'] = Header(receiver_email)
    message['Subject'] = Header(subject)

    # 发送邮件
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # 启动TLS安全传输
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    # print("邮件发送成功！")

