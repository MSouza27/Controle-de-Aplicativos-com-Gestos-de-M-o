import cv2  # Biblioteca para manipulação de vídeos e imagens
import mediapipe as mp  # Biblioteca para detecção de mãos e outros modelos
import subprocess  # Permite executar comandos e abrir aplicativos

# Inicializa as ferramentas do MediaPipe para detecção de mãos
mp_maos = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils
maos = mp_maos.Hands()

# Conecta à câmera do computador e define a resolução do vídeo
camera = cv2.VideoCapture(0)
resolucao_x = 1280  # Largura da resolução do vídeo
resolucao_y = 720   # Altura da resolução do vídeo

camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)  # Define a largura da câmera
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)  # Define a altura da câmera

# Variáveis de controle para verificar se os aplicativos estão abertos
bloco_notas = False
chrome = False
calculadora = False

# Função para encontrar coordenadas das mãos na imagem capturada pela câmera
def encontra_coordenadas_maos(img, lado_invertido=False):
    # Converte a imagem capturada para RGB (necessário para o MediaPipe)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Processa a imagem para detectar mãos
    resultado = maos.process(img_rgb)
    todas_maos = []  # Lista para armazenar informações das mãos detectadas
    if resultado.multi_hand_landmarks:  # Verifica se há mãos detectadas
        for lado_mao, marcacao_maos in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            info_maos = {}  # Dicionário para armazenar as informações de uma mão
            coordenadas = []  # Lista para armazenar as coordenadas de cada marcação
            for marcacao in marcacao_maos.landmark:
                # Converte as coordenadas normalizadas para pixels baseados na resolução
                coord_x, coord_y, coord_z = (int(marcacao.x * resolucao_x),
                                             int(marcacao.y * resolucao_y),
                                             int(marcacao.z * resolucao_x))
                coordenadas.append((coord_x, coord_y, coord_z))  # Adiciona as coordenadas à lista
            info_maos['coordenadas'] = coordenadas  # Armazena as coordenadas no dicionário

            # Define o lado da mão (esquerda ou direita)
            if lado_invertido:
                if lado_mao.classification[0].label == 'Left':
                    info_maos['lado'] = 'Right'
                else:
                    info_maos['lado'] = 'Left'
            else:
                info_maos['lado'] = lado_mao.classification[0].label

            # Adiciona as informações da mão à lista de todas as mãos
            todas_maos.append(info_maos)

            # Desenha os pontos e conexões das mãos na imagem
            mp_desenho.draw_landmarks(img, marcacao_maos, mp_maos.HAND_CONNECTIONS)
    return img, todas_maos

# Função para identificar quais dedos estão levantados
def dedos_levantados(maos):
    dedos = []  # Lista para armazenar o estado de cada dedo
    # Verifica os estados dos dedos indicadores, médios, anelares e mínimos
    for ponta_dedo in [8, 12, 16, 20]:
        # Verifica se a ponta do dedo está acima da articulação
        if maos['coordenadas'][ponta_dedo][1] < maos['coordenadas'][ponta_dedo - 2][1]:
            dedos.append(True)  # Dedo levantado
        else:
            dedos.append(False)  # Dedo abaixado
    return dedos

# Loop principal para capturar imagens da câmera em tempo real
while True:
    sucesso, img = camera.read()  # Captura uma imagem da câmera
    img = cv2.flip(img, 1)  # Inverte a imagem horizontalmente (espelhamento)

    # Processa a imagem para encontrar coordenadas das mãos
    img, todas_maos = encontra_coordenadas_maos(img)

    # Verifica se apenas uma mão foi detectada
    if len(todas_maos) == 1:
        # Identifica os dedos levantados da mão detectada
        info_dedos_mao1 = dedos_levantados(todas_maos[0])

        # Verifica o lado da mão e executa ações com base nos gestos
        if todas_maos[0]['lado'] == 'Right':
            # Abrir o aplicativo Notas
            if info_dedos_mao1 == [True, False, False, False] and bloco_notas == False:
                bloco_notas = True
                subprocess.run(['open', '/System/Applications/Notes.app'])

            # Abrir o navegador Google Chrome
            if info_dedos_mao1 == [True, True, False, False] and chrome == False:
                chrome = True
                subprocess.run(['open', '/Applications/Google Chrome.app'])

            # Abrir a Calculadora
            if info_dedos_mao1 == [True, True, True, False] and calculadora == False:
                calculadora = True
                subprocess.run(['open', '/System/Applications/Calculator.app'])

            # Fechar todos os aplicativos
            if info_dedos_mao1 == [False, False, False, False] and bloco_notas and chrome and calculadora == True:
                bloco_notas = chrome = calculadora = False
                subprocess.run(["osascript", "-e", 'quit app "Google Chrome"'])
                subprocess.run(["osascript", "-e", 'quit app "Notes"'])
                subprocess.run(["osascript", "-e", 'quit app "Calculator"'])

            # Encerra o programa quando o polegar e o mínimo estiverem levantados
            if info_dedos_mao1 == [True, False, False, True]:
                break

    # Exibe a imagem processada em uma janela
    cv2.imshow('Video', img)

    # Encerra o programa ao pressionar a tecla ESC
    tecla = cv2.waitKey(1)
    if tecla == 27:
        break




