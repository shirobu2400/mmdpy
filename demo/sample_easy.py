import mmdpy
import mmdpy_world
import argparse


def main():
    # 引数パーサー
    parser = argparse.ArgumentParser(description="MMD model viewer sample.")
    parser.add_argument("-p", type=str, help="MMD model file name.")
    parser.add_argument("-v", type=str, help="MMD motion file name.")
    args = parser.parse_args()

    # ワールドを生成
    world: mmdpy_world.world = mmdpy_world.world("mmdpy", 640, 480)

    # モデルを読み込み
    model: mmdpy.model = mmdpy.model()
    if args.p is not None and not model.load(args.p):
        print("model load error.")
        exit(0)

    # ワールドにモデルを登録
    world.push(model)

    # モーションを読み込み
    if args.v is not None and not model.motion("motion").load(args.v):
        print("motion load error.")
        exit(0)

    # メインループ
    while True:

        # モーションを実行
        model.motion("motion").step()

        # 登録されているモデルの表示処理一括実行
        if world.run():
            break

    # 終了処理
    world.close()


if __name__ == "__main__":
    main()
