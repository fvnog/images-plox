<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['user_image'])) {
    // Caminho do modelo
    $modelPath = 'model2.png'; // Imagem com fundo transparente
    
    // Processa a imagem enviada
    $uploadedImage = imagecreatefromstring(file_get_contents($_FILES['user_image']['tmp_name']));
    $modelImage = imagecreatefrompng($modelPath);

    // Pega dimensões
    $modelWidth = imagesx($modelImage);
    $modelHeight = imagesy($modelImage);
    $uploadWidth = imagesx($uploadedImage);
    $uploadHeight = imagesy($uploadedImage);

    // Redimensiona a imagem enviada
    $resizedImage = imagecreatetruecolor($modelWidth, $modelHeight);
    imagecopyresampled(
        $resizedImage,
        $uploadedImage,
        0, 0, 0, 0,
        $modelWidth, $modelHeight,
        $uploadWidth, $uploadHeight
    );

    // Combina a imagem redimensionada com o modelo
    imagecopy($resizedImage, $modelImage, 0, 0, 0, 0, $modelWidth, $modelHeight);

    // Define o cabeçalho para exibir a imagem gerada
    header('Content-Type: image/png');
    imagepng($resizedImage);

    // Libera memória
    imagedestroy($uploadedImage);
    imagedestroy($modelImage);
    imagedestroy($resizedImage);
    exit;
} else {
    http_response_code(400);
    echo 'Erro ao processar a imagem.';
}
