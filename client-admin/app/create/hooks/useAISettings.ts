import { useState } from "react";

/**
 * AIモデル設定を管理するカスタムフック
 */
export function useAISettings() {
  // AIモデル関連の状態
  const [model, setModel] = useState<string>("gpt-4o-mini");
  const [workers, setWorkers] = useState<number>(30);
  const [isPubcomMode, setIsPubcomMode] = useState<boolean>(true);

  /**
   * ワーカー数変更時のハンドラー
   */
  const handleWorkersChange = (value: number) => {
    setWorkers(Math.max(1, Math.min(100, value)));
  };

  /**
   * ワーカー数増加ハンドラー
   */
  const increaseWorkers = () => {
    setWorkers((prev) => Math.min(100, prev + 1));
  };

  /**
   * ワーカー数減少ハンドラー
   */
  const decreaseWorkers = () => {
    setWorkers((prev) => Math.max(1, prev - 1));
  };

  /**
   * モデル変更時のハンドラー
   */
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setModel(e.target.value);
  };

  /**
   * パブコムモード変更時のハンドラー
   */
  const handlePubcomModeChange = (checked: boolean | "indeterminate") => {
    if (checked === "indeterminate") return;
    setIsPubcomMode(checked);
  };

  /**
   * モデル説明文を取得
   */
  const getModelDescription = () => {
    if (model === "gpt-4o-mini") {
      return "GPT-4o mini：最も安価に利用できるモデルです。価格の詳細はOpenAIが公開しているAPI料金のページをご参照ください。";
    } else if (model === "gpt-4o") {
      return "GPT-4o：gpt-4o-miniと比較して高性能なモデルです。性能は高くなりますが、gpt-4o-miniと比較してOpenAI APIの料金は高くなります。";
    } else if (model === "o3-mini") {
      return "o3-mini：gpt-4oよりも高度な推論能力を備えたモデルです。性能はより高くなりますが、gpt-4oと比較してOpenAI APIの料金は高くなります。";
    }
    return "";
  };

  /**
   * AI設定をリセット
   */
  const resetAISettings = () => {
    setModel("gpt-4o-mini");
    setWorkers(30);
    setIsPubcomMode(true);
  };

  return {
    model,
    workers,
    isPubcomMode,
    handleModelChange,
    handleWorkersChange,
    increaseWorkers,
    decreaseWorkers,
    handlePubcomModeChange,
    getModelDescription,
    resetAISettings,
  };
}