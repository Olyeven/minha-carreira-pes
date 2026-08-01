import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Minha Carreira de Treinador", page_icon="🧢", layout="wide")

PARTIDAS_FILE = "partidas.csv"
TRANSFERENCIAS_FILE = "transferencias.csv"
TEMPORADAS_FILE = "temporadas.csv"
PERFIL_FILE = "perfil.csv"
FOTOS_DIR = "fotos"
FOTO_TREINADOR = os.path.join(FOTOS_DIR, "treinador.png")
ESCUDO_CLUBE = os.path.join(FOTOS_DIR, "escudo_clube.png")

os.makedirs(FOTOS_DIR, exist_ok=True)

COLUNAS_PARTIDAS = [
    "Data", "Competição", "Mandante", "Adversário",
    "GolsPro", "GolsContra", "Resultado", "Formação", "Destaque",
]
COLUNAS_TRANSFERENCIAS = ["Data", "Jogador", "Posição", "Tipo", "Clube Envolvido", "Valor (milhões)"]
COLUNAS_TEMPORADAS = ["Temporada", "Clube", "Posição Final", "Pontos", "Títulos", "Orçamento Final", "Observações"]
COLUNAS_PERFIL = ["Nome do Treinador", "Nacionalidade", "Clube Atual", "Reputação"]


def carregar(arquivo, colunas):
    if os.path.exists(arquivo):
        df = pd.read_csv(arquivo)
        for c in colunas:
            if c not in df.columns:
                df[c] = ""
        return df[colunas]
    return pd.DataFrame(columns=colunas)


def salvar(df, arquivo):
    df.to_csv(arquivo, index=False)


for chave, arquivo, colunas in [
    ("partidas", PARTIDAS_FILE, COLUNAS_PARTIDAS),
    ("transferencias", TRANSFERENCIAS_FILE, COLUNAS_TRANSFERENCIAS),
    ("temporadas", TEMPORADAS_FILE, COLUNAS_TEMPORADAS),
    ("perfil", PERFIL_FILE, COLUNAS_PERFIL),
]:
    if chave not in st.session_state:
        st.session_state[chave] = carregar(arquivo, colunas)

# --- Sidebar: perfil do treinador ---
st.sidebar.header("🧢 Meu perfil")

up_treinador = st.sidebar.file_uploader("Foto do treinador", type=["png", "jpg", "jpeg"], key="up_treinador")
if up_treinador is not None:
    with open(FOTO_TREINADOR, "wb") as f:
        f.write(up_treinador.getbuffer())
if os.path.exists(FOTO_TREINADOR):
    st.sidebar.image(FOTO_TREINADOR, use_container_width=True)

up_escudo = st.sidebar.file_uploader("Escudo do clube atual", type=["png", "jpg", "jpeg"], key="up_escudo")
if up_escudo is not None:
    with open(ESCUDO_CLUBE, "wb") as f:
        f.write(up_escudo.getbuffer())
if os.path.exists(ESCUDO_CLUBE):
    st.sidebar.image(ESCUDO_CLUBE, width=100)

with st.sidebar.form("form_perfil"):
    perfil_atual = st.session_state.perfil.iloc[0] if not st.session_state.perfil.empty else {}
    nome_t = st.text_input("Nome do treinador", value=perfil_atual.get("Nome do Treinador", ""))
    nacionalidade = st.text_input("Nacionalidade", value=perfil_atual.get("Nacionalidade", ""))
    clube_atual = st.text_input("Clube atual", value=perfil_atual.get("Clube Atual", ""))
    reputacao = st.selectbox(
        "Reputação",
        ["Amador", "Semi-profissional", "Nacional", "Continental", "Mundial"],
        index=0,
    )
    salvar_perfil = st.form_submit_button("Salvar perfil")
    if salvar_perfil:
        st.session_state.perfil = pd.DataFrame(
            [[nome_t, nacionalidade, clube_atual, reputacao]], columns=COLUNAS_PERFIL
        )
        salvar(st.session_state.perfil, PERFIL_FILE)
        st.sidebar.success("Perfil salvo!")

st.title("🧢 Minha Carreira de Treinador - Master League (Football Life 2026)")

aba1, aba2, aba3, aba4 = st.tabs(["📋 Partidas", "🔄 Transferências", "🏆 Temporadas", "📊 Resumo"])

with aba1:
    st.subheader("Nova partida")
    with st.form("form_partida", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_p = st.date_input("Data", value=date.today())
            competicao = st.text_input("Competição")
            mandante = st.selectbox("Mando de campo", ["Casa", "Fora"])
        with c2:
            adversario = st.text_input("Adversário")
            gols_pro = st.number_input("Gols marcados", 0, 20, 0)
            gols_contra = st.number_input("Gols sofridos", 0, 20, 0)
        with c3:
            formacao = st.text_input("Formação usada (ex: 4-3-3)")
            destaque = st.text_input("Jogador destaque da partida")

        enviar = st.form_submit_button("Salvar partida")
        if enviar:
            if gols_pro > gols_contra:
                resultado = "Vitória"
            elif gols_pro < gols_contra:
                resultado = "Derrota"
            else:
                resultado = "Empate"
            nova = pd.DataFrame(
                [[data_p, competicao, mandante, adversario, gols_pro, gols_contra, resultado, formacao, destaque]],
                columns=COLUNAS_PARTIDAS,
            )
            st.session_state.partidas = pd.concat([st.session_state.partidas, nova], ignore_index=True)
            salvar(st.session_state.partidas, PARTIDAS_FILE)
            st.success(f"Partida registrada — {resultado}!")

    st.subheader("Histórico de partidas")
    st.dataframe(st.session_state.partidas[::-1], use_container_width=True, hide_index=True)
    if not st.session_state.partidas.empty:
        csv = st.session_state.partidas.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar histórico de partidas (CSV)", csv, "partidas.csv", "text/csv")

with aba2:
    st.subheader("Nova movimentação no mercado")
    with st.form("form_transferencia", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_tr = st.date_input("Data", value=date.today(), key="data_tr")
            jogador = st.text_input("Jogador")
        with c2:
            posicao = st.text_input("Posição")
            tipo = st.selectbox("Tipo", ["Compra", "Venda", "Empréstimo (entrada)", "Empréstimo (saída)", "Fim de contrato"])
        with c3:
            clube_env = st.text_input("Clube envolvido (origem/destino)")
            valor = st.number_input("Valor (milhões)", 0.0, 1000.0, 0.0, step=0.5)

        enviar_tr = st.form_submit_button("Salvar movimentação")
        if enviar_tr:
            nova_tr = pd.DataFrame(
                [[data_tr, jogador, posicao, tipo, clube_env, valor]], columns=COLUNAS_TRANSFERENCIAS
            )
            st.session_state.transferencias = pd.concat([st.session_state.transferencias, nova_tr], ignore_index=True)
            salvar(st.session_state.transferencias, TRANSFERENCIAS_FILE)
            st.success("Movimentação registrada!")

    st.subheader("Histórico de transferências")
    st.dataframe(st.session_state.transferencias[::-1], use_container_width=True, hide_index=True)
    if not st.session_state.transferencias.empty:
        csv_tr = st.session_state.transferencias.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar histórico de transferências (CSV)", csv_tr, "transferencias.csv", "text/csv")

with aba3:
    st.subheader("Nova temporada")
    with st.form("form_temporada", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            temporada = st.text_input("Temporada (ex: 2025/26)")
            clube_temp = st.text_input("Clube")
            posicao_final = st.text_input("Posição final na liga")
        with c2:
            pontos = st.number_input("Pontos conquistados", 0, 200, 0)
            titulos = st.text_input("Títulos conquistados")
            orcamento = st.number_input("Orçamento final (milhões)", value=0.0, step=0.5)
        obs = st.text_area("Observações")
        enviar_temp = st.form_submit_button("Salvar temporada")
        if enviar_temp:
            nova_temp = pd.DataFrame(
                [[temporada, clube_temp, posicao_final, pontos, titulos, orcamento, obs]],
                columns=COLUNAS_TEMPORADAS,
            )
            st.session_state.temporadas = pd.concat([st.session_state.temporadas, nova_temp], ignore_index=True)
            salvar(st.session_state.temporadas, TEMPORADAS_FILE)
            st.success("Temporada registrada!")

    st.subheader("Histórico de temporadas")
    st.dataframe(st.session_state.temporadas[::-1], use_container_width=True, hide_index=True)
    if not st.session_state.temporadas.empty:
        csv_temp = st.session_state.temporadas.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar histórico de temporadas (CSV)", csv_temp, "temporadas.csv", "text/csv")

with aba4:
    st.subheader("Resumo geral da carreira")
    p = st.session_state.partidas
    if not p.empty:
        vitorias = int((p["Resultado"] == "Vitória").sum())
        empates = int((p["Resultado"] == "Empate").sum())
        derrotas = int((p["Resultado"] == "Derrota").sum())
        jogos = len(p)
        aproveitamento = round((vitorias * 3 + empates) / (jogos * 3) * 100, 1) if jogos else 0
        saldo_gols = int(p["GolsPro"].sum() - p["GolsContra"].sum())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Jogos", jogos)
        c2.metric("Vitórias", vitorias)
        c3.metric("Empates", empates)
        c4.metric("Derrotas", derrotas)
        c5.metric("Aproveitamento", f"{aproveitamento}%")

        c6, c7 = st.columns(2)
        c6.metric("Gols marcados", int(p["GolsPro"].sum()))
        c7.metric("Saldo de gols", saldo_gols)

        try:
            st.line_chart(p.set_index("Data")[["GolsPro", "GolsContra"]])
        except Exception:
            pass
    else:
        st.info("Registre suas partidas na aba 'Partidas' para ver o resumo aqui.")

    if not st.session_state.temporadas.empty:
        st.subheader("Títulos conquistados na carreira")
        titulos_lista = st.session_state.temporadas["Títulos"].dropna()
        titulos_lista = titulos_lista[titulos_lista.astype(str).str.strip() != ""]
        if not titulos_lista.empty:
            for t in titulos_lista:
                st.write(f"🏆 {t}")
        else:
            st.caption("Nenhum título registrado ainda.")
