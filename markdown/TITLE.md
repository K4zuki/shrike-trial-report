# まえがき {-}

## このドキュメントは何 {-}

この本はインド製FPGAボード「Shrike Lite」を直接購入し、MicroPython環境での使い方を解説したドキュメントです。
2025年、インドの企業Vicharak社がRP2040マイコンとSLG34970/ForgeFPGAを載せた製品「Shrike Lite」を発表しました。
筆者は先行販売に申し込み、2025年11月に2個入手しました。また今年1月に秋月電子からも発売され、早々に売り切れてしまいました（5月に再入荷されました）。

## この本で解説する範囲 {-}

この本では、まだボードを購入していない方のために、回路構成・開発ソフト類の使い方を解説したいと思います。なお、ボードの回路図や
RP2040のデフォルトファームウェアはVicharak社のGitHubリポジトリで公開・配布されています。
その他開発に関するヘルプもGitHub上に一通り揃っています。

上記ヘルプサイトでは、FPGAのビットストリーム生成はルネサスの専用ソフトを使い、転送はArduinoまたはMicroPython系の
RP2040ファームに埋め込む方法が解説されていますが、埋め込みのために毎度ビルドするのはかなり面倒くさいです（筆者の感想です）。

そこで本書ではまずRP2040のファームをPico向けのMicroPythonバニライメージに入れ替えます^[工場出荷ファームにちょっとした問題を見つけたので、消します]。
FPGAバイナリの生成は本家と同じ方法ですが、デバイスへの転送は[mpremote]{custom-style="PreprocessorTok"}コマンドを使い、
さらにマイコン-FPGA間転送用スクリプト[McuBoot.py]{custom-style="PreprocessorTok"}を使ってRP2040からFPGAに転送します。

次に、FPGAはSPIフラッシュメモリからもロードできる機能を持っているので、ボードを改造してフラッシュブートも試します。
SPIフラッシュに書き込むスクリプト[FlashBoot.py]{custom-style="PreprocessorTok"}がフラッシュへの書き込みとFPGAへのロードを操作します。

[McuBoot.py]{custom-style="PreprocessorTok"}と[FlashBoot.py]{custom-style="PreprocessorTok"}は
別途あらかじめRP2040側にいれておきます^[転送スクリプトはファームに埋め込んでもよい。とにかくファームをビルドする回数を減らしたい]。

Arduino式は試していませんが、MicroPythonと[mpremote]{custom-style="PreprocessorTok"}のほうが簡単ということを説明したいと思います。

## おことわり {-}

読者の方が再現する場合は開発PCを用意して、Git/PythonとFPGA開発ソフトを入れる必要があります。
また、SPIフラッシュからのロードを試すときは**ボードの改造が必要です**。*比較的*簡単な方法を後述します。
根性と技術のある方は別途フラッシュROMを入手し、正しく配線しておいてください。

開発PCはWindowsを前提にします。FPGAソフトのバージョンは**6.53**を使いました。少し前の6.4x/5xバージョンでもおそらく大丈夫ですが未検証です。

Shrike Lite本体のリビジョンは1月入荷版の**V1.0 R0.4**を対象にします。

\newpage

\toc

# 下準備

開発PCの準備をします。 PythonとFPGA開発ソフト「Go Configure Software Hub」をインストールし、MCUのファームウェアをピコ相当に入れ替えます。

## Python

3.7以降ならどのバージョンでもいいです。[winget]{custom-style="PreprocessorTok"}やストア経由でインストールしてください。
すでに入っているなら追加する必要はありません。以下コマンド例：

```bash 
winget install Python.Python.3.14
```

## この本の原稿リポジトリをクローンしてvenv {#sec:clone-and-venv}

任意のフォルダに移動して原稿リポジトリをクローンします。本家リポジトリもサブモジュールとして同時にダウンロードされます。
クローンしたフォルダに移動して[venv]{custom-style="PreprocessorTok"}を設定します。：

```bash
cd C:\Users\<username>\<workspace>
git clone https://github.com/K4zuki/shrike-trial-report.git --recursive
cd shrike-trial-report
python -m venv venv
```

[examples]{custom-style="PreprocessorTok"}以下にサンプルプロジェクトが揃っています（後ほど動作確認に使います）。

### mpremote

[mpremote]{custom-style="PreprocessorTok"}はMicroPython用ツールセットです。
REPLの起動・ファイルの転送・ライブラリインストール・スクリプトの遠隔実行などに使います。
venvを切り替えたあとで[pip]{custom-style="PreprocessorTok"}でインストールします：

```bash 
.\venv\Scripts\activate
pip install mpremote
```

## MCUのファームを差し替える

Micropythonの公式ページから[ラズピコ用UF２ファームウェア](https://micropython.org/resources/firmware/RPI_PICO-20260406-v1.28.0.uf2)
をダウンロードします。どのバージョンでもいいと思いますが、とりあえず執筆時点の最新版`RPI_PICO-20260406-v1.28.0.uf2`にしました。
ShrikeのBOOTボタンを押しながらRSTを押すか、[mpremote]{custom-style="PreprocessorTok"}でブートローダを起動します。

```bash 
mpremote connect <COM port> bootloader
```

新しいドライブが出現するので、UF2ファイルをコピーします。
コピーが完了するとドライブは自動的に消えます。完了したら、念のためRSTボタンだけをもう一度押すか、USBケーブルを抜き差しします。

## MCUに関連スクリプト一式を転送する {#sec:copy-loader-scripts}

[BusPins.py]{custom-style="PreprocessorTok"}、[McuBoot.py]{custom-style="PreprocessorTok"}、
[FlashBoot.py]{custom-style="PreprocessorTok"}、
[spiflash.py]{custom-style="PreprocessorTok"}、[main.py]{custom-style="PreprocessorTok"}を
[examples]{custom-style="PreprocessorTok"}で順次転送します。
これらのファイルは[data]{custom-style="PreprocessorTok"}ディレクトリ内にあります。

```bash
cd data
mpremote connect <COM port> cp BusPins.py :
mpremote connect <COM port> cp McuBoot.py :
mpremote connect <COM port> cp FlashBoot.py :
mpremote connect <COM port> cp spiflash.py :
mpremote connect <COM port> cp main.py :
```

## Go Configure Software Hub

# Shrike Lite

Shrikeはホストになるマイコンによって複数種類のバージョンがあり、LiteはRP2040がホストマイコンになっています。
RP2350版はクラウドファンディングが行われており、すぐには入手できない状態です。

[@fig:shrike-pinout]にピン配置を示します。

![ピン配置（公式ドキュメントより抜粋）](shrike/docs/images/shrike_pinouts.svg){height=158mm #fig:shrike-pinout}

\newpage

## 入手したくなったら

本家直販または秋月電子通商から購入できます。5月に秋月に再入荷したものは以前とはリビジョンが異なるので注意が必要です。
先述の通り、この本では旧リビジョン**V1.0 R0.4**を対象にします。

## 電源

ホストマイコン及びFPGAのIO電源用に3.3Vレギュレータ、同じくコア電源用に1.1Vレギュレータが搭載されています。両方ともUSBまたはボードのピンから5Vを受ける構成になっています。
1.1Vレギュレータは抵抗分圧で出力電圧を設定する可変タイプです。

- 3.3Vレギュレータ： Diodes AP2112K-3.3TRG1 3.3V/600mA
    - <https://www.digikey.jp/ja/products/detail/diodes-incorporated/AP2112K-3-3TRG1/4470746>
- 1.1Vレギュレータ： Shenzhen Slkormicro Semicon Co., Ltd. SL6206-ADJMR 可変/300mA
    - <https://www.digikey.jp/ja/products/detail/shenzhen-slkormicro-semicon-co-ltd/SL6206-ADJMR/27519079>

## RP2040（マイコン）

> MCU-FPGA間のピン対応表がヘルプページに用意されています。抜粋するので、参考にしてください。
> <https://vicharak-in.github.io/shrike/shrike_pinouts.html#fpga-cpu-interconnect-pin-outs>
>
> ![](images/interconnect-table.png){width=130mm}
>

\newpage

Raspberry Pi Pico（ラズピコ）相当の回路が載っています。UF2ファームウェアもラズピコ用が使えます。GPIO0～3（SPI0バス）と
12～15（EN・PWR・汎用2本）がFPGAと直結されています（[@fig:shrike-pinout]）。
また、GPIO4が汎用出力としてLEDにつながっています。Hにすると点灯します。

## SLG34970（FPGA）

24ピンQFN版の**SLG47910V**が載っています。SPIブートのための４本とEN・PWR・汎用２本がホストマイコンと直結されています。
汎用2本は0&Omega;抵抗を介しています。
このうちSPIバスの４本にはテストパッドが用意されています。後ほど改造に使います。また、GPIO16が汎用出力としてLEDにつながっています。Hで点灯します。
改造していてテストパッドが小さいと思ったので開発側に連絡し、大きくしてもらう約束を取りつけましたので、そのうちテストパッド拡大版が出てくると思います。
いつになるかは不明です。

\newpage

### コンフィグレーションガイド曰く

ルネサスの[コンフィグレーションガイド](#ref-configuration-guide)や[データシート](#ref-slg47910-datasheet)によると、
SLG47910以下ForgeFPGAシリーズは外部SPIフラッシュメモリからビットストリームをロードする機能が備わっています。
データシートのフローチャート（[@fig:configuration-sequence]）によると、パワーオンリセット解除時にまずPWRピンの状態を調べます。
PWRが1（H）ならば強制OTPロードフラグの状態を調べ、フラグが立っていなければSPIバスからのロードを試みます。
SPIバスのCSの状態によって外部マスタ(MCUなど)のデータを受けるスレーブモードか、SPIフラッシュROMの内容を読み出すマスタモードかを選びます。
なお、ENピンの状態はロード元選択に寄与しないので、用がなければHに吊っておきます。

![起動シーケンス（コンフィグレーションガイドより抜粋）](images/slg47910-configuration-sequence.png){width=95mm #fig:configuration-sequence}

まとめると、[CSをLにしながらPWRを上げるとMCUロード、CSをHにプルアップしてPWRを上げるとフラッシュロード]{.underline}を行います。
LにするときはMCUがCSを操作、フラッシュロードのときはCSをハイインピーダンス（入力）にすれば済みます。

\newpage

| The SLG47910 device is configured using a single data pin (SPI_SI).
| To enable SPI Configuration:
| Hold GPIO4 (SPI_CS) HIGH for a minimum delay of 1055 μs to enable SPI mode.
| After entering SPI mode, internal logic will release GPIO4 (SPI_CS) from driving through the GPIO.
| The internal Config-Circuit which acts as the controller will control the SPI interface (GPIO3, GPIO4, GPIO5, and
| GPIO6) throughout the FPGA’s configuration.
| The Config-Circuit sends a wake-up command (0xAB) to the SPI flash device first and then it sends a fast read
| command (0x0B).
| The Config-Circuit will generate an internal Config signal, Done = 1.

# サンプルプロジェクトをコンパイルしてみる

examplesフォルダのサンプルプロジェクト"led_blink"をコンパイルしてみます。おそらく工場出荷ファームウェアに埋め込まれているものと同じものです。
GPIO16につながっているLEDを点滅させます（1秒間点灯・1秒間消灯。

> 新規プロジェクトを作るときは
> [公式ドキュメントページ](https://vicharak-in.github.io/shrike/generating_your_first_bitstream.html#shrike-fpga-bitstream-generation-guide)も参考にしてください。

## サンプルの保存場所

Shrike本家リポジトリは下準備([@sec:clone-and-venv])のときにダウンロードされているはずです。

![原稿リポジトリ構造](images/shrike-submodule-structure.png){height=125mm #fig:submodule-structure}

\newpage

## コンパイル手順

### 既存のプロジェクトを開く

GoConfigure（開発環境）を起動して、["Open my file"]{.blue}ボタンから[examples/led_blink/led_blink.ffpga]{custom-style="PreprocessorTok"}を開きます。

![["Open my file"]{.blue}](images/compile-example-project-1.png){width=150mm #fig:compile-example-project-1}

\newpage

### エディタを開く

メイン画面では、ブロックRAMの起動・IOピンのプルアップ設定などができますが、今回はそのままにします。
中央の青いアイコンをダブルクリックするか上部の「**FPGA Editor**」（てんとう虫の右隣）をクリックしてコードエディタが開きます。

![メイン画面](images/compile-example-project-2.png){width=150mm #fig:compile-example-project-2}

\newpage

### ビットストリーム生成 {#sec:build-bitstream}

コードエディタの左下にある"**Synthesize**"（ネットリスト生成）と"**Generate Bitstream**"
（配置配線）をそれぞれクリックして両方がチェックマークになるまで待ちます。

![左下のボタンでコンパイル](images/compile-example-project-3.png){width=150mm #fig:compile-example-project-3}

コンパイルが完了すると[build/bitstream]{custom-style="PreprocessorTok"}フォルダの中にバイナリファイルとテキストファイルが生成されます。
この本では[FPGA_bitstream_MCU.bin]{custom-style="PreprocessorTok"}と
[FPGA_bitstream_FLASH_MEM.bin]{custom-style="PreprocessorTok"}を使います。
[FPGA_bitstream_OTP.bin]{custom-style="PreprocessorTok"}はOTPに焼くときのバイナリなので、手出し無用です。
以下は各ファイルのサイズを調べるコマンド例です。回路の内容でファイルサイズが変わることはありません。

```bash
pwd
```

```shell
.../shrike-trial-report/shrike/examples/led_blink/ffpga/build/bitstream
```

```bash
ls -l
```

```shell 
total 448
-rw-r--r-- 1 kyama 197610 45096 Apr 30 16:59 FPGA_bitstream_FLASH_MEM.bin
-rw-r--r-- 1 kyama 197610 101849 Apr 30 16:59 FPGA_bitstream_FLASH_MEM.txt
-rw-r--r-- 1 kyama 197610 46408 Apr 30 16:59 FPGA_bitstream_MCU.bin
-rw-r--r-- 1 kyama 197610 104801 Apr 30 16:59 FPGA_bitstream_MCU.txt
-rw-r--r-- 1 kyama 197610 45116 Apr 30 16:59 FPGA_bitstream_OTP.bin
-rw-r--r-- 1 kyama 197610 101950 Apr 30 16:59 FPGA_bitstream_OTP.txt
```

\newpage

# FPGAのブート：マイコンから毎度書き込む（SPIスレーブモード）

RP2040から直接FPGAバイナリを転送します。ボードの改造は不要です。

## ローダスクリプト一式の転送

[@sec:copy-loader-scripts]を参照してスクリプト一式をデバイスにコピーします。以下に再掲します。
[FlashBoot.py]{custom-style="PreprocessorTok"}と[spiflash.py]{custom-style="PreprocessorTok"}も
SPIバスの共有のために間接的に必要なので、全部コピーしてしまいます。

```bash
mpremote connect <COM port> cp BusPins.py :
mpremote connect <COM port> cp McuBoot.py :
mpremote connect <COM port> cp FlashBoot.py :
mpremote connect <COM port> cp spiflash.py :
mpremote connect <COM port> cp main.py :
```

## FPGAバイナリ（MCUロード用）を転送

[@sec:build-bitstream]でビルドしたビットストリームファイル[FPGA_bitstream_MCU.bin]{custom-style="PreprocessorTok"}を
デバイスにコピーします。

```bash
cd shrike/examples/led_blink/ffpga/build/bitstream
mpremote connect <COM port> cp FPGA_bitstream_MCU.bin :
```

## 転送スクリプト

工場出荷ファームウェア内に埋め込まれている*と思われる*スクリプトを示します。

[スクリプト例（本家GitHubより抜粋）](shrike/archive/shrike_micropy/shrike_fpga.py){.listingtable .python}

## 書き込み手順

MicroPythonのREPL上で[mcuboot.load(flashboot)]{custom-style="PreprocessorTok"}を打ち込むとMCUからのロードが実行されます。

# FPGAのブート：SPIフラッシュから読み込む（SPIマスターモード）

## FPGAバイナリ（フラッシュロード用）を転送

[@sec:build-bitstream]でビルドしたビットストリームファイル[FPGA_bitstream_FLASH_MEM.bin]{custom-style="PreprocessorTok"}を
デバイスにコピーします。

```bash
cd shrike/examples/led_blink/ffpga/build/bitstream
mpremote connect <COM port> cp FPGA_bitstream_FLASH_MEM.bin :
```

## フラッシュメモリの品種品種選定

#### 64kB(512kb)以上あれば何でもいいはず {-}

[@sec:build-bitstream]で確認したとおり、FPGAバイナリのファイルサイズは45kB程度なので、フラッシュメモリの容量は64kB(512kbit)またはそれ以上が必要です。
[コンフィグレーションガイド](#ref-configuration-guide)に載っているフラッシュメモリのリスト（[@fig:compatible-flash-memory]）はおそらく上位品種用です。
大は小を兼ねるので、このリストに従うのもありだと思います。筆者は秋月電子に売っている2品種とスイッチサイエンスに売っているモジュールで実験しました
（[W25Q16JVUXIQ](#ref-akizuki-flash-w25q)、[IS25LP040E](#ref-akizuki-flash-is25)、[W25Q16JVSSIQ](#ref-ssci-flash-w25q)）。

![互換フラッシュメモリの例（コンフィグレーションガイド抜粋）](images/w25q64-in-list.png){width=120mm #fig:compatible-flash-memory}

## Shrikeボードを改造する（１）

ボード上に用意されているテストパッドとSPI1バス（IO8～11）を接続します。パッドの直径が小さいので、0.2～0.3mm&phi;のUEW（いわゆるエナメル線）の使用をおすすめします。
筆者はオヤイデ電気の[0.18mm&phi;UEW 20m巻](#ref-oyaide-uew)を使いました。
MCUロード時に影響しないように、ピンヘッダ側に100オームの直列抵抗を入れます。天地を逆にして白い面を上にするとパッドが大きくてハンダしやすいです。
ピンヘッダのハンダを溶かしたところにチップ抵抗をスライドさせてハンダをなじませるようにして付けます。

テストパッドと抵抗の接続ですが、まずテストパッドにハンダを盛っておきます。つぎに抵抗の端子にUEWをハンダしたあと、つなぐ対象のパッドの中心までまで引っ張って、カッターナイフで切ります。
これを4本繰り返したあとにそれぞれに予備ハンダしてからパッドにつけます。山盛りのハンダに予備ハンダしたUEW線を差し込む感じにするとスムーズです。
顕微鏡やマイクロスコープがあると作業に便利です。

::: {#fig:board-mod-examples}

![接続図](images/board-mod-plan.jpg){height=120mm #fig:board-mod-examples-1}

![実装例](images/board-mod-example.jpg){height=120mm #fig:board-mod-examples-2}

Figure: Shrikeボードを改造する

:::

\newpage

### SPIフラッシュメモリモジュールを購入または自作する {#sec:craft-flash-module}

#### モジュールを購入する場合

#### 自作する場合

[@fig:spi-flash-module-1]に自作モジュールの製作例を示します。秋月電子で売っているSPIシリアルフラッシュ
（[SSOP8](#ref-akizuki-flash-w25q)または[SOP8](#ref-akizuki-flash-is25)）とそれぞれに適した変換基板
（[SSOP8](#ref-akizuki-vssop8-board)・[SOP8](#ref-akizuki-sop8-board)）を[両面ユニバーサル基板Fタイプ](#ref-akizuki-ftype)
に載せてUEWで6ピンヘッダに出すだけです。CSピンは[10K&Omega;のチップ抵抗](#ref-akizuki-10k)で3.3Vにプルアップします。

モジュールのピンヘッダとShrikeのヘッダを[6P](#ref-akizuki-qi-6p)と[9P](#ref-akizuki-qi-9p)のQIコネクタでつなげます。

![自作フラッシュメモリモジュール（W25Q16JVUXIQ）](images/spi-flash-module-craft-1.png){width=120mm #fig:spi-flash-module-1}

### フラッシュ書き込み

RP2040からフラッシュに書き込むときは、SPI1バスを使用します。[main.py]{custom-style="PreprocessorTok"}に
変更を加える必要があります（以下に抜粋）。

```python
MISO1 = machine.Pin(SPI1_MISO, machine.Pin.IN, pull=machine.Pin.PULL_UP, value=1)  # uncomment
CS1 = machine.Pin(SPI1_CS, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)  # uncomment
SCLK1 = machine.Pin(SPI1_SCLK, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)  # uncomment
MOSI1 = machine.Pin(SPI1_MOSI, machine.Pin.OPEN_DRAIN, pull=machine.Pin.PULL_UP, value=1)  # uncomment
:
:
:
:
mcuboot = McuBoot.McuBoot(BusPins(SCLK0, MOSI0, MISO0), CS0, EN, PWR, LED)
flashboot = FlashBoot.FlashBoot(BusPins(SCLK1, MOSI1, MISO1), CS1, EN, PWR)  # uncomment
# flashboot = FlashBoot.FlashBoot(BusPins(SCLK0, MISO0, MOSI0), CS0, EN, PWR)  # comment out
```

Listing: main.py {#lst:main-py-spi1}

MicroPythonのREPL上で[flashboot.load(mcuboot)]{custom-style="PreprocessorTok"}を打ち込むとフラッシュからのロードが実行されます。

## Shrikeボードを改造する（2）

改造例（１）と同様にテストパッドからUEWで配線を引き伸ばし、SPIフラッシュに接続します。
CSピンだけはリセット解除後Hに保ちたいので抵抗を介したプルアップが必要ですが、ほかは
直結で大丈夫です。変換基板は裏面を絶縁したあとで[カプトン両面テープ](#ref-monotaro-capton-double-side-tape)などの耐熱両面テープでMCUに固定します。
電源はMCU用のフラッシュメモリのピンにつなげました。

### フラッシュ書き込み

# 関連コード全文掲載シリーズ {.appendix}

## `BusPins.py` {-}

[`BusPins.py`](data/BusPins.py){.python #lst:buspins-py .listingtable}

\newpage

## `McuBoot.py` {-}

[`McuBoot.py`](data/McuBoot.py){.python #lst:mcuboot-py .listingtable}

\newpage

## `FlashBoot.py` {-}

[`FlashBoot.py`](data/FlashBoot.py){.python #lst:flashboot-py .listingtable}

\newpage

## `spiflash.py` {-}

[`spiflash.py`](data/spiflash.py){.python #lst:spiflash-py .listingtable}

\newpage

## `main.py` {-}

[`main.py`](data/main.py){.python #lst:main-py .listingtable}

\newpage

## `shrike/examples/led_blink/ffpga/src/main.v` {-}

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
- [Micropython/UF2ファームウェア]{#ref-micropython-rpi-pico-firmware}
    - <https://micropython.org/download/RPI_PICO/>
- [SPIフラッシュ読み書きスクリプト]{#ref-spi-flash-handler}
    - <https://github.com/SpotlightKid/micropython-stm-lib/blob/master/spiflash/spiflash.py>

\newpage

## 関連部品リスト {-}

- <https://www.renesas.com/ja/products/at25xe011>
- [オヤイデ電気/UEW 0.18mm 20m ボビン巻き]{#ref-oyaide-uew}
    - <https://shop.oyaide.com/products/uew0-18-20m.html>
- [スイッチサイエンス/2MバイトSPIシリアルフラッシュメモリブレークアウト基板（レベルシフト回路搭載）]{#ref-ssci-flash-w25q}
    - <https://www.switch-science.com/products/8593>
    - Winbond/W25Q16JVSSIQ 16Mbit SOP8
        - <https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en&partNo=W25Q16JVSSIQ>
- [秋月電子/\[106076\]フラッシュメモリー W25Q16JVUXIQ]{#ref-akizuki-flash-w25q}
    - 16Mbit
    - https://akizukidenshi.com/catalog/g/g117346/
    - Winbond/W25Q16JVUXIQ 16Mbit USON8
        - <https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-jv/?__locale=en&partNo=W25Q16JVUXIQ>
- [秋月電子/VSSOP8 0.5mmピッチIC(8ピン)変換基板]{#ref-akizuki-vssop8-board}
    - https://akizukidenshi.com/catalog/g/g106076/
- [秋月電子/\[118046\]フラッシュメモリー IS25LP040E]{#ref-akizuki-flash-is25}
    - 4Mbit
    - <https://akizukidenshi.com/catalog/g/g118046/>
- [秋月電子/\[105154\]SOP8(1.27mm)DIP変換基板 金フラッシュ]{#ref-akizuki-sop8-board}
    - https://akizukidenshi.com/catalog/g/g105154/
- [秋月電子/\[130347\]チップ抵抗 1608 1/8W100&Omega;]{#ref-akizuki-100r}
    - <https://akizukidenshi.com/catalog/g/g130347/>
- [秋月電子/\[130355\]チップ抵抗 1608 1/10W10k&Omega;]{#ref-akizuki-10k}
    - <https://akizukidenshi.com/catalog/g/g130355/>
- [秋月電子/\[112731\]両面スルーホールガラスコンポジット・ユニバーサル基板 Fタイプ]{#ref-akizuki-ftype}
    - <https://akizukidenshi.com/catalog/g/g112731/>
- [秋月電子/\[105336\]ピンヘッダー (L型) 1×6 (6P)]{#ref-akizuki-6p-header}
    - <https://akizukidenshi.com/catalog/g/g105336/>
- [秋月電子/\[112155\]コネクター用ハウジング 6P]{#ref-akizuki-qi-6p}
    - <https://akizukidenshi.com/catalog/g/g112155/>
- [秋月電子/\[112158\]コネクター用ハウジング 9P]{#ref-akizuki-qi-9p}
    - <https://akizukidenshi.com/catalog/g/g112158/>
- [秋月電子/\[117982\]超薄型SOP8変換基板]{#ref-akizuki-sop8-1mm-2p}
    - <https://akizukidenshi.com/catalog/g/g117982/>
- [秋月電子/\[112268\]超薄型SOP8変換基板]{#ref-akizuki-sop8-1mm-10p}
    - <https://akizukidenshi.com/catalog/g/g112268/>
- [モノタロウ/カプトン両面テープ NO.760H #25]{#ref-monotaro-capton-double-side-tape}
    - <https://www.monotaro.com/p/7518/1574/>

# あとがき {-}

- ピン配置図生成には[Pinout Leaf Generator](https://github.com/marcteale/pinoutleaf?tab=readme-ov-file#pinout-leaf-generator-)
  を使いました。SVG-PNG変換は、いつものrsvgだと崩れてしまうので、ネットで見つけたツール<https://amamamaou.github.io/svg2png/>を使用しました。
