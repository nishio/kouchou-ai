import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button, Heading, Image, Text, Box, VStack } from "@chakra-ui/react";
import { BookOpenIcon } from "lucide-react";

export function TerminologyGuide() {
  return (
    <DialogRoot size="xl" placement="center" motionPreset="slide-in-bottom">
      <DialogTrigger asChild>
        <Button variant={"ghost"}>
          <BookOpenIcon />
          <Text display={{ base: "none", lg: "block" }}>
            用語解説
          </Text>
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <Heading as={"h2"} size={"xl"} className={"headingColor"}>
            用語解説
          </Heading>
          <DialogCloseTrigger />
        </DialogHeader>
        <DialogBody>
          <VStack spacing={8} align="stretch">
            {/* プロンプト */}
            <Box>
              <Heading as={"h3"} size={"md"} mb={2}>
                プロンプト
              </Heading>
              <Text mb={2}>
                プロンプトとは、AIモデル（大規模言語モデル）に対して与える指示文のことです。広聴AIでは、コメントから意見を抽出したり、クラスタにラベルを付けたりする際に、AIに対して特定の形式で回答するよう指示するために使用されています。
              </Text>
              <Text>
                プロンプトは、AIが実行すべきタスクの内容、期待される出力形式、考慮すべき制約条件などを含み、AIの出力品質を大きく左右する重要な要素です。広聴AIの各処理ステップ（抽出、初期ラベリング、統合ラベリング、要約など）のために、それぞれ専用のプロンプトが用意されたレポートの質を良くするために優れたプロンプトを使ったかどうかが生成されたレポートの質を決めることができます。
              </Text>
            </Box>

            {/* 埋め込み */}
            <Box>
              <Heading as={"h3"} size={"md"} mb={2}>
                埋め込み
              </Heading>
              <Text mb={2}>
                埋め込み（エンベディング）とは、テキストなどの非数値データを数値ベクトル（多次元の数値の配列）に変換する技術です。広聴AIでは、抽出された意見を数値ベクトルに変換することで、意見同士の類似性を計算し、クラスタリングを行うために使用されています。
              </Text>
              <Text>
                埋め込みにより、「似た意味を持つ意見は似たベクトル表現になる」という性質を活用して、意見をグループ化することができます。広聴AIでは、最新の埋め込みモデルを使用して高品質な意見の数値表現を生成し、効果的なクラスタリングを実現しています。
              </Text>
            </Box>

            {/* 濃い(クラスタ) */}
            <Box>
              <Heading as={"h3"} size={"md"} mb={2}>
                濃い(クラスタ)
              </Heading>
              <Text mb={2}>
                「濃い」クラスタとは、クラスタ内の意見が互いに非常に類似している（密集している）クラスタのことを指します。広聴AIでは、クラスタの「密度」を計算し、密度の高いクラスタを「濃いクラスタ」として識別しています。
              </Text>
              <Text>
                単語レベルで言い換えてもわかりやすくならないため、やや専門的な表現ですが、濃いクラスタは「特定のトピックについて多くの人が似たような意見を持っている」ことを示す重要な指標となります。広聴AIのインターフェースでは、クラスタの密度に基づいてフィルタリングすることで、特に意見が集中しているトピックを見つけることができます。
              </Text>
            </Box>

            {/* 縦軸・横軸 */}
            <Box>
              <Heading as={"h3"} size={"md"} mb={2}>
                縦軸・横軸
              </Heading>
              <Text mb={2}>
                広聴AIの散布図（スキャッタープロット）表示における「縦軸」と「横軸」は、多次元の埋め込みベクトルを2次元に削減した際の座標軸です。これらの軸自体には特定の意味はなく、単に似た意見が近くに配置されるように計算されています。
              </Text>
              <Text>
                縦軸・横軸はそれぞれが何を表しているわけではなく、「似た意見は近くに、異なる意見は遠くに」配置されるように自動的に計算された座標です。これにより、意見の全体的な分布や関係性を視覚的に把握することができます。
              </Text>
            </Box>
          </VStack>
        </DialogBody>
      </DialogContent>
    </DialogRoot>
  );
}
