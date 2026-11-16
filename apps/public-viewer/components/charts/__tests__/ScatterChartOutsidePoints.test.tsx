import "@testing-library/jest-dom";
import { Provider } from "@/components/ui/provider";
import type { Argument, Cluster } from "@/type";
import { render, screen } from "@testing-library/react";
import { ScatterChart } from "../ScatterChart";

// jsdom には structuredClone が無く、Chakra v3 の recipe 処理が必要とするため補う
globalThis.structuredClone ??= <T,>(value: T): T => (value === undefined ? value : JSON.parse(JSON.stringify(value)));

type Trace = { x: number[]; y: number[]; hoverinfo?: string; marker?: { size?: number | number[]; color?: unknown } };
// Plotly を実描画せず、渡された trace だけを記録する
let lastData: Trace[] = [];
jest.mock("../ChartCore", () => ({
  ChartCore: (props: { data: Trace[] }) => {
    lastData = props.data;
    return null;
  },
}));

// lucide-react は ESM のみ配布のため空コンポーネントに差し替える
jest.mock("lucide-react", () => new Proxy({}, { get: (_, name) => (name === "__esModule" ? true : () => null) }));

const cluster = (id: string, level: number, parent = ""): Cluster => ({
  id,
  level,
  label: `cluster-${id}`,
  takeaway: "",
  value: 1,
  parent,
  density_rank_percentile: 0.1,
});

const arg = (argId: string, clusterIds: string[], x: number): Argument => ({
  arg_id: argId,
  argument: `arg-${argId}`,
  comment_id: 0,
  x,
  y: x,
  p: 0,
  cluster_ids: clusterIds,
});

// 濃い意見ビューに渡る一覧：最深階層は濃い c1 だけが残り、c2・c3 は密度の絞り込みで外れている
const denseClusters = [cluster("p1", 1), cluster("p2", 1), cluster("c1", 2, "p1")];
const args = [
  arg("a1", ["p1", "c1"], 1),
  arg("a2", ["p1", "c2"], 2),
  arg("a3", ["p2", "c3"], 3),
  arg("a4", ["p1", "c1"], 4),
];

function renderChart(props: Partial<React.ComponentProps<typeof ScatterChart>> = {}) {
  return render(
    <Provider>
      <ScatterChart
        clusterList={denseClusters}
        argumentList={args}
        targetLevel={2}
        showParentAttribution
        showOutsidePoints
        {...props}
      />
    </Provider>,
  );
}

/** ホバーの対象にしない、小さな点の trace（濃い意見グループ外の点） */
const outsideTraces = () => lastData.filter((trace) => trace.hoverinfo === "skip" && trace.marker?.size === 5);

describe("濃い意見ビューで、濃い意見グループに入らない意見も描く（#638）", () => {
  it("濃い意見グループ外の意見を、ホバーしない小さな点の trace として最背面に描く", () => {
    renderChart();
    const outside = outsideTraces();
    expect(outside).toHaveLength(1);
    expect(outside[0].x).toEqual([2, 3]);
    expect(lastData[0]).toBe(outside[0]);
    // 濃い意見グループの点は従来どおり描く
    expect(lastData.some((trace) => trace.hoverinfo !== "skip" && trace.x.includes(1) && trace.x.includes(4))).toBe(
      true,
    );
    expect(screen.getByText("薄い灰色の小さな点は、濃い意見グループに入らない意見です。")).toBeInTheDocument();
  });

  it("属性フィルタで外れた点（灰色・大きさ 7）とは別の trace にする", () => {
    renderChart({ filteredArgumentIds: ["a1"] });
    expect(outsideTraces()[0].x).toEqual([2, 3]);
    // フィルタで外れた a4 は、濃い意見グループの中の灰色の点として描く
    expect(lastData.some((trace) => trace.marker?.size === 7 && trace.x.includes(4))).toBe(true);
  });

  it("showOutsidePoints を付けない表示（全体・詳細クラスタ）では描かない", () => {
    renderChart({ showOutsidePoints: false });
    expect(outsideTraces()).toHaveLength(0);
    expect(screen.queryByText("薄い灰色の小さな点は、濃い意見グループに入らない意見です。")).not.toBeInTheDocument();
  });

  it("すべての意見が表示中のクラスタに入っていれば、背景の trace も注記も出さない", () => {
    renderChart({ argumentList: [args[0], args[3]] });
    expect(outsideTraces()).toHaveLength(0);
    expect(screen.queryByText("薄い灰色の小さな点は、濃い意見グループに入らない意見です。")).not.toBeInTheDocument();
  });
});
