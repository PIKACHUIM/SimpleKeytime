// 生成报告
function generateReport() {
    fetch('/dashboard/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('报告已生成，链接10分钟内有效');
                // 在新标签页打开报告
                window.open(data.report_url, '_blank');

            } else {
                alert('生成报告失败');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('生成报告时出错');
        });
}

// 图表配置
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        if (context.chart.id == 'licenseChart') {
                            label += `活跃授权数: ${context.parsed.y}`;
                        } else {
                            label += `API请求数: ${context.parsed.y}`;
                        }
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                precision: 0
            }
        }
    }
};

// 初始化图表
const apiChart = new Chart(
    document.getElementById('apiChart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                fill: true,
                tension: 0.1
            }]
        },
        options: chartOptions
    }
);

const licenseChart = new Chart(
    document.getElementById('licenseChart'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.1
            }]
        },
        options: chartOptions
    }
);

// 加载API图表数据
function loadApiChartData(range) {
    fetch(`/dashboard/api-stats?type=api&range=${range}`)
        .then(res => res.json())
        .then(data => {
            apiChart.data.labels = data.labels;
            apiChart.data.datasets[0].data = data.data;
            apiChart.update();
        })
        .catch(error => {
            console.error('Error loading API chart data:', error);
            // 默认数据
            apiChart.data.labels = Array.from({length: 24}, (_, i) => `${i}:00`);
            apiChart.data.datasets[0].data = Array(24).fill(0);
            apiChart.update();
        });
}

// 加载授权图表数据
function loadLicenseChartData(range) {
    fetch(`/dashboard/api-stats?type=license&range=${range}`)
        .then(res => res.json())
        .then(data => {
            licenseChart.data.labels = data.labels;
            licenseChart.data.datasets[0].data = data.data;
            licenseChart.update();
        })
        .catch(error => {
            console.error('Error loading license chart data:', error);
            // 默认数据
            licenseChart.data.labels = Array.from({length: 24}, (_, i) => `${i}:00`);
            licenseChart.data.datasets[0].data = Array(24).fill(0);
            licenseChart.update();
        });
}

// 加载notice.md
fetch('/static/notice.md')
    .then(response => {
        if (!response.ok) throw new Error('Notice file not found');
        return response.text();
    })
    .then(text => {
        const noticeContainer = document.getElementById('notice-md');
        if (noticeContainer) {
            noticeContainer.innerHTML = marked.parse(text);
        }
    })
    .catch(error => {
        console.error('Error loading notice.md:', error);
        const noticeContainer = document.getElementById('notice-md');
        if (noticeContainer) {
            noticeContainer.innerHTML = '<p class="text-gray-500">暂无系统公告</p>';
        }
    });

// 默认加载24小时数据
loadApiChartData('24h');
loadLicenseChartData('24h');