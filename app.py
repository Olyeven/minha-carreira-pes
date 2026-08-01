import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Minha Carreira - eFootball", page_icon="⚽", layout="wide")

PARTIDAS_FILE = "partidas.csv"
TEMPORADAS_FILE = "temporadas.csv"

COLUNAS_PARTIDAS = ["Data", "Clube", "Adversário", "Competição", "Resultado", "Gols", "Assistências", "Nota", "Minutos"]
COLUNAS_TEMPORADAS = ["Temporada", "Clube", "Posição na Liga", "Títulos", "Gols na Temporada", "Assistências na Temporada", "Observações"]


def carregar(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)


def salvar(df, arquivo):
    df.to_csv(arquivo, index=False)


if "partidas" not in st.session_state:
    st.session_state.partidas = carregar(PARTIDAS_FILE, COLUNAS_PARTIDAS)
if "temporadas" not in st.session_state:
    st.session_state.temporadas = carregar(TEMPORADAS_FILE, COLUNAS_TEMPORADAS)

st.title("⚽ Minha Carreira - Modo Jogador (eFootball)")

aba1, aba2, aba3 = st.tabs(["📋 Registrar Partida", "🏆 Temporadas", "📊 Resumo"])

with aba1:
    st.subheader("Nova partida")
    with st.form("form_partida", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            data_p = st.date_input("Data", value=date.today())
            clube = st.text_input("Meu clube")
            adversario = st.text_input("Adversário")
        with c2:
            competicao = st.text_input("Competição")
            resultado = st.text_input("Resultado (ex: 3x1)")
            minutos = st.number_input("Minutos jogados", 0, 120, 90)
        with c3:
            gols = st.number_input("Gols", 0, 20, 0)
            assist = st.number_input("Assistências", 0, 20, 0)
            nota = st.number_input("Nota (0-10)", 0.0, 10.0, 7.0, step=0.1)
        enviar = st.form_submit_button("Salvar partida")
        if enviar:
            nova = pd.DataFrame(
                [[data_p, clube, adversario, competicao, resultado, gols, assist, nota, minutos]],
                columns=COLUNAS_PARTIDAS,
            )
            st.session_state.partidas = pd.concat([st.session_state.partidas, nova], ignore_index=True)
            salvar(st.session_state.partidas, PARTIDAS_FILE)
            st.success("Partida registrada!")

    st.subheader("Histórico de partidas")
    st.dataframe(st.session_state.partidas, use_container_width=True)
    if not st.session_state.partidas.empty:
        csv = st.session_state.partidas.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar histórico de partidas (CSV)", csv, "partidas.csv", "text/csv")

with aba2:
    st.subheader("Nova temporada")
    with st.form("form_temporada", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            temporada = st.text_input("Temporada (ex: 2025/26)")
            clube_t = st.text_input("Clube")
            posicao = st.text_input("Posição final na liga")
        with c2:
            titulos = st.text_input("Títulos conquistados")
            gols_t = st.number_input("Gols na temporada", 0, 200, 0)
            assist_t = st.number_input("Assistências na temporada", 0, 200, 0)
        obs = st.text_area("Observações")
        enviar_t = st.form_submit_button("Salvar temporada")
        if enviar_t:
            nova_t = pd.DataFrame(
                [[temporada, clube_t, posicao, titulos, gols_t, assist_t, obs]],
                columns=COLUNAS_TEMPORADAS,
            )
            st.session_state.temporadas = pd.concat([st.session_state.temporadas, nova_t], ignore_index=True)
            salvar(st.session_state.temporadas, TEMPORADAS_FILE)
            st.success("Temporada registrada!")

    st.subheader("Histórico de temporadas")
    st.dataframe(st.session_state.temporadas, use_container_width=True)
    if not st.session_state.temporadas.empty:
        csv_t = st.session_state.temporadas.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar histórico de temporadas (CSV)", csv_t, "temporadas.csv", "text/csv")

with aba3:
    st.subheader("Resumo geral da carreira")
    p = st.session_state.partidas
    if not p.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Partidas jogadas", len(p))
        c2.metric("Gols totais", int(p["Gols"].sum()))
        c3.metric("Assistências totais", int(p["Assistências"].sum()))
        c4.metric("Nota média", round(p["Nota"].mean(), 2))
        try:
            st.line_chart(p.set_index("Data")[["Gols", "Assistências"]])
        except Exception:
            pass
    else:
        st.info("Registre suas partidas na aba 'Registrar Partida' para ver o resumo aqui.")
