import {Context} from "hono";// @ts-ignore
import {FC} from "hono/dist/types/jsx";


export const Index: FC<{ c: Context }> = (props: any): any => {
    return (
        <div className="min-h-screen flex flex-col">
            <nav className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 flex items-center">
                                <i className="fas fa-key text-indigo-600 text-2xl mr-2"></i>
                                <span className="text-xl font-bold text-gray-900">{props.c.env.app_name}</span>
                            </div>
                        </div>
                        <div className="hidden sm:ml-6 sm:flex sm:items-center space-x-4">
                            <a href="#features"
                               className="text-gray-500 hover:text-gray-700 px-3 py-2
                               rounded-md text-sm font-medium">功能</a>
                            <a href="/apiui"
                               className="text-gray-500 hover:text-gray-700 px-3 py-2
                               rounded-md text-sm font-medium">API文档</a>
                            <a href="#contact"
                               className="text-gray-500 hover:text-gray-700 px-3 py-2
                               rounded-md text-sm font-medium">联系</a>
                            <a href="/login"
                               className="text-indigo-600 hover:text-indigo-800 px-3 py-2
                               rounded-md text-sm font-medium">登录</a>
                            <a href="/apply"
                               className="bg-indigo-600 text-white px-4 py-2
                               rounded-md text-sm font-medium hover:bg-indigo-700 transition duration-150">注册</a>
                        </div>
                    </div>
                </div>

            </nav>

            <div className="bg-white py-16 sm:py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                            <span className="block">简单易用的软件</span>
                            <span className="block text-indigo-600">授权管理系统</span>
                        </h1>
                        <p className="mt-3 max-w-md mx-auto text-base text-gray-500
                        sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                            {props.c.env.app_text} 为开发者提供完整的软件授权、更新管理和用户验证解决方案。
                        </p>
                        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
                            <div className="rounded-md shadow">
                                <a href="/apply"
                                   className="w-full flex items-center justify-center px-8 py-3
                                   border border-transparent text-base font-medium rounded-md
                                   text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10">
                                    免费开始
                                </a>
                            </div>
                            <div className="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
                                <a href="#features"
                                   className="w-full flex items-center justify-center px-8 py-3
                                   border border-transparent text-base font-medium rounded-md
                                   text-indigo-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
                                    了解更多
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="features" className="py-12 bg-gray-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="lg:text-center">
                        <h2 className="text-base text-indigo-600 font-semibold tracking-wide uppercase">功能</h2>
                        <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                            为开发者设计的一站式解决方案
                        </p>
                        <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                            从授权管理到版本控制，我们为您处理所有复杂的工作。
                        </p>
                    </div>

                    <div className="mt-10">
                        <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">

                            <div className="relative">
                                <div
                                    className="absolute flex items-center justify-center
                                    h-12 w-12 rounded-md bg-indigo-500 text-white">
                                    <i className="fas fa-key"></i>
                                </div>
                                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">授权管理</p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    轻松生成和管理软件授权密钥，支持多种授权模式，包括时间限制、功能限制等。
                                </p>
                            </div>


                            <div className="relative">
                                <div
                                    className="absolute flex items-center justify-center
                                    h-12 w-12 rounded-md bg-indigo-500 text-white">
                                    <i className="fas fa-sync-alt"></i>
                                </div>
                                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">自动更新</p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    为您的软件提供无缝更新体验，支持强制更新和可选更新，实时推送更新公告。
                                </p>
                            </div>


                            <div className="relative">
                                <div
                                    className="absolute flex items-center justify-center
                                    h-12 w-12 rounded-md bg-indigo-500 text-white">
                                    <i className="fas fa-users"></i>
                                </div>
                                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">用户管理</p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    管理您的软件用户，查看授权状态，处理用户请求，一切尽在掌握。
                                </p>
                            </div>


                            <div className="relative">
                                <div
                                    className="absolute flex items-center justify-center
                                    h-12 w-12 rounded-md bg-indigo-500 text-white">
                                    <i className="fas fa-chart-line"></i>
                                </div>
                                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">数据分析</p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    获取详细的软件使用统计和授权数据，帮助您做出更好的商业决策。
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-indigo-700">
                <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
                    <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
                        <span className="block">准备好开始了吗？</span>
                        <span className="block">立即注册您的开发者账户。</span>
                    </h2>
                    <p className="mt-4 text-lg leading-6 text-indigo-200">
                        加入数千名信任我们的开发者，专注于您的核心业务，让我们处理授权管理。
                    </p>
                    <a href="/apply"
                       className="mt-8 w-full inline-flex items-center justify-center px-5 py-3
                       border border-transparent text-base font-medium rounded-md text-indigo-600
                       bg-white hover:bg-indigo-50 sm:w-auto">
                        免费注册
                    </a>
                </div>
            </div>
        </div>
    )
}