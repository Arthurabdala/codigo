import pygame
import os
import random

class Meteoro(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

class Alien(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Jogo')

        self.gato_original = pygame.image.load('gato_inicial.png')
        self.meteoro_original = pygame.image.load('meteoro.png')  
        self.monstro_original = pygame.image.load('allien_real.png')

        # Aplicar transformação de escala
        self.gato = pygame.transform.scale(self.gato_original, (100, 200))  # Dobrando o tamanho do gato
        self.monstro = pygame.transform.scale(self.monstro_original, (350, 300))  # Reduzindo o tamanho do monstro para metade


        # Define a resolução da tela com base na resolução máxima disponível
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # Centraliza a janela
        display_info = pygame.display.Info()
        self.screen_width, self.screen_height = display_info.current_w, display_info.current_h
        self.window = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)

        self.clock = pygame.time.Clock()

        self.fundo_original = pygame.image.load('fundo.png')
        self.fundo = pygame.transform.scale(self.fundo_original, (self.window.get_width(), self.window.get_height()))

        self.coracao = pygame.image.load('coracao.png') 

        self.assets = {'fundo': self.fundo,
                       'coracao': self.coracao,
                       'gato': self.gato,
                       'meteoro': self.meteoro_original,
                       'monstro': self.monstro}

        self.state = {'fundo_x': 0,
                      't0': -1, 
                      'par_inicial_gato': [100, 0],  # Posição inicial do gato
                      'par_inicial': [100, 0], 
                      'velocidade': [0, 0], 
                      'last_update': 0,
                      'gravidade': 1800,  # Grupo de meteoros
                      'meteoros': pygame.sprite.Group(),
                      'aliens': pygame.sprite.Group()}

        self.spawn_gato()  # Chama o método para definir a posição inicial do gato

        # Temporizador para gerar meteoros a cada 8 segundos
        pygame.time.set_timer(pygame.USEREVENT, 8000)
        # Temporizador para gerar aliens a cada 5 segundos
        pygame.time.set_timer(pygame.USEREVENT + 1, 5000)

    def spawn_gato(self):
        self.state['par_inicial_gato'] = [100, self.screen_height - 200]  # Define a posição inicial do gato na parte inferior da tela

    def recebe_eventos(self):
        game = True
        t1 = pygame.time.get_ticks()
        delta_t = (t1 - self.state['last_update']) / 1000
        self.state['last_update'] = t1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.state['velocidade'][0] += 400
                elif event.key == pygame.K_a:
                    self.state['velocidade'][0] -= 400
                elif event.key == pygame.K_SPACE:
                    if self.state['par_inicial'][1] >= self.screen_height - 200:  # Verifica se o gato está no chão para pular
                        self.state['velocidade'][1] = -800  # Define a velocidade vertical para fazer o gato pular
                elif event.key == pygame.K_s:
                    self.state['velocidade'][1] += 250
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.state['velocidade'][0] -= 400
                elif event.key == pygame.K_a:
                    self.state['velocidade'][0] += 400
                elif event.key == pygame.K_s:
                    self.state['velocidade'][1] -= 250
            elif event.type == pygame.USEREVENT:  # Evento para gerar meteoros
                meteoro = Meteoro(self.assets['meteoro'], self.screen_width + 50, random.randint(self.screen_height // 3, self.screen_height), random.randint(5, 10))
                self.state['meteoros'].add(meteoro)
            elif event.type == pygame.USEREVENT + 1:  # Evento para gerar aliens
                alien = Alien(self.assets['monstro'], self.screen_width + 50, random.randint(self.screen_height // 3, self.screen_height), random.randint(5, 10))
                self.state['aliens'].add(alien)

        self.state['velocidade'][1] += self.state['gravidade'] * delta_t  # Aplica a gravidade

        self.state['par_inicial'][0] = self.state['par_inicial'][0] + self.state['velocidade'][0] * delta_t
        self.state['par_inicial'][1] = self.state['par_inicial'][1] + self.state['velocidade'][1] * delta_t

        if self.state['par_inicial'][0] < 0:
            self.state['par_inicial'][0] = 0
        elif self.state['par_inicial'][0] > self.window.get_width():
            self.state['par_inicial'][0] = self.window.get_width()

        # Verifica se a posição y do gato ultrapassa o limite inferior da tela
        if self.state['par_inicial'][1] > self.screen_height - 200:
            self.state['par_inicial'][1] = self.screen_height - 200

        return game

    def move_fundo(self):
        self.state['fundo_x'] -= 0.8
        if self.state['fundo_x'] <= -self.assets['fundo'].get_width():
            self.state['fundo_x'] = 0

    def desenha(self):
        self.window.fill((0,0,0))
        # Desenha o fundo em duas posições para criar um efeito de loop contínuo
        self.window.blit(self.assets['fundo'], (self.state['fundo_x'], 0))
        self.window.blit(self.assets['fundo'], (self.state['fundo_x'] + self.assets['fundo'].get_width(), 0))

        coracao_redimensionado = pygame.transform.scale(self.assets['coracao'], (30, 30))
        for i in range(7):  # Desenha 7 corações
            self.window.blit(coracao_redimensionado, (10 + 40 * i, 10))

        # Renderiza o gato
        self.window.blit(self.assets['gato'], (self.state['par_inicial'][0], self.state['par_inicial'][1]))

        self.state['meteoros'].update()
        self.state['meteoros'].draw(self.window)
        self.state['aliens'].update()
        self.state['aliens'].draw(self.window)

        pygame.display.update()

    def run(self):
        game = True
        while game:
            self.move_fundo()
            game = self.recebe_eventos()
            self.desenha()
            self.clock.tick(60)

jogo = Jogo()
jogo.run()