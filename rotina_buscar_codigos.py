import os
import traceback

import codempresa
import scpjud
from leitura_relatorios_arteria import search_xml, get_dados_pagamentos_codigo_comprovantes
from classe_sap import SAPAutomation



def rotina_sap():
    pagamentos = get_dados_pagamentos_codigo_comprovantes(search_xml)
    if pagamentos:
        rotina_buscar_doc_compencacao_sap(pagamentos)



def rotina_buscar_doc_compencacao_sap(pagamentos):
    funcoes_sap = SAPAutomation()
    funcoes_sap.login_sap_gui()
    for pagamento in pagamentos:
        rotina_buscar_codigos_sap(funcoes_sap, pagamento)

def rotina_buscar_codigos_sap(sap, pagamento):
    erros = []
    try:
        print("ID ===>", pagamento['ID do Sistema - Pagamento'])
        if pagamento.get('Módulo de Pagamento'):
            if pagamento['Módulo de Pagamento'][0] == 'SAP':
                if pagamento['Número do Pré Editado'] != "":
                    pagamento['cod_empresa'] = pegar_cod_ramo_correto_sap(sap, pagamento['Número do Pré Editado'])
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
        sap_busca(sap)
        buscar_codigo_documento_sap(sap,
                                    os.getenv("parametro_doc"),
                                    pagamento['cod_empresa'],
                                    pagamento['Data Estimada do Recebimento do Comprovante no C&S'],
                                    pagamento)


    except Exception as e:
        erros.append(traceback.print_exc())

#####################################################################
# ROTINAS RETIRADAS DO ANTIGO
#####################################################################

def buscar_codigo_documento_sap(sap, parametro_doc, cod_empresa, dt_recebimento_comprovante, pagamento):
    sap.verfica_sap("wnd[0]/usr/ctxtP_VARIA").text = parametro_doc
    sap.verfica_sap("wnd[0]/usr/ctxtS_BUKRS-LOW").text = cod_empresa
    sap.verfica_sap("wnd[0]/usr/txtS_GJAHR-LOW").text = dt_recebimento_comprovante
    sap.verfica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = ''
    if 'Número do Pré Editado' in pagamento:
        sap.verfica_sap("wnd[0]/usr/ctxtS_EBELN-LOW").text = pagamento['Número do Pré Editado']
    if 'IDLG' in pagamento:
        sap.verfica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = pagamento['IDLG']

    sap.verfica_sap("wnd[0]/tbar[1]/btn[8]").press()

    ## Verificar se relamente precisa do que esta para baixo
    sap.verfica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "0"
    sap.verfica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").contextMenu()
    sap.verfica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&DETAIL")
    sap.verfica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").selectColumn("COLUMNTEXT")


#Função responsável por buscar o Doc_Compensação no SAP
def sap_busca(sap):
    try:
        # aqui vai ter que fazer uma excessao para os saps diferente pq o menu exibe valores diferentes por usuario
        # e o id dos valores sao diferente dependendo do menu
        sap.verfica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00002"
        sap.verfica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00002")
    except Exception as e:
        print(e)

def abrir_pedido_sap(sap, id_pagamento_sap):
    # aqui vai ter que fazer uma excessao para os saps diferente pq o menu exibe valores diferentes por usuario
    # e o id dos valores sao diferente dependendo do menu
    sap.verfica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00005"
    sap.verfica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00005")


    sap.verfica_sap("wnd[0]/mbar/menu[0]/menu[0]").select()
    sap.verfica_sap("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").text = f"{id_pagamento_sap}"
    sap.verfica_sap("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").caretPosition = 10
    sap.verfica_sap("wnd[1]").sendVKey(0)
    sap.verfica_sap("wnd[0]/tbar[1]/btn[7]").press()


def pegar_cod_ramo_correto_sap(sap, id_pagamento_sap):
    abrir_pedido_sap(sap, id_pagamento_sap)
    cod_ramo = pegar_numero_correto_ramo(sap)

    return cod_ramo

def pegar_numero_correto_ramo(sap):
    if not sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                            "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9"):
        sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000"
                            "/btnDYN_4000-BUTTON").press()
    sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                                        "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9").select()
    aux = sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:"
                        "1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB"
                        ":SAPLMEGUI:1221/ctxtMEPO1222-BUKRS").text
    sap.verfica_sap("wnd[0]/tbar[0]/btn[12]").press()
    return aux


rotina_sap()
