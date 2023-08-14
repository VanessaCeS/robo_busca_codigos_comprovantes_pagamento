from funcoes_arteria import search

search_xml = """<SearchReport id="15461" name="REL_BUSCADOCCOMPENSACAO">
  <DisplayFields>
    <DisplayField>20324</DisplayField>
    <DisplayField>15991</DisplayField>
    <DisplayField>18983</DisplayField>
    <DisplayField>20634</DisplayField>
    <DisplayField>16049</DisplayField>
    <DisplayField>16036</DisplayField>
    <DisplayField>20411</DisplayField>
    <DisplayField>20420</DisplayField>
    <DisplayField>18677</DisplayField>
    <DisplayField>18676</DisplayField>
    <DisplayField>16040</DisplayField>
    <DisplayField>25763</DisplayField>
    <DisplayField>25056</DisplayField>
    <DisplayField>20560</DisplayField>
    <DisplayField>17933</DisplayField>
    <DisplayField>21399</DisplayField>
    <DisplayField>18982</DisplayField>
  </DisplayFields>
  <PageSize>1250</PageSize>
  <IsResultLimitPercent>False</IsResultLimitPercent>
  <Criteria>
    <Keywords />
    <Filter>
      <OperatorLogic>1 AND 2 AND ((3 AND 6) OR (4 AND 5)) AND (7 OR 8) </OperatorLogic>
      <Conditions>
        <ReferenceFilterCondition>
          <Field>15951</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>True</IsNoSelectionIncluded>
        </ReferenceFilterCondition>
        <ValueListFilterCondition>
          <Field>18979</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value>83246</Value>
          </Values>
        </ValueListFilterCondition>
        <ValueListFilterCondition>
          <Field>16011</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value>70714</Value>
          </Values>
        </ValueListFilterCondition>
        <ValueListFilterCondition>
          <Field>16011</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value>70713</Value>
          </Values>
        </ValueListFilterCondition>
        <ValueListFilterCondition>
          <Field>15994</Field>
          <Operator>Contains</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value>91009</Value>
          </Values>
        </ValueListFilterCondition>
        <ValueListFilterCondition>
          <Field>15994</Field>
          <Operator>DoesNotContain</Operator>
          <IsNoSelectionIncluded>False</IsNoSelectionIncluded>
          <IncludeChildren>False</IncludeChildren>
          <Values>
            <Value>66596</Value>
          </Values>
        </ValueListFilterCondition>
        <CurrentDateFilterCondition>
          <Field>20634</Field>
          <Operator>PriorToToday</Operator>
        </CurrentDateFilterCondition>
        <CurrentDateFilterCondition>
          <Field>20634</Field>
          <Operator>CurrentDay</Operator>
        </CurrentDateFilterCondition>
      </Conditions>
    </Filter>
    <ModuleCriteria>
      <Module>445</Module>
      <IsKeywordModule>True</IsKeywordModule>
      <BuildoutRelationship>Union</BuildoutRelationship>
      <SortFields>
        <SortField>
          <Field>15991</Field>
          <SortType>Ascending</SortType>
        </SortField>
      </SortFields>
    </ModuleCriteria>
  </Criteria>
</SearchReport>"""

def get_dados_pagamentos_codigo_comprovantes(search_xml):
    dados = search(search_xml, page=1, quantidade=False)
    ids = []
    for i in range(len(dados)):
        ids.append(dados[i]['ID da Aplicação - Pagamento'])
    return dados

# get_dados_pagamentos_codigo_comprovantes(search_xml)
# print(a)