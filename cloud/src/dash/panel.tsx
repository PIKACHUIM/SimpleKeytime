import {Context} from "hono";// @ts-ignore
import {FC} from "hono/dist/types/jsx";


export const Panel: FC<{ c: Context }> = (props: any): any => {
    return (
        <div>
            <div className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900">欢迎回来, {//user.nickname or user.username}!</h2>
                <p className="mt-1 text-sm text-gray-500">这是您的SimpleKeytime控制台，您可以在这里管理您的软件授权和更新。</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/*<!-- 项目统计 --> */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <div className="p-3 rounded-full bg-indigo-100 text-indigo-600">
                            <i className="fas fa-box-open text-xl"></i>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">项目总数</p>
                            <p className="text-2xl font-semibold text-gray-900">{{projects_count}}</p>
                        </div>
                    </div>
                </div>

                <!-- API调用统计 -->
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <div className="p-3 rounded-full bg-green-100 text-green-600">
                            <i className="fas fa-code text-xl"></i>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">API调用总数</p>
                            <p className="text-2xl font-semibold text-gray-900">{{api_calls_count}}</p>
                        </div>
                    </div>
                </div>

                <!-- 授权统计 -->
                <div className="bg-white p-6 rounded-lg shadow">
                    <div className="flex items-center">
                        <div className="p-3 rounded-full bg-purple-100 text-purple-600">
                            <i className="fas fa-key text-xl"></i>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-500">活跃授权</p>
                            <p className="text-2xl font-semibold text-gray-900">{{active_licenses}}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-6 mb-8 h-[500px]">
                <!-- 左侧图表区 -->
                <div className="flex-1 flex flex-col lg:flex-row gap-6 h-full">
                    <!-- API调用图表 -->
                    <div className="flex-1 bg-white p-4 rounded-lg shadow flex flex-col" style="height: 300px;">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-sm font-medium text-gray-900">API调用统计</h3>
                            <div className="flex space-x-1">
                                <button onClick="loadApiChartData('24h')"
                                        className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200">24小时
                                </button>
                                <button onClick="loadApiChartData('7d')"
                                        className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200">7天
                                </button>
                                <button onClick="loadApiChartData('30d')"
                                        className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200">30天
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 min-h-0">
                            <canvas id="apiChart"></canvas>
                        </div>
                    </div>

                    <!-- 活跃授权图表 -->
                    <div className="flex-1 bg-white p-4 rounded-lg shadow flex flex-col" style="height: 300px;">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-sm font-medium text-gray-900">活跃授权统计</h3>
                            <div className="flex space-x-1">
                                <button onClick="loadLicenseChartData('24h')"
                                        className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200">24小时
                                </button>
                                <button onClick="loadLicenseChartData('7d')"
                                        className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200">7天
                                </button>
                                <button onClick="loadLicenseChartData('30d')"
                                        className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200">30天
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 min-h-0">
                            <canvas id="licenseChart"></canvas>
                        </div>
                    </div>
                </div>
                <!-- 右侧公告区 -->
                <div className="lg:w-1/3 bg-white rounded-lg shadow flex flex-col h-full" style="height: 300px;">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h3 className="text-lg font-medium text-gray-900">系统公告</h3>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4">
                        {% for announcement in announcements %}
                        <div className="mb-4 pb-4 border-b border-gray-200 last:border-0">
                            <div className="flex items-start">
                                <div className="flex-shrink-0 pt-1">
                                    <div
                                        className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                                        <i className="fas fa-bullhorn text-blue-600"></i>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <h4 className="text-sm font-medium text-gray-900">{{announcement.title}}</h4>
                                    <div className="mt-1 text-sm text-gray-500 markdown-content">
                                        {{announcement.content}}
                                    </div>
                                    <p className="mt-2 text-xs text-gray-400">{{
                                        announcement
                                        .created_at.strftime('%Y-%m-%d %H:%M')
                                    }}</p>
                                </div>
                            </div>
                        </div>
                        {% else %}
                        <div className="markdown-content" id="notice-md"></div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- 快速操作 -->
            <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">快速操作</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a href="{{ url_for('dashboard_projects') }}"
                       className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:border-indigo-300 hover:shadow-md transition duration-150">
                        <div className="flex items-center">
                            <div className="p-2 rounded-md bg-indigo-100 text-indigo-600 mr-3">
                                <i className="fas fa-plus"></i>
                            </div>
                            <span className="text-sm font-medium">创建新项目</span>
                        </div>
                    </a>
                    <a href="{{ url_for('dashboard_projects') }}"
                       className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:border-indigo-300 hover:shadow-md transition duration-150">
                        <div className="flex items-center">
                            <div className="p-2 rounded-md bg-green-100 text-green-600 mr-3">
                                <i className="fas fa-key"></i>
                            </div>
                            <span className="text-sm font-medium">生成授权密钥</span>
                        </div>
                    </a>
                    <button onClick="generateReport()"
                            className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:border-indigo-300 hover:shadow-md transition duration-150">
                        <div className="flex items-center">
                            <div className="p-2 rounded-md bg-purple-100 text-purple-600 mr-3">
                                <i className="fas fa-chart-line"></i>
                            </div>
                            <span className="text-sm font-medium">查看统计报告</span>
                        </div>
                    </button>
                </div>
            </div>

            <script src="https://cdn.jsdmirror.com/npm/chart.js"></script>
            <script src="https://cdn.jsdmirror.com/npm/marked/marked.min.js"></script>
        </div>
    )
}