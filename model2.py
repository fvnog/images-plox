from flask import Flask, request, jsonify
from flask_cors import CORS  # Importando o CORS
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# Permitir CORS para todas as origens
CORS(app)

# Caminho da imagem modelo2
MODEL2_IMAGE_PATH = 'modelo2.fw.png'
FONT_PATH = 'Roboto-Regular.ttf'  # Caminho para a fonte

# Função para processar a imagem do modelo 2 e adicionar texto
def process_image_model2(user_image, custom_text):
    try:
        # Carregar a imagem enviada pelo usuário
        user_img = Image.open(user_image)
    except Exception as e:
        return None, f'Erro ao abrir a imagem do usuário: {str(e)}'

    try:
        # Carregar o modelo2
        model2_img = Image.open(MODEL2_IMAGE_PATH)
    except Exception as e:
        return None, f'Erro ao carregar a imagem modelo2: {str(e)}'

    # Redimensionar a imagem do usuário para o mesmo tamanho do modelo2
    user_img_resized = user_img.resize(model2_img.size)

    # Combinar as imagens (imagem do usuário atrás do modelo2)
    final_image = Image.new("RGB", model2_img.size)
    final_image.paste(user_img_resized, (0, 0))
    final_image.paste(model2_img, (0, 0), mask=model2_img if model2_img.mode == 'RGBA' else None)

    # Definir a área onde o texto será colocado (exemplo: dentro de um quadro branco)
    text_area_left = 230  # Coordenada X esquerda
    text_area_top = 880  # Coordenada Y superior
    text_area_right = 900  # Coordenada X direita (limite do quadro)
    text_area_bottom = 900  # Coordenada Y inferior (limite do quadro)

    # Definir as propriedades do texto (fonte e tamanho)
    try:
        font = ImageFont.truetype(FONT_PATH, 35)  # Carrega a fonte Roboto-Regular.ttf com tamanho 24
    except IOError as e:
        return None, f'Erro ao carregar a fonte: {str(e)}'

    # Desenhar o texto na imagem
    draw = ImageDraw.Draw(final_image)
    max_width = text_area_right - text_area_left
    lines = wrap_text(custom_text, font, max_width)

    # Coordenadas iniciais para o texto
    y = text_area_top
    for line in lines:
        draw.text((text_area_left, y), line, font=font, fill="black")
        y += font.getbbox(line)[3] - font.getbbox(line)[1]  # Aumenta a coordenada Y para a próxima linha

    return final_image, None

# Função para quebrar o texto em linhas para caber na área definida
def wrap_text(text, font, max_width):
    lines = []
    words = text.split(' ')
    line = ""

    for word in words:
        test_line = line + " " + word if line else word
        width, _ = font.getbbox(test_line)[2:4]  # Largura do texto

        if width <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    return lines

@app.route('/upload_model2', methods=['POST'])
def upload_image_model2():
    if 'user_image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    user_image = request.files['user_image']

    if user_image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Obter o texto enviado pelo usuário
    custom_text = request.form.get('custom_text', '')  # Verifica se há texto no formulário

    # Salvar a imagem do usuário em um diretório temporário
    try:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        user_image_path = os.path.join('uploads', user_image.filename)
        user_image.save(user_image_path)
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar a imagem do usuário: {str(e)}'}), 500

    # Processar a imagem para o modelo2 e adicionar o texto
    processed_image, error = process_image_model2(user_image_path, custom_text)
    if error:
        return jsonify({'error': error}), 400

    # Salvar a imagem final
    try:
        if not os.path.exists('static'):
            os.makedirs('static')

        output_path = os.path.join('static', 'generated_image_2.png')
        processed_image.save(output_path)
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar a imagem processada: {str(e)}'}), 500

    return jsonify({'image_url': output_path})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
