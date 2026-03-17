import streamlit as st
import sqlite3
import pandas as pd

# --- 1. CONFIGURAÇÕES ---
NOME_AGENCIA = "Agência Arkhos"
DB_NAME = 'banco_arkhos.db'
SENHA_MESTRA = "admin123" # Altere para sua senha

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clientes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT, servico TEXT, detalhes TEXT, 
                  atendente TEXT, status TEXT, valor REAL, 
                  contrato_meses INTEGER)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title=NOME_AGENCIA, layout="wide", page_icon="🏛️")

# --- 2. BARRA LATERAL ---
st.sidebar.title(f"🏛️ {NOME_AGENCIA}")
senha_digitada = st.sidebar.text_input("Chave Admin", type="password")
eh_admin = (senha_digitada.strip() == SENHA_MESTRA)

if eh_admin:
    st.sidebar.success("🔓 Admin Ativo")
    menu = st.sidebar.radio("Navegação", ["📊 Dashboard", "➕ Novo Cadastro", "⚙️ Gerenciar Base"])
else:
    st.sidebar.info("🔒 Visualização")
    menu = "📊 Dashboard"

# --- 3. TELAS ---

if menu == "📊 Dashboard":
    st.title(f"📈 Painel {NOME_AGENCIA}")
    # Forçamos a leitura fresca do banco toda vez que entra no Dashboard
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Contratos", len(df))
        c2.metric("Faturamento", f"R$ {df['valor'].sum():,.2f}")
        c3.metric("Ticket Médio", f"R$ {df['valor'].mean():,.2f}")
        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum cliente cadastrado.")

elif menu == "➕ Novo Cadastro":
    st.title("📝 Novo Cadastro")
    with st.form("form_novo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome/Empresa")
            atendente = st.text_input("Atendente")
            valor = st.number_input("Valor (R$)", min_value=0.0)
        with col2:
            opcoes = ["Tráfego Pago", "Social Midia", "Criativos", "Sites", "Análise de Dados", "Outros"]
            servico = st.selectbox("Serviço", opcoes)
            meses = st.number_input("Meses", min_value=1, value=6)
            status = st.select_slider("Status", ["Lead", "Proposta", "Fechado", "Em Execução"])
        
        if st.form_submit_button("Salvar"):
            if nome:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO clientes (nome, servico, atendente, status, valor, contrato_meses) VALUES (?,?,?,?,?,?)",
                          (nome, servico, atendente, status, valor, meses))
                conn.commit()
                conn.close()
                st.success("Cadastrado!")
                st.rerun()

elif menu == "⚙️ Gerenciar Base":
    st.title("⚙️ Gerenciar Clientes")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df.empty:
        nome_sel = st.selectbox("Escolha o Cliente", df['nome'].tolist())
        cliente = df[df['nome'] == nome_sel].iloc[0]
        
        col_ed, col_ex = st.columns(2)

        with col_ed:
            st.subheader("Editar")
            # Adicionamos o parâmetro 'key' único para cada campo
            novo_st = st.selectbox("Status", ["Lead", "Proposta", "Fechado", "Em Execução"], 
                                   index=["Lead", "Proposta", "Fechado", "Em Execução"].index(cliente['status']),
                                   key=f"st_{cliente['id']}")
            novo_vl = st.number_input("Valor", value=float(cliente['valor']), key=f"vl_{cliente['id']}")
            
            if st.button("Salvar Alterações", key="btn_save"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                # Comando SQL direto para garantir a gravação
                c.execute("UPDATE clientes SET status = ?, valor = ? WHERE id = ?", (novo_st, novo_vl, int(cliente['id'])))
                conn.commit()
                conn.close()
                st.success("Alterado com sucesso!")
                # Aguarda um segundo e recarrega
                st.rerun()

        with col_ex:
            st.subheader("Excluir")
            if st.button(f"Remover {nome_sel}", type="primary"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("DELETE FROM clientes WHERE id = ?", (int(cliente['id']),))
                conn.commit()
                conn.close()
                st.warning("Removido!")
                st.rerun()
