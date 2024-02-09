################################################################################################################
# Autor: Diego Fukayama
# Versão: 1.0
# Data de criação: 09/02/2024
# Funcionalidade: Adicionar MACs automaticamente em um endpoint identity group no ISE
################################################################################################################

import requests, warnings, time
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth

# Desabilita mensagem de warning para TLS inseguro
warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.*")

# Variáveis - NECESSÁRIO ALTERAR
main_url = "dominio"
username = "usuario"
password = "senha"

# Variáveis para controle 
mac_success = []
mac_error = []

# Função para criar o grupo caso ele não exista
def create_group(group_name, description):
    url = f"https://{main_url}/ers/config/endpointgroup"
    headers = {
        "ERS-Media-Type": "identity.endpointgroup.1.1",
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }
    xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
    <ns0:endpointgroup xmlns:ns0="identity.ers.ise.cisco.com" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ns1="ers.ise.cisco.com" xmlns:ers="ers.ise.cisco.com" description="{description}" name="{group_name}">
       <systemDefined>false</systemDefined>
    </ns0:endpointgroup>"""

    response = requests.post(url, data=xml_data, headers=headers, auth=HTTPBasicAuth(username, password), verify=False)

    if response.status_code == 201:
        location_header = response.headers.get('Location')
        endpointgroup_id = location_header.split("/endpointgroup/")[-1]
        return endpointgroup_id
    elif "already exists" in response.text:
        print(f"Grupo {group_name} já existente")
        confirm = input("Deseja adicionar os MACs nesse grupo (S/N): ")
        if confirm not in ["S", "s"]:
            print("Rode novamente o script e passe outro grupo")
            exit()
        else:
            # Se o grupo já existe, retorne seu ID sem criar novamente
            return get_group_id(group_name)
    else:
        print(f"Falha ao criar o grupo: {response.text}")
        exit()

# Função para adicionar os MACs nos grupos
def add_mac(group_id, mac_list):
    url = f"https://{main_url}/ers/config/endpoint"
    headers = {
        "ERS-Media-Type": "identity.endpoint.1.2",
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }

    for mac in mac_list:
        xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ns0:endpoint xmlns:ns0="identity.ers.ise.cisco.com" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ns1="ers.ise.cisco.com" xmlns:ers="ers.ise.cisco.com" description="description" id="id" name="name">
        <groupId>{group_id}</groupId>
        <mac>{mac}</mac>
        <staticGroupAssignment>true</staticGroupAssignment>
        <staticProfileAssignment>false</staticProfileAssignment>
        </ns0:endpoint>"""

        response = requests.post(url, data=xml_data, headers=headers, auth=HTTPBasicAuth(username, password), verify=False)
        if response.status_code == 201:
            print(f"{mac} - Adicionado")
            mac_success.append(mac)
        else:
            error_message = extract_error_message_from_xml(response.text)
            print(f"\n{mac} - Falha ao adicionar: {error_message}")
            mac_error.append(mac)

# Função para obter o ID do grupo pelo nome
def get_group_id(group_name):
    url = f"https://{main_url}/ers/config/endpointgroup?filter=name.EQ.{group_name}"
    headers = {
        "ERS-Media-Type": "identity.endpointgroup.1.1",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password), verify=False)
    if response.status_code == 200:
        data = response.json()
        if 'SearchResult' in data and 'resources' in data['SearchResult']:
            resources = data['SearchResult']['resources']
            if resources:
                return resources[0]['id']
    return None

# Função para formatar os valores lidos do arquivo para MACs caso necessário
def format_mac(mac_address):
    # Remover caracteres não hexadecimais
    cleaned_mac = ''.join(c for c in mac_address if c.isdigit() or c.lower() in 'abcdef')

    # Verificar se o comprimento do endereço MAC é válido
    if len(cleaned_mac) != 12:
        raise ValueError(f"O endereço MAC '{mac_address}' não possui 12 caracteres")

    # Formatar o endereço MAC
    formatted_mac = ':'.join(cleaned_mac[i:i+2] for i in range(0, len(cleaned_mac), 2))
    return formatted_mac

def extract_error_message_from_xml(xml_string):
    root = ET.fromstring(xml_string)
    title = root.find(".//title")
    if title is not None:
        return title.text.strip()
    else:
        return None

# Variáveis
mac_list = []
group_name = input("Informe o nome do grupo: ")
file = input("Informe o arquivo com os MACs: ")

# Le o arquivo e formata para MAC caso necessário
with open(file, 'r') as file:
	for line in file:
		mac_address = line.strip()
		try:
			formatted_mac = format_mac(mac_address)
			mac_list.append(formatted_mac)
		except ValueError as e:
			print(f"Erro ao formatar o endereço MAC '{mac_address}': {e}")

# Exibe os MACs a serem adicionados
print("Lista de endereços MAC a serem adicionados:")
for mac in mac_list:
	print(mac)

# Confirma com o usuário se ele deseja prosseguir com a adição dos MACs
confirm = input(f"Deseja continuar com a adição dos MACs no grupo '{group_name}' (S/N): ")

if confirm not in ['S', 's']:
	exit()
else:
	description = input("Insira uma descrição para o grupo: ")
	id = create_group(group_name, description)
	
	# Adiciona o MAC no grupo
	add_mac(id, mac_list)
     
	print(f"MACs Adicionados: {len(mac_success)} | MACs não adicionados: {len(mac_error)}")
	
	confirm = input("Deseja ver quais MACs foram adicionados (S/N): ")
	if confirm in ['S','s']:
		print(str(mac_success))

	confirm = input("Deseja ver quais MACs não foram adicionados (S/N): ")
	if confirm in ['S', 's']:
		print(str(mac_error))
	else:
		exit()
