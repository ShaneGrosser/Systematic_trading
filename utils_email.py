from string import Template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def send_email(strategy, bp, sp, pos, vwap):
    s = smtplib.SMTP(host='outlook.mercuria.met', port=25)
    s.starttls()
    names, emails = get_contacts('P:/Coding/Systematic trading/contacts.txt')
    message_template = read_template('P:/Coding/Systematic trading/message.txt')

    bp = str(round(bp, 2))
    sp = str(round(sp, 2))
    vwap = str(round(vwap, 2))

    # For each contact, send the email:
    for name, email in zip(names, emails):
        msg = MIMEMultipart()  # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title(), STRATEGY_NAME=strategy, POSITION=pos, VWAP=vwap,
                                              BUY=bp, SELL=sp)

        # setup the parameters of the message
        msg['From'] = 'sgrosser@mercuria.com'
        msg['To'] = email
        msg['Subject'] = "%s strategy report" % strategy

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        s.send_message(msg)

        del msg

