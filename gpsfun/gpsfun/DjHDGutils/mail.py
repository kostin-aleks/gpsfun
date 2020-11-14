from datetime import datetime

from django.conf import settings
from django.core import mail


#from django.core.mail import send_mail as django_send_mail, send_mass_mail as django_send_mass_mail

'''
settings have 2 params:
EMAIL_DEBUG_MODE
SAFE_EMAILS
If EMAIL_DEBUG_MODE == True:
    send mails only to emails in SAFE_EMAILS
    mails with no in SAFE_EMAILS write on file system to SITE_ROOT /outbox/

'''


def make_safe_recipient_list(recipient_list):
    if settings.EMAIL_DEBUG_MODE==True:
        safe_recipient_list = set(recipient_list).intersection(set(settings.SAFE_EMAILS))
        unsafe_recipient_list = set(recipient_list).difference(safe_recipient_list)
        return (list(safe_recipient_list),
                list(unsafe_recipient_list))

    return (recipient_list, None)


def send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=None, auth_password=None, content_subtype='plain', attachments=None):

    safe_recipient_list, unsafe_recipient_list = make_safe_recipient_list(recipient_list)
    num_sent = 0

    if unsafe_recipient_list:
        num_sent = log_mail(subject,
                            message,
                            from_email,
                            unsafe_recipient_list)

    if safe_recipient_list:
        connection = mail.get_connection(username=auth_user,
                                         password=auth_password,
                                         fail_silently=fail_silently)

        message = mail.EmailMessage(subject, message, from_email, recipient_list, connection=connection)
        message.content_subtype = content_subtype
        if attachments:
            for item in attachments:
                message.attach(*item)

        #  message.send() can return None if message not send 
        num_sent += (message.send() or 0)
    return num_sent


def send_mass_mail(datatuple, fail_silently=False, auth_user=None, auth_password=None):
    """
    send_mass_mail not support message in html format

    """
    safe_datatuple = []
    unsafe_datatuple = []

    if settings.EMAIL_DEBUG_MODE==True:
        for one_tuple in datatuple:
            safe_recipient_list, unsafe_recipient_list = make_safe_recipient_list(one_tuple[3])
            if safe_recipient_list:
                one_tuple[3] = safe_recipient_list
                safe_datatuple.append(one_tuple)

            if unsafe_recipient_list:
                one_tuple[3] = unsafe_recipient_list
                unsafe_datatuple.append(one_tuple)
    else:
        safe_datatuple = datatuple

    num_sent = 0
    if unsafe_datatuple:
        num_sent += log_mass_mail(unsafe_datatuple)

    if safe_datatuple:
        num_sent += mail.send_mass_mail(safe_datatuple, fail_silently, auth_user, auth_password)

    return num_sent


def log_mail(subject, message, from_email, unsafe_recipient_list):
    fd = open("%soutbox/msg-%s"%(settings.SITE_ROOT,
                                 datetime.now()), "w")

    fd.write("From: %s\r\n" % str(from_email.encode("UTF-8")))
    fd.write("To: %s\r\n" % str(",".join(unsafe_recipient_list).encode("UTF-8")))
    fd.write("Subject: %s\r\n\r\n" % str(subject.encode("UTF-8")))
    fd.write(str(message.encode("UTF-8")))
    fd.close()
    return 1


def log_mass_mail(datatuple):
    num_log = 0
    for item_tuple in datatuple:
        num_log += log_mail(item_tuple[0], item_tuple[1], item_tuple[2], item_tuple[3])
    return num_log
