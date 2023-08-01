import time
import win32com.client
import subprocess
from time import sleep
import sys
from util import path_arquivos
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup


load_dotenv('.env')


# ==============================================================================
#   Funções SAP
# ==============================================================================
def exec_sap_gui():
    subprocess.Popen(os.environ.get('path_sap'))
    sleep(2)
    sapgui = win32com.client.GetObject("SAPGUI")
    application = sapgui.GetScriptingEngine
    connection = application.OpenConnection("SAP ECC", True)
    sleep(2)
    session = connection.Children(0)
    verfica_sap(session, "wnd[0]/usr/txtRSYST-MANDT")
    return session


def login_sap_gui(session=None):
    try:
        verfica_sap(session, "wnd[0]/usr/txtRSYST-MANDT").text = "400"
        verfica_sap(session, "wnd[0]/usr/txtRSYST-BNAME").text = os.environ.get('login_sap')
        verfica_sap(session, "wnd[0]/usr/pwdRSYST-BCODE").text = os.environ.get('senha_sap')
        verfica_sap(session, "wnd[0]/usr/txtRSYST-LANGU").text = "PT"
        verfica_sap(session, "wnd[0]").sendVKey(0)

        if verfica_sap(session, "wnd[1]/usr/radMULTI_LOGON_OPT1"):
            verfica_sap(session, "wnd[1]/usr/radMULTI_LOGON_OPT1").select()
            verfica_sap(session, "wnd[1]").sendVKey(0)
    except Exception:
        print(sys.exc_info()[0])


def verfica_sap(session: object = None, objeto: object = None, get_correct: object = None) -> object:
    aux = 0
    if not get_correct:
        try:
            objeto = get_sap_correct_path(objeto, session) if objeto else None
        except Exception as e:
            return False
    while aux < 10:
        try:
            session.FindById(objeto)
            return session.FindById(objeto)
        except Exception as e:
            sleep(1)
            aux += 1
            pass
    return False


def verfica_sap_rapido(session=None, objeto=None, get_correct=None):
    aux = 0
    if not get_correct:
        try:
            objeto = get_sap_correct_path(objeto, session) if objeto else None
        except Exception as e:
            return False
    while aux < 2:
        try:
            session.FindById(objeto)
            return session.FindById(objeto)
        except Exception as e:
            sleep(1)
            aux += 1
            pass
    return False


def verfica_sap2(session=None, objeto=None, get_correct=None):
    aux = 0
    if not get_correct:
        try:
            objeto = get_sap_correct_path(objeto, session) if objeto else None
        except Exception as e:
            return False
    while aux < 10:
        try:
            session.FindById(objeto)
            return session.FindById(objeto)
        except Exception as e:
            # sleep(1)
            aux += 1
            pass
    return False


def get_sap_id(path, session):
    existing = path.split('/')
    existing = [pth.replace('sub', '').strip() for pth in existing if 'SAPLMEGUI:' in existing]
    path_children = session.findById(path).Children
    found = []
    for child in path_children:
        if 'SAPLMEGUI:' in child.Name:
            found.append(child.Name)
    if found:
        if len(found) > 1:
            for f in found:
                if f in existing:
                    return f
            print('Mais de um id encontrado')
        else:
            return found[0]
    else:
        print('Nenhum id encontrado')


def get_sap_correct_path(full_path, session):
    divided_path = full_path.split('SAPLMEGUI:')
    existing = full_path.split('/')
    existing = [part[part.find('SAPLMEGUI:') + 10:part.find('SAPLMEGUI:') + 14] for part in existing if
                'SAPLMEGUI:' in part]
    # print(divided_path)
    how_many = full_path.count('SAPLMEGUI:')
    if how_many == 0:
        return full_path
    curr_path = ''
    for i, path in enumerate(divided_path[:-1]):
        if not curr_path:
            curr_path = path[:path.rindex('/') + 1]
        else:
            curr_path += path[path.index('/'):path.rindex('/') + 1]
        path_children = session.FindById(curr_path).Children
        found = []
        for child in path_children:
            if 'SAPLMEGUI:' in child.Name:
                found.append(child)
        if found:
            if len(found) > 1:
                for f in found:
                    if f.Name[-4:] in existing:
                        found = [f]
                        break
            if len(found) > 1:
                print(found)
                raise Exception('Mais de um id encontrado')
            else:
                curr_path = found[0].id[found[0].id.find('wnd'):]
        else:
            print('Nenhum id encontrado')
    path_ending = divided_path[-1]
    if '/' in path_ending:
        path_ending = path_ending[path_ending.index('/'):]
    return curr_path + path_ending


def abrir_pedido_planilha(session=None):
    # verificar tempo de espera para executar do verificar
    # pesquisa o codigo para criar pagamentos por planilha
    verfica_sap(session, "wnd[0]/tbar[0]/okcd").text = "ZMM015"
    verfica_sap(session, "wnd[0]").sendVKey(0)


def get_tabela_no_sap(session):
    tabela = {}
    i = 1
    a = True
    tentativa = 1
    while a:
        aux = verfica_sap2(session, f"wnd[1]/usr/lbl[{i},1]").text if verfica_sap2(session,
                                                                                   f"wnd[1]/usr/lbl[{i},1]") else ''
        if aux != '':
            value = {}
            b = True
            j = 3
            t = 1
            while b:
                v = verfica_sap2(session, f"wnd[1]/usr/lbl[{i},{j}]").text if verfica_sap2(session,
                                                                                           f"wnd[1]/usr/lbl[{i},{j}]") else ''
                if v != '':
                    value[f"[{i},{j}]"] = v
                    j += 1
                    t = 1
                else:
                    t += 1
                    j += 1
                if t > 3:
                    b = False
            tabela[aux] = value
            i += len(aux) + 1
            tentativa = 1
        else:
            tentativa += 1
            i += len(aux) + 1
        if tentativa > 3:
            a = False
    return tabela


def escolha_banco(aux, dados_banco):
    for a, b in aux['Conta bancária'].items():
        if b.lstrip('0') == dados_banco['conta'].lstrip('0'):
            linha_correta_conta = a
            break
    for c, d in aux['Chave do banco'].items():
        if d.lstrip('0') == dados_banco['nome_banco'].lstrip('0') + dados_banco['agencia']:
            linha_correta_banco = c
            break
    if linha_correta_conta.replace("[", '').replace("]", "").split(",")[1] == \
            linha_correta_banco.replace("[", '').replace("]", "").split(",")[1]:
        return linha_correta_conta
    raise Exception(f'Erro não encontrado a conta informada no pagamento no sistema sap.')


def escolha_banco_jud(aux, dados_banco):
    for a, b, c, d in zip(aux['Conta bancária'].keys(), aux['Conta bancária'].values(), aux['Chave do banco'].keys(),
                          aux['Chave do banco'].values()):
        if b.replace("-", "").lstrip('0') == dados_banco['conta'].replace("-", "").lstrip('0') \
                and dados_banco['nome_banco'].replace("-", "").lstrip('0') in d.lstrip('0') and \
                dados_banco['agencia'] in d.lstrip('0'):
            return a
    raise Exception(f'Erro não encontrado a conta informada no pagamento no sistema sap.')


def selecionar_criar_pedido(session):
    verfica_sap(session,
                "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").selectedNode = "F00004"
    verfica_sap(session, "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode(
        "F00004")


def alert_erro_fechar(session):
    if verfica_sap_rapido(session, "wnd[1]/usr/btnBUTTON_1"):
        verfica_sap_rapido(session, "wnd[1]/usr/btnBUTTON_1").press()


def selecionar_tipo_pedido(session, tipo):
    if verfica_sap(session, "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105"
                            "/txtMEPO_TOPLINE-EBELN").text != '':
        verfica_sap(session, "wnd[0]/mbar/menu[0]/menu[1]").select()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/cmbMEPO_TOPLINE"
                "-BSART").key = f"{tipo}"


def preencher_dados_leal_lagun(session, valor):
    if not verfica_sap(session,
                       "wnd[0]/usr/subSUB0:SAPLMEGUI:0019/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                       "/subSUB1:SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22"):
        verfica_sap(session,
                    "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4002"
                    "/btnDYN_4000-BUTTON").press()
        alert_erro_fechar(session)
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22").select()
    alert_erro_fechar(session)
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/chkEKPO_CI-ZZPEXS").setFocus()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/chkEKPO_CI-ZZPEXS").selected = -1
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/txtEKPO_CI-ZZPJDT").text = \
        "2001.5101016129-8"
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/txtEKPO_CI-ZZPJDT").setFocus()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/txtEKPO_CI-ZZPJDT").caretPosition = 17
    verfica_sap(session, "wnd[0]").sendVKey(0)
    alert_erro_fechar(session)
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/ctxtEKPO_CI-ZZQIPL").setFocus()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/ctxtEKPO_CI-ZZQIPL").caretPosition = 0
    verfica_sap(session, "wnd[0]").sendVKey(2)
    alert_erro_fechar(session)
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/ctxtEKPO_CI-ZZQIPL").setFocus()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/ctxtEKPO_CI-ZZQIPL").caretPosition = 0
    verfica_sap(session, "wnd[0]").sendVKey(4)
    verfica_sap(session, "wnd[1]/usr/lbl[46,5]").setFocus()
    verfica_sap(session, "wnd[1]/usr/lbl[46,5]").caretPosition = 6
    verfica_sap(session, "wnd[1]").sendVKey(2)
    alert_erro_fechar(session)
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/txtEKPO_CI-ZZVREP").text = f"{float(valor) * 0.03:.2f}"
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/txtEKPO_CI-ZZVREP").setFocus()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0010/subSUB3:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1301/subSUB2:SAPLMEGUI:1303/tabsITEM_DETAIL/tabpTABIDT22/ssubTABSTRIPCONTROL1SUB"
                ":SAPLMEGUI:1318/ssubCUSTOMER_DATA_ITEM:SAPLXM06:0111/txtEKPO_CI-ZZVREP").caretPosition = len(
        f"{float(valor) * 0.03:.2f}")
    verfica_sap(session, "wnd[0]").sendVKey(0)
    alert_erro_fechar(session)


def close_sap(session):
    verfica_sap(session, "wnd[0]").close()
    verfica_sap(session, "wnd[1]/usr/btnSPOP-OPTION1").press()


def anexar_doc_sap(session, nome, pap):
    verfica_sap(session, "wnd[0]/titl/shellcont/shell").pressContextButton("%GOS_TOOLBOX")
    verfica_sap(session, "wnd[0]/titl/shellcont/shell").pressButton("%GOS_TOOLBOX")
    verfica_sap(session, "wnd[0]/shellcont/shell").pressContextButton("CREATE_ATTA")
    verfica_sap(session, "wnd[0]/shellcont/shell").selectContextMenuItem("PCATTA_CREA")
    # SELECIONA A PASTA ONDE ESTA O ARQUIVO
    verfica_sap(session, "wnd[1]/usr/ctxtDY_PATH").text = path_arquivos + f"\\{pap}"
    # SELECIONA O NOME DO ARQUIVO
    verfica_sap(session, "wnd[1]/usr/ctxtDY_FILENAME").text = f"{nome}"
    verfica_sap(session, "wnd[1]/tbar[0]/btn[0]").press()


def abrir_pagamento_sap_por_id(session, id_pagamento_sap):
    verfica_sap(session, "wnd[0]/tbar[0]/btn[12]").press()
    verfica_sap(session, "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode("F00002")
    verfica_sap(session, "wnd[0]/mbar/menu[0]/menu[0]").select()
    verfica_sap(session, "wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").text = f"{id_pagamento_sap}"
    verfica_sap(session, "wnd[1]/usr/subSUB0:SAPLMEGUI:0003/ctxtMEPO_SELECT-EBELN").caretPosition = 10
    verfica_sap(session, "wnd[1]").sendVKey(0)
    # Habilita o modo edicao
    verfica_sap(session, "wnd[0]/tbar[1]/btn[7]").press()


def selecionar_codigo_barra(session):
    if not verfica_sap(session, "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                                "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT11"):
        verfica_sap(session, "wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000"
                             "/btnDYN_4000-BUTTON").press()
    verfica_sap(session, "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                         ":SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT11").select()
    verfica_sap(session,
                "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                ":SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT11/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1227"
                "/ssubCUSTOMER_DATA_HEADER:SAPLXM06:0101/btnBT_UPBARCODE").press()
    time.sleep(1)
    soup = BeautifulSoup(
        verfica_sap(session, "wnd[1]/usr/cntlCC_ATTACH_BARR/shellcont/shell").BrowserHandle.Document.body.innerHTML,
        "lxml")
    id_doc = soup.find("div", class_="doc").attrs["onclick"].replace("select(this.id, '", "").replace("')", "")
    # session.findById("wnd[1]/usr/cntlCC_ATTACH_BARR/shellcont/shell").BrowserHandle.Document.body
    verfica_sap(session, "wnd[1]/usr/cntlCC_ATTACH_BARR/shellcont/shell").sapEvent("", "",
                                                                                   f"sapevent:BARZREAD|{id_doc}")
    time.sleep(2)
    soup = BeautifulSoup(verfica_sap(session, "wnd[1]/usr/subSS_OBJ_BARR:/ITSSAUTO/SAPLFG0013:0012/cntlCC_OBJ_HTML"
                                              "/shellcont/shell").BrowserHandle.Document.body.innerHTML, "lxml")
    barcode = soup.find("input", attrs={'name': 'barcode'})
    if barcode:
        barcode = barcode.get('id')
        check_box = soup.findAll("input", attrs={'type': 'checkbox'})
        for checks in check_box:
            check = '&' + checks.get("id") + '=' + checks.get("value")
        time.sleep(1)
        verfica_sap(session,
                    "wnd[1]/usr/subSS_OBJ_BARR:/ITSSAUTO/SAPLFG0013:0012/cntlCC_OBJ_HTML/shellcont/shell").sapEvent("",
                                                                                                                    f"barcode={barcode}{check}",
                                                                                                                    "sapevent:ZBARCODE_LIST")
        time.sleep(1)
        if verfica_sap(session, "wnd[2]/tbar[0]/btn[0]"):
            verfica_sap(session, "wnd[2]/tbar[0]/btn[0]").press()
    else:
        print("A guia não tem codigo de barras para seleção.")
    verfica_sap(session, "wnd[1]").close()

#####################################################$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$##################################
