#akari本体から実行するプログラム
from rmtp import RMTP
from media import Media

def main()->None:

    #これを繰り返す
    rmtp=Media()
    rmtp.akari_random_move()
    rmtp.close()

if __name__ == "__main__":
    main()