/**
 * APIエラーを処理する
 * @param error エラーオブジェクト
 * @param defaultMessage デフォルトのエラーメッセージ
 * @returns 処理済みのエラーオブジェクト
 */
export function handleApiError(error: unknown, defaultMessage: string): Error {
  console.error(error);
  
  if (error instanceof Error) {
    const errorMessage = error.message;
    
    // URLやアクセス権限のエラー
    if (errorMessage.includes("Unauthorized") || errorMessage.includes("401")) {
      return new Error("スプレッドシートへのアクセス権限がありません。公開設定を確認してください。");
    }
    // 存在しないシートなど
    else if (errorMessage.includes("404") || errorMessage.includes("Not Found")) {
      return new Error("スプレッドシートが見つかりません。URLを確認してください。");
    }
    // スプレッドシート形式の問題
    else if (errorMessage.includes("comment") || errorMessage.includes("カラム")) {
      return new Error("スプレッドシートの形式が正しくありません。commentカラムが必要です。");
    }
    // その他のエラー
    else {
      return new Error(defaultMessage);
    }
  }
  
  return new Error(defaultMessage);
}

/**
 * トーストエラーメッセージを表示する
 * @param toaster トースターオブジェクト
 * @param error エラーオブジェクト
 * @param title エラータイトル
 */
export function showErrorToast(
  toaster: { create: (options: { type: string; title: string; description?: string; duration?: number }) => void },
  error: unknown,
  title: string
): void {
  const errorMessage = error instanceof Error ? error.message : "不明なエラーが発生しました";
  
  toaster.create({
    type: "error",
    title,
    description: errorMessage,
  });
}