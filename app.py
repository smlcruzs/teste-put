from flask import Flask, request, jsonify, send_file
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os
from docx import Document

# Configuração do Flask
app = Flask(__name__)

# Configuração do Swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "API de Atualizações"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Simulação do banco de dados (em um banco real, você utilizaria algo como SQLAlchemy)
db = {
    'Ilhéus': {
        'contato': 'contato@ilhéus.com',
        'valor': 1000,
        'desconto': 10,
        'links': ['www.ilheus.com']
    },
    'Pituba': {
        'contato': 'contato@pituba.com',
        'valor': 1500,
        'desconto': 15,
        'links': ['www.pituba.com']
    }
}

# Função para ler o arquivo .docx e identificar as palavras-chave
def extrair_dados_do_docx(docx_path):
    document = Document(docx_path)
    dados_extraidos = {}
    
    for para in document.paragraphs:
        if 'contato' in para.text.lower():
            dados_extraidos['contato'] = para.text.split(":")[-1].strip()
        elif 'valor' in para.text.lower():
            dados_extraidos['valor'] = float(para.text.split(":")[-1].strip())
        elif 'desconto' in para.text.lower():
            dados_extraidos['desconto'] = float(para.text.split(":")[-1].strip())
        elif 'links' in para.text.lower():
            dados_extraidos['links'] = para.text.split(":")[-1].strip().split(',')
    
    return dados_extraidos

# Função simulando o Stringger (em um ambiente real, ele identificaria as unidades do texto)
def identificar_unidade(texto):
    # Exemplo simples: se o texto contém "Ilhéus" ou "Pituba", ele retorna a unidade
    if 'Ilhéus' in texto:
        return 'Ilhéus'
    elif 'Pituba' in texto:
        return 'Pituba'
    return None

# Endpoint para atualizar dados da unidade com base no arquivo .docx
@app.route('/atualizar', methods=['POST'])
def atualizar_dados():
    # Extrai os dados do corpo da requisição
    dados = request.get_json()

    # Identifica a unidade mencionada
    unidade = identificar_unidade(dados.get('unidade'))
    
    if not unidade:
        return jsonify({'erro': 'Unidade não identificada'}), 400
    
    # Caminho do arquivo .docx enviado
    docx_path = 'path_to_your_doc_file.docx'  # Substitua pelo caminho real

    # Extrai os dados do arquivo .docx
    dados_extraidos = extrair_dados_do_docx(docx_path)

    # Atualiza as informações conforme os dados fornecidos
    unidade_data = db.get(unidade)
    if unidade_data:
        # Atualizando com dados extraídos do .docx
        if 'contato' in dados_extraidos:
            unidade_data['contato'] = dados_extraidos['contato']
        if 'valor' in dados_extraidos:
            unidade_data['valor'] = dados_extraidos['valor']
        if 'desconto' in dados_extraidos:
            unidade_data['desconto'] = dados_extraidos['desconto']
        if 'links' in dados_extraidos:
            unidade_data['links'] = dados_extraidos['links']
        
        # Criando o arquivo JSON com os dados atualizados
        file_path = f"{unidade}_dados_atualizados.json"
        with open(file_path, 'w') as json_file:
            json.dump(unidade_data, json_file, indent=4)

        # Retorna o arquivo JSON com os dados atualizados
        return send_file(file_path, as_attachment=True, mimetype='application/json', download_name=file_path)
    
    return jsonify({'erro': 'Unidade não encontrada no banco de dados'}), 404

# Endpoint para pegar as informações de uma unidade
@app.route('/informacoes', methods=['GET'])
def obter_informacoes():
    unidade = request.args.get('unidade')
    unidade_data = db.get(unidade)
    
    if unidade_data:
        return jsonify(unidade_data), 200
    
    return jsonify({'erro': 'Unidade não encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)
