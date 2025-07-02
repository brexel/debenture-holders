import streamlit as st
import pandas as pd
import os

# Caminho da subpasta onde estão os arquivos
base_path = os.path.join(os.path.dirname(__file__), 'base')

# Interface
st.set_page_config(page_title="Análise de Ativos em Fundos", layout="wide")
st.title("🔍 Análise de Fundos por Ativo")

# Inputs
data_referencia = st.text_input("Digite a data de referência (ex: 202502):", "202502")
ativo_alvo = st.text_input("Digite o código do ativo (ex: VIAD12):", "VIAD12").upper()

if st.button("Rodar Análise"):
    try:
        # Arquivos CSV
        arquivo_blc4 = os.path.join(base_path, f'cda_fi_BLC_4_{data_referencia}.csv')
        arquivo_gestores = os.path.join(base_path, 'cad_fi_hist_gestor.csv')

        # Leitura e filtro
        df = pd.read_csv(arquivo_blc4, sep=';', encoding='latin1', low_memory=False)
        df_ativo = df[df['CD_ATIVO'].astype(str).str.contains(ativo_alvo, na=False)].copy()

        if df_ativo.empty:
            st.warning(f"Nenhum fundo encontrado com o ativo {ativo_alvo} na base {data_referencia}.")
            st.stop()

        df_ativo = df_ativo[['CNPJ_FUNDO_CLASSE', 'DENOM_SOCIAL', 'CD_ATIVO', 'QT_POS_FINAL', 'VL_MERC_POS_FINAL']]
        df_ativo['QT_POS_FINAL'] = pd.to_numeric(df_ativo['QT_POS_FINAL'], errors='coerce')
        df_ativo['VL_MERC_POS_FINAL'] = pd.to_numeric(df_ativo['VL_MERC_POS_FINAL'], errors='coerce')
        df_ativo.sort_values(by='VL_MERC_POS_FINAL', ascending=False, inplace=True)

        df_ativo_fmt = df_ativo.copy()
        df_ativo_fmt['QT_POS_FINAL'] = df_ativo_fmt['QT_POS_FINAL'].map('{:,.0f}'.format)
        df_ativo_fmt['VL_MERC_POS_FINAL'] = df_ativo_fmt['VL_MERC_POS_FINAL'].map('R$ {:,.2f}'.format)

        st.subheader("📄 Fundos com o ativo")
        st.dataframe(df_ativo_fmt, use_container_width=True)

        # Gestores
        gestores = pd.read_csv(arquivo_gestores, sep=';', encoding='latin1', low_memory=False)
        gestores = gestores[gestores['DT_FIM_GESTOR'].isna()].copy()
        gestores['CNPJ_FUNDO'] = gestores['CNPJ_FUNDO'].astype(str).str.replace(r'\D', '', regex=True)
        df_ativo['CNPJ_FUNDO_CLASSE'] = df_ativo['CNPJ_FUNDO_CLASSE'].astype(str).str.replace(r'\D', '', regex=True)
        df_merge = pd.merge(df_ativo, gestores, left_on='CNPJ_FUNDO_CLASSE', right_on='CNPJ_FUNDO', how='left')

        df_gestor = df_merge.groupby('GESTOR', as_index=False).agg({
            'QT_POS_FINAL': 'sum',
            'VL_MERC_POS_FINAL': 'sum'
        })
        df_gestor['QT_POS_FINAL_FMT'] = df_gestor['QT_POS_FINAL'].map('{:,.0f}'.format)
        df_gestor['VL_MERC_POS_FINAL_FMT'] = df_gestor['VL_MERC_POS_FINAL'].map('R$ {:,.2f}'.format)
        df_gestor.sort_values(by='VL_MERC_POS_FINAL', ascending=False, inplace=True)

        st.subheader("🏢 Posição por gestora")
        st.dataframe(df_gestor[['GESTOR', 'QT_POS_FINAL_FMT', 'VL_MERC_POS_FINAL_FMT']], use_container_width=True)

        st.success("Análise concluída!")
        st.markdown(f"**Quantidade total:** {df_ativo['QT_POS_FINAL'].sum():,.0f}")
        st.markdown(f"**Valor total de mercado:** R$ {df_ativo['VL_MERC_POS_FINAL'].sum():,.2f}")

    except Exception as e:
        st.error(f"Erro ao processar: {str(e)}")
