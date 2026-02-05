"use client";

import { Box, Code, Text } from "@chakra-ui/react";

type ApiConnectionErrorProps = {
  isServerSide: boolean;
};

export const ApiConnectionError = ({ isServerSide }: ApiConnectionErrorProps) => {
  return (
    <Box>
      <Text fontWeight="bold">エラー：データの取得に失敗しました</Text>
      {isServerSide ? (
        <Text>
          サーバー側でAPIに接続できませんでした。
          <Code ml={2}>API_BASEPATH</Code> が正しいか確認してください。
        </Text>
      ) : (
        <Text>
          ブラウザからAPIに接続できませんでした。
          <Code ml={2}>NEXT_PUBLIC_API_BASEPATH</Code> が正しいか確認してください。
        </Text>
      )}
    </Box>
  );
};
