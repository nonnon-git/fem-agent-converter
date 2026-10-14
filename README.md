Google Cloud Hackason 提出用
Zennの記事
https://zenn.dev/nonn_engi/articles/5f913f1b09dcea
YouTubeデモ動画
https://youtu.be/qT_mxNqrOls
本体
https://fem-agent-converter-460440303785.asia-northeast1.run.app/


# FEM Agent Converter — 大規模構造解析の設定ファイル変換をAIで自動化

## 対象ユーザー
日常的に大規模な構造解析を行うCAEエンジニア。

## 解決したい課題
大規模構造解析では、解析ソフトウェアの仕様に従って、膨大な数の設定項目を正確に記述する必要があります。しかし、その設定方法を網羅した技術マニュアルは数千ページに及び、設定項目も数百に上ります。
例えば、ANSYS LS-DYNA Keyword User's Manual は、Volume I だけで4,315ページあり、Volume III まで合わせると総ページ数は7,000ページを超えます。
こうしたマニュアルから必要な仕様を探し、個々の設定項目を理解して、正しい文法で解析設定を記述する作業には、多大な労力がかかります。さらに、同じ種類の設定が解析モデル内に多数存在する場合、それぞれに対応する変換作業も必要になります。

## 解決策
FEM Agent Converterは、AIエージェントを活用して技術マニュアルから必要な仕様を検索・参照し、解析設定ファイルの変換スクリプトを自動生成します。
ユーザーは代表となるキーワードブロックを入力するだけで、同名のキーワードブロックを一括変換するスクリプトを取得できます。
これにより、キーワードごとにマニュアルのページを選び、AIに文献を登録し直してスクリプトを生成するという、従来の煩雑な作業を削減します。

## アプリの特徴・従来手法との違い
従来は、NotebookLMに技術マニュアルの必要なページを文献として登録し、キーワードごとに変換スクリプトを生成していました。

しかし、変換対象となる設定項目が多い一方で、登録可能な文献数には制限があります。そのため、1つのキーワードを変換するたびに、関連する文献を探して登録し、不要な文献を削除して入れ替えたうえで、再びスクリプトを生成するという作業が必要でした。

本アプリでは、こうした文献の選定・登録・削除を繰り返す作業をなくしました。ユーザーは代表となるキーワードブロックを入力するだけで、必要な技術情報を参照し、同じ名前のキーワードブロックを一括変換するためのスクリプトを取得できます。

**マニュアルの検索から設定変換スクリプトの生成までをAIエージェントで効率化し、CAEエンジニアが本来注力すべき解析業務に集中できる環境を目指します。**

### 実証ケース：CCSA Toyota Camry衝突解析モデル

本アプリの適用対象として、CCSA（Center for Collision Safety and Analysis）が公開するToyota Camryの車両衝突解析モデルを使用します。

このモデルは約225万要素、約1,000部品で構成され、実車の衝突試験結果との比較による検証が行われた、大規模かつ実用的な有限要素モデルです。

対象ファイルには43種類のキーワードが含まれており、その中には *CONSTRAINED_SPOTWELD_ID のように7,000回以上出現するキーワードも存在します。
本アプリは、代表的なキーワードブロックを入力することで、同種のキーワードを一括変換するスクリプトの生成を支援します。これにより、膨大な設定記述を個別に調査・変換する作業の削減を目指します。

## 変換キーワードブロックの例
以下の例には*PART, *SECTION_SHELL, *MAT_PIECEWISE_LINEAR_PLASTICITYの3つのキーワードブロックが含まれています。

*PART
$#                                                                         title
418_doorfrontwindowframe
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
   2000361   2000361   2000361
*SECTION_SHELL
$#   secid    elform      shrf       nip     propt   qr/irid     icomp     setyp
   2000361        16       0.0         3       1.0                             1
$#      t1        t2        t3        t4      nloc     marea      idof    edgset
      1.35      1.35      1.35      1.35
*MAT_PIECEWISE_LINEAR_PLASTICITY
$#     mid        ro         e        pr      sigy      etan      fail      tdel
   20003617.89000E-9  210000.0       0.3     250.0          1.00000E21
$#       c         p      lcss      lcsr        vp       lcf   
    8000.0       8.0   2000250
$#    eps1      eps2      eps3      eps4      eps5      eps6      eps7      eps8

$#     es1       es2       es3       es4       es5       es6       es7       es8

## 変換後の出力文字列（OpenRadiossフォーマット）
上記のスクリプトにサンプルデータを入力した際の、厳密な文字数制限（フィールド幅）を満たした出力結果です。

/PART/2000365
377_doorrearwindow
   2000365   2000365
/PROP/TYPE1/2000365
Shell_2000365
        24         2         2         0                                     0.0
                 0.0                 0.0                 0.0       0.0       0.0
         3         0              4.1400            0.833333    1    1         0
/MAT/LAW44/2000365
Mat_2000365
         2.57300E-09
             70000.0              0.2200
              1000.0              1000.0                 1.0       0.0   1.0E+20
                 0.0                 1.0         0         0                 0.0         2
              0.0150             1.0E+20             2.0E+20

## アプリが出力した変換スクリプト
3つのキーワードブロックそれぞれに対して、解析設定ファイルに含まれる同じキーワードを一括で変換するスクリプトになっています。
今回はLS-DYNAの言葉で書かれた解析設定ファイルを、Openradiossの言葉で書かれた解析設定ファイルに変換しています。

import re

def parse_ls_dyna(text):
    lines = text.strip().split('\n')
    data = {
        'part': {},
        'section_shell': {},
        'mat': {}
    }

    current_keyword = None
    keyword_lines = []

    for line in lines:
        if line.startswith('*'):
            if current_keyword:
                process_keyword(current_keyword, keyword_lines, data)
            current_keyword = line.strip().split('_')[0] if 'MODIFIED' not in line else line.strip()
            keyword_lines = []
        else:
            if not line.startswith('$') and line.strip():
                keyword_lines.append(line)

    if current_keyword:
        process_keyword(current_keyword, keyword_lines, data)

    return data

def process_keyword(keyword, lines, data):
    if keyword == '*PART':
        if len(lines) >= 2:
            data['part']['title'] = lines[0].strip()
            line2 = lines[1]
            data['part']['pid'] = int(line2[0:10].strip())
            data['part']['secid'] = int(line2[10:20].strip())
            data['part']['mid'] = int(line2[20:30].strip())

    elif keyword == '*SECTION':
        if len(lines) >= 2:
            line1 = lines[0]
            data['section_shell']['secid'] = int(line1[0:10].strip())
            data['section_shell']['elform'] = int(line1[10:20].strip())
            data['section_shell']['shrf'] = float(line1[20:30].strip()) if line1[20:30].strip() else 0.0
            data['section_shell']['nip'] = int(line1[30:40].strip()) if line1[30:40].strip() else 0

            line2 = lines[1]
            data['section_shell']['t1'] = float(line2[0:10].strip()) if line2[0:10].strip() else 0.0

    elif 'MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY' in keyword:
        if len(lines) >= 2:
            line1 = lines[0]
            data['mat']['mid'] = int(line1[0:10].strip())
            data['mat']['ro'] = float(line1[10:20].strip())
            data['mat']['e'] = float(line1[20:30].strip())
            data['mat']['pr'] = float(line1[30:40].strip())
            data['mat']['sigy'] = float(line1[40:50].strip()) if line1[40:50].strip() else 0.0
            data['mat']['etan'] = float(line1[50:60].strip()) if line1[50:60].strip() else 0.0
            data['mat']['fail'] = float(line1[60:70].strip()) if line1[60:70].strip() else 0.0

            line2 = lines[1]
            data['mat']['c'] = float(line2[0:10].strip()) if line2[0:10].strip() else 0.0
            data['mat']['p'] = float(line2[10:20].strip()) if line2[10:20].strip() else 0.0
            data['mat']['vp'] = float(line2[40:50].strip()) if line2[40:50].strip() else 0.0

def convert_to_openradioss(data):
    output = []

    # 1. /PART
    part = data.get('part')
    if part:
        output.append(f"/PART/{part['pid']}")
        output.append(part['title'])
        output.append(f"{part['secid']:>10}{part['mid']:>10}")

    # 2. /PROP/TYPE1
    shell = data.get('section_shell')
    if shell:
        secid = shell['secid']
        elform = shell['elform']
        shrf = shell['shrf']
        nip = shell['nip']
        t1 = shell['t1']

        # デフォルト値の補完
        ashear = shrf if shrf != 0.0 else 5/6
        ishell = 24 if elform == 2 else 1  # ELFORM=2 -> QEPH
        ismstr = 2
        ish3n = 2
        idrill = 0
        p_thick_fail = 0.0
        hm, hf, hr, dm, dn = 0.0, 0.0, 0.0, 0.0, 0.0
        n = nip if nip > 0 else 3
        istrain = 0
        ithick = 1
        iplas = 1
        ipos = 0

        output.append(f"/PROP/TYPE1/{secid}")
        output.append(f"Shell_{secid}")
        output.append(f"{ishell:>10}{ismstr:>10}{ish3n:>10}{idrill:>10}{p_thick_fail:>40.1f}")
        output.append(f"{hm:>20.1f}{hf:>20.1f}{hr:>20.1f}{dm:>10.1f}{dn:>10.1f}")
        output.append(f"{n:>10}{istrain:>10}{t1:>20.4f}{ashear:>20.6f}{ithick:>5}{iplas:>5}{ipos:>10}")

    # 3. /MAT/LAW44
    mat = data.get('mat')
    if mat:
        mid = mat['mid']
        ro = mat['ro']
        e = mat['e']
        pr = mat['pr']
        sigy = mat['sigy']
        etan = mat['etan']
        fail = mat['fail']
        c = mat['c']
        p = mat['p']
        vp = mat['vp']

        # デフォルト値の補完
        p_val = p if p != 0.0 else 1.0
        vp_val = int(vp) if vp != 0.0 else 2
        sigma_max0 = 10**20
        eps_t1 = 10**20
        eps_t2 = 2 * 10**20

        output.append(f"/MAT/LAW44/{mid}")
        output.append(f"Mat_{mid}")
        output.append(f"{ro:>20.5E}")
        output.append(f"{e:>20.1f}{pr:>20.4f}")
        output.append(f"{sigy:>20.1f}{etan:>20.1f}{1.0:>20.1f}{0.0:>10.1f}{sigma_max0:>10.1E}")
        output.append(f"{c:>20.1f}{p_val:>20.1f}{0:>10}{0:>10}{0.0:>20.1f}{vp_val:>10}")
        output.append(f"{fail:>20.4f}{eps_t1:>20.1E}{eps_t2:>20.1E}")

    return "\n".join(output)

# サンプルデータの実行
lsdyna_input = """
*PART
$#                                                                         title
377_doorrearwindow
$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid
   2000365   2000365   2000365
*SECTION_SHELL
$#   secid    elform      shrf       nip     propt   qr/irid     icomp     setyp
   2000365         2       0.0         3       1.0                             1
$#      t1        t2        t3        t4      nloc     marea      idof    edgset
      4.14      4.14      4.14      4.14
*MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY
$#     mid        ro         e        pr      sigy      etan      fail      tdel
   20003652.57300E-9   70000.0      0.22    1000.0    1000.0     0.015
$#       c         p      lcss      lcsr        vp   epsthin    epsmaj    numint
                                                                             1.0
$#    eps1      eps2      eps3      eps4      eps5      eps6      eps7      eps8

$#     es1       es2       es3       es4       es5       es6       es7       es8
"""

parsed_data = parse_ls_dyna(lsdyna_input)
openradioss_output = convert_to_openradioss(parsed_data)
print(openradioss_output)


## 今後の展望
本アプリは、既存の解析設定ファイルを変換する作業の自動化を出発点としています。
将来的には、技術マニュアルの検索・参照、解析条件の整理、設定ファイルの生成、整合性検証までを一貫して行うAIエージェントへと発展させることを目指します。
最終的には、エンジニアが解析したい現象や条件を仕様として与えることで、既存の有限要素モデルを活用しながら、OpenRadiossの解析モデルを効率的に構築できる環境を実現したいと考えています。
