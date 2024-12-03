from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP,SMTPAuthenticationError,SMTPNotSupportedError
from email.mime.base import MIMEBase
from email import encoders

from time import sleep
from dotenv import load_dotenv
import os
load_dotenv()
#Verificando o email se é valido ou não
def verificar_email(email: list|str):
    email_erros = []
    if isinstance(email,str):
        emails = [n.strip() for n in email.split(',') if n != '']
    else:
        emails = [n.strip() for n in email if n != '']
    for mail in emails:
        dominio = mail.split('@')[-1]
        try:
            servidor = SMTP('smtp.' + dominio, 587)
            servidor.set_debuglevel(0)
            servidor.helo()
            servidor.quit()
        except Exception as e:
            email_erros.append(mail)
    if email_erros == []:
        return True
    return False

def enviar_email(destinatario:str,corpo_email_texto=None,anexo:str = None, porta_smtp = 587):
    #email que vai enviar
    remetente = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    assunto_email = "Relatório"
    #pegando o domínio do email utilizado
    dominio = remetente.split('@')[-1]
    smtp_server = 'smtp.' + dominio
    smtp_port = porta_smtp
    #pegando todos os emails
    all_destinatarios = destinatario.strip() 
    
    #verificando os emails
    if verificar_email(all_destinatarios):
        mime_multipart = MIMEMultipart()
        mime_multipart['from'] = remetente
        mime_multipart['to'] = destinatario
        mime_multipart['subject'] = assunto_email
        try:
            texto_email = corpo_email_texto
            corpo_email = MIMEText(texto_email,'plain','utf-8')
            mime_multipart.attach(corpo_email)
            #verificando se tem arquivos ou não
            if anexo is not None:
                #verificando se é somente um arquivo ou uma pasta de arquivos
                if '.' in anexo:
                    nome_anexo = anexo.split('\\')[-1]
                    try:
                        #abrindo o arquivo em forma de bytes
                        with open(anexo,'rb') as arqby:
                            file = MIMEBase('application', 'octet-stream')
                            file.set_payload(arqby.read())
                            encoders.encode_base64(file)
                            file.add_header('Content-Disposition',f'attachment; filename={nome_anexo}')
                            mime_multipart.attach(file)
                    except FileNotFoundError:
                        print('Email não enviado')
                        return
                else:
                    arquives = os.listdir(anexo)
                    files_bloq = []
                    for arquive in arquives:
                        try:
                            with open(os.path.join(anexo,arquive),'rb') as arqby:
                                file = MIMEBase('application', 'octet-stream')
                                file.set_payload(arqby.read())
                                encoders.encode_base64(file)
                                file.add_header('Content-Disposition',f'attachment; filename={arquive}')
                                mime_multipart.attach(file)
                        except FileNotFoundError:
                            files_bloq.append(arquive)
                    if len(files_bloq) > 0:
                        print('Email não enviado')
                        return
            #fazendo a conexão
            with SMTP(smtp_server,smtp_port) as server:
                server.ehlo()
                try:
                    server.starttls()
                except SMTPNotSupportedError:
                    pass
                server.login(remetente,password)
                server.sendmail(remetente,all_destinatarios,mime_multipart.as_string())
            
                print('Email enviado com Sucesso')
                sleep(5)
                return True
        
        except SMTPAuthenticationError:
            print('Email não enviado')
        except FileNotFoundError:
            print('Email não enviado')
