




def send_email(subject, body):
    receiver_list = ['65361006@qq.com']
    
    
    key='lmiqlrkobjiwbhih'      #换成你的QQ邮箱SMTP的授权码(QQ邮箱设置里)
    EMAIL_ADDRESS='65361006@qq.com'      #换成你的邮箱地址
    EMAIL_PASSWORD=key

    import smtplib
    smtp=smtplib.SMTP('smtp.qq.com',25)

    import ssl
    context=ssl.create_default_context()
    sender=EMAIL_ADDRESS                                         #发件邮箱
    receiver=receiver_list
                                          #收件邮箱
    from email.message import EmailMessage
    msg=EmailMessage()
    msg['subject']=subject       #邮件主题
    msg['From']=sender
    msg['To']=','.join(receiver)
    msg.set_content(body)         #邮件内容

    with smtplib.SMTP_SSL("smtp.qq.com",465,context=context) as smtp:
        smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
        smtp.send_message(msg)
