# mmdpy
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
```

# demo code
```bash
$ python demo/sample_glfw.py -p <pmd, pmx model path> -v <vmd motion path>      # GLFW を用いた実装
$ python demo/sample_legacy.py -p <pmd, pmx model path> -v <vmd motion path>    # 古典的なOprnGLの実装
```
