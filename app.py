import streamlit as st
# 先ほど作ったagent.pyから、エージェント本体をインポート
from agent import agent_executor

# --- ページの設定 ---
st.set_page_config(page_title="FEM Auto-Converter Agent", page_icon="⚙️", layout="wide")
st.title("⚙️ FEM Auto-Converter Agent")
st.caption("LS-DYNAのキーワードブロックを貼り付けると、自律型AIがAltairマニュアルを検索してOpenRadioss用の変換スクリプトを作成します。")

# --- チャット履歴の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "OpenRadiossへのマッピングスクリプトを作成します。変換したいLS-DYNAのキーワードブロックを貼り付けてください。"}
    ]

# --- 過去のチャット履歴を画面に表示 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- チャット入力欄 ---
# st.chat_input を使うと、画面下部に固定されるChatGPT風の入力欄が1行で完成します
if prompt := st.chat_input("LS-DYNAのキーワードをペースト (Shift+Enterで改行)"):
    
    # 1. ユーザーの入力を画面に表示し、履歴に保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AIの応答エリアを作成
    with st.chat_message("assistant"):
        # 思考中のぐるぐるアニメーションを表示
        with st.spinner("マニュアルを自律探索して変換器を構築中..."):
            try:
                # エージェントを実行（スタミナは30に設定）
                result = agent_executor.invoke(
                    {"messages": [("user", prompt)]},
                    config={"recursion_limit": 30}
                )
                
                # 最終回答を抽出
                final_content = result["messages"][-1].content
                if isinstance(final_content, list):
                    response_text = final_content[0].get("text", "")
                else:
                    response_text = final_content
                
                # 結果を画面に表示し、履歴に保存
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_msg = f"エラーが発生しました: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})