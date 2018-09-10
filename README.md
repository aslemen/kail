# kail
## 目的
（Penn Treebank形式で用いられるような）括弧の代わりに，
インデントを用いて，Kainokiデータを表現する文法を策定する．
また，従来のPenn形式との相互変換も提供する．

## 美点
括弧の管理から解放される．
インデントの管理はしておく必要があるが，
インデントをはっきりと示してくれるエディターのプラグインがあるので，事故を防ぐことはより簡単になる．

## 難点
他のプログラム（Tregex GUI，Tsurgeon）などとの連携は難しい．
現状では，編集時になったら形式をKailに変換して，
その他のときはPenn形式に戻すとかしないといけない．

## 依存するPython3 パッケージ
- click（コマンドライン・ジェネレーター）
- setup

## インストール（暫定）
```sh
python3 setup.py develop --user
```

## コンパイル
```sh
nuitka kail --recurse-all
```

## アンインストール
```sh
python3 setup.py develop --uninstall

```

## 使い方
### Usage
```sh
kail [OPTIONS]
```

### Options
```
  -i, --input_format [penn|kail]
  -o, --output_format [penn|kail]
  --comments / --no_comments コメントを除去するか否か
  --compact / --pretty 1行形式か，複数行形式化（-o pennの場合のみ）
  -r, --input_file FILENAME 入力ファイル名（デフォルト：standard input）
  -w, --output_file FILENAME　出力ファイル名（デフォルト：standard output）
  --help                          Show this message and exit.
```

特に，`-i`と`-o`を同じ形式にすると，ちょうどデータの整形ができるようになるので，
そのような目的で使うこともできる．

## サンプル
### Kail
```
S
    IP-MAT
        PP-SBJ 0 {TARO}
            NP
                NPR
                        太郎　# 太郎は靴紐を結んでいなかったので当然ではある．
            P-OPTR
                        は
        VB
                        転ん
        AXD
                        だ
    ID
                        2;kai_test
```
上のように，終端ノードだけを突出させることも可能！

### 対応するPenn形式
```
(S (IP-MAT (PP-SBJ;{TARO} (NP (NPR 太郎))
                          ;; 太郎は靴紐を結んでいなかったので当然ではある．
                          (P-OPTR は))
                  (VB 転ん)
                  (AXD だ))
    (ID 2_kai_test))
```
