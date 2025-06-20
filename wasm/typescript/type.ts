// 関数型の定義
export type DomParser = {
  get_memory:() => any;
  allocate_buffer:(size: number) => number;
  html_pointer:(ptr: number, length: number) => boolean;
  dealloc_buffer:(ptr: number, length: number )=> void;
  load_html: (html: string) => boolean;
  load_html_from_bytes(data: Uint8Array): boolean;
  contains: (path: string, key: string) => string[];
  contain_sibling: (path: string, key: string) => string[];
  get_text: (path: string) => string;
  get_text_all: (path: string) => string[];
};


// 取得項目の定義
export type Data = {
  name: string
  address: string,
  tel: string,
  time: string,
  service: Array<string>,
  labelList: Array<string>
}
