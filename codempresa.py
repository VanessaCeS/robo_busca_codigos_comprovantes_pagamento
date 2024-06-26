
cod_empresa = {
    "CAIXA SEGURADORA S/A": "C000",
    "CAIXA VIDA E PREVIDÊNCIA S/A": "C010",
    "CAIXA CAPITALIZAÇÃO S/A": "C020",
    "CAIXA CAPITALIZAÇÃO": "C020",
    "CAIXA CONSÓRCIOS S/A": "C060",
    "CAIXA CONSORCIOS S/A": "C060",
    'CNP CONSÓRCIOS S.A. ADMINISTRADORA DE CONSÓRCIOS': 'C060',
    "CAIXA CONSÓRCIOS S/A - ADMINISTRADORA DE CONSÓRCIOS": "C060",
    "CAIXA SEGURADORA ESPECIALIZADA EM SAÚDE": "C080",
    "CAIXA SEGURADORA ESPECIALIZADA EM SAÚDE S/A": "C080",
    "CAIXA ESPECIALIZADA EM SAÚDE": "C080",
    "XS2 VIDA & PREVIDENCIA S/A": "D011"
}

def pegar_cod_empresa(nome_empresa):
    if nome_empresa:
        for nome in dict.keys(cod_empresa):
            if nome_empresa[0] == nome:
                return  cod_empresa[nome]


def get_empresa_responsavel(ramo, produto):
    if ramo in {'5 - CAIXA CAP'}:
        return 'CAIXA CAPITALIZAÇÃO S/A'
    if ramo in {'4 - CAIXA CONSORCIOS S/A'}:
        return 'CAIXA CONSORCIOS S/A'
    if ramo in {'7 - CAIXA SAÚDE S.A'}:
        # return 'CAIXA SEGURADORA ESPECIALIZADA EM SAÚDE'
        return 'CAIXA ESPECIALIZADA EM SAÚDE'
    if ramo in {
                            '0 - AGUARDANDO CADASTRO',
                            '0 - SEM RAMO',
                            '14 - COMPREENSIVO RESIDENCI',
                            '166 - AÇÕES RESSARCIMENTO',
                            '18 - COMPREENSIVO EMPRESARI',
                            '21 - TRANSPORTES NACIONAIS',
                            '22 - TRANSPORTES INTERNACIONAIS',
                            '27 - RURAL',
                            '31 - AUTOMOVEIS',
                            '40 - GARANTIA DE OBRIGAÇÕES',
                            '41 - LUCROS CESSANTES',
                            '42 - ASSISTENCIA AUTO',
                            '45 - GARANTIA PUBLICA - COH',
                            '48 - CREDITO INTERNO',
                            '51 - RESPONSABILIDADE GERAL',
                            '53 - RESPONSABILID.CIVIL VEICULOS',
                            '6 - SUSEP PREVHAB',
                            '60 - CREDITO DOMESTICO',
                            '61 - FORA SFH MIP',
                            '65 - FORA SFH DFI',
                            '66 - HABITACIONAL',
                            '67 - RISCOS DE ENGENHARIA',
                            '68 - FORA SFH',
                            '6899 - NÃO LOCALIZADO',
                            '70 - CREDITO DOMESTICO RISC',
                            '71 - RISCOS DIVERSOS',
                            '72 - BILHETE RESIDENCIAL',
                            '73 - GLOBAL DE BANCOS/JOIAS PENHOR.',
                            '75 - SEGURO GARANTIA',
                            '76 - RISCOS FINANCEIROS',
                            '88 - DPVAT',
                            '9 - VERA CRUZ',
                            '99 - DIVERSOS'}:
        return 'CAIXA SEGURADORA S/A'
    if ramo in {'198 - PREVHAB - Não Oficial', '16 - COMPREENSIVO CONDOMINI'}:
        return 'CAIXA SEGURADORA S/A'
    if ramo in {
                            '69 - VIAGEM',
                            '2 - PREVHAB',
                            '20 - ACIDENTES PESSOAIS PAS',
                            '3 - CAIXA VIDA E PREVIDENC',
                            '37 - MICROSSEGUROS PESSOAS',
                            '77 - PRESTAMISTA',
                            '80 - ACIDENTES PESSOAIS',
                            '81 - ACIDENTES PESSOAIS INDIVIDUAL',
                            '82 - ACIDENTES PESSOAIS COLETIVO',
                            '91 - VIDA',
                            '91 - VIDA INDIVIDUAL',
                            '93 - VIDA EM GRUPO',
                            '97 - VG/APC',
                            '98 - PRESTAMISTA - VIDA DO PRODUTOR RURAL'}:
        if produto.split(" - ")[0] in {
                                                    '3721',
                                                    '3722',
                                                    '3723',
                                                    '3724',
                                                    '3725',
                                                    '6931',
                                                    '6932',
                                                    '6933',
                                                    '6934',
                                                    '6935',
                                                    '6936',
                                                    '6937',
                                                    '6938',
                                                    '6939',
                                                    '6940',
                                                    '6941',
                                                    '6942',
                                                    '6943',
                                                    '6944',
                                                    '6945',
                                                    '6946',
                                                    '7761',
                                                    '7768',
                                                    '7771',
                                                    '7762',
                                                    '7742',
                                                    '7765',
                                                    '7766',
                                                    '7763',
                                                    '7743',
                                                    '7745',
                                                    '7746',
                                                    '7769',
                                                    '7741',
                                                    '7770',
                                                    '8519',
                                                    '8516',
                                                    '8517',
                                                    '8520',
                                                    '8518',
                                                    '8513',
                                                    '8511',
                                                    '8512',
                                                    '8514',
                                                    '8515',
                                                    '8521',
                                                    '8526',
                                                    '8524',
                                                    '8525',
                                                    '8527',
                                                    '8523',
                                                    '8522',
                                                    '8246',
                                                    '8241',
                                                    '8247',
                                                    '8242',
                                                    '8248',
                                                    '9749',
                                                    '9386',
                                                    '9729',
                                                    '9741',
                                                    '9742',
                                                    '9731',
                                                    '9732',
                                                    '9381',
                                                    '9387',
                                                    '9743',
                                                    '9733',
                                                    '9382',
                                                    '9723',
                                                    '9722',
                                                    '9721',
                                                    '9735',
                                                    '9736',
                                                    '9737',
                                                    '9745',
                                                    '9746',
                                                    '9747',
                                                    '9821',
                                                    '9811'}:
            return 'XS2 VIDA & PREVIDENCIA S/A'
        else:
            return 'CAIXA VIDA E PREVIDÊNCIA S/A'
        
pegar_cod_empresa("CAIXA VIDA E PREVIDÊNCIA S/A")