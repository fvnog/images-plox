<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload de Imagem e Texto</title>
    <!-- Link para o Bootstrap -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Carregar Imagem e Texto</h1>

        <!-- Formulário para upload -->
        <form id="uploadForm" enctype="multipart/form-data" class="border p-4 rounded shadow-sm">
            <div class="mb-3">
                <label for="imageInput" class="form-label">Escolha uma imagem:</label>
                <input type="file" id="imageInput" name="user_image" accept="image/*" class="form-control" required>
            </div>

            <div class="mb-3">
                <label for="customText" class="form-label">Texto Personalizado:</label>
                <input type="text" id="customText" name="custom_text" placeholder="Texto para a imagem" class="form-control">
            </div>

            <button type="submit" class="btn btn-primary w-100">Enviar</button>
        </form>

        <!-- Exibir imagens geradas -->
        <h2 class="text-center mt-5">Imagens Geradas</h2>
        <div class="row">
            <div class="col-12 col-md-6 text-center">
                <h4>Imagem 1</h4>
                <img id="generatedImage" src="" alt="Imagem Gerada 1" class="img-fluid mt-3" style="max-width: 100%; display: none;">
                <input type="radio" name="imageChoice" value="image1" id="image1Choice"> Escolher Imagem 1
            </div>
            <div class="col-12 col-md-6 text-center">
                <h4>Imagem 2</h4>
                <img id="generatedImage2" src="" alt="Imagem Gerada 2" class="img-fluid mt-3" style="max-width: 100%; display: none;">
                <input type="radio" name="imageChoice" value="image2" id="image2Choice"> Escolher Imagem 2
            </div>
        </div>

        <!-- Formulário para enviar a imagem escolhida -->
        <div id="additionalForm" class="mt-4" style="display: none;">
            <h3>Detalhes Adicionais</h3>
            <div class="mb-3">
                <label for="title" class="form-label">Título:</label>
                <input type="text" id="title" name="title" class="form-control" placeholder="Digite o título" required>
            </div>
            <div class="mb-3">
                <label for="description" class="form-label">Descrição:</label>
                <textarea id="description" name="description" class="form-control" placeholder="Digite a descrição" required></textarea>
            </div>
            <button type="submit" id="sendImageData" class="btn btn-success w-100">Enviar Detalhes</button>
        </div>

        <!-- Mensagem de erro -->
        <div id="errorMessage" class="alert alert-danger mt-4" style="display: none;"></div>
    </div>

    <!-- Script do jQuery e do Bootstrap -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
       $(document).ready(function() {
    // Função para carregar a imagem inicial
    function loadInitialImages() {
        var timestamp = new Date().getTime();

        // Carregar a imagem gerada do servidor 5000
        var initialImageUrl = "http://127.0.0.1:5000/static/generated_image.png";
        $('#generatedImage').attr('src', initialImageUrl + '?t=' + timestamp).show();

        // Carregar a imagem gerada do servidor 5001
        var initialImageUrl2 = "http://127.0.0.1:5001/static/generated_image_2.png";
        $('#generatedImage2').attr('src', initialImageUrl2 + '?t=' + timestamp).show();
    }

    // Carregar as imagens iniciais ao carregar a página
    loadInitialImages();

    // Ao enviar o formulário de upload, realizar o upload
    $('#uploadForm').submit(function(event) {
        event.preventDefault();

        // Limpar mensagens de erro
        $('#errorMessage').hide();

        // Preparar o FormData para enviar a imagem e o texto
        var formData = new FormData();
        formData.append('user_image', $('#imageInput')[0].files[0]);
        formData.append('custom_text', $('#customText').val());

        // Enviar as duas requisições simultaneamente
        var request1 = $.ajax({
            url: 'http://127.0.0.1:5000/upload', // Requisição para o servidor 5000
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });

        var request2 = $.ajax({
            url: 'http://127.0.0.1:5001/upload_model2', // Requisição para o servidor 5001
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });

        // Após o envio, processar as respostas de ambos os servidores
        $.when(request1, request2).done(function(response1, response2) {
            // Resposta do servidor 5000
            if (response1[0].image_url) {
                var timestamp = new Date().getTime();
                $('#generatedImage').attr('src', response1[0].image_url + '?t=' + timestamp).show();
            } else {
                $('#errorMessage').text('Erro ao processar a imagem no servidor 5000.').show();
            }

            // Resposta do servidor 5001
            if (response2[0].image_url) {
                var timestamp = new Date().getTime();
                $('#generatedImage2').attr('src', response2[0].image_url + '?t=' + timestamp).show();
            } else {
                $('#errorMessage').text('Erro ao processar a imagem no servidor 5001.').show();
            }
        }).fail(function(xhr, status, error) {
            // Exibir mensagem de erro geral se as requisições falharem
            $('#errorMessage').text('Erro ao processar as imagens: ' + error).show();
        });
    });

    // Ao escolher uma imagem, exibir o formulário de detalhes adicionais
    $('input[name="imageChoice"]').change(function() {
        $('#additionalForm').show();
    });

    // Enviar os detalhes quando o botão for clicado
    $('#sendImageData').click(function(event) {
        event.preventDefault();

        // Validar se uma imagem foi escolhida
        var imageChoice = $('input[name="imageChoice"]:checked').val();
        if (!imageChoice) {
            $('#errorMessage').text('Por favor, escolha uma imagem.').show();
            return;
        }

        // Determinar a URL da imagem com base na escolha
        var imageUrl = '';
        if (imageChoice === 'image1') {
            imageUrl = $('#generatedImage').attr('src');
        } else if (imageChoice === 'image2') {
            imageUrl = $('#generatedImage2').attr('src');
        }

        // Preparar os dados para o envio
        var formData = {
            title: $('#title').val(),
            description: $('#description').val(),
            imageChoice: imageChoice,
            imageUrl: imageUrl // Agora passando a URL da imagem
        };

        $.ajax({
            url: 'http://127.0.0.1:5002/post', // Atualize para a rota correta do Flask
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    alert('Detalhes enviados com sucesso!');
                } else {
                    $('#errorMessage').text('Erro ao enviar os detalhes.').show();
                }
            },
            error: function(xhr, status, error) {
                $('#errorMessage').text('Erro: ' + error).show();
            }
        });
    });
});

    </script>
</body>
</html>
