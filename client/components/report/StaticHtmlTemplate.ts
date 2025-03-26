export function generateStaticHtml(reportName: string, result: any, meta: any): string {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${result.config.question} - ${meta.reporter}</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      margin: 0;
      padding: 0;
    }
    .container {
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 1px solid #eaeaea;
    }
    .header-logo {
      height: 40px;
    }
    .overview {
      background-color: #f9f9f9;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 30px;
    }
    .chart-container {
      width: 100%;
      height: 600px;
      margin: 30px 0;
      border: 1px solid #eaeaea;
      border-radius: 8px;
    }
    .cluster {
      margin-bottom: 20px;
      padding: 15px;
      border: 1px solid #eaeaea;
      border-radius: 8px;
    }
    .cluster h3 {
      margin-top: 0;
      color: #2c5282;
    }
    .footer {
      margin-top: 50px;
      padding-top: 20px;
      border-top: 1px solid #eaeaea;
      text-align: center;
      font-size: 0.9em;
      color: #666;
    }
    .tabs {
      display: flex;
      margin-bottom: 20px;
    }
    .tab {
      padding: 10px 20px;
      cursor: pointer;
      border: 1px solid #eaeaea;
      border-bottom: none;
      border-radius: 8px 8px 0 0;
      margin-right: 5px;
    }
    .tab.active {
      background-color: #2c5282;
      color: white;
    }
    .back-button {
      display: inline-block;
      margin-bottom: 20px;
      padding: 8px 16px;
      background-color: #f0f0f0;
      border-radius: 4px;
      text-decoration: none;
      color: #333;
    }
    .back-button:hover {
      background-color: #e0e0e0;
    }
  </style>
</head>
<body>
  <div class="container">
    <a href="javascript:history.back()" class="back-button">← 戻る</a>
    
    <div class="header">
      <h1 id="report-title"></h1>
      <div>
        <img src="reporter.png" alt="${meta.reporter}" class="header-logo" onerror="this.style.display='none'" />
      </div>
    </div>
    
    <div class="overview" id="overview"></div>
    
    <div class="tabs">
      <div class="tab active" onclick="switchTab('scatter')">散布図</div>
      <div class="tab" onclick="switchTab('treemap')">ツリーマップ</div>
    </div>
    
    <div class="chart-container" id="chart"></div>
    
    <div id="clusters"></div>
    
    <div class="footer">
      <p>このレポートは広聴AIによって生成されました</p>
      <p>© ${new Date().getFullYear()} ${meta.reporter}</p>
      <p><a href="${meta.webLink || '#'}" target="_blank">${meta.reporter}のウェブサイト</a></p>
    </div>
  </div>

  <script>
    let result;
    let currentChart = 'scatter';
    
    function switchTab(chartType) {
      currentChart = chartType;
      document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
      document.querySelector(\`.tab[onclick="switchTab('\${chartType}')"]\`).classList.add('active');
      renderChart();
    }
    
    function renderChart() {
      const chart = echarts.init(document.getElementById('chart'));
      
      if (currentChart === 'scatter') {
        renderScatterChart(chart);
      } else if (currentChart === 'treemap') {
        renderTreemapChart(chart);
      }
    }
    
    function renderScatterChart(chart) {
      const scatterData = result.arguments.map(arg => {
        return {
          value: [arg.x, arg.y],
          id: arg.arg_id,
          argument: arg.argument,
          clusterIds: arg.cluster_ids
        };
      });
      
      const level1Clusters = result.clusters.filter(c => c.level === 1);
      
      const series = level1Clusters.map(cluster => {
        const clusterArgs = scatterData.filter(arg => 
          arg.clusterIds.includes(cluster.id)
        );
        
        return {
          name: cluster.label,
          type: 'scatter',
          data: clusterArgs.map(arg => ({
            value: arg.value,
            argument: arg.argument
          })),
          symbolSize: 10
        };
      });
      
      const option = {
        title: {
          text: '意見の分布'
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return params.data.argument;
          }
        },
        legend: {
          data: level1Clusters.map(c => c.label),
          type: 'scroll',
          orient: 'vertical',
          right: 10,
          top: 20,
          bottom: 20
        },
        xAxis: {},
        yAxis: {},
        series: series
      };
      
      chart.setOption(option);
    }
    
    function renderTreemapChart(chart) {
      const level1Clusters = result.clusters.filter(c => c.level === 1);
      
      const treeData = {
        name: 'すべての意見',
        children: level1Clusters.map(cluster => ({
          name: cluster.label,
          value: cluster.value,
          id: cluster.id,
          children: result.clusters
            .filter(c => c.parent === cluster.id)
            .map(subCluster => ({
              name: subCluster.label,
              value: subCluster.value,
              id: subCluster.id
            }))
        }))
      };
      
      const option = {
        title: {
          text: 'クラスター構造'
        },
        tooltip: {
          formatter: function(info) {
            return [
              '<div style="font-weight:bold">' + info.name + '</div>',
              '意見数: ' + info.value
            ].join('');
          }
        },
        series: [{
          name: 'クラスター',
          type: 'treemap',
          data: treeData.children,
          label: {
            show: true,
            formatter: '{b}'
          },
          breadcrumb: {
            show: true
          },
          upperLabel: {
            show: true,
            height: 30
          }
        }]
      };
      
      chart.setOption(option);
    }
    
    function displayClusters() {
      const level1Clusters = result.clusters.filter(c => c.level === 1);
      
      const clustersHtml = level1Clusters.map(cluster => {
        return \`
          <div class="cluster">
            <h3>\${cluster.label}</h3>
            <p>\${cluster.takeaway || ''}</p>
            <p>意見数: \${cluster.value}</p>
          </div>
        \`;
      }).join('');
      
      document.getElementById('clusters').innerHTML = clustersHtml;
    }
    
    fetch('./hierarchical_result.json')
      .then(response => response.json())
      .then(data => {
        result = data;
        
        document.getElementById('report-title').textContent = result.config.question;
        
        document.getElementById('overview').innerHTML = \`
          <h2>概要</h2>
          <p>\${result.overview}</p>
          <p>コメント数: \${result.comment_num}</p>
        \`;
        
        renderChart();
        
        displayClusters();
      })
      .catch(error => {
        console.error('Failed to load report data:', error);
        document.body.innerHTML = '<div class="container"><h1>エラー</h1><p>レポートデータの読み込みに失敗しました。</p></div>';
      });
  </script>
</body>
</html>`;
}
