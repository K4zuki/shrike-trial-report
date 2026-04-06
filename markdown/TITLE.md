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

そこで筆者はまずRP2040のファームをPico向けのMicroPythonバニライメージに入れ替えました^[工場出荷ファームにちょっとした問題を見つけたので、消しました]。
FPGAバイナリの生成は本家と同じ^[というか他に手段はないです]ですが、ファイルシステムへの転送は`mpremote`コマンドを使い、
さらにマイコン-FPGA間転送用スクリプト`rp2slg.py`(仮)を使ってRP2040からFPGAに転送します。
`rp2slg.py`(仮)は別途あらかじめRP2040側にいれておきます^[転送スクリプトはファームに埋め込んでもよい。とにかくファームをビルドする回数を減らしたい]。

次に、FPGAはSPIフラッシュメモリからもロードできる機能を持っているので、ボードを改造してフラッシュブートも試します。
SPIフラッシュに書き込むスクリプト`rom_writer.py`(仮)を用意してFPGAバイナリ

Arduino式は試していませんが、MicroPythonと`mpremote`のほうが簡単ということを説明したいと思います。

## おことわり {-}

読者の方が再現する場合はホストPCにPythonとFPGA開発ソフトを入れておく必要があります。
また、SPIフラッシュからのロードを試すときは別途フラッシュROMを入手し、正しく繋いでおく必要があります。

開発PCはWindowsを前提にします。FPGAソフトのバージョンは**6.53**を使いました。少し前の6.4x/5xバージョンでもおそらく大丈夫ですが未検証です。

## 参考文献 {-}

- Vicharak/shrike (GitHub)
    - <https://github.com/vicharak-in/shrike>
- ルネサス/Configuration guide
    - <https://www.renesas.com/ja/document/mah/forgefpga-configuration-guide>
- ルネサス/SLG47910 Datasheet
    - <https://www.renesas.com/ja/document/dst/slg47910-datasheet?r=25546631>
- ルネサス/開発ソフト
    - <https://www.renesas.com/ja/software-tool/go-configure-software-hub>
- ルネサス/開発ソフトマニュアル
    - <https://www.renesas.com/ja/document/gde/forgefpga-workshop-user-guide>
- スイッチサイエンス/2MバイトSPIシリアルフラッシュメモリブレークアウト基板（レベルシフト回路搭載）
    - <https://www.switch-science.com/products/8593>
    - Winbond/W25Q16JVSSIQ 16Mbit SOP8
        - <https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en&partNo=W25Q16JVSSIQ>
- 秋月電子/フラッシュメモリー W25Q16JVUXIQ
    - 16Mbit
    - https://akizukidenshi.com/catalog/g/g117346/
    - Winbond/W25Q16JVUXIQ 16Mbit USON8
        - <https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en&partNo=W25Q16JVUXIQ>
- 秋月電子/フラッシュメモリー IS25LP040E
    - 4Mbit
    - <https://akizukidenshi.com/catalog/g/g118046/>
- 秋月電子/Shrike-lite
    - <https://akizukidenshi.com/catalog/g/g131458/>
- Micropython/UF2ファームウェア
    - <https://micropython.org/download/RPI_PICO/>
- SPIフラッシュ読み書きスクリプト
    - <https://github.com/SpotlightKid/micropython-stm-lib/blob/master/spiflash/spiflash.py>

\toc

# 下準備

開発マシンにPythonとFPGA開発ソフト「Go Configure Software Hub」をインストールします。

## Python

3.7以降ならどのバージョンでもいいです。`winget`やストア経由でインストールしてください。

```shell 
winget install Python.Python.3.14
```

## 本家リポジトリをクローンしてvenv

任意のフォルダに移動して本家リポジトリをクローンします。クローンしたフォルダに移動してvenvを設定します。

```shell
cd C:\Users\<username>\<workspace>
git clone https://github.com/vicharak-in/shrike.git
cd shrike
python -m venv venv 
```

`examples`以下にサンプルプロジェクトが揃っています（後ほど動作確認に使います）。

### mpremote

`mpremote`はmicropython用ツールセットです。venvを起動したあとで`pip`でインストールします。

```shell 
.\venv\Scripts\activate
pip install mpremote
```

## MCUのファームを差し替える

## Go Configure Software Hub

# Shrike Lite

ShrikeはホストになるマイコンがRP2350かRP2040かで２種類のバージョンがあり、LiteはRP2040がホストマイコンになっています。
RP2350版はクラウドファンディングが行われており、すぐには入手できない状態です。

## 入手したくなったら

本家直販または秋月電子通商から購入できます。

## 電源

ホストマイコン及びFPGAのIO電源用に3.3Vレギュレータ、FPGAのコア電源用に1.1Vレギュレータが搭載されています。両方ともUSBまたはボードのピンから5Vを受ける構成になっています。

## RP2040（マイコン）

Raspberry Pi Pico（ラズピコ）相当の回路が載っています。UF2ファームウェアもラズピコ用が使えます。GPIO0～3（SPI0バス）と12～15（EN・PWR・汎用2本）がFPGAと直結されています（[@fig:shrike-pinout]）。

## SLG34970（FPGA）

24ピンQFN版が載っています。SPIブートのための４本とEN・PWR・汎用２本がホストマイコンと直結されています。

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

[@fig:shrike-pinout]にピン配置を示します。

![ピン配置](https://vicharak-in.github.io/shrike/_images/shrike_pinouts.svg){width=150mm #fig:shrike-pinout}

FPGAの入出力方向はロードの方法にかかわらず不変です。つまり、たとえばMPUロードもフラッシュロードもGPIO5がデータを受け取るピンなのですが、
SPIバスの命名規則ではMOSI（MPUからロード）になったりMISO（フラッシュからロード）になったりします。

# サンプルプロジェクトをコンパイルしてみる

# FPGAのブート：マイコンから毎度書き込む（SPIスレーブモード）

```text
46408 Mar 29 15:07 FPGA_bitstream_MCU.bin
```

## 転送スクリプトの転送（一度だけ実行）

```shell
mpremote connect <COM port> cp rp2slg.py :
```

## 転送スクリプト

[スクリプト例（本家GitHubより改変）](data/rp2slg.py){.listingtable .python}

## 書き込み手順

```shell
mpremote connect <COM port> run ./rp2slg.py
```

# FPGAのブート：SPIフラッシュから読み込む（SPIマスターモード）

```text
45096 Mar 29 15:07 FPGA_bitstream_FLASH_MEM.bin
```

## フラッシュ書き込み

RP2040からフラッシュに書き込むときは、SPI1バスを使用します。

# あとがき {-}

- ピン配置図生成には[Pinout Leaf Generator](https://github.com/marcteale/pinoutleaf?tab=readme-ov-file#pinout-leaf-generator-)
  を使いました。SVG-PNG変換は、いつものrsvgだと崩れてしまうので、ネットで見つけたツール<https://amamamaou.github.io/svg2png/>を使用しました。
