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
- NLTK
- click
- pathlib
- setup

## インストール（暫定）
```sh
python3 setup.py develop --user
```

## アンインストール
```sh
python3 setup.py develop --uninstall

```

## 使い方
### Penn -> Kail
入力はファイルを通してのみである（標準入力を使う場合は，一旦一時ファイルに保存しておく）．
こういう面倒くさい仕様は，NLTKのせいである．
```sh
kail simplize <file>
```

### Kail -> Penn
入力は標準入力を通してのみである．
```sh
(cat <file>) | kail recover 
```

## サンプル
### Kail
```
S
    IP-MAT
        PP-SBJ 0 {TARO}
            NP
                NPR
                        太郎
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
                          (P-OPTR は))
                  (VB 転ん)
                  (AXD だ))
    (ID 2_kai_test))
```
