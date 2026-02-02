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

/**
 * 文档翻译
 */
export function TranslateDocument(data: FormData) {
    return request({
        url: apiPrefix + 'document/',
        method: 'post',
        data: data,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
}

/**
 * 下载翻译后的文档
 */
export function DownloadDocument(file_path: string) {
    return request({
        url: apiPrefix + 'document/download/',
        method: 'get',
        params: { file_path },
        responseType: 'blob',
    });
}

/**
 * 文档上传（带配置信息）
 */
export function DocumentUpload(data: FormData) {
    return request({
        url: apiPrefix + 'document/upload/',
        method: 'post',
        data: data,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
}

/**
 * 生成PPT
 */
export function GeneratePPT(data: {
    text: string;
    theme: string;
    slide_count: number;
    include_charts: boolean;
    language: string;
}) {
    return request({
        url: apiPrefix + 'generate_ppt/',
        method: 'post',
        data: data,
    });
}

/**
 * 下载PPT文件
 */
export function DownloadPPT(file_path: string) {
    return request({
        url: apiPrefix + 'ppt/download/',
        method: 'get',
        params: { file_path },
        responseType: 'blob',
    });
}

/**
 * 获取PPT文件列表
 */
export function GetPPTList(query: UserPageQuery) {
    return request({
        url: '/api/system/pptfile/',
        method: 'get',
        params: query,
    });
}

/**
 * 获取PPT详情
 */
export function GetPPTDetail(id: string) {
    return request({
        url: '/api/system/pptfile/' + id + '/',
        method: 'get',
    });
}

/**
 * 更新PPT文件信息
 */
export function UpdatePPT(obj: EditReq) {
    return request({
        url: '/api/system/pptfile/' + obj.id + '/',
        method: 'put',
        data: obj,
    });
}

/**
 * 删除PPT文件
 */
export function DeletePPT(id: string) {
    return request({
        url: '/api/system/pptfile/' + id + '/',
        method: 'delete',
    });
}

/**
 * PPT分享
 */
export function SharePPT(id: string) {
    return request({
        url: '/api/system/pptfile/' + id + '/share/',
        method: 'post',
    });
}

/**
 * PPT统计
 */
export function GetPPTStatistics(id: string) {
    return request({
        url: '/api/system/pptfile/' + id + '/statistics/',
        method: 'get',
    });
}

/**
 * 上传文件并生成PPT
 */
export function UploadFileAndGeneratePPT(data: FormData) {
    return request({
        url: '/api/system/pptfile/',
        method: 'post',
        data: data,
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
}

/**
 * 读取上传的文件内容
 */
export function ReadUploadFile(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
            resolve(e.target?.result as string)
        }
        reader.onerror = (e) => {
            reject(e)
        }
        reader.readAsText(file)
    });
}
