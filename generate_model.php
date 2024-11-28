<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['user_image'], $_POST['custom_text'])) {
    // Texto personalizado
    $customText = $_POST['custom_text'];

    // Caminho do modelo (imagem base)
    $modelPath = 'model.png'; // Imagem maior (como moldura)

    // Carrega a imagem enviada e o modelo
    $uploadedImage = imagecreatefromstring(file_get_contents($_FILES['user_image']['tmp_name']));
    $modelImage = imagecreatefrompng($modelPath);

    // Dimensões do modelo
    $modelWidth = imagesx($modelImage);
    $modelHeight = imagesy($modelImage);

    // Redimensiona a imagem enviada para 300x200
    $resizedImage = imagecreatetruecolor(300, 200);
    imagecopyresampled(
        $resizedImage,
        $uploadedImage,
        0, 0, 0, 0,
        300, 200,
        imagesx($uploadedImage),
        imagesy($uploadedImage)
    );

    // Aplica bordas arredondadas à imagem redimensionada
    $radius = 20; // Tamanho do raio para bordas arredondadas
    $mask = imagecreatetruecolor(300, 200);
    $transparent = imagecolorallocatealpha($mask, 0, 0, 0, 127); // Transparente
    imagefill($mask, 0, 0, $transparent);
    imagefilledarc($mask, 0, 0, $radius * 2, $radius * 2, 0, 90, imagecolorallocate($mask, 0, 0, 0), IMG_ARC_PIE);
    imagefilledarc($mask, 300, 0, $radius * 2, $radius * 2, 90, 180, imagecolorallocate($mask, 0, 0, 0), IMG_ARC_PIE);
    imagefilledarc($mask, 0, 200, $radius * 2, $radius * 2, 270, 360, imagecolorallocate($mask, 0, 0, 0), IMG_ARC_PIE);
    imagefilledarc($mask, 300, 200, $radius * 2, $radius * 2, 180, 270, imagecolorallocate($mask, 0, 0, 0), IMG_ARC_PIE);
    imagecopy($mask, $resizedImage, 0, 0, 0, 0, 300, 200);
    imagecopymerge($resizedImage, $mask, 0, 0, 0, 0, 300, 200, 100);

    // Cria a imagem final com transparência para fundo
    $finalImage = imagecreatetruecolor($modelWidth, $modelHeight);
    imagesavealpha($finalImage, true); // Permite transparência na imagem final
    $transparent = imagecolorallocatealpha($finalImage, 0, 0, 0, 127); // Fundo transparente
    imagefill($finalImage, 0, 0, $transparent);

    // Copia a imagem do modelo para a imagem final (sem fundo branco)
    imagecopy($finalImage, $modelImage, 0, 0, 0, 0, $modelWidth, $modelHeight);

    // Copia a imagem redimensionada (com bordas arredondadas) sobre o modelo
    $xCenter = ($modelWidth - 300) / 2; // Centraliza a imagem do usuário no modelo
    $yCenter = ($modelHeight - 200) / 2; // Centraliza a imagem do usuário no modelo
    imagecopy($finalImage, $resizedImage, $xCenter, $yCenter, 0, 0, 300, 200);

    // Adiciona o texto sobrepondo o modelo
    $black = imagecolorallocate($finalImage, 0, 0, 0);
    $fontPath = __DIR__ . '/Roboto-Regular.ttf'; // Caminho da fonte (adicione um arquivo .ttf no mesmo diretório)
    imagettftext($finalImage, 20, 0, 10, $modelHeight / 2, $black, $fontPath, $customText); // Texto no centro da imagem

    // Salva a imagem gerada em um diretório temporário
    $outputPath = 'uploads/generated_image.png';
    imagepng($finalImage, $outputPath);

    // Libera memória
    imagedestroy($uploadedImage);
    imagedestroy($modelImage);
    imagedestroy($resizedImage);
    imagedestroy($finalImage);
    imagedestroy($mask);

    // Retorna a URL da imagem gerada
    echo json_encode(['image_url' => $outputPath]);
    exit;
} else {
    http_response_code(400);
    echo 'Erro ao processar a imagem e o texto.';
}
