python で書かれたの mmd 表示ライブラリ<br>まだ途中。
pmx, pmd, vmd 対応(一部、確認していないモデルがあります)<br>
物理演算、今後対応予定<br>

# Reference
```python
# 表示機能作成
model = mmdpy.model()

# モデル読み込み
model.load(<model path>)

# モーション命名
model.motion(<motion name>)

# モーション読み込み
model.motion(<motion name>).load(<motion path>)

# モーションを 1[step] 実行
model.motion(<motion name>).step()

# モーションの終了判定
mode.motion(<motion name>).finish()

# 表示
model.draw()

# ボーン構造の表示
model.bonetree()

# ボーンの移動(IK)
model.bone(<bone name>).move(<position 3d vector>)

# ボーンの移動(強制)
model.bone(<bone name>).slide(<position 3d vector>)

# ボーンの回転
model.bone(<bone name>).rotX(<rotation>)
model.bone(<bone name>).rotY(<rotation>)
model.bone(<bone name>).rotZ(<rotation>)
model.bone(<bone name>).rot(<axis>, <rotation>)

# ボーンの場所取得
model.bone(<bone name>).get_position() -> <position 3d vector>

# モーションの上書き、追加
<ボーン回転、移動>
model.motion(<motion name>).reflection()

# モーションの保存(調整中)
model.motion(<motion name>).save(<file name>)
```

# Demo code
```bash
# GLFW を用いた実装
$ python demo/sample_glfw.py -p <pmd, pmx model path> -v <vmd motion path>

# 古典的なOpenGLの実装
$ python demo/sample_legacy.py -p <pmd, pmx model path> -v <vmd motion path>
```

# 簡単に使う場合
```python
## demo/sample_easy.py
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
```
