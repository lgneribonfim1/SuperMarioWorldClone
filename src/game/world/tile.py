from src.game.core.game_object import GameObject


class Tile(GameObject):
    """Tile sólido comum (chão, parede, bloco). Define a INTERFACE de
    colisão que Level usa — cada tipo de tile decide como se comporta,
    em vez de Level ficar checando `hasattr(solid, 'is_slope')` etc.
    espalhado em vários métodos diferentes."""

    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

        self.is_wall = False   # "parede unilateral": pode ser atravessada de baixo pra cima
        self.is_block = False  # bloco interativo (Mystery/Yellow já têm suas próprias classes)
        self.is_slope = False  # mantido por compatibilidade com código legado que só checa a flag

    def hit(self, level):
        pass

    # ------------------------------------------------------------
    # INTERFACE DE COLISÃO — cada subclasse pode sobrescrever.
    # ------------------------------------------------------------
    def blocks_horizontal(self):
        """True = bloqueia o player lateralmente (AABB cheio de parede).
        Tiles 'parede unilateral' (is_wall) NÃO bloqueiam horizontalmente —
        são plataformas atravessáveis por baixo e pelos lados, só sólidas
        por cima. Sem isso, um player em movimento embaixo de uma delas era
        empurrado/expulso pro lado ao encostar no AABB cheio (mesmo bug de
        classe que já resolvemos nas rampas)."""
        return not self.is_wall

    def resolve_vertical_landing(self, player, prev_rect, previous_ground_tile):
        """Chamado quando o player está caindo (direction.y > 0) e o rect
        dele colide com o deste tile. `prev_rect` é uma cópia do
        player.rect de ANTES de qualquer movimento deste frame (horizontal
        E vertical); `previous_ground_tile` é o tile em que o player estava
        apoiado no frame anterior. Usados juntos pra distinguir "pouso de
        verdade" (não sobrepunha este tile antes, ou já estava apoiado
        nele) de "estava atravessando por dentro" (ex: pulou por baixo de
        uma plataforma/rampa e ainda não saiu de dentro dela) — nesse
        segundo caso não deve pousar, deve atravessar. Deve ajustar
        player.rect.y e player.direction.y, e retornar o tile a usar como
        current_ground_tile (ou None se não deve pousar neste frame)."""
        was_overlapping = self.rect.colliderect(prev_rect)
        was_grounded_here = previous_ground_tile is self
        if was_overlapping and not was_grounded_here:
            return None  # estava atravessando por dentro — não pousa, continua caindo
        player.rect.bottom = self.rect.top
        player.direction.y = 0
        return self

    def blocks_vertical_from_below(self):
        """True = bloqueia o player batendo a cabeça (vindo de baixo pra
        cima). Tiles marcados como 'parede unilateral' (is_wall) deixam
        passar por baixo — comportamento herdado do código original."""
        return not self.is_wall


class SlopeTile(Tile):
    """Rampa de 45°. Toda a matemática da diagonal (altura em função de x,
    direção de deslizamento) vive AQUI — fonte única de verdade. Level e
    Player só chamam os métodos, nunca recalculam a diagonal por conta
    própria."""

    VALID_DIRECTIONS = ("up_right", "up_left", "down_right", "down_left")

    def __init__(self, pos, image, slope_dir, friction_mod=1.0):
        super().__init__(pos, image)
        if slope_dir not in self.VALID_DIRECTIONS:
            raise ValueError(f"slope_dir inválido: {slope_dir!r} (esperado um de {self.VALID_DIRECTIONS})")
        self.is_slope = True
        self.slope_dir = slope_dir
        self.friction_mod = friction_mod

    def height_at(self, world_x):
        """Retorna a coordenada Y (mundo) da superfície da rampa em um X
        qualquer, entre o topo (0) e a base (altura do tile) do tile."""
        x_ratio = (world_x - self.rect.x) / self.rect.width
        x_ratio = max(0.0, min(1.0, x_ratio))

        if self.slope_dir in ("up_right", "down_left"):
            # sobe da esquerda pra direita (mais baixo à esquerda)
            return self.rect.y + (self.rect.height - self.rect.height * x_ratio)
        else:  # "up_left", "down_right"
            # sobe da direita pra esquerda (mais baixo à direita)
            return self.rect.y + (self.rect.height * x_ratio)

    def downhill_direction(self):
        """-1 = ladeira abaixo é pra ESQUERDA, +1 = pra DIREITA."""
        return -1 if self.slope_dir in ("up_right", "down_left") else 1

    def blocks_horizontal(self):
        # Rampa NUNCA bloqueia horizontalmente — a altura é sempre resolvida
        # verticalmente por height_at(). Ver histórico: essa era a causa do
        # bug de "expulsão" ao pular sobre a rampa.
        return False

    def resolve_vertical_landing(self, player, prev_rect, previous_ground_tile):
        # Mesma proteção do Tile base, mas por SOBREPOSIÇÃO DE RETÂNGULO (2D)
        # em vez de comparar só a coordenada Y. Uma comparação só em Y contra
        # a altura local da rampa (que muda com X) se mostrou frágil: numa
        # aproximação rápida (velocidade horizontal alta), o "alvo" foge mais
        # rápido do que a métrica conseguia acompanhar, e a rampa parava de
        # colidir por completo. Sobreposição de retângulo não tem esse
        # problema — é insensível à velocidade horizontal.
        was_overlapping = self.rect.colliderect(prev_rect)
        was_grounded_here = previous_ground_tile is self
        if was_overlapping and not was_grounded_here:
            return None  # estava atravessando por dentro (ex: veio de baixo) — não pousa

        target_y = self.height_at(player.rect.centerx) - player.rect.height
        if player.rect.bottom >= target_y - 2:
            player.rect.y = target_y
            player.direction.y = 0
            return self
        return None  # ainda caindo em direção à rampa, não pousou de fato ainda

    def blocks_vertical_from_below(self):
        return False  # sempre atravessável por baixo (pular através da diagonal)


class Decoration(Tile):
    """Tile decorativo (árvores, arbustos, flores). Sem colisão."""
    def __init__(self, pos, image, layer="back"):
        super().__init__(pos, image)
        self.is_collidable = False
        self.layer = layer  # "back" ou "front"
