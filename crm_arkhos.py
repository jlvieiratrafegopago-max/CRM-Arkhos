import streamlit as st
import sqlite3
import pandas as pd

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
# DICA: Você pode mudar a senha e o nome da agência aqui embaixo
NOME_AGENCIA = "Agência Arkhos"
SENHA_MESTRA = "1234" # Digite sua senha atualizada aqui
DB_NAME = 'banco_arkhos.db'

def init_db():
    """Inicia o banco de dados caso ele não exista"""
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

# Configuração da Página no Navegador
st.set_page_config(page_title=NOME_AGENCIA, layout="wide", page_icon="🏛️")

# --- 2. CONTROLE DE ACESSO (BARRA LATERAL) ---
st.sidebar.title(f"🏛️ {NOME_AGENCIA}")
senha_digitada = st.sidebar.text_input("Acesso Administrativo", type="password")

# Comparação de segurança (Limpa espaços em branco acidentais)
eh_admin = (senha_digitada.strip() == SENHA_MESTRA.strip())

if eh_admin:
    st.sidebar.success("🔓 Modo Admin Ativo")
    menu = st.sidebar.radio("Navegação", ["📊 Dashboard", "➕ Novo Cadastro", "⚙️ Gerenciar Base"])
else:
    st.sidebar.info("🔒 Modo Visualização")
    menu = "📊 Dashboard"

# --- 3. TELAS DO SISTEMA ---

# --- TELA: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title(f"📈 Painel de Controle - {NOME_AGENCIA}")
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df.empty:
        # Métricas de resumo
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Clientes", len(df))
        c2.metric("Faturamento Total", f"R$ {df['valor'].sum():,.2f}")
        c3.metric("Ticket Médio", f"R$ {df['valor'].mean():,.2f}")
        
        st.divider()
        st.subheader("Lista de Contratos Ativos")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("O banco de dados está vazio. Acesse o modo Admin para cadastrar.")

# --- TELA: NOVO CADASTRO ---
elif menu == "➕ Novo Cadastro":
    st.title("📝 Cadastro de Novo Cliente")
    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome/Empresa")
            atendente = st.text_input("Responsável (Atendente)")
            valor = st.number_input("Valor Mensal (R$)", min_value=0.0, step=50.0)
        with col2:
            servico = st.selectbox("Tipo de Serviço", ["Tráfego Pago", "Social Media", "Criação de Site", "Consultoria IA"])
            meses = st.number_input("Duração do Contrato (Meses)", min_value=1, value=6)
            status = st.select_slider("Fase Atual", ["Lead", "Proposta", "Fechado", "Em Execução"])
        
        notas = st.text_area("Observações do Projeto")
        
        if st.form_submit_button("Finalizar Cadastro"):
            if nome and atendente:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute('''INSERT INTO clientes (nome, servico, detalhes, atendente, status, valor, contrato_meses) 
                             VALUES (?,?,?,?,?,?,?)''', (nome, servico, notas, atendente, status, valor, meses))
                conn.commit()
                conn.close()
                st.success(f"✅ {nome} cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha o Nome e o Atendente.")

# --- TELA: GERENCIAR (EDITAR/EXCLUIR) ---
elif menu == "⚙️ Gerenciar Base":
    st.title("⚙️ Administração da Base")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df.empty:
        id_cliente = st.selectbox("Selecione o Cliente pelo ID", df['id'].tolist())
        cliente_dados = df[df['id'] == id_cliente].iloc[0]

        col_edit, col_del = st.columns(2)

        with col_edit:
            st.subheader("Atualizar Dados")
            novo_status = st.selectbox("Mudar Status", ["Lead", "Proposta", "Fechado", "Em Execução"], 
                                      index=["Lead", "Proposta", "Fechado", "Em Execução"].index(cliente_dados['status']))
            novo_valor = st.number_input("Atualizar Valor (R$)", value=float(cliente_dados['valor']))
            
            if st.button("Salvar Alterações"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE clientes SET status=?, valor=? WHERE id=?", (novo_status, novo_valor, id_cliente))
                conn.commit()
                conn.close()
                st.success("Dados atualizados!")
                st.rerun()

        with col_del:
            st.subheader("Zona de Perigo")
            st.error(f"Apagar permanentemente: {cliente_dados['nome']}?")
            if st.button("CONFIRMAR EXCLUSÃO"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
                conn.commit()
                conn.close()
                st.warning("Registro removido.")
                st.rerun()