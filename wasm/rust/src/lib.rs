mod utils;

use scraper::{selector, Element, Html, Selector};
use std::cell::RefCell;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsValue;

#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

thread_local! {
    static DOCUMENT: RefCell<Option<Html>> = RefCell::new(None);
}

#[wasm_bindgen]
pub fn get_memory() -> wasm_bindgen::JsValue {
    wasm_bindgen::memory()
}

// メモリ確保用の関数
#[wasm_bindgen]
pub fn allocate_buffer(size: usize) -> u32 {
    let mut buffer = vec![0u8; size];
    let ptr = buffer.as_mut_ptr() as u32;
    std::mem::forget(buffer);
    ptr
}

// 指定ポインタでHTMLを処理
#[wasm_bindgen]
pub fn html_pointer(ptr: u32, length: usize) -> bool {
    let data = unsafe { std::slice::from_raw_parts(ptr as *const u8, length) };
    match std::str::from_utf8(data) {
        Ok(html_str) => {
            let document = Html::parse_document(html_str);
            DOCUMENT.with(|doc| {
                *doc.borrow_mut() = Some(document);
            });
            true
        }
        Err(_) => false,
    }
}

// メモリ解放用の関数
#[wasm_bindgen]
pub fn dealloc_buffer(ptr: u32, length: usize) {
    unsafe {
        let _ = Vec::from_raw_parts(ptr as *mut u8, 0, length);
    }
}

#[wasm_bindgen]
pub fn load_html(html_content: &str) -> bool {
    let document = Html::parse_document(html_content);
    DOCUMENT.with(|doc| {
        *doc.borrow_mut() = Some(document);
    });
    true
}

#[wasm_bindgen]
pub fn load_html_from_bytes(data: &[u8]) -> bool {
    match std::str::from_utf8(data) {
        Ok(html_str) => {
            let document = Html::parse_document(html_str);
            DOCUMENT.with(|doc| {
                *doc.borrow_mut() = Some(document);
            });
            true
        }

        Err(_) => false,
    }
}

pub fn check_selector(path: &str) -> Selector {
    match Selector::parse(path) {
        Ok(s) => s,
        Err(err) => {
            panic!("[Error Selector]: {:?}", err);
        }
    }
}

#[wasm_bindgen]
pub fn get_text(path: &str) -> String {
    let selector: Selector = check_selector(path);
    DOCUMENT.with(|doc| {
        let doc_ref = doc.borrow();
        if let Some(document) = &*doc_ref {
            match document.select(&selector).nth(0) {
                Some(element) => element.text().collect::<Vec<_>>().join(" "),
                None => String::from("Element not found"),
            }
        } else {
            "HTML is not loaded".to_string()
        }
    })
}

#[wasm_bindgen]
pub fn get_text_all(path: &str) -> Vec<String> {
    let selector: Selector = check_selector(path);
    DOCUMENT.with(|doc| {
        let doc_ref = doc.borrow();
        if let Some(document) = &*doc_ref {
            let mut results: Vec<String> = Vec::new();
            for element in document.select(&selector) {
                let texts: Vec<&str> = element.text().collect::<Vec<_>>();
                for text in texts {
                    results.push(text.to_string());
                }
            }
            return results;
        } else {
            vec!["HTML is not loaded".to_string()]
        }
    })
}

#[wasm_bindgen]
pub fn contains(path: &str, key: &str) -> Vec<String> {
    let selector: Selector = check_selector(path);
    DOCUMENT.with(|doc| {
        let doc_ref = doc.borrow();
        if let Some(document) = &*doc_ref {
            let mut results: Vec<&str> = Vec::new();
            for element in document.select(&selector) {
                let texts: Vec<&str> = element.text().collect::<Vec<_>>();
                for text in texts {
                    results.push(text);
                }
            }

            let filtered: Vec<String> = results
                .iter()
                .filter(|word| word.contains(key))
                .map(|s| s.to_string())
                .collect();

            return filtered;
        } else {
            vec!["HTML is not loaded".to_string()]
        }
    })
}

#[wasm_bindgen]
pub fn contain_sibling(path: &str, key: &str) -> Vec<String> {
    let selector: Selector = check_selector(path);
    DOCUMENT.with(|doc| {
        let doc_ref = doc.borrow();
        if let Some(document) = &*doc_ref {
            let mut results: Vec<String> = Vec::new();
            for element in document.select(&selector) {
                if let Some(prev_sibling) = element.prev_sibling_element() {
                    let tag_names: Vec<&str> = path.split('+').collect::<Vec<_>>();
                    let tag_name: &str = tag_names[0].trim();

                    if prev_sibling.value().name() == tag_name {
                        let th_text = prev_sibling.text().collect::<String>();

                        if th_text.contains(key) {
                            let element_text: String = element.text().collect::<String>();
                            results.push(element_text.trim().to_string());
                        }
                    }
                }
            }
            results
        } else {
            vec!["HTML is not loaded".to_string()]
        }
    })
}
