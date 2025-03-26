'use client'

import React from 'react'
import { Button } from '@chakra-ui/react'
import { DownloadIcon } from '@chakra-ui/icons'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { Result, Meta } from '@/type'
import { getApiBaseUrl } from '@/app/utils/api'
import { generateStaticHtml } from './StaticHtmlTemplate'

type Props = {
  reportName: string
  result: Result
  meta: Meta
}

export function DownloadButton({ reportName, result, meta }: Props) {
  const handleDownload = async () => {
    try {
      const zip = new JSZip()

      zip.file(`${reportName}/hierarchical_result.json`, JSON.stringify(result, null, 2))
      
      zip.file(`${reportName}/metadata.json`, JSON.stringify(meta, null, 2))

      const htmlContent = generateStaticHtml(reportName, result, meta)
      zip.file(`${reportName}/index.html`, htmlContent)

      const readmeContent = `# 広聴AI 静的レポート

このZIPファイルには、「${result.config.question}」に関するレポートが含まれています。

## 使用方法
1. ZIPファイルを解凍します
2. 解凍したフォルダ内の「index.html」をブラウザで開きます

## ファイル構成
- index.html: レポート表示用HTMLファイル
- hierarchical_result.json: レポートデータ
- metadata.json: メタデータ

## GitHub Pagesでのホスト方法
1. GitHubリポジトリを作成します
2. 解凍したファイルをリポジトリにアップロードします
3. リポジトリの設定からGitHub Pagesを有効にします
`
      zip.file(`${reportName}/README.md`, readmeContent)

      try {
        const iconResponse = await fetch(getApiBaseUrl() + `/reports/${reportName}/icon.png`)
        if (iconResponse.ok) {
          const iconBlob = await iconResponse.blob()
          zip.file(`${reportName}/icon.png`, iconBlob)
        }

        const reporterResponse = await fetch(getApiBaseUrl() + `/reports/${reportName}/reporter.png`)
        if (reporterResponse.ok) {
          const reporterBlob = await reporterResponse.blob()
          zip.file(`${reportName}/reporter.png`, reporterBlob)
        }
      } catch (error) {
        console.error('Failed to fetch images:', error)
      }

      const content = await zip.generateAsync({ type: 'blob' })
      saveAs(content, `${reportName}-static.zip`)
    } catch (error) {
      console.error('Failed to create ZIP file:', error)
      alert('エクスポート中にエラーが発生しました。')
    }
  }

  return (
    <Button
      leftIcon={<DownloadIcon />}
      colorScheme="blue"
      variant="outline"
      onClick={handleDownload}
      size="sm"
    >
      静的HTMLとしてダウンロード
    </Button>
  )
}
