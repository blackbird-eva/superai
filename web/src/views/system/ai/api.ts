import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, EditReq, InfoReq, PageQuery } from '@fast-crud/fast-crud';

export const apiPrefix = '/api/system/transdicts/';

/**
 * 获取翻译字典列表
 */
export function GetList(query: UserPageQuery) {
    return request({
        url: apiPrefix,
        method: 'get',
        params: query,
    });
}

/**
 * 获取翻译字典详情
 */
export function GetObj(id: InfoReq) {
    return request({
        url: apiPrefix + id,
        method: 'get',
    });
}

/**
 * 新增翻译字典
 */
export function AddObj(obj: AddReq) {
    return request({
        url: apiPrefix,
        method: 'post',
        data: obj,
    });
}

/**
 * 更新翻译字典
 */
export function UpdateObj(obj: EditReq) {
    return request({
        url: apiPrefix + obj.id + '/',
        method: 'put',
        data: obj,
    });
}

/**
 * 删除翻译字典
 */
export function DelObj(id: string) {
    return request({
        url: apiPrefix + id + '/',
        method: 'delete'
    });
}

/**
 * 获取翻译字典分类列表
 */
export function GetCategories() {
    return request({
        url: apiPrefix + 'categories/',
        method: 'get',
    });
}

/**
 * 读取 Excel 文件内容
 */
export function ReadExcel() {
    return request({
        url: apiPrefix + 'read_excel/',
        method: 'get',
    });
}

/**
 * 导入 Excel 数据到数据库
 */
export function ImportExcel() {
    return request({
        url: apiPrefix + 'read_excel/',
        method: 'post',
    });
}

/**
 * 文本翻译
 */
export function Translate(data: { text: string; source_lang: string; target_lang: string }) {
    return request({
        url: apiPrefix + 'translate/',
        method: 'post',
        data: data,
    });
}
