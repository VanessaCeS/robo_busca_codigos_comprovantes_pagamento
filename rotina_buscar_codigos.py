from leitura_relatorios_arteria import search_xml, get_dados_pagamentos_codigo_comprovantes
import funcoes_sap


def rotina_sap():
    pagamentos = get_dados_pagamentos_codigo_comprovantes(search_xml)
    if pagamentos:
        rotina_buscar_codigos_sap(pagamentos)

def rotina_buscar_codigos_sap(pagamentos):
    session = funcoes_sap.exec_sap_gui()
    funcoes_sap.login_sap_gui(session)
    for pagamento in pagamentos:
        rotina_buscar_codigos_sap(pagamento)
