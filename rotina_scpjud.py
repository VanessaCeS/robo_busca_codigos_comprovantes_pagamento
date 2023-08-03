def buscar_pagamentos_mps(pagamentos):
    for pagamento in pagamentos:
        if pagamento['Módulo de Pagamento'] == ['MPS']:
            mps.append(pagamento)
    return mps

def login_scpjud():
    username = os.getenv("USER_SCPJUD_PROD")
    password = os.getenv("PASSWORD_SCPJUD_PROD")
    session = Session()

    session.headers.update({"Accept": "application/json"})
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
    )
    first_request = session.get(f"{url}/scpjudweb/")
    soup = BeautifulSoup(first_request.content, "lxml")
    token = soup.find("input", {"name": "__RequestVerificationToken"})["value"]
    login_data = {
        "__RequestVerificationToken": token,
        "DesconectarSessaoSimultanea": "true",
        "UsuarioNome": username,
        "RedirectUrl": "/scpjudweb/",
        "Senha": password,
    }
    session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    session.post(f"{url}/scpjudweb/Autenticacao/Entrar", data=login_data)
    page_pagamentos = session.get(f"{url}/scpjudweb/Pagamentos")
    soup = BeautifulSoup(page_pagamentos.content, "lxml")
    token = soup.find(None, {"scpjud-token-validacao": True})["scpjud-token-validacao"]
    session.headers.update({"RequestVerificationToken": token})
    return session

def pesquisar_idlg(pagamentos):
    session = login_scpjud()
    for pagamento in pagamentos:
        try:
            n_scpjud = pagamento['Número do Cliente (Recibo)'].strip().replace(' ', '+')
            n_ocorrencia = pagamento['Número de Ocorrência']
            
            dados_pagamento = session.get(f'{url}/scpjudweb/Api/Pagamento/SelecionarHistoricoPagamentos?NumeroOcorrencia={n_ocorrencia}&NumeroProcesso={n_scpjud}&OffSet=0&PericiasJudiciais=false&TamanhoPagina=14').json()

            operacao_id = dados_pagamento[0]['OperacaoID']
            n_sinistro_processo = dados_pagamento[0]['NumeroSinistro']
            
            dados = session.get(f'{url}/scpjudweb/Api/Processo/DetalharMovimentacaoSinistro?+APOL_SINISTRO={n_sinistro_processo}&OCORR_HISTORICO={n_ocorrencia}&OPERACAO_MOVIMENTO={operacao_id}&PROCESSO_JUDICIAL={n_scpjud}').json()
            n_idlg = dados['IDLG'][0].strip() 
            return n_idlg
        
        except Exception as e:
            print('Error ', e)

