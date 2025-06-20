## Sample scripts for job interviews
### ・クローリングスクリプト
```
./crawling
  ├── async_selenium
          selenium の async リクエスト

  ├── fetch
          fetch リクエスト

  ├── gnavi
          「ぐるなび」をクロール (scrapy) 
          件数: 約 41万件

  ├── saison
          「セゾンのふるさと納税」をクロール (ajax リクエスト)
          件数: 約 77万件

  └── tabelog
          「食べログ」をクロール (aiohttp)
          件数: 約 87万件
```

### ・AIクロールプロトタイプ
Transformers(BertForQuestionAnswering)を利用した文字列抽出
```
./qa
  ├── chunk_file.py
          データを集約するスクリプト

  ├── inference.py
          推論処理

  ├── Inference_Result.png
          推論結果(画像)

  ├── qa_module
  │   ├── pre_process.py
                エンコーディング処理を行う

  │   ├── qa_toknizer.py
                日本語用の QAトークナイザ

  │   └── set_log.py
  ├── qa_train.py
          学習処理

  └── train
          Q&A 用のデータ
            ├── dev.json
            ├── test.json
            └── train.json
```
### ・WebAssembly(HTMLパーサ)
Rust(scraper)を用いたパース処理
```
./wasm
├── rust
│   ├── Cargo.toml
│   ├── pkg
                ビルドされた wasmモジュール

│   └── src
│       ├── lib.rs
│       └── utils.rs
                htmlパーサ処理

└── typescript
    ├── package.json
    ├── pkg
                wasmモジュール

    ├── type.ts
    ├── wasm_memory.ts
    └── wasm.ts
                検証用クローリングスクリプト
```
