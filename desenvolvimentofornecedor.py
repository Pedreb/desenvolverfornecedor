import streamlit as st
import requests


def get_states():
    """Retorna a lista de estados do Brasil."""
    return {
        "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
        "DF": "Distrito Federal", "ES": "Espírito Santo",
        "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
        "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
        "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
        "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
        "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
    }


def get_cities_by_state(state_codes):
    """Obtém a lista de cidades filtradas por estado via API do IBGE."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    response = requests.get(url)
    if response.status_code == 200:
        cities = [cidade for cidade in response.json() if
                  cidade["microrregiao"]["mesorregiao"]["UF"]["sigla"] in state_codes]
        return sorted([cidade["nome"] for cidade in cities])
    return []


def consultar_cnpj(cnpj):
    """Consulta informações da empresa na API da Receita Federal."""
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj.replace('.', '').replace('/', '').replace('-', '')}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        data = response.json()
        return data.get("nome"), data.get("fantasia")
    return None, None


st.title("Desenvolvimento de Fornecedores com Inteligência Artificial")

# 1 - Tipo de fornecedor
tipo_fornecedor = st.multiselect("Você procura qual tipo de fornecedor?", ["Fabricante", "Distribuidor", "Varejo"])

Material = st.text_input("Qual nome do item ou serviço?")

# 2 - Referências da empresa (texto fixo)
st.write("Quais as referências dessa empresa no mercado e no Reclame Aqui?")

# 3 - Consulta de CNPJ para excluir empresas
if "excluir_empresas" not in st.session_state:
    st.session_state.excluir_empresas = []

cnpj = st.text_input("Digite o CNPJ da empresa que você deseja excluir da pesquisa")
if st.button("Consultar e Excluir Empresa"):
    if cnpj:
        nome, fantasia = consultar_cnpj(cnpj)
        if nome:
            st.success(f"✅ **Nome Empresarial:** {nome}")
            st.success(f"🏢 **Nome Fantasia:** {fantasia if fantasia else 'Não informado'}")
            if nome not in st.session_state.excluir_empresas:
                st.session_state.excluir_empresas.append(nome)
                st.success(f"Empresa {nome} adicionada à lista de exclusão.")
        else:
            st.error("❌ CNPJ não encontrado ou inválido!")
    else:
        st.warning("Digite um CNPJ válido para consultar e excluir.")

st.write("Empresas excluídas:",
         ", ".join(st.session_state.excluir_empresas) if st.session_state.excluir_empresas else "Nenhuma específica")

# 4 - Estado específico (Múltipla seleção)
states_dict = get_states()
estados_selecionados = st.multiselect("Selecione um ou mais estados", options=list(states_dict.values()))
state_codes_selected = [code for code, name in states_dict.items() if name in estados_selecionados]

# 5 - Cidade específica (Opcional e baseada nos estados selecionados)
cidade_escolhida = ""
cidade_necessaria = st.radio("Deseja especificar uma cidade?", ["Não", "Sim"])
if cidade_necessaria == "Sim" and state_codes_selected:
    cidades = get_cities_by_state(state_codes_selected)
    cidade_escolhida = st.selectbox("Selecione a cidade", cidades) if cidades else "Cidade não encontrada"


# 7 - Preço praticado (texto fixo)
st.write("Qual preço praticado se estiver evidente no site da empresa?")

# Botão para gerar o prompt
if st.button("Gerar Prompt"):
    # Geração do Prompt
    generated_prompt = f"""
    Preciso de informações sobre desenvolvimento de fornecedores para minha empresa.

    1. Tipo de Fornecedor: Busco um fornecedor do tipo {tipo_fornecedor}.
    2. Material: {Material}.
    3. Referências no mercado: Verifique a reputação da empresa no mercado e no Reclame Aqui.
    4. Não incluir as seguintes empresas: {', '.join(st.session_state.excluir_empresas) if st.session_state.excluir_empresas else "Nenhuma específica"}.
    5. Incluir empresas apenas desses estados específicos: {', '.join(estados_selecionados) if estados_selecionados else "Indiferente"}.
    6. Cidade específica: {'Necessário ser em ' + cidade_escolhida if cidade_necessaria == 'Sim' else 'Localização livre'}.
    7. Preço: Caso o preço esteja disponível no site da empresa, informe o valor praticado.

    Preciso de uma resposta clara, estratégica e aplicável à realidade da minha empresa.
    """

    st.subheader("Prompt Gerado:")
    st.code(generated_prompt, language='markdown')

    st.write("Copie o prompt acima e utilize a I.A para obter a melhor resposta!")



