import os
import re
import util
import scpjud
import traceback
import funcoes_arteria
import codempresa
from datetime import datetime
from dotenv import load_dotenv
from classe_sap import SAPAutomation
from leitura_relatorios_arteria import search_xml, get_dados_pagamentos_codigo_comprovantes

sap = SAPAutomation()
load_dotenv() 
url = {
    "PROD": "https://websites.caixaseguradora.com.br",
    # "HM": "https://websiteshm.caixaseguradora.com.br",
}
url = url[os.getenv("AMBIENTE")]
padrao_regex = r".*411$"

def rotina_sap():
    pagamentos = get_dados_pagamentos_codigo_comprovantes(search_xml)
    if pagamentos:
        rotina_buscar_doc_compencacao_sap(pagamentos)

def rotina_buscar_doc_compencacao_sap(pagamentos):
    sap.login_sap_gui()
    for pagamento in pagamentos:
        rotina_buscar_codigos_sap(pagamento)

def rotina_buscar_codigos_sap(pagamento):
    erros = []
    try:
        # if pagamento['ID do Sistema - Pagamento'] == '6705547' or pagamento['ID do Sistema - Pagamento'] == '6710044':
            if pagamento.get('Módulo de Pagamento'):
                if pagamento['Módulo de Pagamento'][0] == 'SAP':
                        if pagamento['Número do Pré Editado'] != "":
                            pagamento['cod_empresa'] = pegar_cod_ramo_correto_sap(pagamento['Número do Pré Editado'])
                        else:
                            return "Não existe pre editado para a pesquisa."
                        
            if pagamento.get('Módulo de Pagamento'):
                if pagamento['Módulo de Pagamento'][0] == 'MPS':
                    return metodo_pagamento_mps(pagamento)
                    
            print("PAGAMENTO ==> ", pagamento)
            verificar_doc_compensacao(pagamento)
            mandar_banco_de_dados(pagamento)
            buscar_codigo_documento_sap(os.getenv("parametro_doc"),
                                                pagamento['cod_empresa'],
                                                pagamento['Data Estimada do Recebimento do Comprovante no C&S'],
                                                pagamento)
    except Exception as e:
        print("ERROR", e)
        erros.append(traceback.print_exc())

def pegar_cod_ramo_correto_sap(id_pagamento_sap):
    abrir_pedido_sap(id_pagamento_sap)
    cod_ramo = pegar_numero_correto_ramo()
    return cod_ramo

def abrir_pedido_sap(id_pagamento_sap):
    if re.match(padrao_regex, os.getenv("sap_username")):
        sap_busca()
        sap.verifica_sap("wnd[0]/mbar/menu[0]/menu[0]").select()
        sap.verifica_sap("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").text = f"{id_pagamento_sap}"
        sap.verifica_sap("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").caretPosition = 9
        sap.verifica_sap("wnd[1]").sendVKey(0)

#Função responsável por buscar o Doc_Compensação no SAP
def sap_busca():
    try:
        if re.match(padrao_regex, os.getenv("sap_username")):
            sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00002"
            sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00002")
        else:
            sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00005"
            sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00005")
    except Exception as e:
        print("Erro ao iniciar busca ", e)

def pegar_numero_correto_ramo():
    if not sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                            "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9"):
        sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000"
                            "/btnDYN_4000-BUTTON").press()
    sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                                        "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9").select()
    aux = sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:"
                        "1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB"
                        ":SAPLMEGUI:1221/ctxtMEPO1222-BUKRS").text
    sap.verifica_sap("wnd[0]/tbar[0]/btn[12]").press()
    sap.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()
    return aux

def metodo_pagamento_mps(pagamento):
    pagamento['IDLG'] = scpjud.login_scpjud(pagamento['Número do Cliente (Recibo)'],
                                                            pagamento['Número de Ocorrência'],
                                                            pagamento['Sinistro Principal do Processo'])
    if pagamento['IDLG'] != '':
        dados_update = {'IDLG': f'{pagamento["IDLG"]}', "Observação Costa e Silva": ''}
        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
        # util.execute_sql_integra(pagamento['ID do Sistema - Pagamento'],{"idlg": pagamento['IDLG']})
    else:
        data = pegar_data()
        print("DATA IDLG ==> ", data)
        dados_update = {"Observação Costa e Silva": f"IDLG indisponível até a presente data - {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
    if pagamento['Número de Ocorrência'] != "":
        pagamento['cod_empresa'] = codempresa.cod_empresa[codempresa.get_empresa_responsavel(pagamento['Ramo'], pagamento['Produto'])]
    else:
        return "Não existe ocorrencia para o pagamento"
    
def verificar_doc_compensacao(pagamento):
    if pagamento['DOC. Compensação'] == '':
        data = pegar_data() 
        dados_update = {"Observação Costa e Silva": f"Sem DOC disponível no SAP até a presente data - {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
        
        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
    else: 
        dados_update = {"DOC. Compensação": f"{pagamento['DOC. Compensação']}", "Observação Costa e Silva": ''}
        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])

def pegar_data(): 
    return datetime.now()

def mandar_banco_de_dados(pagamento):
    if len(pagamento['Responsável pelo Pagamento']) > 0:
        resp_pagamento_id = pagamento['Responsável pelo Pagamento'][0]['id']
        resp_pagamento_nome = pagamento['Responsável pelo Pagamento'][0]['name']
    else:
         resp_pagamento_id = None
         resp_pagamento_nome = None

    if len(pagamento['Solicitante']) > 0:
        solicitante_id = pagamento['Solicitante'][0]['id']
        solicitante_nome = pagamento['Solicitante'][0]['name']
    else:
         solicitante_id = None
         solicitante_nome = None
    
    dados = [
        pagamento['ID do Sistema - Pagamento'],
        pagamento['ID da Aplicação - Pagamento'],
        pagamento['Número do Pré Editado'],
        pagamento['Data Estimada do Recebimento do Comprovante no C&S'][-4:],
        pagamento['Módulo de Pagamento'][0],
        pagamento['cod_empresa'],
        pagamento['Número do Cliente (Recibo)'],
        pagamento['Número de Ocorrência'],
        pagamento['Sinistro Principal do Processo'],
        pagamento['DOC. Compensação'],
        '',
        resp_pagamento_id,
        resp_pagamento_nome,
        pagamento['Produto'],
        pagamento['ID do processo - Robo - Integra'],
        pagamento['ID BAJ'],
        pagamento['ID do Favorecido'],
        solicitante_id,
        solicitante_nome,
        ""
        ]
    
    util.execute_sql_integra(pagamento['ID do Sistema - Pagamento'], dados)
    

def buscar_codigo_documento_sap(parametro_doc, cod_empresa, dt_recebimento_comprovante, pagamento):
        sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00003")
        sap.verifica_sap("wnd[0]/usr/ctxtP_VARIA").text = parametro_doc
        sap.verifica_sap("wnd[0]/usr/ctxtS_BUKRS-LOW").text = cod_empresa
        sap.verifica_sap("wnd[0]/usr/txtS_GJAHR-LOW").text = dt_recebimento_comprovante[-4:]
        sap.verifica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = ''

        if 'Número do Pré Editado' in pagamento:
            sap.verifica_sap("wnd[0]/usr/ctxtS_EBELN-LOW").text = pagamento['Número do Pré Editado']
        if 'IDLG' in pagamento and 'IDLG' != '':
            sap.verifica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = pagamento['IDLG']

        sap.verifica_sap("wnd[0]/tbar[1]/btn[8]").press()

        solicitante_nome = pagamento.get('Solicitante')[0]['name']
        solicitante_id = pagamento.get('Solicitante')[0]['id']
        achar_comprovantes(pagamento['Número do Pré Editado'], cod_empresa, pagamento["ID do Sistema - Pagamento"],solicitante_id, solicitante_nome, pagamento['ID do processo - Robo - Integra'])

def achar_comprovantes(id_pagamento_sap, cod_empresa, id_sistema_pagamento, solicitante_id, solicitante_nome, id_proceso):
        if cod_empresa != 'D011':
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "AUGBL"
            doc_compesacao = sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").GetCellValue(0,'AUGBL')
            if doc_compesacao != '':
                sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").clickCurrentCell()
                sap.buscar_comprovante(id_sistema_pagamento, solicitante_id, solicitante_nome, id_proceso)

            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "BELNR"
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").clickCurrentCell()
            sap.buscar_comprovante(id_sistema_pagamento,solicitante_id, solicitante_nome, id_proceso)
            
        status_pagamento(id_sistema_pagamento)
        sap.voltar_menu_principal()

        abrir_pedido_sap(id_pagamento_sap)
        sap.buscar_comprovante(id_sistema_pagamento,solicitante_id, solicitante_nome, id_proceso) 

def status_pagamento(id_sistema_pagamento):
        sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "BUTXT"
        txt_lcto = sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").GetCellValue(0,'BUTXT')
        # util.execute_sql_integra(id_sistema_pagamento,{"situacao_pagamento": txt_lcto})
        
        txt_lcto.upper()
        if txt_lcto != "" and txt_lcto != "PAGAMENTO EFETUADO":

            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "0"
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").contextMenu()
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&DETAIL")
            
            sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellRow = 56
            sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").firstVisibleRow = 49
            sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").selectedRows = "56"

            data = pegar_data()
            dados_update = {"Observação Costa e Silva": f"Pagamento rejeitado - {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
            sap.verifica_sap("wnd[1]").close()
        

rotina_sap()
