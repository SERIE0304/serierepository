"""
Run once on Render via shell: python seed_diet_questions.py
Adds 20 diet knowledge questions to the Questions sheet.
"""
import time
import sheets

questions = [
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "「ダイエット」という言葉の語源となったギリシャ語の意味として正しいものはどれか？",
        "choices": ["生き方・生活習慣・住まい・食事療法", "運動・健康・美容・食事", "節食・制限・管理・健康", "体重・体型・体脂肪・体温"],
        "correct_index": 0,
        "explanation": "ダイエットはギリシャ語で「生き方」「生活習慣」「住まい」「食事療法」を意味します。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "ホメオダイエットの目的として正しいものはどれか？",
        "choices": ["体脂肪を減らしそれをセットポイント（恒常性）にする", "筋肉量を増やして基礎代謝を上げる", "カロリーを厳しく制限して体重を素早く落とす", "運動量を増やして消費カロリーを最大化する"],
        "correct_index": 0,
        "explanation": "ホメオダイエットの目的は体脂肪を減らし、それをセットポイント（恒常性）にすることです。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "腹囲の正しい測定位置はどれか？",
        "choices": ["へそのラインで測る", "お腹周りの一番細い部分で測る", "みぞおちのラインで測る", "腰骨のラインで測る"],
        "correct_index": 0,
        "explanation": "腹囲はへそのラインで測ります。お腹周りの一番細い部分で測るのはウエストです。腹囲が1cm縮むごとに体重1kg減の目安になります。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "ホメオダイエットでTDEE（1日の総カロリー）計算に推奨する係数はどれか？",
        "choices": ["基礎代謝×1.4", "基礎代謝×1.2", "基礎代謝×1.55", "基礎代謝×1.725"],
        "correct_index": 0,
        "explanation": "ホメオダイエットでは基礎代謝×1.4を推奨しています。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "ダイエット中、体重・体温・ボルトスコアを報告してもらう頻度は？",
        "choices": ["5日に1度", "毎日", "週に1度", "10日に1度"],
        "correct_index": 0,
        "explanation": "5日に1度、体重と体温とボルトスコアを教えてもらいます。体温測定は体重測定より重要です。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "体温が1度上昇すると代謝量はどう変化するか？",
        "choices": ["13%上昇する", "10%上昇する", "20%上昇する", "5%上昇する"],
        "correct_index": 0,
        "explanation": "体温が1度上昇すると代謝量は13%上昇します。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "体温が1度低下した場合の変化として正しいものはどれか？",
        "choices": ["免疫力30%低下・代謝12%低下", "免疫力10%低下・代謝10%低下", "免疫力20%低下・代謝15%低下", "免疫力50%低下・代謝20%低下"],
        "correct_index": 0,
        "explanation": "体温が1度低下すると免疫力が30%低下し、代謝も12%低下します。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "生理期間の定義として正しいものはどれか？",
        "choices": ["生理初日5日前から生理後2日の間（6日〜10日間）", "生理初日から生理後7日間", "生理3日前から生理後3日間", "生理初日から生理後5日間"],
        "correct_index": 0,
        "explanation": "生理期間の定義は生理初日5日前から生理後2日の間（6日〜10日間）です。この期間はメンテナンスタームとして扱います。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "生理期間中の運動・食事の対応として正しいものはどれか？",
        "choices": ["トレーニングは行わずストレッチのみ、カロリー制限も緩める", "通常通りトレーニングとカロリー制限を継続する", "有酸素運動のみ行い筋トレは休む", "断食を行って腸内環境を整える"],
        "correct_index": 0,
        "explanation": "生理期間中はトレーニングは行わずストレッチだけで良く、カロリー制限と運動を緩めます。欲求が多い人はメンテナンスカロリー＋300kcalまで許容します。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "健康と美容のための1ヶ月の適切なダイエット量はどれか？",
        "choices": ["1kg〜2kg", "3kg〜4kg", "0.5kg未満", "2kg〜3kg"],
        "correct_index": 0,
        "explanation": "1ヶ月でおおよそ1kg〜2kgが健康と美容のための適切なダイエット量です。あくまでも1ヶ月1kgがベストです。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "2週間で何g減っていない場合にリフィードを行うか？",
        "choices": ["300g", "500g", "200g", "100g"],
        "correct_index": 0,
        "explanation": "2週間で300g痩せていない場合にリフィードを行います。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "安定期（停滞期）の定義として正しいものはどれか？",
        "choices": ["1ヶ月で体重が600g以下しか減っていない状態", "1ヶ月で体重が500g以下しか減っていない状態", "2週間で体重が変わらない状態", "3ヶ月で1kg以下しか減っていない状態"],
        "correct_index": 0,
        "explanation": "安定期（停滞期）は1ヶ月で体重が600gしか減っていない状態と確定した場合です。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "カーボサイクルを止める目安は何kg痩せた時か？",
        "choices": ["2kg", "1kg", "3kg", "5kg"],
        "correct_index": 0,
        "explanation": "カーボサイクルは2kg痩せた時点で止める、または1ヶ月以内で止めます。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "脂質1gのカロリーは何kcalか？",
        "choices": ["9kcal", "4kcal", "7kcal", "6kcal"],
        "correct_index": 0,
        "explanation": "脂質は1gあたり9kcalです。タンパク質・炭水化物は4kcal、アルコールは7kcalです。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "NG食品として正しい組み合わせはどれか？",
        "choices": ["人工甘味料・多量のアルコール・多量の赤肉", "白米・もち麦・発酵食品", "プーアル茶・杜仲茶・コーヒー", "エビオス錠・百草丸・整腸薬"],
        "correct_index": 0,
        "explanation": "人工甘味料・多量のアルコール・多量の赤肉・人工科学的な調味料がNGです。白米や発酵食品は推奨されています。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "ホメオダイエットで推奨されるお茶はどれか？",
        "choices": ["プーアル茶・杜仲茶", "センナ茶・ダイエット茶", "麦茶・緑茶", "ハーブティー・ローズヒップ茶"],
        "correct_index": 0,
        "explanation": "プーアル茶または杜仲茶が推奨されます（ダイエット開始から約4ヶ月目から）。センナ茶などの痩せるお茶は腸内環境が乱れるためNGです。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "もち麦と白米を混ぜる場合の理想的なもち麦の比率はどれか？",
        "choices": ["20%〜30%", "10%〜15%", "40%〜50%", "5%〜10%"],
        "correct_index": 0,
        "explanation": "もち麦の比率は20%〜30%が理想です。30%は超えない方が良く、20%以上あれば効果が出やすいです。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "リフィード時の糖質摂取量の基本（体重1kgあたり）はどれか？",
        "choices": ["糖質9〜12g（基本は10g）", "糖質5g", "糖質20g", "糖質15g"],
        "correct_index": 0,
        "explanation": "リフィード時は体重1kg×糖質9〜12g（基本は体重1kg×10g）が目安です。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "朝だけ断食の日の摂取カロリーは通常のアンダーカロリーの何分の何にするか？",
        "choices": ["3分の2", "2分の1", "4分の3", "3分の1"],
        "correct_index": 0,
        "explanation": "朝だけ断食の日には1日の摂取カロリーを普段のアンダーカロリーの3分の2にします。",
    },
    {
        "track": "実務編",
        "category": "ダイエット知識",
        "question_text": "ホメオダイエットの契約期間として正しいものはどれか？",
        "choices": ["最大15ヶ月", "最大6ヶ月", "最大12ヶ月", "最大24ヶ月"],
        "correct_index": 0,
        "explanation": "ホメオダイエットの契約期間は最大15ヶ月です。",
    },
]

print(f"追加する問題数: {len(questions)}")
for i, q in enumerate(questions):
    qid = sheets.add_question(
        q["track"], q["category"], q["question_text"],
        q["choices"], q["correct_index"], q["explanation"]
    )
    print(f"[{i+1}/20] ID={qid} 追加: {q['question_text'][:35]}...")
    time.sleep(2)

print("\n完了！")
