import json
import re

COMMA_AND_SPACE_AND_RIGHT_BRACKET = re.compile(r",\s*(\])")

TEST = """Response was: 以下は、提供されたテキストの要約です。

[
  "創作文化は…",
  "生成AIは無断で特徴を抽出…",
  "多くのクリエイターは…",
  "生成AIによるコンテンツは…"
]"""


def parse_response(response):
    """
    指定されたレスポンス文字列からJSON配列を安全に抽出し、パースする。
    オブジェクトリスト形式にも対応。

    以下はdoctestによるテスト例。

    >>> parse_response('以下は...\\n```json\\n["a", "b"]\\n```')
    ['a', 'b']

    >>> parse_response('Response was: なんか説明\\n[ "x", "y" ] さらに何か')
    ['x', 'y']

    >>> parse_response('No json here')
    Traceback (most recent call last):
    ...
    RuntimeError: JSON list not found

    >>> parse_response('["a", "b" , ]')
    ['a', 'b']

    >>> parse_response(TEST)
    ['創作文化は…', '生成AIは無断で特徴を抽出…', '多くのクリエイターは…', '生成AIによるコンテンツは…']

    >>> parse_response('"a"')
    ['a']

    >>> parse_response('[{"意見": "意見1"}, {"意見": "意見2"}]')
    ['意見1', '意見2']

    >>> parse_response('[{"意見": "意見1", "トピック": "トピック1"}, {"意見": "意見2", "トピック": "トピック2"}]')
    ['意見1', '意見2']
    """
    try:
        obj = json.loads(response)
        
        if isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
            items = []
            for item in obj:
                if "意見" in item and isinstance(item["意見"], str):
                    items.append(item["意見"].strip())
                else:
                    for _key, value in item.items():
                        if isinstance(value, str) and value.strip():
                            items.append(value.strip())
                            break
            return items
        
        if isinstance(obj, str):
            obj = [obj]
            
        if isinstance(obj, list):
            items = [a.strip() for a in obj if a and isinstance(a, str) and a.strip()]
            return items
            
        return []
        
    except Exception:
        # 不要なコードブロックを除去
        response = response.replace("```json", "").replace("```", "")

        # JSON配列部分を抽出
        match = re.search(r"\[.*?\]", response, flags=re.DOTALL)
        if not match:
            # JSON配列が見つからなければraise
            raise RuntimeError("JSON list not found") from None

        json_str = match.group(0)
        # ", ]" のようなパターンを "]" に置換
        json_str = COMMA_AND_SPACE_AND_RIGHT_BRACKET.sub(r"\1", json_str)

        try:
            obj = json.loads(json_str)
            
            if isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
                items = []
                for item in obj:
                    if "意見" in item and isinstance(item["意見"], str):
                        items.append(item["意見"].strip())
                    else:
                        for _key, value in item.items():
                            if isinstance(value, str) and value.strip():
                                items.append(value.strip())
                                break
                return items
            
            if isinstance(obj, str):
                obj = [obj]
                
            if isinstance(obj, list):
                items = [a.strip() for a in obj if a and isinstance(a, str) and a.strip()]
                return items
                
            return []
            
        except Exception as e:
            print("Error:", e)
            print("Input was:", json_str)
            print("Response was:", response)
            print("JSON was:", obj)
            print("skip")
            return []


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
