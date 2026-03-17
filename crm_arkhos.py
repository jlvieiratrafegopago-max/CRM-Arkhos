import streamlit as st
import sqlite3
import pandas as pd

# --- 1. CONFIGURAÇÕES ---
NOME_AGENCIA = "Agência Arkhos"
DB_NAME = 'banco_arkhos.db'
SENHA_MESTRA = "admin123" # Altere aqui para sua senha de preferência

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

# --- 3. LÓGICA DAS TELAS ---

if menu == "📊 Dashboard":
    st.title(f"📈 Painel {NOME_AGENCIA}")
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
        st.info("Nenhum cliente cadastrado ainda.")

elif menu == "➕ Novo Cadastro":
    st.title("📝 Novo Cadastro de Cliente")
    with st.form("form_novo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome/Empresa")
            atendente = st.text_input("Atendente Responsável")
            valor = st.number_input("Valor Mensal (R$)", min_value=0.0)
        with col2:
            opcoes = ["Tráfego Pago", "Social Midia", "Criativos", "Sites", "Análise de Dados", "Outros"]
            servico = st.selectbox("Tipo de Serviço", opcoes)
            meses = st.number_input("Duração Contrato (Meses)", min_value=1, value=6)
            status = st.select_slider("Status do Projeto", ["Lead", "Proposta", "Fechado", "Em Execução"])
        
        detalhes = st.text_area("Observações Adicionais")
        
        if st.form_submit_button("Salvar Cliente"):
            if nome:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO clientes (nome, servico, detalhes, atendente, status, valor, contrato_meses) VALUES (?,?,?,?,?,?,?)",
                          (nome, servico, detalhes, atendente, status, valor, meses))
                conn.commit()
                conn.close()
                st.success(f"✅ {nome} cadastrado com sucesso!")
                st.rerun()

elif menu == "⚙️ Gerenciar Base":
    st.title("⚙️ Edição Completa de Clientes")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()

    if not df.empty:
        nome_sel = st.selectbox("Selecione o Cliente para editar:", df['nome'].tolist())
        cliente = df[df['nome'] == nome_sel].iloc[0]
        id_cliente = int(cliente['id'])

        st.subheader(f"Editando informações de: {nome_sel}")
        
        # FORMULÁRIO DE EDIÇÃO TOTAL
        with st.form("form_edicao"):
            col1, col2 = st.columns(2)
            
            with col1:
                ed_nome = st.text_input("Editar Nome/Empresa", value=cliente['nome'])
                ed_atendente = st.text_input("Editar Atendente", value=cliente['atendente'])
                ed_valor = st.number_input("Editar Valor (R$)", value=float(cliente['valor']))
            
            with col2:
                opcoes = ["Tráfego Pago", "Social Midia", "Criativos", "Sites", "Análise de Dados", "Outros"]
                idx_servico = opcoes.index(cliente['servico']) if cliente['servico'] in opcoes else 0
                ed_servico = st.selectbox("Editar Serviço", opcoes, index=idx_servico)
                
                ed_meses = st.number_input("Editar Meses", value=int(cliente['contrato_meses']))
                
                status_opcoes = ["Lead", "Proposta", "Fechado", "Em Execução"]
                idx_status = status_opcoes.index(cliente['status']) if cliente['status'] in status_opcoes else 0
                ed_status = st.selectbox("Editar Status", status_opcoes, index=idx_status)
            
            ed_detalhes = st.text_area("Editar Observações", value=cliente['detalhes'])
            
            # Botão de salvar dentro do formulário
            if st.form_submit_button("💾 SALVAR TODAS AS ALTERAÇÕES"):
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("""UPDATE clientes 
                             SET nome=?, servico=?, detalhes=?, atendente=?, status=?, valor=?, contrato_meses=? 
                             WHERE id=?""", 
                          (ed_nome, ed_servico, ed_detalhes, ed_atendente, ed_status, ed_valor, ed_meses, id_cliente))
                conn.commit()
                conn.close()
                st.success("✅ Cadastro atualizado com sucesso!")
                st.rerun()

        st.divider()
        # ÁREA DE EXCLUSÃO (Fora do formulário de edição)
        st.subheader("🗑️ Zona de Exclusão")
        if st.button(f"REMOVER {nome_sel.upper()} DA BASE", type="primary"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
            conn.commit()
            conn.close()
            st.warning("Cliente removido permanentemente.")
            st.rerun()
    else:
        st.info("Não há clientes cadastrados para gerenciar.")
