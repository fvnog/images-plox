from google.cloud import storage
from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Inicializar o Flask
app = Flask(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar as credenciais do Google Cloud (geralmente, a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS é usada)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"

# Carregar o token de acesso do Instagram a partir da variável de ambiente
INSTAGRAM_ACCESS_TOKEN = os.getenv("IGQWRQc0NUaGlRV2FIMC0xdFRpVWdCYTROWnl1SVhjdmg0WXM4S05XUlNsdTdtNkNGU3dZAanhfMldwYWtsbHd0WUtJbTF5T0lKQmpVQlJNNUxDVjQ4UVJsUnpxam5fS2h6SGdaZAEwwZAkZAyaEdKNTktdnIxUms3ME0ZD")

# Função para fazer upload da imagem para o Google Cloud Storage
def upload_image_to_gcs(file):
    storage_client = storage.Client()
    bucket = storage_client.bucket('app_teste_plox')  # Substitua pelo nome do seu bucket
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)
    blob.make_public()  # Tornar o arquivo público

    # Retornar a URL pública da imagem
    return blob.public_url

# Função para publicar no Instagram
def post_to_instagram(image_url, title, description):
    url = f'https://graph.facebook.com/v12.0/{INSTAGRAM_ACCESS_TOKEN}/media'
    image_data = {
        'image_url': image_url,
        'caption': f'{title}\n{description}',  # Título e descrição para a postagem
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }

    media_response = requests.post(url, data=image_data)
    media_json = media_response.json()
    
    media_id = media_json.get('id')
    if not media_id:
        return {'error': 'Erro ao criar mídia no Instagram', 'details': media_json}

    publish_url = f'https://graph.facebook.com/v12.0/{INSTAGRAM_ACCESS_TOKEN}/media_publish'
    publish_data = {'creation_id': media_id, 'access_token': INSTAGRAM_ACCESS_TOKEN}
    publish_response = requests.post(publish_url, data=publish_data)
    publish_json = publish_response.json()

    if publish_json.get('error'):
        return {'error': 'Erro ao publicar mídia no Instagram', 'details': publish_json}
    
    return publish_json


@app.route('/post', methods=['POST'])
def create_post():
    try:
        # Imprimir para verificar os dados recebidos
        print("Dados recebidos:")
        print("Título:", request.form['title'])
        print("Descrição:", request.form['description'])

        title = request.form['title']
        description = request.form['description']
        
        # Obter o arquivo de imagem enviado
        image_file = request.files['user_image']  # 'user_image' é o campo de arquivo no frontend

        # Fazer upload da imagem para o Google Cloud Storage e obter a URL pública
        image_url = upload_image_to_gcs(image_file)

        # Chamar a função para publicar no Instagram com a URL da imagem
        instagram_response = post_to_instagram(image_url, title, description)

        if 'error' in instagram_response:
            return jsonify(instagram_response), 500

        return jsonify({'success': True, 'message': 'Post publicado no Instagram com sucesso!'})

    except Exception as e:
        # Captura qualquer erro e imprime
        print("Erro:", str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)
