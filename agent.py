import os
import time # ←これを追加
import requests
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent

import urllib.parse # これをファイルの先頭付近に追加
import re


@tool
def fetch_page(url: str) -> str:
    """指定されたURLのWebページからテキスト情報を抽出します。URLは完全な形式で入力してください。"""
    print(f"\n[ツール実行] {url} にアクセス中...")
    time.sleep(2)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # 1. 最小限のノイズ除去 (ヘッダーとフッターのみ)
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        # 2. リンクのMarkdown化 (すべてのリンクを確実に変換)
        for a in soup.find_all('a', href=True):
            full_url = urllib.parse.urljoin(url, a['href'])
            a.replace_with(f"[{a.get_text(strip=True)}]({full_url})")
            
        # 3. テキスト抽出と圧縮
        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 4. 文字数制限 (4万文字に拡大し、より多くの情報を保持)
        return text[:40000]
    except Exception as e:
        return f"ページの取得に失敗しました: {e}"

tools = [fetch_page]

def main():
    print("=== Altair 公式マニュアル自律探索エージェント (LangGraph版) ===")
    
    # 2. モデルの初期化
    project_id = "project-70b8d2ab-934e-47ee-960"
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        vertexai=True,  # ← これを追加！（最重要）
        project=project_id,
        location="asia-northeast1",
        temperature=0.0
    )

    # 3. エージェントのシステムプロンプト（AIの脳内ルール）
    system_prompt = """あなたはOpenRadiossとLS-DYNAの専門家であり、優秀なPythonエンジニアです。
        ユーザーからLS-DYNAのキーワードブロック（データ）のみが渡されます。以下のルールに従って、自律的に変換スクリプトを作成してください。
        
        【探索とマッピングのルール】
        1. 必ず起点URL（ https://help.altair.com/hwsolvers/rad/topics/solvers/rad/ls_dyna_keywords_r.htm ）をツールで読み込むこと。
        2. OpenRadioss側の各パラメータの対応関係と、厳密な文字数制限の仕様を必ず特定すること。
        3. 迷子になった場合や関連情報がない場合は「該当情報が見つかりませんでした」と即答すること。
        
        【スクリプト生成と出力のルール】
        1. マニュアルに記載された変数のフィールド幅（10文字、20文字など）を正確に読み取り、Pythonのf-string（例: `f"{val:>10}"` や `f"{val:>20}"`）に厳格に反映させること。勝手にすべてを10文字と解釈しないこと。
        2. LS-DYNA側で省略されている値（0.0など）がある場合、OpenRadioss側のマニュアルに指定されている「デフォルト値（例: Ashear=5/6 など）」を特定し、スクリプト内で適切に補完するロジックを実装すること。
        3. ユーザーが入力したサンプルデータをその関数に入力した場合の、変換後の出力文字列も必ず提示すること。
        """

    # 4. LangGraphでエージェントを組み立てる（これが最新の正攻法！）
    agent_executor = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )

    while True:
            print("\n========================================")
            print("質問を入力してください。")
            print("(※複数行のペーストOK。送信するには新しい行で「go」と入力してEnter。終了する場合は「exit」)")
            print("----------------------------------------")
            
            lines = []
            exit_flag = False
            
            # 複数行の入力を受け付けるループ
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                    
                # 最初からexitと打たれた場合は終了フラグを立てる
                if line.strip().lower() == 'exit' and not lines:
                    exit_flag = True
                    break
                
                # goと打たれたら入力受付を終了してAIへ送信
                if line.strip().lower() == 'go':
                    break
                    
                lines.append(line)
                
            if exit_flag:
                print("エージェントを終了します。")
                break
                
            # 入力された複数行を1つのテキストに結合
            user_query = "\n".join(lines).strip()
            
            # 空打ち防止
            if not user_query:
                continue
            
            try:
                print("\n[エージェントが思考を開始しました...]")
                # エージェントの実行
                result = agent_executor.invoke(
                    {
                        "messages": [
                            ("user", user_query)
                        ]
                    },
                    config={"recursion_limit": 30}
                )
                
                print("\n[最終回答]")
                # 修正ここから -----------------------------------
                final_content = result["messages"][-1].content
                
                if isinstance(final_content, list):
                    # リスト（辞書）形式で返ってきた場合は 'text' の中身だけを抽出
                    print(final_content[0].get("text", ""))
                else:
                    # 通常の文字列として返ってきた場合はそのまま表示
                    print(final_content)
                # 修正ここまで -----------------------------------
                
            except Exception as e:
                print(f"\n[エラー]: {e}")

if __name__ == "__main__":
    main()