import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv() 


def login_scpjud(n_scpjud, n_ocorrencia, n_sinistro_processo):
    try:
        # # URL da página de login
        login_url = os.getenv("scpjud_link")

        # # Dados de autenticação
        username = os.getenv("user_spjud")
        password = os.getenv("password_spjud")

        # # Criar uma sessão para manter a autenticação
        session = requests.Session()

        # # Cabeçalho de User-AgentUse
        session.headers = {"userAgent": "Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2909.25 Safari/537.36",
                "content-type": "application/x-www-form-urlencoded"}
        
        # faz a solicitação GET para a página de login
        response = session.get(login_url)

        # extrai o token da resposta da página de login
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': '__RequestVerificationToken'})['value']

        # envia as credenciais de login e o token em uma solicitação POST
        login_data = {
            'UsuarioNome': username,
            'Senha': password,
            '__RequestVerificationToken': token,
            'DesconectarSessaoSimultanea':True,
            'RedirectUrl': '/scpjudweb/' 
        }

        set_dados_login = session.post(login_url, data=login_data)

        souplogado = BeautifulSoup(set_dados_login.text, 'html.parser')

        #Busca novo token da sessão e o atualiza ao logar
        token_session = souplogado.find(attrs={'scpjud-token-validacao': True}).attrs['scpjud-token-validacao']
        session.headers.update({'RequestVerificationToken': token_session})
       
        response = session.get(os.getenv("scpjud_homepage"))

        #Trata o valor e o formata para inclusão nos parâmetros de rota de busca do idlg
        n_scpjud = n_scpjud.strip()
        n_scpjud = n_scpjud.replace(' ', '+')

        dados_historico_pagamento = session.get(os.getenv("scpjud_link_histpagamento")+ n_ocorrencia +"&NumeroProcesso="+ n_scpjud +"&OffSet=0&PericiasJudiciais=false&TamanhoPagina=14")
        dados_historico_pagamento = dados_historico_pagamento.json()
        if len(dados_historico_pagamento) > 0:   
            for n_operacao in dados_historico_pagamento:
                n_operacao = str(n_operacao['OperacaoID'])
                break
        
        #Endpoint de busca dos dados do detalhamento do pagamento no SCPJUD
        scpjud_detalhes_link = os.getenv("scpjud_detalhamento")
        
        #Endpoint de busca do número do IDLG do pagamento no SCPJUD
        busca_idlg = session.get(scpjud_detalhes_link+"APOL_SINISTRO="+n_sinistro_processo+"&OCORR_HISTORICO="+n_ocorrencia+"&OPERACAO_MOVIMENTO="+n_operacao+"&PROCESSO_JUDICIAL="+n_scpjud)
        dados_scpjud = busca_idlg.json()
        n_idlg = dados_scpjud['IDLG'][0].strip()
        print(n_idlg)

        return n_idlg

    except Exception as e:
        print(e)
