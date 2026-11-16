import { Link, Text } from "@chakra-ui/react";

/** 残高不足・レート制限（429）の見分け方と対処、ChatGPT Plus との違いをまとめた説明書のページ（#292） */
export const API_BILLING_DOCS_URL =
  "https://digitaldemocracy2030.github.io/kouchou-ai/self-hosting/api-billing-and-rate-limits/";

/** 接続確認の結果が残高不足・レート制限のときに出す、説明書へのリンク */
export function ApiBillingDocsLink() {
  return (
    <Text as="span" display="block" mt="1" fontSize="sm">
      見分け方と対処：
      <Link href={API_BILLING_DOCS_URL} target="_blank" rel="noopener noreferrer" textDecoration="underline">
        APIの課金と429エラー（残高不足・レート制限）
      </Link>
    </Text>
  );
}
