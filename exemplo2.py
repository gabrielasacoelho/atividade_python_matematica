import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
import matplotlib as plt


# Configuração da página
st.set_page_config(page_title="Ensino Superior", layout="wide", page_icon="🎓")


def carregar_dados(path):
    formacao_bruto = pd.read_excel(path, header=None)
    
    #somente configuração de planilha
    formacao_total = formacao_bruto.iloc[3:36, 0:10].copy()


    # tudo que precisa conter dentro da lista 
    formacao_total.columns = [
        "Localidade",
        "Total_Geral",
        "Homens_Geral",
        "Mulheres_Geral",
        "Total_CTEM",
        "Homens_CTEM",
        "Mulheres_CTEM",
        "Total_Educacao_Saude",
        "Homens_Educacao_Saude",
        "Mulheres_Educacao_Saude"
    ]
    
    # Tira espaços extra dos nome de estados e regiões
    formacao_total["Localidade"] = formacao_total["Localidade"].astype(str).str.strip()


    # faz com que os valores sejam transformados Int
    colunas_numericas = formacao_total.columns.drop("Localidade")
    for coluna in colunas_numericas:
        formacao_total[coluna] = pd.to_numeric(formacao_total[coluna], errors="coerce")


    # Retorna a tabela pra ser usada no resto do código
    return formacao_total
path = "Tabela_3_Areas_gerais_de_formacao_na_graduacao (2).xlsx"    


    
# mostra uma mensagem explicando que erro esta acontecendo para facilitar 
try:
    df = carregar_dados(path)


except Exception as erro:
    st.error(
        "Confira se a planilha está na mesma pasta do arquivo .py e se o nome está escrito certo."
    )


regioes = [
    "Norte",
    "Nordeste",
    "Sudeste",
    "Sul",
    "Centro-Oeste"
]


# Cria uma lista que tem os nomes dos estados, pra isso tira da planilha Brasil e regiões
localidades_nEstados = ["Brasil"] + regioes


estados = sorted([localidade
        for localidade in df["Localidade"].unique()
        if localidade not in localidades_nEstados
    ])




#titulo
st.title("🎓 Ensino Superior no Brasil")


st.write(
    "Este painel apresenta dados sobre pessoas que já concluíram "
    "o ensino superior. É possível comparar estados, regiões, áreas "
    "de formação e a distribuição entre homens e mulheres."
)


st.caption(
    "Fonte: Tabela 10063 do IBGE, conforme a planilha disponibilizada "
    "para o projeto. A planilha não informa uma série de anos."
)








st.sidebar.header("🔎 Filtros")


#escolhe Brasil uma região ou um estado
opcoes_localidade = ["Brasil"] + regioes + estados


localidade_escolhida = st.sidebar.selectbox(
    "Estado ou região",
    opcoes_localidade,
    index=0
)


# escolhe a área de formação
opcoes_area = [
    "Todas as áreas",
    "CTEM",
    "ESPSB"
]


area_escolhida = st.sidebar.selectbox(
    "Área de formação",
    opcoes_area
)


# seleciona o sexo usado, o gráfico de comparação mostrando homens e mulheres, a diferença entre os dois grupos 
sexo_escolhido = st.sidebar.selectbox(
    "Sexo para os indicadores",
    ["Todos", "Homens", "Mulheres"]
)


# Procuramos a localidade escolhida no filtro.
# Como cada estado/região aparece em uma linha, usamos essa linha.
linha_localidade = df[df["Localidade"] == localidade_escolhida]


# Essa verificação evita erros caso o nome selecionado não exista.
if linha_localidade.empty:
    st.error("Não encontrei os dados dessa localidade na planilha.")
    st.stop()


# Pegamos a primeira linha encontrada e transformamos em uma série.
dados_localidade = linha_localidade.iloc[0]


#numeros da area escolhida
# pegamos os números gerais, que representam todas os locais
total_area = dados_localidade["Total_Geral"]
homens_area = dados_localidade["Homens_Geral"]
mulheres_area = dados_localidade["Mulheres_Geral"]


# se a pessoa escolher CTEM, nos vamos trocar os números pelos dados de CTEM
#CTEM = Ciência, Tecnologia, Engenharias e Matemática 
if area_escolhida == "CTEM":
    total_area = dados_localidade["Total_CTEM"]
    homens_area = dados_localidade["Homens_CTEM"]
    mulheres_area = dados_localidade["Mulheres_CTEM"]


# se a pessoa escolher ESPSB nos vamos usar as três colunas correspondentes da planilha
elif area_escolhida == "ESPSB":
    total_area = dados_localidade["Total_Educacao_Saude"]
    homens_area = dados_localidade["Homens_Educacao_Saude"]
    mulheres_area = dados_localidade["Mulheres_Educacao_Saude"]


    
    
if total_area and total_area > 0:
    percentual_mulheres = (mulheres_area / total_area) * 100
    percentual_homens = (homens_area / total_area) * 100
else:
    percentual_mulheres = 0
    percentual_homens = 0


#total de homens e mulheres  na area 
if sexo_escolhido == "Homens":
    total_sexo = homens_area
elif sexo_escolhido == "Mulheres":
    total_sexo = mulheres_area
else:
    total_sexo = total_area


    st.subheader(f"Indicadores — {localidade_escolhida}")


# dividimos a linha em três espaços para deixar os números organizados
coluna1, coluna2, coluna3 = st.columns(3)


#metric = Métricas de Machine Learning (Avaliação de Modelos) foi usado no exemplo de apoio e na atividade do supermercado
with coluna1:
    st.metric(label=f"Pessoas — {sexo_escolhido}", value=f"{total_sexo:,.0f}".replace(",", "."))
with coluna2:
    st.metric(label="Participação de mulheres", value=f"{percentual_mulheres:.1f}%")


with coluna3:
    st.metric(label="Participação de homens", value=f"{percentual_homens:.1f}%")


    
# Organiza os valores em uma tabela menor. Cada linha é uma área e cada coluna é um sexo
dados_grafico = pd.DataFrame({
    "Área de formação": [
        "Total geral",
        "CTEM",
        "ESPSB"
    ],
    "Homens": [
        dados_localidade["Homens_Geral"],
        dados_localidade["Homens_CTEM"],
        dados_localidade["Homens_Educacao_Saude"]
    ],
    "Mulheres": [
        dados_localidade["Mulheres_Geral"],
        dados_localidade["Mulheres_CTEM"],
        dados_localidade["Mulheres_Educacao_Saude"]
    ]
})


# O formato longo do df facilita a criação de barras empilhadas(melt)
dados_grafico = dados_grafico.melt(
    id_vars="Área de formação",
    var_name="Sexo",
    value_name="Quantidade"
)


# Para cada área calculamos a porcentagem de homens e mulheres. Assim cada barra representa o total daquela área
totais_por_area = dados_grafico.groupby("Área de formação")["Quantidade"].transform("sum")


dados_grafico["Percentual"] = (dados_grafico["Quantidade"] / totais_por_area) * 100




# Se uma área específica for escolhida o gráfico mostra só ela. Se "Todas as áreas" for escolhida aparece as três categorias
if area_escolhida == "CTEM":
    dados_grafico = dados_grafico[
        dados_grafico["Área de formação"] == "CTEM"
    ]


elif area_escolhida == "ESPSB":
    dados_grafico = dados_grafico[
        dados_grafico["Área de formação"] == "ESPSB"
    ]




st.subheader("Distribuição por sexo em cada área de formação")


st.write(
    "Cada barra representa o total das pessoas daquela categoria. "
    "As partes da barra mostram a participação de homens e mulheres."
)


# Criamos o gráfico de barras empilhadas.
grafico = px.bar(
    dados_grafico,
    x = "Área de formação",
    y = "Percentual",
    color = "Sexo",
    text = dados_grafico["Percentual"].round(1).astype(str) + "%",
    barmode = "stack",
    labels = {"Área de formação": "Área de formação","Percentual": "Participação (%)","Sexo": "Sexo"},
    title = "Participação de homens e mulheres"
)


# Ajusta o eixo X para ir de 0% a 100%
grafico.update_layout(
    yaxis=dict(range=[0, 100]),  # eixo Y
    legend_title="Sexo",         
    xaxis_title="",              # eixo X
    yaxis_title="Participação"  
)


st.plotly_chart(grafico, use_container_width=True)





# Monta uma tabela simples para que os números também sejam consultados sem depender do gráfico
tabela_detalhada = pd.DataFrame({
    "Área de formação": [
        "Total geral",
        "CTEM",
        "Educação, serviços pessoais, saúde e bem-estar"
    ],
    "Total de pessoas": [
        dados_localidade["Total_Geral"],
        dados_localidade["Total_CTEM"],
        dados_localidade["Total_Educacao_Saude"]
    ],
    "Homens": [
        dados_localidade["Homens_Geral"],
        dados_localidade["Homens_CTEM"],
        dados_localidade["Homens_Educacao_Saude"]
    ],
    "Mulheres": [
        dados_localidade["Mulheres_Geral"],
        dados_localidade["Mulheres_CTEM"],
        dados_localidade["Mulheres_Educacao_Saude"]
    ]
})


# Aplicamos o filtro de área também na tabela.
if area_escolhida == "CTEM":
    tabela_detalhada = tabela_detalhada[
        tabela_detalhada["Área de formação"] == "CTEM"
    ]


elif area_escolhida == "Educação, serviços pessoais, saúde e bem-estar":
    tabela_detalhada = tabela_detalhada[
        tabela_detalhada["Área de formação"]
        == "Educação, serviços pessoais, saúde e bem-estar"
    ]




import plotly.graph_objects as go


st.divider()
st.header("Pesquisas complementares")
st.caption(
    "Os gráficos desta parte mudam com os filtros da barra lateral: Estado ou região, Área de formação, "
    "Sexo e Ano. A planilha é do Censo 2022; os anos de 2000 e 2010 valem só para a taxa histórica (pergunta 2)."
)


# Filtro novo (a planilha não tem anos, então ele só atua na pergunta 2)
st.sidebar.divider()
ano_escolhido = st.sidebar.selectbox(
    "Ano (Censo)",
    ["Todos", 2000, 2010, 2022],
    help="A planilha é do Censo 2022. 2000 e 2010 aparecem só na taxa histórica da pergunta 2."
)


# ---------------------------------------------------------------------
# Dados da planilha, lidos por inteiro
# ---------------------------------------------------------------------
# A função carregar_dados() acima fatia a planilha em linhas fixas (iloc[3:36]); aqui lemos todas as
# linhas e ficamos só com as que têm números (assim entram os 27 estados, inclusive Acre e Alagoas).
def carregar_dados_completos(caminho):
    bruto = pd.read_excel(caminho, header=None).iloc[:, 0:10].copy()
    bruto.columns = [
        "Localidade", "Total_Geral", "Homens_Geral", "Mulheres_Geral",
        "Total_CTEM", "Homens_CTEM", "Mulheres_CTEM",
        "Total_Educacao_Saude", "Homens_Educacao_Saude", "Mulheres_Educacao_Saude"
    ]
    for coluna in bruto.columns.drop("Localidade"):
        bruto[coluna] = pd.to_numeric(bruto[coluna], errors="coerce")
    bruto = bruto.dropna(subset=["Total_Geral"]).copy()   # descarta título, cabeçalhos e rodapé
    bruto["Localidade"] = bruto["Localidade"].astype(str).str.strip()
    return bruto


df_completo = carregar_dados_completos(path)
df_estados = df_completo[~df_completo["Localidade"].isin(["Brasil"] + regioes)].copy()


# Colunas da planilha para cada área e sexo
colunas_area = {
    "Total geral": {"Homens": "Homens_Geral", "Mulheres": "Mulheres_Geral", "Total": "Total_Geral"},
    "CTEM": {"Homens": "Homens_CTEM", "Mulheres": "Mulheres_CTEM", "Total": "Total_CTEM"},
    "ESPSB": {"Homens": "Homens_Educacao_Saude", "Mulheres": "Mulheres_Educacao_Saude", "Total": "Total_Educacao_Saude"},
}
area_chave = "Total geral" if area_escolhida == "Todas as áreas" else area_escolhida
sexo_chave = "Total" if sexo_escolhido == "Todos" else sexo_escolhido      # coluna usada com o filtro de sexo


estados_sudeste = ["Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo"]
estados_por_regiao = {
    "Norte": ["Acre", "Amapá", "Amazonas", "Pará", "Rondônia", "Roraima", "Tocantins"],
    "Nordeste": ["Alagoas", "Bahia", "Ceará", "Maranhão", "Paraíba", "Pernambuco", "Piauí", "Rio Grande do Norte", "Sergipe"],
    "Sudeste": estados_sudeste,
    "Sul": ["Paraná", "Rio Grande do Sul", "Santa Catarina"],
    "Centro-Oeste": ["Distrito Federal", "Goiás", "Mato Grosso", "Mato Grosso do Sul"],
}


# Quais estados entram nos gráficos conforme o filtro "Estado ou região":
#  Brasil -> os 27 estados | região -> os estados dela | estado -> os estados da região dele
def escopo_estados(local):
    if local == "Brasil":
        return list(df_estados["Localidade"]), "todos os estados"
    if local in regioes:
        return estados_por_regiao[local], f"estados do {local}"
    regiao_do_estado = [r for r, lista in estados_por_regiao.items() if local in lista][0]
    return estados_por_regiao[regiao_do_estado], f"estados do {regiao_do_estado} (destaque: {local})"


def numero_br(v):
    return f"{v:g}".replace(".", ",")




st.subheader("1) Como a população com nível superior está distribuída nos estados do Sudeste?")


coluna_q1 = colunas_area[area_chave][sexo_chave]


df_sudeste = df_completo[df_completo["Localidade"].isin(estados_sudeste)][["Localidade", coluna_q1]].copy()
df_sudeste.columns = ["Estado", "Pessoas"]
df_sudeste["Percentual do Sudeste"] = df_sudeste["Pessoas"] / df_sudeste["Pessoas"].sum() * 100
df_sudeste["Destaque"] = df_sudeste["Estado"].apply(
    lambda e: "Selecionado" if (e == localidade_escolhida or localidade_escolhida == "Sudeste") else "Demais"
)
df_sudeste = df_sudeste.sort_values("Pessoas", ascending=False)


total_sudeste = df_sudeste["Pessoas"].sum()
total_brasil_q1 = df_completo.loc[df_completo["Localidade"] == "Brasil", coluna_q1].iloc[0]


coluna_a, coluna_b = st.columns([3, 2])
with coluna_a:
    grafico_sudeste = px.bar(
        df_sudeste,
        x="Estado",
        y="Pessoas",
        color="Destaque",
        color_discrete_map={"Selecionado": "#e4572e", "Demais": "#6baed6"},
        text=df_sudeste["Percentual do Sudeste"].round(1).astype(str) + "%",
        title=f"Pessoas com nível superior no Sudeste — {area_escolhida} — {sexo_escolhido}"
    )
    grafico_sudeste.update_layout(xaxis_title="", yaxis_title="Pessoas", legend_title="")
    st.plotly_chart(grafico_sudeste, use_container_width=True)





# ---------------------------------------------------------------------
# PESQUISA 2 (por código): evolução histórica da taxa
# Muda com: Estado ou região e Ano (e os números da planilha mudam com Área e Sexo)
# ---------------------------------------------------------------------
st.subheader("2) Qual a evolução histórica dessa taxa nos estados e no total consolidado?")


# A planilha do projeto não tem anos, então esta resposta usa números publicados pelo IBGE
# (Censo Demográfico): % da população de 25 anos ou mais com ensino superior completo.
# 2022 existe para o Brasil, as regiões e todos os estados. 2000 e 2010 só foram encontrados para alguns.
taxa_por_ano = {
    2000: {"Brasil": 6.8, "Pará": 3.3, "Paraíba": 5.3, "Maranhão": 1.9},
    2010: {"Brasil": 11.3, "Pará": 6.2, "Paraná": 12.75},
    2022: {
        "Brasil": 18.4,
        "Norte": 14.4, "Nordeste": 13.0, "Sudeste": 21.0, "Sul": 20.2, "Centro-Oeste": 21.8,
        "Distrito Federal": 37.0, "São Paulo": 23.3, "Santa Catarina": 21.4, "Amapá": 20.9, "Paraná": 20.7,
        "Mato Grosso do Sul": 19.8, "Rio de Janeiro": 19.6, "Roraima": 19.0, "Rio Grande do Sul": 18.8,
        "Mato Grosso": 18.6, "Espírito Santo": 18.2, "Tocantins": 18.1, "Goiás": 18.0, "Minas Gerais": 17.8,
        "Acre": 17.3, "Rondônia": 15.6, "Rio Grande do Norte": 15.1, "Amazonas": 15.0, "Sergipe": 14.9,
        "Paraíba": 14.5, "Pernambuco": 14.0, "Piauí": 13.9, "Alagoas": 13.4, "Ceará": 12.7,
        "Bahia": 12.0, "Pará": 12.0, "Maranhão": 11.1,
    },
}


def serie_da_localidade(nome):
    return {a: tabela[nome] for a, tabela in taxa_por_ano.items() if nome in tabela}


ano_referencia = 2022 if ano_escolhido == "Todos" else ano_escolhido
valor_local = taxa_por_ano[ano_referencia].get(localidade_escolhida)
valor_brasil = taxa_por_ano[ano_referencia]["Brasil"]


# ----- texto da resposta -----
if ano_escolhido == "Todos":
    if localidade_escolhida == "Brasil":
        texto_resposta = (
            "**Resposta (Brasil):** a taxa de pessoas com 25 anos ou mais com ensino superior completo quase triplicou: "
            "foi de **6,8% em 2000** para **11,3% em 2010** e **18,4% em 2022**."
        )
    else:
        serie_escolhida = serie_da_localidade(localidade_escolhida)
        pontos_txt = ", ".join(f"{numero_br(serie_escolhida[a])}% em {a}" for a in sorted(serie_escolhida))
        texto_resposta = f"**Resposta ({localidade_escolhida}):** a taxa foi de {pontos_txt}."
        if len(serie_escolhida) == 1:
            texto_resposta += " Não encontrei os números de 2000 e 2010 para este recorte, por isso só há o ponto de 2022."
        texto_resposta += f" Em 2022 ficou {'acima' if valor_local > 18.4 else 'abaixo'} da média do Brasil (18,4%)."
else:
    if valor_local is None:
        texto_resposta = (f"**Resposta ({localidade_escolhida}, {ano_escolhido}):** não encontrei a taxa deste recorte "
                          f"para {ano_escolhido}. O Brasil tinha {numero_br(valor_brasil)}% nesse ano.")
    else:
        texto_resposta = (f"**Resposta ({localidade_escolhida}, {ano_escolhido}):** a taxa era de {numero_br(valor_local)}% "
                          f"(Brasil: {numero_br(valor_brasil)}%).")
st.write(texto_resposta)


# ----- números que mudam com os filtros -----
# total_sexo e percentual_mulheres vêm do código principal, já calculados com Estado, Área e Sexo
coluna_m1, coluna_m2, coluna_m3 = st.columns(3)
with coluna_m1:
    if valor_local is not None:
        delta_txt = None
        if localidade_escolhida != "Brasil":
            diferenca = valor_local - valor_brasil
            delta_txt = ("+" if diferenca >= 0 else "-") + f"{abs(diferenca):.1f}".replace(".", ",") + " p.p. em relação ao Brasil"
        st.metric(f"Taxa em {ano_referencia} — {localidade_escolhida}", f"{valor_local:.1f}%".replace(".", ","), delta=delta_txt)
    else:
        st.metric(f"Taxa em {ano_referencia} — {localidade_escolhida}", "sem dado")
with coluna_m2:
    st.metric(f"Pessoas — {area_escolhida}, {sexo_escolhido} (planilha)", f"{total_sexo:,.0f}".replace(",", "."))
with coluna_m3:
    st.metric(f"Participação de mulheres — {area_escolhida}", f"{percentual_mulheres:.1f}%")


# ----- gráfico de linhas: Brasil x localidade escolhida -----
linhas_evolucao = []
for nome in dict.fromkeys(["Brasil", localidade_escolhida]):
    for ano_ponto, valor_ponto in serie_da_localidade(nome).items():
        linhas_evolucao.append((nome, ano_ponto, valor_ponto))
evolucao = pd.DataFrame(linhas_evolucao, columns=["Localidade", "Ano", "Taxa (%)"])


grafico_evolucao = px.line(
    evolucao, x="Ano", y="Taxa (%)", color="Localidade", markers=True,
    title=f"Evolução da taxa de ensino superior completo — {localidade_escolhida} x Brasil"
)
grafico_evolucao.update_layout(xaxis=dict(tickmode="array", tickvals=[2000, 2010, 2022]), yaxis_title="% da população de 25 anos ou mais")
if ano_escolhido != "Todos":
    grafico_evolucao.add_vline(x=ano_escolhido, line_dash="dash", line_color="#e4572e", annotation_text=str(ano_escolhido))
st.plotly_chart(grafico_evolucao, use_container_width=True)


# ----- ranking do ano escolhido (2022 quando o ano está em "Todos") -----
nomes_ranking = [n for n in taxa_por_ano[ano_referencia] if n not in regioes]
if localidade_escolhida in regioes and localidade_escolhida in taxa_por_ano[ano_referencia]:
    nomes_ranking.append(localidade_escolhida)
ranking = pd.DataFrame({
    "Localidade": nomes_ranking,
    "Taxa (%)": [taxa_por_ano[ano_referencia][n] for n in nomes_ranking]
})
ranking["Destaque"] = ranking["Localidade"].apply(
    lambda n: "Selecionado" if n == localidade_escolhida else ("Brasil" if n == "Brasil" else "Demais")
)
ranking = ranking.sort_values("Taxa (%)", ascending=False)


grafico_ranking = px.bar(
    ranking, x="Localidade", y="Taxa (%)", color="Destaque",
    color_discrete_map={"Selecionado": "#e4572e", "Brasil": "#f2c14e", "Demais": "#6baed6"},
    text="Taxa (%)", title=f"Taxa de ensino superior completo em {ano_referencia} (25 anos ou mais)"
)
grafico_ranking.update_layout(xaxis_title="", yaxis_title="%", legend_title="")
st.plotly_chart(grafico_ranking, use_container_width=True)


st.caption(
    "Fonte: Censo Demográfico 2000, 2010 e 2022 (IBGE), conforme divulgado pela imprensa e por órgãos estaduais. "
    "A curva e o ranking valem para todas as pessoas (não existe versão histórica por área ou sexo); "
    "os três números acima vêm da planilha e mudam com os filtros de Estado, Área e Sexo."
)




# ---------------------------------------------------------------------
# PESQUISA 3 (EM FOTO): % de mulheres em Exatas x Humanas
# Muda com: Estado ou região, Área de formação e Sexo
# ---------------------------------------------------------------------
st.subheader("3) Percentual de mulheres em cursos de Exatas versus Humanas (por estado e no total)")


sexo_foto = "Homens" if sexo_escolhido == "Homens" else "Mulheres"      # com "Todos", a pergunta é sobre mulheres
areas_foto = ["CTEM", "ESPSB"] if area_escolhida == "Todas as áreas" else [area_escolhida]
estados_foto, escopo_foto = escopo_estados(localidade_escolhida)


st.write(
    f"A imagem mostra o percentual de **{sexo_foto.lower()}** entre as pessoas formadas em "
    "**Exatas (CTEM)** e **Humanas/Saúde (ESPSB: educação, serviços pessoais, saúde e bem-estar)** — "
    f"{escopo_foto}. As linhas tracejadas marcam o valor de "
    f"{localidade_escolhida if (localidade_escolhida in ['Brasil'] + regioes) else 'Brasil'}."
)


# A "foto" (imagem PNG) é gerada aqui mesmo, com matplotlib, e guardada na memória (não precisa de arquivo).
def gerar_foto_pesquisa(dados, areas, sexo, ref_nome, ref_valores, destaque, escopo):
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt


    cores = {"CTEM": "#2b6cb0", "ESPSB": "#d9822b", "Total geral": "#6b7280"}
    rotulos = {"CTEM": "Exatas (CTEM)", "ESPSB": "Humanas/Saúde (ESPSB)", "Total geral": "Total geral"}


    est = dados.sort_values("pct_" + areas[0])
    n = len(est)
    k = len(areas)
    h = 0.8 / k
    fig, ax = plt.subplots(figsize=(10, max(4.5, 0.35 * n * k + 2.5)), dpi=130)


    for j, area in enumerate(areas):
        posicoes = [i - 0.4 + h * (j + 0.5) for i in range(n)]
        valores = est["pct_" + area]
        ax.barh(posicoes, valores, h, label=rotulos[area], color=cores[area])
        for p, v in zip(posicoes, valores):
            ax.text(v + 0.5, p, f"{v:.1f}%", va="center", fontsize=7)
        ax.axvline(ref_valores[area], color=cores[area], ls="--", lw=1)


    ax.set_yticks(list(range(n)))
    ax.set_yticklabels(est["Localidade"], fontsize=8)
    for rotulo in ax.get_yticklabels():                # estado escolhido em vermelho e negrito
        if rotulo.get_text() == destaque:
            rotulo.set_color("#c0392b")
            rotulo.set_fontweight("bold")
    ax.set_xlim(0, 100)
    ax.set_xlabel(f"% de {sexo.lower()} entre as pessoas formadas")
    ax.set_title(f"{sexo} formados: Exatas x Humanas — {escopo}\nLinhas tracejadas: {ref_nome}", fontsize=11)
    handles, nomes = ax.get_legend_handles_labels()
    fig.legend(handles, nomes, loc="lower center", ncol=2, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(rect=[0, 0.05, 1, 1])


    memoria = io.BytesIO()
    fig.savefig(memoria, format="png")
    plt.close(fig)
    memoria.seek(0)
    return memoria


try:
    dados_foto = df_estados[df_estados["Localidade"].isin(estados_foto)][["Localidade"]].copy()
    for area in areas_foto:
        cols = colunas_area[area]
        dados_foto["pct_" + area] = df_estados.loc[dados_foto.index, cols[sexo_foto]] / df_estados.loc[dados_foto.index, cols["Total"]] * 100


    nome_referencia = localidade_escolhida if localidade_escolhida in ["Brasil"] + regioes else "Brasil"
    linha_ref = df_completo[df_completo["Localidade"] == nome_referencia].iloc[0]
    valores_ref = {a: linha_ref[colunas_area[a][sexo_foto]] / linha_ref[colunas_area[a]["Total"]] * 100 for a in areas_foto}
    destaque_foto = localidade_escolhida if localidade_escolhida not in ["Brasil"] + regioes else ""


    foto = gerar_foto_pesquisa(dados_foto, areas_foto, sexo_foto, nome_referencia, valores_ref, destaque_foto, escopo_foto)
    st.image(foto, caption=f"Percentual de {sexo_foto.lower()} formados — {escopo_foto}", use_container_width=True)
except ModuleNotFoundError:
    st.error("Para gerar a imagem é preciso instalar o matplotlib: pip install matplotlib")






#
st.divider()
st.header("📰 Notícias e contexto")
st.caption("Links externos para leitura. Confira a data de cada matéria, pois algumas são de anos anteriores.")


noticias = {
    "🧠 Fuga de cérebros": [
        ("Estudo aponta que 1,2% dos doutores formados no Brasil estavam fora do país em 2025",
         "Revista Pesquisa FAPESP",
         "https://revistapesquisa.fapesp.br/estudo-aponta-que-12-dos-doutores-que-se-formaram-no-brasil-estava-fora-do-pais-em-2025",
         "Levantamento do Ipea com doutores formados entre 2013 e 2024 indica uma taxa de fuga de cérebros baixa."),
        ("Brasil vê fuga de cérebros aumentar",
         "Baguete (fev. 2025)",
         "https://www.baguete.com.br/public/noticias/brasil-ve-fuga-de-cerebros-aumentar",
         "A saída de profissionais brasileiros qualificados para os Estados Unidos chegou a nível recorde em 2024."),
    ],
    "💻 Escassez de profissionais de TI e Exatas": [
        ("Apagão profissional: há vagas abertas, mas talentos estão fugindo do Brasil",
         "Tecnoblog",
         "https://tecnoblog.net/495835/apagao-profissional-ha-vagas-abertas-mas-talentos-estao-fugindo-do-brasil/",
         "O país forma cerca de 46 mil profissionais de TI por ano, número que não cobre a demanda, segundo a Brasscom."),
        ("Sobram vagas, apesar de salário alto: o que explica escassez de profissionais de TI no Brasil?",
         "InfoMoney",
         "https://www.infomoney.com.br/?p=2260681",
         "A Brasscom estimou demanda por mais de 540 mil profissionais de tecnologia até 2025; a formação deficitária é um dos gargalos."),
    ],
    "👩‍🔬 Mulheres nas áreas STEM": [
        ("Brasil é o terceiro colocado na participação feminina na ciência",
         "Diário do Comércio",
         "https://diariodocomercio.com.br/tecnologia/brasil-terceiro-colocado-participacao-feminina/",
         "Relatório da Elsevier mostra mulheres em 45% da produção científica em 2022, com queda da presença ao longo da carreira."),
        ("Como elevar a presença das mulheres em posições de liderança STEM",
         "Vertiv",
         "https://www.vertiv.com/pt-latam/about/news-and-events/articles/blog-posts/how-to-drive-participation-of-women-in-stem-leadership-beyond-the-current-124/",
         "Cita a UNESCO (35% dos formados em STEM são mulheres) e a baixa presença feminina em engenharia e computação."),
        ("Trabalho sobre mulheres em STEM com dados do INEP",
         "SBC (Women in Information Technology)",
         "https://sol.sbc.org.br/index.php/wit/article/download/43382/43146/",
         "Informa que, em 2022, 30,3% das pessoas graduadas em áreas STEM no Brasil eram mulheres, segundo o Censo da Educação Superior."),
    ],
}


colunas_noticias = st.columns(3)
for coluna_n, (tema, itens) in zip(colunas_noticias, noticias.items()):
    with coluna_n:
        st.subheader(tema)
        for titulo, fonte, link, resumo in itens:
            st.markdown(f"**[{titulo}]({link})**  \n*{fonte}*  \n{resumo}")
