import os
import re
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests import Session
import requests
import codempresa
import scpjud
import util
from leitura_relatorios_arteria import search_xml, get_dados_pagamentos_codigo_comprovantes
from classe_sap import SAPAutomation
sap = SAPAutomation()
load_dotenv() 
url = {
    "PROD": "https://websites.caixaseguradora.com.br",
    "HM": "https://websiteshm.caixaseguradora.com.br",
}
url = url[os.getenv("AMBIENTE")]
mps = []
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
        if pagamento.get('Módulo de Pagamento'):
            if pagamento['Módulo de Pagamento'][0] == 'SAP':
                if pagamento['Número do Pré Editado'] != "":
                    pagamento['cod_empresa'] = pegar_cod_ramo_correto_sap(pagamento['Número do Pré Editado'])
                else:
                    return "Não existe pre editado para a pesquisa."
        if pagamento.get('Módulo de Pagamento'):
            if pagamento['Módulo de Pagamento'][0] == 'MPS':
                pagamento['IDLG'] = scpjud.login_scpjud(pagamento['Número do Cliente (Recibo)'],
                                                        pagamento['Número de Ocorrência'],
                                                        pagamento['Sinistro Principal do Processo'])

                if pagamento['Número de Ocorrência'] != "":
                    pagamento['cod_empresa'] = codempresa.cod_empresa[codempresa.get_empresa_responsavel(pagamento['Ramo'], pagamento['Produto'])]
                else:
                    return "Não existe ocorrencia para o pagamento"
        # sap_busca(sap)
        buscar_codigo_documento_sap(os.getenv("parametro_doc"),
                                    pagamento['cod_empresa'],
                                    pagamento['Data Estimada do Recebimento do Comprovante no C&S'],
                                    pagamento)


    except Exception as e:
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
    print("AUX = ", aux)
    return aux

#Função responsável por buscar o Doc_Compensação no SAP
def sap_busca():
    try:
        sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00002"
        sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00002")
    except Exception as e:
        print(e)

def buscar_codigo_documento_sap(parametro_doc, cod_empresa, dt_recebimento_comprovante, pagamento):
        sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00003")
        sap.verifica_sap("wnd[0]/usr/ctxtP_VARIA").text = parametro_doc
        sap.verifica_sap("wnd[0]/usr/ctxtS_BUKRS-LOW").text = cod_empresa
        sap.verifica_sap("wnd[0]/usr/txtS_GJAHR-LOW").text = dt_recebimento_comprovante[-4:]
        sap.verifica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = ''
        if 'Número do Pré Editado' in pagamento:
            sap.verifica_sap("wnd[0]/usr/ctxtS_EBELN-LOW").text = pagamento['Número do Pré Editado']
        if 'IDLG' in pagamento:
            sap.verifica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = pagamento['IDLG']
        sap.verifica_sap("wnd[0]/tbar[1]/btn[8]").press()
        ## Verificar se relamente precisa do que esta para baixo
        sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "0"
        sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").contextMenu()
        sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&DETAIL")
        sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").selectColumn("COLUMNTEXT")
        sap.verifica_sap("wnd[1]").close()

        achar_comprovantes(pagamento['Número do Pré Editado'])
        # pegar_tabela_detalhes()

# def pegar_tabela_detalhes():
#     # if not sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellColumn == "COLUMNTEXT" == "Doc.compensação": 
#     #     pass
#     # if sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellColumn == "COLUMNTEXT" == "Ref.bancária": 
#     #     pass
#     # if sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").currentCellColumn == "COLUMNTEXT" ==  "Texto lançto.":
#     #     pass
#     # else: 
#     #     #manda para o arteria que não tem doc compensacao
#     #     pass
    
#     # sap.verifica_sap("wnd[1]").close()
#     achar_comprovantes()

def achar_comprovantes(id_pagamento_sap):
    # doc compensacao
    # sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "AUGBL"
    # sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").clickCurrentCell()
    # sap.buscar_comprovante()
    # # numero documento
    # sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "BELNR"
    # sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").clickCurrentCell()
    # sap.buscar_comprovante()
    sap.voltar_menu_principal()
    # pedido 
    abrir_pedido_sap(id_pagamento_sap)
    sap.verifica_sap("wnd[0]/titl/shellcont/shell").pressButton("%GOS_TOOLBOX")
    sap.buscar_comprovante()


    
    
    

def enviar_dados_arteria(record_id, n_doc_compensacao, observacao, idlg = ''):
    load_dotenv()
    AMBIENTE = os.getenv('AMBIENTE')
    url_ambiente = os.getenv(f'URL_{AMBIENTE}')
    req_body = {
                "Content": {
                    "Id": int(record_id),
                    "LevelId": 242,
                    "FieldContents": {
                        "25763": {
                            "Type": 1,
                            "Value": n_doc_compensacao,
                            "FieldId": 25763
                        },
                        "25056": {
                            "Type": 1,
                            "Value": observacao,
                            "FieldId": 25056
                        },
                        "25762": {
                            "Type": 1,
                            "Value": idlg,
                            "FieldId": 25762
                        },

                    }
                }
            }
    req_header = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q =0.9,*/*;q=0.8",
        "Content-type": "application/json",
        "Authorization": "Archer session-id={0}".format(util.get_token2())}
    update_request = requests.put(url_ambiente + '/RSAarcher/api/core/content/', json=req_body, headers=req_header)
    if update_request.status_code == 200:
        return record_id
        
rotina_sap()
