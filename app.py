from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas as origens

# Configurações do S3
AWS_BUCKET_NAME = "seu-bucket-name"
AWS_REGION = "sa-east-1"
s3_client = boto3.client('s3')

# Caminho da imagem modelo
MODEL_IMAGE_PATH = 'model.fw.png'

def process_image(user_image_path, custom_text):
    try:
        user_img = Image.open(user_image_path)
        model_img = Image.open(MODEL_IMAGE_PATH).convert('RGB')
        model_array = np.array(model_img)
        black_area_mask = np.all(model_array == [0, 0, 0], axis=-1)
        black_area_coords = np.argwhere(black_area_mask)

        if len(black_area_coords) == 0:
            return None, "Área preta não encontrada na imagem."

        y_min, x_min = black_area_coords.min(axis=0)
        y_max, x_max = black_area_coords.max(axis=0)
        user_img_resized = user_img.resize((x_max - x_min, y_max - y_min))
        model_img.paste(user_img_resized, (x_min, y_min))

        if custom_text:
            try:
                font = ImageFont.truetype('Roboto-Regular.ttf', 60)
            except IOError:
                return None, 'Fonte não encontrada (Roboto-Regular.ttf).'

            draw = ImageDraw.Draw(model_img)
            padding_x = 100
            padding_y = 40
            white_area_y_min = y_max
            white_area_y_max = model_img.height
            white_area_width = model_img.width - 2 * padding_x

            lines = []
            current_line = ''
            for word in custom_text.split():
                test_line = current_line + ' ' + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font)
                text_width = bbox[2] - bbox[0]
                if text_width <= white_area_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            text_height = sum(
                [draw.textbbox((0, 0), line, font)[3] - draw.textbbox((0, 0), line, font)[1] for line in lines]
            )
            total_text_height = white_area_y_max - white_area_y_min - 2 * padding_y
            vertical_space = total_text_height - text_height
            text_y = white_area_y_min + padding_y + vertical_space // 2
            text_y = min(text_y, white_area_y_max - text_height - 300)

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font)
                text_width = bbox[2] - bbox[0]
                text_x_position = (white_area_width - text_width) // 2 + padding_x
                draw.text((text_x_position, text_y), line, fill=(0, 0, 0), font=font)
                text_y += draw.textbbox((0, 0), line, font)[3] - draw.textbbox((0, 0), line, font)[1] + padding_y

        return model_img, None
    except Exception as e:
        return None, f"Erro no processamento da imagem: {str(e)}"

def upload_to_s3(file_path, bucket_name, s3_file_name):
    try:
        s3_client.upload_file(file_path, bucket_name, s3_file_name)
        s3_url = f'https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_file_name}'
        return s3_url, None
    except FileNotFoundError:
        return None, "Arquivo não encontrado para upload."
    except NoCredentialsError:
        return None, "Credenciais AWS não configuradas."
    except Exception as e:
        return None, f"Erro ao enviar ao S3: {str(e)}"

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'user_image' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400

    user_image = request.files['user_image']
    custom_text = request.form.get('custom_text', '')

    if user_image.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400

    try:
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        user_image_path = os.path.join('uploads', user_image.filename)
        user_image.save(user_image_path)
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar a imagem do usuário: {str(e)}'}), 500

    processed_image, error = process_image(user_image_path, custom_text)
    if error:
        return jsonify({'error': error}), 400

    try:
        if not os.path.exists('static'):
            os.makedirs('static')

        output_path = os.path.join('static', 'generated_image.png')
        processed_image.save(output_path)
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar a imagem processada: {str(e)}'}), 500

    s3_file_name = f'generated_images/{os.path.basename(output_path)}'
    s3_url, error = upload_to_s3(output_path, AWS_BUCKET_NAME, s3_file_name)
    if error:
        return jsonify({'error': error}), 500

    return jsonify({'image_url': s3_url})

if __name__ == '__main__':
    app.run(debug=True)
