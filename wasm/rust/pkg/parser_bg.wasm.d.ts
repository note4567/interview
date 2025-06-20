/* tslint:disable */
/* eslint-disable */
export const memory: WebAssembly.Memory;
export const get_memory: () => any;
export const allocate_buffer: (a: number) => number;
export const html_pointer: (a: number, b: number) => number;
export const load_html: (a: number, b: number) => number;
export const load_html_from_bytes: (a: number, b: number) => number;
export const get_text: (a: number, b: number) => [number, number];
export const get_text_all: (a: number, b: number) => [number, number];
export const contains: (a: number, b: number, c: number, d: number) => [number, number];
export const contain_sibling: (a: number, b: number, c: number, d: number) => [number, number];
export const dealloc_buffer: (a: number, b: number) => void;
export const __wbindgen_export_0: WebAssembly.Table;
export const __wbindgen_malloc: (a: number, b: number) => number;
export const __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
export const __wbindgen_free: (a: number, b: number, c: number) => void;
export const __externref_drop_slice: (a: number, b: number) => void;
export const __wbindgen_start: () => void;
