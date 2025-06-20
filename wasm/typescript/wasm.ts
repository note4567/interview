import puppeteer from "puppeteer";
import { Data , DomParser} from './type.js';

async function main(url: string) {
  // Wasmモジュールの読み込み
  const wasm = await import('./pkg/parser.js');
  const parser: DomParser = wasm as DomParser;

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
    })
    const page = await browser.newPage();

    console.log(url)
    await page.goto(url);

    const htmlContent = await page.content();
    const encoder = new TextEncoder();
    const binaryHTML = encoder.encode(htmlContent);

    // html の読み込み
    const load_start = performance.now();
    parser.load_html_from_bytes(binaryHTML);
    const load_end = performance.now();
    console.log(`処理時間_load: ${(load_end - load_start).toFixed(4)} ms`);

    let count :number = 0;
    const start = performance.now();
    while(count < 100) {
      parser.contain_sibling("th + td", "店名");
      parser.contain_sibling("th + td", "ジャンル");
      parser.contain_sibling("th + td", "予約・");
      parser.contain_sibling("th + td", "住所");
      parser.contain_sibling("th + td", "交通手段");
      parser.contain_sibling("th + td", "営業時間");
      parser.contain_sibling("th + td", "予算");
      parser.contain_sibling("th + td", "口コミ集計");
      parser.contain_sibling("th + td", "支払い方法");
      parser.contain_sibling("th + td", "席数");
      parser.contain_sibling("th + td", "個室");
      parser.contain_sibling("th + td", "貸切");
      parser.contain_sibling("th + td", "禁煙");
      parser.contain_sibling("th + td", "駐車場");
      parser.contain_sibling("th + td", "空間・設備");
      parser.contain_sibling("th + td", "ドリンク");
      parser.contain_sibling("th + td", "料理");
      parser.contain_sibling("th + td", "利用シーン");
      parser.contain_sibling("th + td", "ロケーション");
      
      count++
    }
    const end = performance.now(); 
    console.log(`処理時間_抽出: ${(end - start).toFixed(4)} ms`);
    console.log(`[処理時間]: ${(end - load_start).toFixed(4)} ms`);
  } catch (error) {
    console.error
  } finally {
    if (browser) {
      await browser.close();
    }
    console.log('End');
  }
}

const url: string = "https://tabelog.com/tokyo/A1309/A130905/13119724/";
main(url);
