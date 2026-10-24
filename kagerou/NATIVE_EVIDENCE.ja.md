# Kagerou: 原プログラムの根拠

[中文](NATIVE_EVIDENCE.zh.md) | [English](NATIVE_EVIDENCE.en.md) | [Русский](NATIVE_EVIDENCE.ru.md) | [日本語](NATIVE_EVIDENCE.ja.md)

[文書一覧](../docs/README.ja.md)

特典版アダプターの識別、命令、配置の開発資料です。2026-10-10記録、特典資源は2026-10-11更新。原ゲーム実行ではなく静的解析で、アドレスはImageBase0x400000のVAです。読取器は本ディレクトリに独立実装し、他アダプターから意味を借用しません。

## 入力版

| ファイル | SHA-256 |
| --- | --- |
| 原 kagerou.exe | `f02998fae350945f4de4dc7eab47997e1e2d9b8aa43d49740a80aad893dcde9b` |
| 中文 kagerou_gbk.exe | `0d024e5cfe6c70f5a9a9149df5fbf040dfb7d97cdeefba03a13625d121dea8de` |

両方i386 PE32。.text差は0x456d4a/0x45d0f3の字体charset 0x80→0x86だけですが、他sectionにも翻訳差があり、全EXEが二バイトパッチという意味ではありません。

初期は原147/中文140場面、対応特典版は原162（modern98/rscript19が64）、再生成中文155で未訳7は原版へ戻します。modern-36 containerは同一schemaを意味しません。旧各組のexcmdは861、特典936（mode0:590/1:263/2:83）。

## 分派

main0x41bd00、0x41c12fが非VMの低16bitから3を引き、byte索引0x41d4f8とhandler表0x41d2e8で分岐。native.pyが直接読み、既存opcode表をバイナリー根拠の代用にしません。

| Opcode | handler | 経路 |
| --- | --- | --- |
| 0x14 | 0x41c5e9 | 二式→0x41f250 gload |
| 0x1a | 0x41cad3 | 0x41ff10 queue |
| 0x1c | 0x41cae7 | 三式→0x41ff40 update |
| 0x51 | 0x41c9ae | 0x41f020 TXT |
| 0x52 | 0x41ca0b | 0x41eeb0 TXA |
| 0xff | 0x41d29d | 五式→0x421f00→0x431320 |

TXTは式、raw DWORD、二式、二raw文字列、最後の式を読み、第一文字列を捨て第二を保持、最後は低16bit。これは読取・呼出の根拠で、配置・音声・待ちの完全解析ではありません。

## EXCMD

0x431320はmode低16bitの0/1/2以外なら戻ります。第五引数は未使用。モデルは解決済みunsigned WORD五つを取り、式自体は受けません。

### mode0: ロードとfocus

0x431370はslot1–7のみ、設定Xで0x41dda0(slot,cg,0,x,0,0)、第四引数0なら0x431440(slot)、0x482188が0なら0x41dd30でrefresh。非キューload+focusは二度refreshし得るため、一回の即時キュー更新にまとめません。Xは0x431385–0x4313cc:

```text
WORD[0x482a6a] != 0:
    signed WORD[0x47eede + 2 * slot]
otherwise:
    signed WORD[0x47eeba + 2 * (6 * (WORD[0x482a66] / 3) + slot)]
```

非負WORD除算は切捨て。slot1–6:

| 指定設定 | X |
| --- | --- |
| layout0、alternate=false | 200,200,300,400,500,600 |
| layout6、alternate=false | 600,600,500,400,300,200 |
| alternate=true | 400,200,300,400,500,600 |

分岐定数であって既定値の証明ではありません。slot7はload可ですがfocus loopは1–6。7を6へ直しません。

### mode1: 消去

0x431410→0x41e020(slot,0)、queue状態でrefresh。二条件jumpはWORD値を除外せず、後段0x41dd70がslot<100を検査。0はそのままで「全立ち絵消去」ではありません。

### mode2: focus と色

0x431440はr20を書き、層1–6を処理します。

| 層 | depth (0x41f940) | draw (0x41f7f0) |
| --- | --- | --- |
| 対象 | 8 | mode0,strength0 |
| 他、WORD[0x482a6c]==0 | 層番号 | mode4,strength50 |
| 他、非零 | 層番号 | mode0,strength0 |

0x431478の二push esiはdepth1でなく層依存。depthは0x41f940→0x41e360、drawは0x41f7f0→0x41e2d0→0x4058b0→0x408e40。表0x408f40/0x408f24のmode4→0x408ea6は内部mode3、strength50*255/100=127。vtable0x473f7cの+b0/+b4は0x43fa30/0x43fb00で+28/+2cへ。

0x4406e0→0x4412c4/0x44125c→0x440e65は透明輪郭で0x444380、それ以外0x444220。表0x4a732cでRGBを変換し、opacity減少・grayscaleではありません。0x446079..0x4460edは0x475c38=256.0、0x475c50=1/256、切捨て0x4616b0:

```text
L(level,channel) = trunc(channel*(256-level)/256)
output = L(a,L(level,source)) + L(255-a,destination)
```

aは第四byteの反転alpha。127は129/256で、50%や128/255ではありません。共通dim256はRGB LUTのみ、(4,50)を("dim256",127)へ。別作品の数値modeは不変。PNG coverage/GPU混合の境界丸めは完全一致でなく、隔離GL2はopacity0/部分/全、strength0/127/255を誤差2階調で確認します。

## 動画

window0x4233c0のmessage0x40eは0x47ecf8のmov/0002.mpg、0x41eは0x47ece8のmov/0001.mpgを参照後、起動状態を設定。実資源は0002/0003のみ。movie3は1131/1239/1326/1417/1418。

利用者承認により、存在する0002→0001を起動時のみ、0001不足は警告、脚本movieは保持。`game/script.rpy` のrenpy.sessionでタイトル復帰・同process full_restartの再生を防ぎます。

## 0999 → 1000 の呼出

EXE hash不変で特典162場面が基準。0059/0201/0301/0302/1501..1511追加。0001はCGへjump201、回想へjump301、0302はgosubで"scmode"入口。旧中文命令全体で置換せず、TXT再構築で新命令と末尾入口表を保持します。これはTSC根拠で全鑑賞・unlockの実確認ではありません。

setclk 0x41cb59→0x41ffa0→0x41e800→0x405cb0はobject+298にenable/result/hoverを設定し、任意の説明図setlinkは不要。0099%selectは21–24にsetclkのみで合法です。関連図なしを除外・選択skipしません。

0050はgosub999後、insubの第一引数に1000、局所入口がgosub r10 0...を実行。旧実装はtarget解決前にr10–19を上書きし0000を呼びました。targetと全引数を先に解決し、脚本は変えません。

- opcode15 0x41d820がtarget+10引数を一時WORDへ、0x41da10、0x41da7a→0x41d930でtarget装入後0x41dabe..0x41dad3で引数記入。
- opcode200は0x41c427で局所DWORD、0x41c43d..0x41c449で引数、0x41daf0へ。
- opcode16 0x41c481..0x41c487→0x41db80は呼出元とcursorを復元、0x41dbf9はr0。0999末尾return0は合法。

## 文字と原点

- 0x41f0e1はWORD[0x482ae0]==1で0x41ee80消去。tclsmode0x4206d0が書き、起動は2を指定。
- 0x42d81aは既本文+非零wait時に0x47ee88の^nを前置。0x42d86cはCP932【(0x47ee94)開始なら0x47ee80のU+3000,^nを追加。TXTは単純結合ではない。
- append0x42d8d1→0x430db0、失敗時0x42d8da→0x430f30で旧頁を消して現段落を追加。移植はbyte容量でなく実高さで検査し、段落内改頁は未完成。
- native方向WORD[0x482a5e]は0=縦/1=横。旧icon解釈は逆。SETE0x430437、0時0x453ef0で+1b0=1、0x455400→0x455800でY進行・右から左。1は0x455420でX進行・下へ。移植の1=縦/0=横へ表を写像し、依頼により既定縦。CFG初期化0x419bb0はBSSゼロで、EXE中の既定方向byte1は証明できず、原CFGも取り込みません。

preset0x43027f..0x43042b、0x453eb0は+170/+16cに物理寸法:

| 方向 | index | 字体 | 物理領域 | gap | ruby |
| --- | --- | --- | --- | --- | --- |
| 縦 | 0 | 24 | 646×480 | 10 | 9 |
| 縦 | 1 | 18 | 494×360 | 8 | 8 |
| 縦 | 2 | 12 | 342×240 | 6 | 6 |
| 横 | 0 | 18 | 360×513 | 9 | 9 |
| 横 | 1 | 16 | 320×456 | 8 | 8 |
| 横 | 2 | 12 | 240×342 | 6 | 6 |

原定数でpixel同値の証明ではありません。依頼により両方向24/18/12pxを使い、方向切替は幾何・字形だけ変えます。原領域・原点・gapは保持。縦大は646×480で、横の360×513ではありません。

- 0x43045c..0x430788はnative方向でsnap+54*direction+18*sizeのX/Y定数。54組をnative.pyへ。縦0/0=(114,30)、横0/0=(400,20)、縦2/8=(20,270)。縦anchorは(x+width,y)、物理heightで折返し。TextSegmentは方向を継承しないためHarfBuzz縦字形が必要。隔離captureで正立・切替を確認。
- tbox0x41c8cb→0x41f220は第二引数で0x41e550/0x41e570、条件refresh。hide0x42da47はclear-page0x42d9d0も呼ぶため、0999末尾tbox0 0だけで本文を消す。txcls0x41ca48→0x41ecd0→0x41e590。
- locmode0x41c801→0x41f890は四式、層0=1..99。0x41e310→0x405740で原点。第四値非零は未解決、サンプルは0。0x408569..0x4085d5は一/二値非零で整数半幅/高を引くため中央原点。半pixelは目視確認。
- endscene0x41cb25はreplayWORD0x4821f8を調べ、通常は継続、非零でinterpreter退出。runtime既定false。初調査ではnative gallery入口の根拠は未取得でした。

共通runtimeは既知register/media/widgetsを提供し、作品固有overrideをコピーしません。転換は互換処理で、精密pixelは未確認です。

## ルビの構文と位置

以下は本EXE根拠です。代替字体はGDIと同じ描画とは限りません。

- 4544d9..4544e6→45f150は|で本文cell indexを+7cへ保存、+78設定、|は非表示。
- 4544ff..45459dは括弧間をコピーし、span終端を現index−1、45f170へ。|なしでは45f18b..45f197が始端も終端cellへ。躯[み]・介[お]は一字ルビ。現1000.tscは両構文、1000.rpy:29の抉[えぐ]・熾[おこ]が報告例。
- 45ead0は横45eb20/縦45ed60。次X/Yが原点へ戻ると新行・列。境界ではceil(残ルビ*現本文/残本文)を分配し、45eb9d..45ebde /45eddd..45ee1eで再帰。
- 横45ec75..45ed3fは短ルビを本文spanの均等cellで中央化、長ルビ全体を中央化し実幅で進める。Y=本文cell上端−offset+74で、ascender推測ではない。
- 縦45eeb3..45efa8は高さ方向同様、ルビ右端=最初本文右端+offset+74、下へ進む。転置Ren'Pyではcell-top-minus-offsetを使い、字体高を再加算しない。
- 4303cb..43042bはルビsize+68、offset+74へ9/8/6。共通計測はこの設定を使い、発売年で推測しない。

両構文、改行/列分配、offset、SDK方向を検査し、セーブなしの1000冒頭captureを使います。他EXEの既定を証明せず、Forest/Khimeの幾何を保持します。

## 待機と特典鑑賞

- 0x430cb0..0x430d39の表[24,18,12,18,16,12]はnative3*direction+sizeでgrps/waitNN選択。body/grow三角でない。四LWGは各60frame、metadata順と各原点。
- 0x4191a9がpointer0x47e588、WORD+190=50。0x4192b1→0x44fc90→0x44fca0が50ms timer、0x44b980進行、0x44b9ab循環。body/grow glowと違う。
- 0x430dfc→0x430f60→0x455b30は最後の本文cell、0x430e01は縦なら左下、横なら右上。画面固定角でなくルビを除いたlayout cellへ置く。
- 縦の『「【はHarfBuzz inkがadvanceを超えることがある。共通native層で許容bearingをcellに収め、全角advance/gapを変えない。24/18/12pxでSDK境界検査。
- folder0x41cee0→0x41fb80、層0は0x41fbb1..0x41fbc8で1..99。gallery folder0 grpo_exとlocmode0 0 0 0を両方適用し、thumbnailに立ち絵中央原点を残さない。共通folder-allを本作根拠で使い、特典TSCに鑑賞を任せる。

2026-10-11は実EXE定数、162TSC、隔離SDK消去/folder/原点/字体/boundsと両方向captureを確認。lintの日本語名・不可達警告は保持。全ルート・Androidは未確認。

## 読書コントロール

### 特典版の立ち絵folder漏れ（2026-10-11）

特典0001は全層grpo、galleryはgrpo_ex/top-left。0050→0999→1000は0000のslots1..6 grpo_bu/中央設定を再実行せず、EXCMDがないgrpo/3011を要求し、透明fallbackで立ち絵が消えていました。コピー不足ではありません。

EXCMD slots1..6装入時、0000/9999が明示するfolder/原点を復元し、一般folder-all・gallery・slot7は変えません。EXE431370→41dda0→405940は現folderを使い、旧EXEの自動resetは未確認。これは現脚本・素材に基づく移植修正です。隔離日中テストは実title→0050/0999→1000最初の立ち絵を、セーブなしで確認。

0x42c2be..0x42c2d6はcompane(585,572)、0x42bfce..0x42bfe3はexcompane(0,550)。寸法・原点はmetadata、excompane背景なし。constructorの名前pointerはメモリー順の証明ではありません。

| 名前/field | 原経路 | 移植 |
| --- | --- | --- |
| skip/+60 | 42d5f0→42ce10→417f10 | Skip |
| rev/+68 | 42d630→42ce90→417ee0 | Rollback |
| bak/+74 | 42d5d0→42c890 履歴 | 依頼によりホイール同等回帰 |
| hide/+78 | 42d6d0→42ced0→417e10 | UI非表示 |
| voc/+7c | 42d6f0→42cc30→417e90 | ボイス再生 |
| auto/+84 | 42d710→42cda0→417fe0 | 自動 |
| slide/+6c | 42d540→42d770→431070 | 枠透明度 |

素材にあるボタンだけ表示し、余計なmenu/saveを足しません。Backは意図的に共通回帰・権限を使い、原履歴/旧互換ページは使いません。sliderは背景+58の+b4 alpha、42fd4c→431070既定128。共通255が背景・立ち絵を隠したため128/255へ。旧既定1.0を一度移行し、他選択は保持し後から1.0も再選択可。原pixel混合は未目視比較。

save slot404135はsaveconf、404272/4042acはdate/new位置のみ残しplaceholder解放、40448b..404528は動的配置。4048b5の書式は%04d/%02d/%02d %02d:%02d。404a0cが最新、404a1cは黒saveconf/new.pngでなくdat_new。共通image mapと保存章metadataを使い、slot/pageはmetadata。原日付字体・色・blendは未確認。隔離SDKでBack/ホイールが前台詞・局所registerを復元することを確認しましたが、この仕様は依頼によるものです。

excompaneはmessage433でrefresh:

| control | callback | WORD | 動作 |
| --- | --- | --- | --- |
| size | 42e200 | 482a60 | 三preset |
| shdw | 42e230 | 482a64 | 0=shadow、近似描画 |
| dir | 42e260 | 482a5e | 方向 |
| snap | 42e290 | 482a66 | 九anchor |
| tfcs | 42e2c0 | 482a68 | 0=旧段落暗化 |
| lfcs | 42e2f0 | 482a6a | 立ち絵座標 |
| lctr | 42e320 | 482a6c | 0=非focusRGB暗化 |
| font | 42ded0 | 字体dialog | 共通listで代替 |

tfcs0の0x430f40→0x455b90は旧段落mode2/alpha128、移植は{alpha=128/255}。0x4314c0はslots1..6を抽出座標へ。0x431510..0x431532は設定/r20でdraw再適用し、register/depth不変。0x42e320→0x433→0x416b05→0x421bc0→0x421c40→0x421edd→0x4314c0はlctr色とicon即更新。

## ボイス群

- 0x40ce96は0x47e254のpv%02d、0x40cf3fはpv00..pv09の十群。素材はpv01..05のon/offだけ。0x429a60はoff0、on1の順。
- 0x40e740→0x40e710→0x40e72bはWORD[0x482238+2*group]を書き、現音声を停止しない。0x419c1f..0x419c73は五つの0x00010001で十WORDをon。
- 0x41a630はglobal0x48221c、ID/10000、0x41a661はgroupの有効判定。残り四桁をgroup0=%s/%04d.wav、他0x47e8ac=%s/%d/%04d.wavへ。
- refresh0x40dcec..0x40dd34は十WORD。pv01_on/offの選択/hoverはpixel同一なので共通frame再使用、文字ボタンにしない。
- 指定作品のみ群機能を有効化しForest/Khime不変。mockは既定、一群mute、他群継続、現音声非中断、replay制限。日中captureは五群。試聴と原CFG取込は未検証。

## 未完事項

[利用ガイド](README.ja.md#確認と制限)を参照してください。

## 音楽鑑賞（2026-10-11）

現EXEで特典の音楽入口を処理できます。更新日だけで新EXE不足と判断しません。title setclksys23 7 3 0は0x409d82→0x417cb0/0x417d88[7]→0x417d57→0x419ac0、windowID0x482164から0x44eab0。0x4196abはconstructor0x41a8a0、0x4196b6は登録、0x4196d2は戻りAXを0x482164へ。保存先は直前callに属し次の登録ではありません。resource0x47e8f0=muscmenu。

| 経路 | 動作 |
| --- | --- |
| 0x41a8a0 | 物語BGM停止、最初を選択し未再生。画像1..20を列挙しunlock検査なし |
| 0x41b410 | 停止中:別曲は選択のみ、同曲で開始。再生中:即restart、pause解除 |
| 0x41b530 /0x41b5d0 /0x41b380 | play /pause-resume /stop。再生中playは無操作 |
| 0x41b660 /0x41b680 | 最初でprev禁止、末尾nextは停止し先頭選択 |
| 0x41b340 | message0x7e8,param0で次。移植は独立channel完了 |
| 0x41b6c0 /0x4512b0 | 一時0x49ddec音量のみ。0..255→trunc((value−255)*3000/255) centi-dB |
| 0x41b220 | 退出で停止しglobal音量復元。旧BGMは再開しない |

0x41b5a5→0x451140は物語BGMスイッチを迂回し、移植は別channel。最小はmuteでなく−30dB。muscmenu metadataの位置と_f/_p、現資源15曲、共通翻訳overlayを使います。共通templateは登録system_actionsのみでsystem7を一般化しません。0x41ac16..0x41ac3aはlevel境界をsliderへ、0x41ac89は赤placeholder解放。描くのはbar/bar_fだけでlevelではありません。

自動テストは選択、pause、切替、境界、decode開始/終了、一時音量、清理。合成WAVの隔離描画テストで実Ren'Py完了→次曲、退出時外BGM非再開を確認。実音量、native全UI、全回想は未検証。

## 非focus立ち絵（2026-10-11）

分派、vtable、LUT、lctr refreshを本EXEから確認し、他移植から推定しません。隔離SDKでfocus、focus保持load、queue、即lctr変更、r20/depth/slot7保持を専用persistentで検査。GL2合成pixelで透明、強度、通常復元、Forest/Khime回帰も確認。lintの既存警告は残ります。native実行pixel、旧セーブ、Android GPUは未検証で、正確な転換・履歴は別課題です。

## update のミリ秒計時（2026-10-11）

0x41cae7→0x41ff40→0x41e5b0がeffect/steps/wait。0x41e5cc..0x41e5d1でsteps0→10、0x41e7e0で即時/溶解/点陣/白/黒。

| 効果 | native loop | 名目秒 |
| --- | --- | --- |
| 1 | 0x450630、0x4506c5はsteps+1 | (step+1)*wait/1000 |
| 2 | 0x4504e0、0x450540はsteps−1、非正skip | max(0,step−1)*wait/1000 |
| 3/4 | 0x450f50/0x450cb0、二段階steps+1 | 2*(step+1)*wait/1000 |
| mask | 0x450380、倍steps−1 | (2*step−1)*wait/1000 |
| 1xx/2xx | 0x4507a0/0x450940、31/41frame各Sleep5 | 0.310/0.410 |

WINMM timeGetTime IAT0x4732dc、Sleep5 IAT0x473070は少なくとも一回待ち、差がWaitより大きくなるまで反復。codex-msは名目回数でWindows調度を再現しません。当時の効果2 pixelationは次節で修正。現日本語定数0..3、1 32 40=1.32秒、1 16 20=.34秒、0999の1 15 100=1.60秒（旧12.8/3.2/15）。Kagerouのみms選択、他移植は本調査でeffect2時刻のみ修正。constructor前もsteps0→10としてゼロ除算回避。byte検査/隔離SDKは時間・register引数・queueを確認し精密pixel/調度は未確認。

## update2: 順序付き置換（2026-10-11）

0x45050aはdraw18で縮放ではありません。0x4412c4[18]→0x44125c[13]→0x440c17、不透明0x440c33→0x4437d0。0x443855..0x44385bは強度>>4で0x47ef38の16WORDを選び、0x443899..0x4438efは(x%4)+4*(y%4)bit1で新pixel、0で旧。0x45e01a..0x45e01cのDIB高符号反転によりtop-downです。

```text
FFDF EFDF 6FDF 6FD7 6BD7 6BD6 6B56 6A56
2A56 2A52 0A52 0A12 0812 0810 0800 0000
```

0x44e4b0が現windowをsourceへ、destination+9cは旧frame。強度floor((step-frame)*255/step)、steps−1後0x44e450で新画面確定。maskは単調増加で、Pixellate二段階や旧8×8SVGとは異なります。

読み取り専用modelで表を検査し、共通RScriptOrderedDissolveは仮想pixelで合成後縮放。[他四作の根拠](../docs/UPDATE_EFFECT2.ja.md)もあります。隔離GL2は1/3/10/16/32steps、全4×4方向、終画面を確認し、native実行/Android同値の証明ではありません。
