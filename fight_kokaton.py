import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        self.img_flip = pg.transform.flip(self.img, True, False)  # self.imgを左右反転

        self.imgs = {
        (0,0): pg.transform.rotozoom(self.img, 0,1.0),
        (0, -5): pg.transform.rotozoom(self.img, 90,1.0),
        (5, -5): pg.transform.rotozoom(self.img, 45,1.0),
        (5, 0): pg.transform.rotozoom(self.img, 0,1.0),
        (5, 5): pg.transform.rotozoom(self.img, -45,1.0),
        (0, 5): pg.transform.rotozoom(self.img, -90,1.0),
        (-5, +5): pg.transform.rotozoom(self.img_flip, 45,1.0),
        (-5, 0): pg.transform.rotozoom(self.img_flip, 0,1.0),
        (-5, -5): pg.transform.rotozoom(self.img_flip, -45,1.0),
        }


        self.img = self.imgs[(5, 0)] # デフォルト画像
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(self.imgs[tuple(sum_mv)], self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        color = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255), (255, 255, 255), (0, 0, 0)]
        rad = random.randint(10, 50)
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, random.choice(color), (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        mv_lst = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]
        self.vx, self.vy = random.choice(mv_lst), random.choice(mv_lst)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Beam:
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.img = pg.image.load(f"ex03/fig/beam.png")
        self.img = pg.transform.rotozoom(self.img, 0, 2.0)
        self.rct = self.img.get_rect()
        self.rct.left = bird.rct.right
        self.rct.centery = bird.rct.centery
        self.vx, self.vy = +5, 0    
    
    def update(self, screen: pg.Surface):
        """
        ビームを移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Explosion:
    """
    爆発に関するクラス
    """
    def __init__(self, bomb: Bomb):
        """
        爆発画像Surfaceを生成する
        引数1 bomb：爆発する爆弾のインスタンス
        """
        self.img = pg.image.load(f"ex03/fig/explosion.gif")
        self.img = pg.transform.rotozoom(self.img, 0, 2.0)
        self.imgs = [pg.transform.flip(self.img, True, False),pg.transform.flip(self.img, True, True),pg.transform.flip(self.img, False, True),pg.transform.flip(self.img, False, False)]
        self.rct = self.img.get_rect()
        self.rct.center = bomb.rct.center
        self.life = 100


    def update(self, screen: pg.Surface):
        """
        爆発画像をアニメーションさせる
        """
        self.life -= 1
        self.img = self.imgs[self.life % 4]
        screen.blit(self.img, self.rct)
        
class Score:

    """
    スコアに関するクラス
    """
    def __init__(self):
        """
        スコアを0に初期化する
        """
        self.score = 0
        self.font = pg.font.SysFont("hgp創英角ポップ体", 30)
        self.color = (0, 0, 255)
        self.img = self.font.render(f"SCORE:{self.score}", 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT-50)

    def update(self, screen: pg.Surface):
        """
        スコアを更新する
        """
        self.img = self.font.render(f"SCORE:{self.score}", 0, self.color)
        screen.blit(self.img, self.rct)

class Limit:
    def __init__(self):
        self.limit = 10000000000
        self.font = pg.font.SysFont("hgp創英角ポップ体", 30)
        self.color = (255, 0, 0)
        self.img = self.font.render(f"LIMIT:{self.limit}", 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT-100)

    def update(self, screen: pg.Surface):
        # 制限時間を更新する
        self.img = self.font.render(f"LIMIT:{self.limit}", 0, self.color)
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS+1)]
    ex_bombs = []
    beam = None
    score = Score()
    limit = Limit()

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam = Beam(bird)   # ビームクラスのインスタンスを生成する



        
        screen.blit(bg_img, [0, 0])
        for i,bomb in enumerate(bombs):
            if bomb is not None:
                bomb.update(screen)
                if bird.rct.colliderect(bomb.rct):
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
                if limit.limit == 0:
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
                if beam is not None:
                    if bomb.rct.colliderect(beam.rct):
                        # 爆弾とビームが衝突したら，爆弾を消去する
                        bombs[i] = None
                        beam = None
                        bird.change_img(6, screen)
                        Explosion(bomb).update(screen)
                        ex_bombs.append(Explosion(bomb))
                        score.score += 1
        
                        
                        pg.display.update()
        


        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        
        bombs = [bomb for bomb in bombs if bomb is not None]
        ex_bombs = [ex_bomb for ex_bomb in ex_bombs if ex_bomb.life > 0]
        if bomb is not None:
            bomb.update(screen)
        if beam is not None:
            beam.update(screen)
        second = tmr // 50
        limit.limit -= second
        score.update(screen)
        limit.update(screen)
        pg.display.update()
        tmr += 1
        
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()