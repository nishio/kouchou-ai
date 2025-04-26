"use client";

import { Tooltip } from "@/components/ui/tooltip";
import { Box, Text } from "@chakra-ui/react";
import { HelpCircleIcon } from "lucide-react";
import { ReactNode } from "react";

type TermDefinitions = {
  [key: string]: {
    title: string;
    description: string;
  };
};

export const termDefinitions: TermDefinitions = {
  "プロンプト": {
    title: "プロンプト",
    description: "AIモデル（大規模言語モデル）に対して与える指示文のことです。広聴AIでは、コメントから意見を抽出したり、クラスタにラベルを付けたりする際に、AIに対して特定の形式で回答するよう指示するために使用されています。"
  },
  "埋め込み": {
    title: "埋め込み",
    description: "テキストなどの非数値データを数値ベクトル（多次元の数値の配列）に変換する技術です。広聴AIでは、抽出された意見を数値ベクトルに変換することで、意見同士の類似性を計算し、クラスタリングを行うために使用されています。"
  },
  "濃いクラスタ": {
    title: "濃い(クラスタ)",
    description: "クラスタ内の意見が互いに非常に類似している（密集している）クラスタのことを指します。広聴AIでは、クラスタの「密度」を計算し、密度の高いクラスタを「濃いクラスタ」として識別しています。"
  },
  "縦軸横軸": {
    title: "縦軸・横軸",
    description: "広聴AIの散布図（スキャッタープロット）表示における「縦軸」と「横軸」は、多次元の埋め込みベクトルを2次元に削減した際の座標軸です。これらの軸自体には特定の意味はなく、単に似た意見が近くに配置されるように計算されています。"
  }
};

type TermTooltipProps = {
  term: keyof typeof termDefinitions;
  children: ReactNode;
};

export function TermTooltip({ term, children }: TermTooltipProps) {
  const definition = termDefinitions[term];
  
  if (!definition) {
    return <>{children}</>;
  }

  return (
    <Tooltip
      showArrow
      content={
        <Box p={2}>
          <Text fontWeight="bold" mb={1}>{definition.title}</Text>
          <Text fontSize="sm">{definition.description}</Text>
        </Box>
      }
    >
      <span style={{ display: "inline-flex", alignItems: "center" }}>
        {children}
        <HelpCircleIcon size={14} style={{ marginLeft: "4px", cursor: "pointer" }} />
      </span>
    </Tooltip>
  );
}
