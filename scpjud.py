import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from classe_sap import SAPAutomation

sap = SAPAutomation()
load_dotenv() 
url = {
    "PROD": "https://websites.caixaseguradora.com.br",
    "HM": "https://websiteshm.caixaseguradora.com.br",
}
url = url[os.getenv("AMBIENTE")]

def login_scpjud(n_scpjud, n_ocorrencia, n_sinistro_processo):
    try:
        login_url = os.getenv("scpjud_link")
        username = os.getenv("USER_SCPJUD_PROD")
        password = os.getenv("PASSWORD_SCPJUD_PROD")

        session = requests.Session()
        session.headers = {"userAgent": "Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2909.25 Safari/537.36",
                "content-type": "application/x-www-form-urlencoded"}
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
        login_data = {
            'UsuarioNome': username,
            'Senha': password,
            '__RequestVerificationToken': token,
            'DesconectarSessaoSimultanea':True,
            'RedirectUrl': '/scpjudweb/' 
        }

        set_dados_login = session.post(login_url, data=login_data)
        souplogado = BeautifulSoup(set_dados_login.text, 'html.parser')
        token_session = souplogado.find(attrs={'scpjud-token-validacao': True}).attrs['scpjud-token-validacao']
        session.headers.update({'RequestVerificationToken': token_session})
        response = session.get(os.getenv("scpjud_homepage"))

        return pegar_dados_scpjud(n_scpjud, n_ocorrencia, n_sinistro_processo, session)
    
    except Exception as e:
        print("Erro no SCPJUD", e)
        sap.voltar_menu_principal()

def pegar_dados_scpjud(n_scpjud, n_ocorrencia, n_sinistro_processo, session):
    n_scpjud = n_scpjud.strip()
    n_scpjud = n_scpjud.replace(' ', '+')

    dados_historico_pagamento = session.get(os.getenv("scpjud_link_histpagamento")+ n_ocorrencia +"&NumeroProcesso="+ n_scpjud +"&OffSet=0&PericiasJudiciais=false&TamanhoPagina=14")
    dados_historico_pagamento = dados_historico_pagamento.json()
    
    if len(dados_historico_pagamento) > 0:   
        for n_operacao in dados_historico_pagamento:
            n_operacao = str(n_operacao['OperacaoID'])
            break
        
    scpjud_detalhes_link = os.getenv("scpjud_detalhamento")
    busca_idlg = session.get(scpjud_detalhes_link+"APOL_SINISTRO="+n_sinistro_processo+"&OCORR_HISTORICO="+n_ocorrencia+"&OPERACAO_MOVIMENTO="+n_operacao+"&PROCESSO_JUDICIAL="+n_scpjud)
    dados_scpjud = busca_idlg.json()
    n_idlg = dados_scpjud['IDLG'][0].strip()

    return n_idlg
