import time
import traceback

import win32com.client
import subprocess
from time import sleep
import sys
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv('.env')


class SAPAutomation:
    def __init__(self):
        self.sap_username = os.environ.get('sap_username')
        self.sap_password = os.environ.get('sap_password')
        self.path_sap = os.environ.get('path_sap')
        self.session = self.exec_sap_gui()

    def exec_sap_gui(self):
        subprocess.Popen(self.path_sap)
        sleep(2)
        sapgui = win32com.client.GetObject("SAPGUI")
        application = sapgui.GetScriptingEngine
        connection = application.OpenConnection("SAP ECC", True)
        sleep(2)
        session = connection.Children(0)
        sleep(2)
        return session

    def get_sap_id(self, path):
        existing = path.split('/')
        existing = [pth.replace('sub', '').strip() for pth in existing if 'SAPLMEGUI:' in existing]
        path_children = self.session.findById(path).Children
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
            print('50 - Nenhum id encontrado')

    def get_sap_correct_path(self, full_path, session):
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
                print('84 - Nenhum id encontrado')
        path_ending = divided_path[-1]
        if '/' in path_ending:
            path_ending = path_ending[path_ending.index('/'):]
        return curr_path + path_ending

    def verifica_sap(self, objeto: object = None, get_correct: object = None) -> object:
        aux = 0
        if not get_correct:
            try:
                objeto = self.get_sap_correct_path(objeto, self.session) if objeto else None
            except Exception as e:
                return False
        while aux < 4:
            try:
                self.session.FindById(objeto)
                return self.session.FindById(objeto)
            except Exception as e:
                sleep(1)
                aux += 1
                pass
        return False

    def verifica_sap_rapido(self, objeto=None, get_correct=None):
        aux = 0
        if not get_correct:
            try:
                objeto = self.get_sap_correct_path(objeto, self.session) if objeto else None
            except Exception as e:
                return False
        while aux < 2:
            try:
                self.session.FindById(objeto)
                return self.session.FindById(objeto)
            except Exception as e:
                sleep(1)
                aux += 1
                pass
        return False

    def verifica_sap2(self, objeto=None, get_correct=None):
        aux = 0
        if not get_correct:
            try:
                objeto = self.get_sap_correct_path(objeto, self.session) if objeto else None
            except Exception as e:
                return False
        while aux < 10:
            try:
                self.session.FindById(objeto)
                return self.session.FindById(objeto)
            except Exception as e:
                # sleep(1)
                aux += 1
                pass
        return False

    def get_tabela_no_sap(self):
        tabela = {}
        i = 1
        a = True
        tentativa = 1
        while a:
            aux = self.verifica_sap_rapido(f"wnd[1]/usr/lbl[{i},1]").text if self.verifica_sap_rapido(
                f"wnd[1]/usr/lbl[{i},1]") else ''
            print("AUX ==> ", aux)
            if aux != '':
                value = {}
                b = True
                j = 3
                t = 1
                while b:
                    v = self.verifica_sap_rapido(f"wnd[1]/usr/lbl[{i},{j}]").text if self.verifica_sap_rapido(
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

    # fazer a função de pegar a mensaguem do alert de erro e retornar-la
    def alert_erro_fechar(self):
        if self.verifica_sap_rapido("wnd[1]/usr/btnBUTTON_1"):
            self.verifica_sap_rapido("wnd[1]/usr/btnBUTTON_1").press()

    def login_sap_gui(self):
        try:
            if self.verifica_sap("wnd[0]/usr/txtRSYST-MANDT"):
                self.verifica_sap("wnd[0]/usr/txtRSYST-MANDT").text = "400"
                self.verifica_sap("wnd[0]/usr/txtRSYST-BNAME").text = self.sap_username
                self.verifica_sap("wnd[0]/usr/pwdRSYST-BCODE").text = self.sap_password
                self.verifica_sap("wnd[0]/usr/txtRSYST-LANGU").text = "PT"
                self.verifica_sap("wnd[0]").sendVKey(0)

                if self.verifica_sap("wnd[1]/usr/radMULTI_LOGON_OPT1"):
                    self.verifica_sap("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
                    self.verifica_sap("wnd[1]").sendVKey(0)
        except Exception:
            print(sys.exc_info()[0])

    def sap_logoff(self):
        self.verifica_sap("wnd[0]").close()
        self.verifica_sap("wnd[1]/usr/btnSPOP-OPTION1").press()
        os.system("taskkill /IM saplogon.exe /F")

    def get_itens_menu(self, id_menu):
        menu = self.session(id_menu)
        itens_menu = []
        for item in menu.children:
            itens_sub_menu = []
            if item.text.strip() and item.id.strip():
                if item.childen:
                    for sub_item in item:
                        if sub_item.text.strip() and sub_item.id.strip():
                            itens_sub_menu.append({
                                'nome': sub_item.text.strip(),
                                'id': sub_item.id.split(item.id.split(menu)[1])[1],
                            })
                    itens_menu.append({
                        'nome': item.text.strip(),
                        'id': item.id.split(menu)[1],
                        'sub_menu': itens_sub_menu
                    })

        return itens_menu

    def selecionar_codigo_barra(self):
        if not self.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200"
                                "/subSUB1:SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT11"):
            self.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0016/subSUB1:SAPLMEVIEWS:1100/subSUB1:SAPLMEVIEWS:4000"
                             "/btnDYN_4000-BUTTON").press()
        self.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
                         ":SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT11").select()
        self.verifica_sap(
            "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB1:SAPLMEVIEWS:1100/subSUB2:SAPLMEVIEWS:1200/subSUB1"
            ":SAPLMEGUI:1102/tabsHEADER_DETAIL/tabpTABHDT11/ssubTABSTRIPCONTROL2SUB:SAPLMEGUI:1227"
            "/ssubCUSTOMER_DATA_HEADER:SAPLXM06:0101/btnBT_UPBARCODE").press()
        time.sleep(2)
        soup = BeautifulSoup(
            self.verifica_sap("wnd[1]/usr/cntlCC_ATTACH_BARR/shellcont/shell").BrowserHandle.Document.body.innerHTML,
            "lxml")
        id_doc = soup.find("div", class_="doc").attrs["onclick"].replace("select(this.id, '", "").replace("')", "")

        self.verifica_sap("wnd[1]/usr/cntlCC_ATTACH_BARR/shellcont/shell").sapEvent("", "",
                                                                                   f"sapevent:BARZREAD|{id_doc}")
        time.sleep(2)
        soup = BeautifulSoup(self.verifica_sap("wnd[1]/usr/subSS_OBJ_BARR:/ITSSAUTO/SAPLFG0013:0012/cntlCC_OBJ_HTML"
                                              "/shellcont/shell").BrowserHandle.Document.body.innerHTML, "lxml")

        barcode = soup.find("input", attrs={'name': 'barcode'})
        if barcode:
            barcode = barcode.get('id')
            check_box = soup.findAll("input", attrs={'type': 'checkbox'})
            for checks in check_box:
                check = '&' + checks.get("id") + '=' + checks.get("value")
            time.sleep(1)

            self.verifica_sap(
                "wnd[1]/usr/subSS_OBJ_BARR:/ITSSAUTO/SAPLFG0013:0012/cntlCC_OBJ_HTML/shellcont/shell").\
                sapEvent("", f"barcode={barcode}{check}", "sapevent:ZBARCODE_LIST")
            time.sleep(1)
            if self.verifica_sap("wnd[2]/tbar[0]/btn[0]"):
                self.verifica_sap("wnd[2]/tbar[0]/btn[0]").press()
        else:
            print('A guia não tem codigo de barras.')
        self.verifica_sap("wnd[1]").close()

    def selecionar_tipo_pedido(self, tipo):
        if self.verifica_sap("wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105"
                            "/txtMEPO_TOPLINE-EBELN").text != '':
            self.verifica_sap("wnd[0]/mbar/menu[0]/menu[1]").select()
        self.verifica_sap(
            "wnd[0]/usr/subSUB0:SAPLMEGUI:0013/subSUB0:SAPLMEGUI:0030/subSUB1:SAPLMEGUI:1105/cmbMEPO_TOPLINE"
            "-BSART").key = f"{tipo}"

    ##########################################

    def get_element_id_by_text(self, text):
        if self.session:
            element = self.session.findById("wnd[0]")
            element_id = self._find_element_by_text(element, text)
            return element_id

    def _find_element_by_text(self, element, text):
        try:
            if element.Text == text:
                return element.ID
            elif element.Children:
                for child in element.Children:
                    element_id = self._find_element_by_text(child, text)
                    if element_id:
                        return element_id
        except Exception as e:
            print('')

    def get_screen_fields(self):
        fields_dict = {
            "input_fields": [],
            "button_fields": [],
            "label_fields": [],
            "other_fields": []
        }

        if self.session:
            element = self.session.findById("wnd[0]")
            self._process_screen_element(element, fields_dict)

        return fields_dict

    def _process_screen_element(self, element, fields_dict):
        element_type = element.Type

        if element_type == "GuiTextField" or element_type == "GuiCTextField":
            field_info = {
                "element_text": element.text,
                "element_name": element.Name,
                "element_id": element.ID,
                "element_type": element.Type
            }
            fields_dict["input_fields"].append(field_info)

        elif element_type == "GuiButton":
            field_info = {
                "element_text": element.text,
                "element_name": element.Name,
                "element_id": element.ID,
                "element_functions": element.Type
            }
            fields_dict["button_fields"].append(field_info)

        elif element_type == "GuiLabel":
            field_info = {
                "element_text": element.text,
                "element_name": element.Name,
                "element_id": element.ID,
                "element_functions": element.Type
            }
            fields_dict["label_fields"].append(field_info)

        else:
            field_info = {
                "element_text": element.text,
                "element_name": element.Name,
                "element_id": element.ID,
                "element_functions": element.Type
            }
            fields_dict["other_fields"].append(field_info)
        try:
            if element.Children:
                for child in element.Children:
                    self._process_screen_element(child, fields_dict)
        except Exception as e:
            print(traceback.print_exc())


    def buscar_comprovante(self):
        try:
            self.verifica_sap("wnd[0]/shellcont/shell").pressButton("VIEW_ATTA")
            self.buscar_boy()
            self.verifica_sap("wnd[1]/tbar[0]/btn[0]").press()
            self.verifica_sap("wnd[0]/shellcont").close()
            self.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()
        except Exception as e:
            self.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()
            print("AAAAAAAAAAAAAA => ", e)
        

    def voltar_menu_principal(self):
        self.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()
        self.verifica_sap("wnd[0]/tbar[0]/btn[3]").press()

    def buscar_boy(self):
        tamanho_tabela = self.verifica_sap("wnd[1]/usr/cntlCONTAINER_0100/shellcont/shell").RowCount
        linha = 0
        while linha < tamanho_tabela:
            try:

                if self.verifica_sap("wnd[1]/usr/cntlCONTAINER_0100/shellcont/shell").GetCellValue(linha,'CREATOR'):
                    txt = self.verifica_sap("wnd[1]/usr/cntlCONTAINER_0100/shellcont/shell").GetCellValue(linha,'CREATOR')
                    print("Nome ==> ", txt)
                linha = linha + 1
            except Exception as e:
                print("AAAAA ===> ", e)


