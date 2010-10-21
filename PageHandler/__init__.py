from google.appengine.api import mail

def SendContactMail(params):
    senderName = params.get('name')
    senderEmail = params.get('email')
    body = params.get('reference')
    
    mail.send_mail(sender = 'www.martinadlerphotography.com <gae@cloudnine.se>',
              to = 'carl.fredrik.bonander@gmail.com',
              subject = 'From ' + senderName,
              body = 'Email: ' + senderEmail + '\n\n' + body)
    
    return { 'status' : 1, 'message' : 'Message sent' }


