import os
import util
import scpjud
import traceback
import codempresa
import funcoes_arteria
import motivorecusapag
from datetime import datetime
from dotenv import load_dotenv
from classe_sap import SAPAutomation
from leitura_relatorios_arteria import search_xml_busca_cvp_e_csh, search_xml_busca_cnp, get_dados_pagamentos_codigo_comprovantes
sap = SAPAutomation()
load_dotenv() 
url = {
    "PROD": "https://websites.caixaseguradora.com.br",
}
url = url[os.getenv("AMBIENTE")]
padrao_regex = r".*411$"

def rotina_sap():
    rotina_buscar_doc_compencacao_sap_cvp_e_csh()
    rotina_buscar_doc_compencacao_sap_cnp()

def rotina_buscar_doc_compencacao_sap_cnp():    
    pagamentos = get_dados_pagamentos_codigo_comprovantes(search_xml_busca_cnp)
    sap.exec_sap_gui('CNP')
    sap.login_sap_gui('CNP')
    
    for pagamento in pagamentos:
        pagamento['Tipo Pagamento'] = 'cnp'
        rotina_buscar_codigos_sap(pagamento)


def rotina_buscar_doc_compencacao_sap_cvp_e_csh():
    pagamentos = get_dados_pagamentos_codigo_comprovantes(search_xml_busca_cvp_e_csh)
    sap.login_sap_gui()
    for pagamento in pagamentos:
        pagamento['Tipo Pagamento'] = False
        rotina_buscar_codigos_sap(pagamento)
    sap.sap_logoff()


def rotina_buscar_codigos_sap(pagamento):
    erros = []
    try:
            if pagamento.get('Módulo de Pagamento'):
                if pagamento['Módulo de Pagamento'][0] == 'SAP':
                        if pagamento['Número do Pré Editado'] != "":
                            pagamento['cod_empresa'] = pegar_cod_ramo_correto_sap(pagamento['Número do Pré Editado'], pagamento['Tipo Pagamento'])
                        else:
                            return "Não existe pre editado para a pesquisa."
            if pagamento.get('Módulo de Pagamento'):
                if pagamento['Módulo de Pagamento'][0] == 'MPS':
                    pagamento['IDLG'] = scpjud.login_scpjud(pagamento['Número do Cliente (Recibo)'],
                                                            pagamento['Número de Ocorrência'],
                                                            pagamento['Sinistro Principal do Processo'], pagamento["ID do Sistema - Pagamento"])
                    if pagamento['Número do Pré Editado'] != '':
                        pagamento['Número do Pré Editado'] = ''

                    if pagamento['IDLG'] == '' or pagamento['IDLG'] == None:
                        if pagamento['DOC. Compensação'] == '':
                            data = pegar_data()
                            dados_update = {"Observação Costa e Silva": f"""IDLG indisponível até a presente data  
                            <br> 
                            Sem DOC disponível no SAP até a presente data - {data.day}/{data.month} - {data.strftime('%X')[:-3]}    
                                            """}
                            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
                        else:
                            data = pegar_data()
                            dados_update = {"Observação Costa e Silva": f"IDLG indisponível até a presente data - {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
                            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
                        sap.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()
                        pass
                    else:
                        dados_update = {'IDLG': f'{pagamento["IDLG"]}'}
                        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])

                    if pagamento['Número de Ocorrência'] != "":
                        pagamento['cod_empresa'] = codempresa.cod_empresa[codempresa.get_empresa_responsavel(pagamento['Ramo'], pagamento['Produto'])]
                    else:
                        return "Não existe ocorrencia para o pagamento"
            print("pagamento --->> ", pagamento)
            mandar_banco_de_dados(pagamento)
            if pagamento['DOC. Compensação'] == '' and 'IDLG' not in pagamento: 
                data = pegar_data() 
                dados_update = {"Observação Costa e Silva": f"Sem DOC disponível no SAP até a presente data - {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
                funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
            else: 
                dados_update = {"DOC. Compensação": f"{pagamento['DOC. Compensação']}"}
                funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])
            if 'IDLG' in pagamento and pagamento["IDLG"] == '':
                pass
            else:
                buscar_codigo_documento_sap(os.getenv("parametro_doc"),
                                            pagamento['cod_empresa'],
                                            pagamento['Data Estimada do Recebimento do Comprovante no C&S'],
                                            pagamento, 
                                            pagamento['Tipo Pagamento'])
                
    except Exception as e:
        print("ERROR", e)
        erros.append(traceback.print_exc())

def pegar_cod_ramo_correto_sap(id_pagamento_sap, tipo_pagamento):
    abrir_pedido_sap(id_pagamento_sap)
    cod_ramo = pegar_numero_correto_ramo(tipo_pagamento)
    return cod_ramo

def abrir_pedido_sap(id_pagamento_sap):
        sap_busca()
        sap.verifica_sap("wnd[0]/mbar/menu[0]/menu[0]").select()
        sap.verifica_sap("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").text = f"{id_pagamento_sap}"
        sap.verifica_sap("wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").caretPosition = 9
        sap.verifica_sap("wnd[1]").sendVKey(0)

#Função responsável por buscar o Doc_Compensação no SAP
def sap_busca():
    try:
        sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00005"
        sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00005")
    except Exception as e:
         print("Erro ao iniciar busca ", e)

def pegar_numero_correto_ramo(tipo_pagamento):
    if not sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                            "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9"):
        sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000"
                            "/btnDYN_4000-BUTTON").press()
    sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                                        "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9").select()
    if tipo_pagamento:
        aux = sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:"
                        "1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB"
                        ":SAPLMEGUI:1221/ctxtMEPO1222-BUKRS").text
    else:
        aux = sap.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:"
                        "1200/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT9/ssubTABSTRIPCONTROL2SUB"
                        ":SAPLMEGUI:1221/ctxtMEPO1222-BUKRS").text
    sap.verifica_sap("wnd[0]/tbar[0]/btn[12]").press()
    sap.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()
    return aux
    
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

    if 'IDLG' in pagamento:
        idlg = pagamento['IDLG']
    else:
        idlg = None

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
        None,
        resp_pagamento_id,
        resp_pagamento_nome,
        pagamento['Produto'],
        pagamento['ID do processo - Robo - Integra'],
        pagamento['ID BAJ'],
        pagamento['ID do Favorecido'],
        solicitante_id,
        solicitante_nome,
        idlg
        ]
    
    colunas =  ['id_sistema_pagamento', 'pagamento_id', 'numero_preeditado', 'data_exercicio', 'mod_pagamento', 'ramo', 'numero_scpjud', 'numero_ocorrencia', 'numero_sinistro', 'doc', 'situacao_pagamento', 'resp_pagamento_id', 'resp_pagamento_nome', 'produto', 'id_processo', 'id_baj', 'id_favorecido', 'solicitante_id', 'solicitante_nome', 'idlg']

    util.execute_sql_integra(pagamento['ID do Sistema - Pagamento'], dados, colunas)
    
    

def buscar_codigo_documento_sap(parametro_doc, cod_empresa, dt_recebimento_comprovante, pagamento, tipo_pagamento):
        if tipo_pagamento:
            sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00003")
        else:
            sap.verifica_sap("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00002")
        print('ano --> ', dt_recebimento_comprovante[-4:])
        sap.verifica_sap("wnd[0]/usr/ctxtP_VARIA").text = parametro_doc
        sap.verifica_sap("wnd[0]/usr/ctxtS_BUKRS-LOW").text = cod_empresa
        ano = dt_recebimento_comprovante[-4:] if dt_recebimento_comprovante != '01/01/2024' else '2023'
        sap.verifica_sap("wnd[0]/usr/txtS_GJAHR-LOW").text = ano

        sap.verifica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = ''

        if 'Número do Pré Editado' in pagamento:
            sap.verifica_sap("wnd[0]/usr/ctxtS_EBELN-LOW").text = pagamento['Número do Pré Editado']
        if 'IDLG' in pagamento and pagamento['IDLG'] != '' and  pagamento['IDLG'] != None:
            sap.verifica_sap("wnd[0]/usr/txtS_ZIDLG-LOW").text = pagamento['IDLG']

        sap.verifica_sap("wnd[0]/tbar[1]/btn[8]").press()
        if pagamento.get('Solicitante') != '':
            solicitante = pagamento.get('Solicitante')[0]['id']
        else:
            solicitante = ''
            data = pegar_data()
            dados_update = {"Observação Costa e Silva": f"Não há solicitante associado a esse pagamento - <br> {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', pagamento["ID do Sistema - Pagamento"])

        achar_comprovantes(pagamento['Número do Pré Editado'], cod_empresa, pagamento["ID do Sistema - Pagamento"], solicitante,  pagamento['ID do processo - Robo - Integra'], pagamento['Módulo de Pagamento'][0], pagamento['Ramo'], pagamento['DOC. Compensação'], pagamento['Tipo Pagamento'])

            
def achar_comprovantes(id_pagamento_sap, cod_empresa, id_sistema_pagamento, solicitante_id,  id_processo, mod_pagamento, ramo, compesacao, tipo_pagamento):
    if sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell"):    
        if cod_empresa == 'C010':
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "AUGBL"
            doc_compesacao = sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").GetCellValue(0,'AUGBL')
            dados_update = {"DOC. Compensação": f"{doc_compesacao}"}
            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
        elif cod_empresa != 'D011':
                sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "AUGBL"
                doc_compesacao = sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").GetCellValue(0,'AUGBL')
                if doc_compesacao != '':
                    dados_update = {"DOC. Compensação": f"{doc_compesacao}"}
                    funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
                    
                    sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").clickCurrentCell()
                    if not tipo_pagamento:
                        sap.buscar_comprovante_csh(id_sistema_pagamento, solicitante_id,  id_processo, ramo)
                    else:
                        sap.buscar_comprovante(id_sistema_pagamento, solicitante_id,  id_processo, ramo)

                sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "BELNR"
                sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").clickCurrentCell()
                if not tipo_pagamento:
                    sap.buscar_comprovante_csh(id_sistema_pagamento,solicitante_id,  id_processo, ramo)
                else:
                    sap.buscar_comprovante(id_sistema_pagamento,solicitante_id,  id_processo, ramo)
                    
        elif cod_empresa == 'D011' and compesacao == '':
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "AUGBL"
            doc_compesacao = sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").GetCellValue(0,'AUGBL')
            dados_update = {"DOC. Compensação": f"{doc_compesacao}"}
            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
    
        status_pagamento(id_sistema_pagamento)
        sap.voltar_menu_principal()

        if mod_pagamento == 'SAP':
            abrir_pedido_sap(id_pagamento_sap)
            sap.buscar_comprovante(id_sistema_pagamento,solicitante_id,  id_processo, ramo) 
    else:
        data = pegar_data()
        dados_update = {"Observação Costa e Silva": f"Não há dados referentes ao pagamento no SAP - <br> {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
        dados_update = {'IDLG': ''}
        funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
        sap.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()

def status_pagamento(id_sistema_pagamento):
        sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").currentCellColumn = "BUTXT"
        txt_lcto = sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").GetCellValue(0,'BUTXT').upper()
        util.execute_sql_integra(id_sistema_pagamento, [txt_lcto.lower()], ['situacao_pagamento'])

        if txt_lcto != "" and txt_lcto != "PAGAMENTO EFETUADO":
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "0"
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").contextMenu()
            sap.verifica_sap("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&DETAIL")

            motivo = busca_motivo_recusa()
            data = pegar_data()
            dados_update = {"Observação Costa e Silva": f"{txt_lcto} - {motivo} - <br> {data.day}/{data.month} - {data.strftime('%X')[:-3]}"}
            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
            sap.verifica_sap("wnd[1]").close()
        else:
            data = pegar_data()
            dados_update = {"Observação Costa e Silva": ""}
            funcoes_arteria.cadastrar_arteria(dados_update, 'Pagamento', id_sistema_pagamento)
        
def busca_motivo_recusa():
        value_motivo = False
        i = 0
        while not value_motivo:
            try:
                if sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").GetCellValue(i, "COLUMNTEXT") == 'Ref.bancária':
                    recusa_pagamento = sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").GetCellValue(i, "VALUE")
                    value_motivo = True
                    break
                elif sap.verifica_sap("wnd[1]/usr/cntlGRID/shellcont/shell").GetCellValue(i, "COLUMNTEXT") != 'Ref.bancária':
                    i+=1
                else:
                    print('Campo texto de motivo da recusa do pagamento não encontrado')
                    break
                                
            except Exception as e:
                print('Erro em pegar motivo da recusa', e)
                value_motivo = True
                recusa_pagamento = ''

        if recusa_pagamento and recusa_pagamento != '':
            motivo_full = ''
            for cod in range(0, len(recusa_pagamento), 2):
                cod = recusa_pagamento[cod:cod+2]
                motivo_full += f'{cod}({motivorecusapag.codrecusa.get(cod, "")})\n'
            motivo_full = motivo_full.rstrip('\n')
            return (motivo_full or '')    
rotina_sap()