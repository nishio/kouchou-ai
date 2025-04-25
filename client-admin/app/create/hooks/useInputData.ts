import { toaster } from "@/components/ui/toaster";
import { useCallback, useState } from "react";
import { deleteSpreadsheetData, getSpreadsheetData, importSpreadsheet } from "../api/spreadsheet";
import { parseCsv } from "../parseCsv";
import { InputType, SpreadsheetComment } from "../types";
import { showErrorToast } from "../utils/error-handler";

/**
 * 入力データを管理するカスタムフック
 */
export function useInputData(
  onDataLoaded: (commentCount: number) => void
) {
  // 入力タイプの状態
  const [inputType, setInputType] = useState<InputType>("file");
  
  // CSVファイル関連の状態
  const [csv, setCsv] = useState<File | null>(null);
  
  // スプレッドシート関連の状態
  const [spreadsheetUrl, setSpreadsheetUrl] = useState<string>("");
  const [spreadsheetImported, setSpreadsheetImported] = useState<boolean>(false);
  const [spreadsheetLoading, setSpreadsheetLoading] = useState<boolean>(false);
  const [spreadsheetData, setSpreadsheetData] = useState<SpreadsheetComment[]>([]);
  const [importedId, setImportedId] = useState<string>("");
  
  // カラム関連の状態
  const [csvColumns, setCsvColumns] = useState<string[]>([]);
  const [selectedCommentColumn, setSelectedCommentColumn] = useState<string>("");

  /**
   * CSVファイル変更時のハンドラー
   */
  const handleCsvChange = useCallback(async (file: File | null) => {
    setCsv(file);
    if (file) {
      try {
        const parsed = await parseCsv(file);
        if (parsed.length > 0) {
          const columns = Object.keys(parsed[0]);
          setCsvColumns(columns);
          if (columns.includes("comment")) {
            setSelectedCommentColumn("comment");
          }
          onDataLoaded(parsed.length);
        }
      } catch (error) {
        showErrorToast(toaster, error, "CSVファイルの読み込みに失敗しました");
      }
    } else {
      setCsvColumns([]);
      setSelectedCommentColumn("");
    }
  }, [onDataLoaded]);

  /**
   * スプレッドシートのインポート
   */
  const handleImportSpreadsheet = useCallback(async (id: string) => {
    if (!spreadsheetUrl.trim()) {
      toaster.create({
        type: "error",
        title: "入力エラー",
        description: "スプレッドシートのURLを入力してください",
      });
      return;
    }

    setSpreadsheetLoading(true);
    try {
      await importSpreadsheet(spreadsheetUrl, id);
      setImportedId(id);

      // スプレッドシートのデータを取得
      const commentData = await getSpreadsheetData(id);
      setSpreadsheetData(commentData.comments);

      if (commentData.comments.length > 0) {
        const columns = Object.keys(commentData.comments[0]);
        setCsvColumns(columns);
        if (columns.includes("comment")) {
          setSelectedCommentColumn("comment");
        }
      }

      // 推奨クラスタ数を設定
      onDataLoaded(commentData.comments.length);

      toaster.create({
        type: "success",
        title: "成功",
        description: `スプレッドシートのデータ ${commentData.comments.length} 件を取得しました`,
      });
      setSpreadsheetImported(true);
    } catch (error) {
      showErrorToast(toaster, error, "データ取得エラー");
      setSpreadsheetImported(false);
    } finally {
      setSpreadsheetLoading(false);
    }
  }, [spreadsheetUrl, onDataLoaded]);

  /**
   * スプレッドシートデータのクリア
   */
  const handleClearSpreadsheetData = useCallback(async () => {
    try {
      setSpreadsheetLoading(true);
      if (importedId) {
        await deleteSpreadsheetData(importedId);
      }

      toaster.create({
        type: "success",
        title: "成功",
        description: "データをクリアしました",
      });
    } catch (error) {
      showErrorToast(toaster, error, "警告");
    } finally {
      // UIの状態をリセット
      setSpreadsheetImported(false);
      setSpreadsheetData([]);
      setSpreadsheetLoading(false);
      setImportedId("");
      setSpreadsheetUrl("");
      setSelectedCommentColumn("");
      setCsvColumns([]);
    }
  }, [importedId]);

  /**
   * 入力タイプ変更時のハンドラー
   */
  const handleInputTypeChange = useCallback((newType: InputType) => {
    setInputType(newType);

    if (newType === "file" && csv) {
      // CSVのカラムを再構築
      parseCsv(csv).then((parsed) => {
        if (parsed.length > 0) {
          const columns = Object.keys(parsed[0]);
          setCsvColumns(columns);
          if (columns.includes("comment")) {
            setSelectedCommentColumn("comment");
          }
          onDataLoaded(parsed.length);
        }
      });
    } else if (newType === "spreadsheet" && spreadsheetData.length > 0) {
      // スプレッドシートのカラムを再構築
      const columns = Object.keys(spreadsheetData[0]);
      setCsvColumns(columns);
      if (columns.includes("comment")) {
        setSelectedCommentColumn("comment");
      }
      onDataLoaded(spreadsheetData.length);
    } else {
      // データがない場合はカラムリセット
      setCsvColumns([]);
      setSelectedCommentColumn("");
    }
  }, [csv, spreadsheetData, onDataLoaded]);

  /**
   * スプレッドシートのインポートが可能かどうか
   */
  const canImport = spreadsheetUrl.trim() !== "" && !spreadsheetImported;

  return {
    inputType,
    csv,
    spreadsheetUrl,
    spreadsheetImported,
    spreadsheetLoading,
    spreadsheetData,
    importedId,
    csvColumns,
    selectedCommentColumn,
    canImport,
    setInputType: handleInputTypeChange,
    setCsv: handleCsvChange,
    setSpreadsheetUrl,
    setSelectedCommentColumn,
    setCsvColumns,
    importSpreadsheet: handleImportSpreadsheet,
    clearSpreadsheetData: handleClearSpreadsheetData,
  };
}