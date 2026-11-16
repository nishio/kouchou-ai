import "@testing-library/jest-dom";
import { Provider } from "@/components/ui/provider";
import { LanguageProvider } from "@/lib/i18n/LanguageContext";
import type { Result } from "@/type";
import { render, screen, within } from "@testing-library/react";
import fixture from "../dev/viewer-fixture.json";
import { Analysis } from "./Analysis";

// jsdom には structuredClone が無く、Chakra v3 の recipe 処理が必要とするため補う
globalThis.structuredClone ??= <T,>(value: T): T => (value === undefined ? value : JSON.parse(JSON.stringify(value)));

// lucide-react は ESM のみ配布で Jest が変換しないため、全アイコンを空コンポーネントにする
jest.mock("lucide-react", () => new Proxy({}, { get: (_, name) => (name === "__esModule" ? true : () => null) }));

function renderAnalysis(result: Result) {
  return render(
    <Provider>
      <LanguageProvider>
        <Analysis result={result} />
      </LanguageProvider>
    </Provider>,
  );
}

/** 「集約した意見グループ数」の欄（見出しの文言を含む一番内側の縦並び） */
function clusterCountBlock() {
  return screen.getByText("集約した意見グループ数").parentElement as HTMLElement;
}

describe("集約した意見グループ数の表記（#213）", () => {
  it("2 階層のレポートは、矢印を使わず各階層の数を階層名つきで並べる", () => {
    const result = structuredClone(fixture) as unknown as Result;
    const level1 = result.clusters.filter((c) => c.level === 1).length;
    const level2 = result.clusters.filter((c) => c.level === 2).length;
    renderAnalysis(result);

    const block = clusterCountBlock();
    expect(block).not.toHaveTextContent("→");
    expect(within(block).getByText("第1階層").previousElementSibling).toHaveTextContent(String(level1));
    expect(within(block).getByText("第2階層").previousElementSibling).toHaveTextContent(String(level2));
  });

  it("1 階層のレポートは、数だけを出し、階層名を付けない", () => {
    const result = structuredClone(fixture) as unknown as Result;
    result.clusters = result.clusters.filter((c) => c.level <= 1);
    const level1 = result.clusters.filter((c) => c.level === 1).length;
    renderAnalysis(result);

    const block = clusterCountBlock();
    expect(block).toHaveTextContent(String(level1));
    expect(within(block).queryByText("第1階層")).not.toBeInTheDocument();
    expect(block).not.toHaveTextContent("→");
  });
});
