import { RouteRecordRaw } from 'vue-router';
import { storeToRefs } from 'pinia';
import pinia from '/@/stores/index';
import { useUserInfo } from '/@/stores/userInfo';
import { useRequestOldRoutes } from '/@/stores/requestOldRoutes';
import { Session } from '/@/utils/storage';
import { NextLoading } from '/@/utils/loading';
import { dynamicRoutes, notFoundAndNoPower } from '/@/router/route';
import { formatTwoStageRoutes, formatFlatteningRoutes, router } from '/@/router/index';
import { useRoutesList } from '/@/stores/routesList';
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
import { useMenuApi } from '/@/api/menu/index';
import { handleMenu } from '../utils/menu';
import { BtnPermissionStore } from '/@/plugin/permission/store.permission';
import {SystemConfigStore} from "/@/stores/systemConfig";
import {useDeptInfoStore} from "/@/stores/modules/dept";
import {DictionaryStore} from "/@/stores/dictionary";
import {useFrontendMenuStore} from "/@/stores/frontendMenu";
import {toRaw} from "vue";
const menuApi = useMenuApi();

const layouModules: any = import.meta.glob('../layout/routerView/*.{vue,tsx}');
const viewsModules: any = import.meta.glob('../views/**/*.{vue,tsx}');

/**
 * 获取目录下的 .vue、.tsx 全部文件
 * @method import.meta.glob
 * @link 参考：https://cn.vitejs.dev/guide/features.html#json
 */
const dynamicViewsModules: Record<string, Function> = Object.assign({}, { ...layouModules }, { ...viewsModules });

/**
 * 后端控制路由：初始化方法，防止刷新时路由丢失
 * @method NextLoading 界面 loading 动画开始执行
 * @method useUserInfo().setUserInfos() 触发初始化用户信息 pinia
 * @method useRequestOldRoutes().setRequestOldRoutes() 存储接口原始路由（未处理component），根据需求选择使用
 * @method setAddRoute 添加动态路由
 * @method setFilterMenuAndCacheTagsViewRoutes 设置路由到 vuex routesList 中（已处理成多级嵌套路由）及缓存多级嵌套数组处理后的一维数组
 */
export async function initBackEndControlRoutes() {
	// 界面 loading 动画开始执行
	if (window.nextLoading === undefined) NextLoading.start();
	// 无 token 停止执行下一步
	if (!Session.get('token')) return false;
	// 触发初始化用户信息 pinia
	// https://gitee.com/lyt-top/vue-next-admin/issues/I5F1HP
	await useUserInfo().getApiUserInfo();
	// 获取路由菜单数据
	const res = await getBackEndControlRoutes();
	// 无登录权限时，添加判断
	// https://gitee.com/lyt-top/vue-next-admin/issues/I64HVO
	// if (res.data.length <= 0) return Promise.resolve(true);
	// 处理路由（component），替换 dynamicRoutes（/@/router/route）第一个顶级 children 的路由
	console.log('[Router] 开始处理路由，原始数据:', res.data);
	const {frameIn,frameOut} = handleMenu(res.data)
	console.log('[Router] 处理后的路由数据:', frameIn);
	dynamicRoutes[0].children = await backEndComponent(frameIn);
	console.log('[Router] 最终的动态路由:', dynamicRoutes[0].children);
	// 添加动态路由
	await setAddRoute();
	// 设置路由到 vuex routesList 中（已处理成多级嵌套路由）及缓存多级嵌套数组处理后的一维数组
	await setFilterMenuAndCacheTagsViewRoutes();
}

export async function setRouters(){
	const {frameInRoutes,frameOutRoutes} = await useFrontendMenuStore().getRouter()
	const frameInRouter = toRaw(frameInRoutes)
	const frameOutRouter = toRaw(frameOutRoutes)
	dynamicRoutes[0].children = frameInRouter
	dynamicRoutes.forEach((item:any)=>{
		router.addRoute(item)
	})
	frameOutRouter.forEach((item:any)=>{
		router.addRoute(item)
	})
	const storesRoutesList = useRoutesList(pinia);
	storesRoutesList.setRoutesList([...dynamicRoutes[0].children,...frameOutRouter]);
	const storesTagsView = useTagsViewRoutes(pinia);
	storesTagsView.setTagsViewRoutes([...dynamicRoutes[0].children,...frameOutRouter])

}

/**
 * 设置路由到 vuex routesList 中（已处理成多级嵌套路由）及缓存多级嵌套数组处理后的一维数组
 * @description 用于左侧菜单、横向菜单的显示
 * @description 用于 tagsView、菜单搜索中：未过滤隐藏的(isHide)
 */
export function setFilterMenuAndCacheTagsViewRoutes() {
	const storesRoutesList = useRoutesList(pinia);
	storesRoutesList.setRoutesList(dynamicRoutes[0].children as any);
	setCacheTagsViewRoutes();
}

/**
 * 缓存多级嵌套数组处理后的一维数组
 * @description 用于 tagsView、菜单搜索中：未过滤隐藏的(isHide)
 */
export function setCacheTagsViewRoutes() {
	const storesTagsView = useTagsViewRoutes(pinia);
	storesTagsView.setTagsViewRoutes(formatTwoStageRoutes(formatFlatteningRoutes(dynamicRoutes))[0].children);
}

/**
 * 处理路由格式及添加捕获所有路由或 404 Not found 路由
 * @description 替换 dynamicRoutes（/@/router/route）第一个顶级 children 的路由
 * @returns 返回替换后的路由数组
 */
export function setFilterRouteEnd() {
	let filterRouteEnd: any = formatTwoStageRoutes(formatFlatteningRoutes(dynamicRoutes));
	// notFoundAndNoPower 防止 404、401 不在 layout 布局中，不设置的话，404、401 界面将全屏显示
	// 关联问题 No match found for location with path 'xxx'
	filterRouteEnd[0].children = [...filterRouteEnd[0].children, ...notFoundAndNoPower];
	return filterRouteEnd;
}

/**
 * 添加动态路由
 * @method router.addRoute
 * @description 此处循环为 dynamicRoutes（/@/router/route）第一个顶级 children 的路由一维数组，非多级嵌套
 * @link 参考：https://next.router.vuejs.org/zh/api/#addroute
 */
export async function setAddRoute() {
	await setFilterRouteEnd().forEach((route: RouteRecordRaw) => {
		router.addRoute(route);
	});
}

/**
 * 请求后端路由菜单接口
 * @description isRequestRoutes 为 true，则开启后端控制路由
 * @returns 返回后端路由菜单数据
 */
export function getBackEndControlRoutes() {
	//获取所有的按钮权限
	BtnPermissionStore().getBtnPermissionStore();
	// 获取系统配置
	SystemConfigStore().getSystemConfigs()
	// 获取所有部门信息
	useDeptInfoStore().requestDeptInfo()
	// 获取字典信息
	DictionaryStore().getSystemDictionarys()
	return menuApi.getSystemMenu();
}

/**
 * 重新请求后端路由菜单接口
 * @description 用于菜单管理界面刷新菜单（未进行测试）
 * @description 路径：/src/views/system/menu/component/addMenu.vue
 */
export function setBackEndControlRefreshRoutes() {
	getBackEndControlRoutes();
}

/**
 * 后端路由 component 转换
 * @param routes 后端返回的路由表数组
 * @returns 返回处理成函数后的 component
 */
export function backEndComponent(routes: any) {
	if (!routes) return;
	return routes.map((item: any) => {
		console.log('[Router] 处理路由:', item.name, 'component:', item.component);
		if (item.component) {
			const componentPath = item.component as string;
			const componentFn = dynamicImport(dynamicViewsModules, componentPath);
			if (componentFn) {
				item.component = componentFn;
			} else {
				console.error(`[Router] glob 匹配失败，使用动态导入: ${componentPath}`);
				// 使用 Vite 的动态导入，注意这里的路径处理
				item.component = () => import(`../views/${componentPath}.vue`);
			}
		}
		if(item.is_catalog){
			// 对目录的处理
			item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/parent')
		}
		if(item.is_link){
			// 对外链接的处理
			if(item.is_iframe){
				item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/iframes')
			}else {
				item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/link')
			}
		}else{
			if(item.is_iframe){
				// const iframeRoute:RouteRecordRaw = {
				// 	...item
				// }
				// router.addRoute(iframeRoute)
				item.meta.isLink = item.link_url
				// item.path = `${item.path}Link`
				// item.name = `${item.name}Link`
				// item.meta.isIframe = item.is_iframe
				// item.meta.isKeepAlive = false
				// item.meta.isIframeOpen = true
				item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/link.vue')
			}
		}
		item.children && backEndComponent(item.children);
		return item;
	});
}

/**
 * 后端路由 component 转换函数
 * @param dynamicViewsModules 获取目录下的 .vue、.tsx 全部文件
 * @param component 当前要处理项 component
 * @returns 返回处理成函数后的 component
 */
export function dynamicImport(dynamicViewsModules: Record<string, Function>, component: string) {
	if (!component) return null;

	const keys = Object.keys(dynamicViewsModules);

	console.log(`[Router] ========== 开始匹配组件 ==========`);
	console.log(`[Router] 查找的组件: ${component}`);

	// 处理 component 路径，移除 .vue 后缀
	let newComponent = component.replace('.vue', '').replace(/^\/+/, '');

	// 生成可能的组件路径
	const possiblePaths = [
		newComponent,
		`${newComponent}.vue`,
		`/${newComponent}`,
		`/${newComponent}.vue`,
		`system/${newComponent}`,
		`system/${newComponent}.vue`
	];

	console.log(`[Router] 尝试匹配的路径:`, possiblePaths);

	// 遍历所有可能的路径进行匹配
	for (const path of possiblePaths) {
		// 检查 keys 中是否有匹配的
		for (const key of keys) {
			let k = key
				.replace(/..\/views|../, '')
				.replace("ode_modules/@great-dream/", '')
				.replace("/plugins", '');

			if (k.endsWith(path) || k === path) {
				console.log(`[Router] 匹配成功! key: ${key}, 匹配路径: ${path}`);
				return dynamicViewsModules[key];
			}
		}
	}

	console.error(`[Router] ========== 匹配失败 ==========`);
	console.error(`[Router] 所有可用的 keys (前20个):`, keys.slice(0, 20));
	return null;
}
