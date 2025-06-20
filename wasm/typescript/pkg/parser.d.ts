/* tslint:disable */
/* eslint-disable */
export function get_memory(): any;
export function allocate_buffer(size: number): number;
export function html_pointer(ptr: number, length: number): boolean;
export function dealloc_buffer(ptr: number, length: number): void;
export function load_html(html_content: string): boolean;
export function load_html_from_bytes(data: Uint8Array): boolean;
export function get_text(path: string): string;
export function get_text_all(path: string): string[];
export function contains(path: string, key: string): string[];
export function contain_sibling(path: string, key: string): string[];
