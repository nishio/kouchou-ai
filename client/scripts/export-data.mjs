import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outDir = path.join(__dirname, "../out");

// APIからデータを取得してJSONファイルとして保存する関数
async function exportData() {
  const apiBasePath = process.env.NEXT_PUBLIC_API_BASEPATH;
  const apiKey = process.env.NEXT_PUBLIC_PUBLIC_API_KEY || "";
  
  try {
    console.log("=== Exporting data for static build ===");
    console.log(`API Base Path: ${apiBasePath}`);
    
    // メタデータの取得と保存
    console.log("Fetching metadata...");
    const metaResponse = await fetch(`${apiBasePath}/meta/metadata.json`);
    if (!metaResponse.ok) {
      throw new Error(`Failed to fetch metadata: ${metaResponse.status}`);
    }
    const meta = await metaResponse.json();
    
    await fs.mkdir(path.join(outDir, "meta"), { recursive: true });
    await fs.writeFile(
      path.join(outDir, "meta", "metadata.json"),
      JSON.stringify(meta)
    );
    console.log("✅ Metadata exported successfully");
    
    // レポート一覧の取得
    console.log("Fetching reports list...");
    const reportsResponse = await fetch(`${apiBasePath}/reports`, {
      headers: {
        "x-api-key": apiKey,
        "Content-Type": "application/json",
      },
    });
    if (!reportsResponse.ok) {
      throw new Error(`Failed to fetch reports: ${reportsResponse.status}`);
    }
    const reports = await reportsResponse.json();
    
    // レポートディレクトリの作成
    await fs.mkdir(path.join(outDir, "reports"), { recursive: true });
    
    // レポート一覧の保存
    await fs.writeFile(
      path.join(outDir, "reports", "index.json"),
      JSON.stringify(reports)
    );
    console.log(`✅ Reports list exported (${reports.length} reports)`);
    
    // 各レポートのデータを取得して保存
    console.log("Fetching individual report data...");
    for (const report of reports) {
      if (report.status === "ready") {
        console.log(`Processing report: ${report.slug}`);
        const resultResponse = await fetch(`${apiBasePath}/reports/${report.slug}`, {
          headers: {
            "x-api-key": apiKey,
            "Content-Type": "application/json",
          },
        });
        
        if (!resultResponse.ok) {
          console.warn(`⚠️ Failed to fetch report ${report.slug}: ${resultResponse.status}`);
          continue;
        }
        
        const result = await resultResponse.json();
        
        // レポートデータの保存
        await fs.writeFile(
          path.join(outDir, "reports", `${report.slug}.json`),
          JSON.stringify(result)
        );
        console.log(`✅ Report ${report.slug} exported`);
      } else {
        console.log(`Skipping report ${report.slug} (status: ${report.status})`);
      }
    }
    
    console.log("=== All data exported successfully ===");
  } catch (error) {
    console.error("❌ Error exporting data:", error);
    process.exit(1);
  }
}

exportData();
