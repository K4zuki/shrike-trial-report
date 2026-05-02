# まえがき {-}

## このドキュメントは何 {-}

この本はインド製FPGAボード「Shrike Lite」を直接購入し、MicroPython環境での使い方を解説したドキュメントです。
2025年、インドの企業Vicharak社がRP2040マイコンとSLG34970/ForgeFPGAを載せた製品「Shrike Lite」を発表しました。
筆者は先行販売に申し込み、2025年11月に2個入手しました。また今年1月に秋月電子からも発売され、早々に売り切れてしまいました（4月に再入荷らしいです）。

## この本で解説する範囲 {-}

この本では、まだボードを購入していない方のために、回路構成・開発ソフト類の使い方を解説したいと思います。なお、ボードの回路図や
RP2040のデフォルトファームウェアはVicharak社のGitHubリポジトリで公開・配布されています。
その他開発に関するヘルプもGitHub上に一通り揃っています。

上記ヘルプサイトでは、FPGAのビットストリーム生成はルネサスの専用ソフトを使い、転送はArduinoまたはMicroPython系の
RP2040ファームに埋め込む方法が解説されていますが、埋め込みのために毎度ビルドするのはかなり面倒くさいです（筆者の感想です）。

そこで本書ではまずRP2040のファームをPico向けのMicroPythonバニライメージに入れ替えます^[工場出荷ファームにちょっとした問題を見つけたので、消しました]。
FPGAバイナリの生成は本家と同じ方法^[いまのところ他に手段はないです。RTLはCLIでできるけどP&Rができません。]ですが、ファイルシステムへの転送は
`mpremote`コマンドを使い、さらにマイコン-FPGA間転送用スクリプト`McuBoot.py`を使ってRP2040からFPGAに転送します。

次に、FPGAはSPIフラッシュメモリからもロードできる機能を持っているので、ボードを改造してフラッシュブートも試します。
SPIフラッシュに書き込むスクリプト`FlashBoot.py`がフラッシュへの書き込みとFPGAへのロードを操作します。

`McuBoot.py`と
`FlashBoot.py`は別途あらかじめRP2040側にいれておきます^[転送スクリプトはファームに埋め込んでもよい。とにかくファームをビルドする回数を減らしたい]。

Arduino式は試していませんが、MicroPythonと`mpremote`のほうが簡単ということを説明したいと思います。

## おことわり {-}

読者の方が再現する場合は開発PCを用意して、Git/PythonとFPGA開発ソフトを入れる必要があります。
また、SPIフラッシュからのロードを試すときは**ボードの改造が必要です**。*比較的*簡単な方法を後述します。
根性と技術のある方は別途フラッシュROMを入手し、正しく配線しておいてください。

開発PCはWindowsを前提にします。FPGAソフトのバージョンは**6.53**を使いました。少し前の6.4x/5xバージョンでもおそらく大丈夫ですが未検証です。

\newpage

\toc

# 下準備

開発PCの準備をします。 PythonとFPGA開発ソフト「Go Configure Software Hub」をインストールし、MCUのファームウェアをピコ相当に入れ替えます。

## Python

3.7以降ならどのバージョンでもいいです。`winget`やストア経由でインストールしてください。
すでに入っているなら追加する必要はありません。以下コマンド例：

```shell 
winget install Python.Python.3.14
```

## この本の原稿リポジトリをクローンしてvenv

任意のフォルダに移動して原稿リポジトリをクローンします。本家リポジトリもサブモジュールとして同時にダウンロードされます。
クローンしたフォルダに移動してvenvを設定します。：

```shell
cd C:\Users\<username>\<workspace>
git clone https://github.com/K4zuki/shrike-trial-report.git --recursive
cd shrike-trial-report
python -m venv venv 
```

`examples`以下にサンプルプロジェクトが揃っています（後ほど動作確認に使います）。

### mpremote

`mpremote`はMicroPython用ツールセットです。REPLの起動・ファイルの転送・ライブラリインストール・スクリプトの遠隔実行などに使います。
venvを切り替えたあとで`pip`でインストールします：

```shell 
.\venv\Scripts\activate
pip install mpremote
```

## MCUのファームを差し替える

Micropythonの公式ページから[ラズピコ用UF２ファームウェア](https://micropython.org/resources/firmware/RPI_PICO-20260406-v1.28.0.uf2)
をダウンロードします。どのバージョンでもいいと思いますが、とりあえず最新版にします。

## MCUに転送スクリプト一式を移動する

`McuBoot.py`、`FlashBoot.py`、`main.py`を`mpremote`で順次転送します。

- `mpremote connect <COM port> cp McuBoot.py :`
- `mpremote connect <COM port> cp FlashBoot.py :`
- `mpremote connect <COM port> cp main.py :`

## Go Configure Software Hub

# Shrike Lite

Shrikeはホストになるマイコンによって複数種類のバージョンがあり、LiteはRP2040がホストマイコンになっています。
RP2350版はクラウドファンディングが行われており、すぐには入手できない状態です。

[@fig:shrike-pinout]にピン配置を示します。

![ピン配置（公式ドキュメントより抜粋）](shrike/docs/images/shrike_pinouts.svg){height=158mm #fig:shrike-pinout}

\newpage

## 入手したくなったら

本家直販または秋月電子通商から購入できます。4月入荷予定が5月になるなど、入荷状況は不安定なようです。

## 電源

ホストマイコン及びFPGAのIO電源用に3.3Vレギュレータ、FPGAのコア電源用に1.1Vレギュレータが搭載されています。両方ともUSBまたはボードのピンから5Vを受ける構成になっています。
フラッシュロード周りで気になることがあったので、1.1Vレギュレータは後ほど改造します。

## RP2040（マイコン）

<https://vicharak-in.github.io/shrike/shrike_pinouts.html#fpga-cpu-interconnect-pin-outs>

Raspberry Pi Pico（ラズピコ）相当の回路が載っています。UF2ファームウェアもラズピコ用が使えます。GPIO0～3（SPI0バス）と12～15（EN・PWR・汎用2本）がFPGAと直結されています（[@fig:shrike-pinout]）。

![ピン対応表（公式ドキュメントより抜粋）](images/interconnect-table.png){width=150mm}

## SLG34970（FPGA）

24ピンQFN版が載っています。SPIブートのための４本とEN・PWR・汎用２本がホストマイコンと直結されています。
このうちSPIバスの４本にはテストパッドが用意されています。後ほど改造に使います。

> Configuration Modes
> An internal configuration wrapper is used to configure the ForgeFPGA core and the GoConfigure software is
> used to generate the bitstream. The configuration can be done using three different configuration bitstream
> sources:
> 8.1.1 External SPI Flash (SPI Master Mode)
> In this mode the SLG47910 operates as the SPI Master, and the external SPI Flash is the SPI Slave device.
> During SPI mode, GPIO3 is used to output the SPI_SCLK, while GPIO4, GPIO5, and GPIO6 are used as
> SPI_SS, SPI_SI, and SPI_SO respectively. To enter SPI Master mode, the SPI_SS line should be HIGH when
> the chip configuration process starts.
> 8.1.2 MCU as a host (SPI Slave Mode)
> In this mode the SLG47910 is the SPI Slave device and a connected MCU is the SPI Master. During SPI mode,
> GPIO3 is used as the SPI_SCLK input, while GPIO4, GPIO5, and GPIO6 are used as SPI_SS, SPI_SI, and
> SPI_SO respectively. To enter MCU Slave mode, the SPI_SS line should be LOW when the chip configuration
> process starts.

\newpage

## ピン配置

FPGAの入出力方向はロードの方法にかかわらず不変です。つまり、たとえばMPUロードもフラッシュロードもGPIO5がデータを受け取るピンなのですが、
SPIバスの命名規則ではMOSI（MPUからロード）になったりMISO（フラッシュからロード）になったりします。

# サンプルプロジェクトをコンパイルしてみる

examplesフォルダのサンプルプロジェクトをコンパイルしてみます。おそらく工場出荷ファームウェアに埋め込まれているものと同じものです。
`examples/led_blink/led_blink.ffpga`をGoConfigureで開きます。

# FPGAのブート：マイコンから毎度書き込む（SPIスレーブモード）

RP2040から直接FPGAバイナリを転送します。

```text
46408 Mar 29 15:07 FPGA_bitstream_MCU.bin
```

## 転送スクリプトの転送（一度だけ実行）

```shell
mpremote connect <COM port> cp McuBoot.py :
```

## 転送スクリプト

[スクリプト例（本家GitHubより改変）](data/McuBoot.py){.listingtable .python}

## 書き込み手順

```shell
mpremote connect <COM port> run ./McuBoot.py
```

# FPGAのブート：SPIフラッシュから読み込む（SPIマスターモード）

```text
45096 Mar 29 15:07 FPGA_bitstream_FLASH_MEM.bin
```

## Shrikeボードを改造する

ボード上に用意されているテストパッドとIO8～11を接続します。テストパッドが小さいので、0.2～0.3mm^2^ のUEW（いわゆるエナメル線）が使いやすいです。
IO10とCLKのジャンパ線は、コンデンサがあるのでちょっと遠回りになりましたが、まあ大丈夫です。
本来は間に100オームくらいが入っていると安心ですが、手持ちがないので直結しました。

::: {#fig:board-mod-examples}

![接続図](images/board-mod-plan.jpg){height=120mm #fig:board-mod-examples-1}

![実装例](images/board-mod-example.jpg){height=120mm #fig:board-mod-examples-2}

Figure: Shrikeボードを改造する

:::

\newpage

## SPIフラッシュメモリモジュールを自作する

![自作フラッシュメモリモジュール（W25Q16JVUXIQ）](images/spi-flash-module-craft-1.png){width=120mm}

## フラッシュ書き込み

RP2040からフラッシュに書き込むときは、SPI1バスを使用します。

# 関連コード全文掲載シリーズ

## `McuBoot.py`

[`McuBoot.py`](data/McuBoot.py){.python #lst:mcuboot-py .listingtable}

\newpage

## `FlashBoot.py`

[`FlashBoot.py`](data/FlashBoot.py){.python #lst:flashboot-py .listingtable}

\newpage

## `main.py`

[`main.py`](data/main.py){.python #lst:main-py .listingtable}

\newpage

## `shrike/examples/led_blink/ffpga/src/main.v`

[`main.v`](shrike/examples/led_blink/ffpga/src/main.v){.verilog #lst:main-v .listingtable}

# 参考リンク集 {.appendix}

## 参考文献 {-}

- [秋月電子/Shrike-lite]{#ref-akizuki-shrike}
    - <https://akizukidenshi.com/catalog/g/g131458/>
- [Vicharak/shrike (GitHub)]{#ref-shrike-github}
    - <https://github.com/vicharak-in/shrike>
    - Tag v1.0.0
        - <https://github.com/vicharak-in/shrike/releases/tag/v1.0.0>
    - ドキュメントページ
        - <https://vicharak-in.github.io/shrike/>
- [ルネサス/Configuration guide]{#ref-configuration-guide}
    - <https://www.renesas.com/ja/document/mah/forgefpga-configuration-guide>
    - R19US0005EU0250 Rev.2.5 / Jan 28, 2026
- [ルネサス/SLG47910 Datasheet]{#ref-slg47910-datasheet}
    - <https://www.renesas.com/ja/document/dst/slg47910-datasheet?r=25546631>
    - R19DS0120EU0105 Rev 1.05 / Apr 7, 2025
- [ルネサス/開発ソフト（ユーザ登録とログインが必要）]{#ref-ide-download}
    - <https://www.renesas.com/ja/software-tool/go-configure-software-hub>
- [ルネサス/開発ソフトマニュアル]{#ref-ide-manual}
    - <https://www.renesas.com/ja/document/gde/forgefpga-workshop-user-guide>
    - R19US0007EU0202 Rev.2.02 / Dec 1, 2025
    - バージョン6.51が対象
- Micropython/UF2ファームウェア []{#ref-micropython-rpi-pico-firmware}
    - <https://micropython.org/download/RPI_PICO/>
- SPIフラッシュ読み書きスクリプト []{#ref-spi-flash-handler}
    - <https://github.com/SpotlightKid/micropython-stm-lib/blob/master/spiflash/spiflash.py>

\newpage

## 関連部品リスト {-}

- <https://www.renesas.com/ja/products/at25xe011>
- スイッチサイエンス/2MバイトSPIシリアルフラッシュメモリブレークアウト基板（レベルシフト回路搭載）[]{#ref-ssci-flash-w25q}
    - <https://www.switch-science.com/products/8593>
    - Winbond/W25Q16JVSSIQ 16Mbit SOP8
        - <https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en&partNo=W25Q16JVSSIQ>
- 秋月電子/フラッシュメモリー W25Q16JVUXIQ []{#ref-akizuki-flash-w25q}
    - 16Mbit
    - https://akizukidenshi.com/catalog/g/g117346/
    - Winbond/W25Q16JVUXIQ 16Mbit USON8
        - <https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en&partNo=W25Q16JVUXIQ>
- 秋月電子/VSSOP8 0.5mmピッチIC(8ピン)変換基板 []{#ref-akizuki-vssop8-board}
    - https://akizukidenshi.com/catalog/g/g106076/
- 秋月電子/フラッシュメモリー IS25LP040E []{#ref-akizuki-flash-is25}
    - 4Mbit
    - <https://akizukidenshi.com/catalog/g/g118046/>
- 秋月電子/SOP8(1.27mm)DIP変換基板 金フラッシュ []{#ref-akizuki-sop8-board}
    - https://akizukidenshi.com/catalog/g/g105154/
- 秋月電子/チップ抵抗 1608 1/8W100&Omega;
    - <https://akizukidenshi.com/catalog/g/g130347/>
- 秋月電子/チップ抵抗 1608 1/10W10k&Omega;
    - <https://akizukidenshi.com/catalog/g/g130355/>

# あとがき {-}

- ピン配置図生成には[Pinout Leaf Generator](https://github.com/marcteale/pinoutleaf?tab=readme-ov-file#pinout-leaf-generator-)
  を使いました。SVG-PNG変換は、いつものrsvgだと崩れてしまうので、ネットで見つけたツール<https://amamamaou.github.io/svg2png/>を使用しました。
