import streamlit as st
import pandas as pd
from datetime import datetime

# ページ設定
st.set_page_config(page_title="JANKEN SURVIVAL PRO", layout="wide")

# CSS読み込み
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

local_css("style.css")

# --- 【修正済み】勝敗判定ロジック関数 ---
def judge_winners(living_hands):
    """
    生き残っているプレイヤーの手(dict)を受け取り、勝ち残ったプレイヤーのリストを返す
    """
    hands_list = list(living_hands.values())
    unique_hands = set(hands_list)
    
    # 1. あいこの判定（1種類のみ、または3種類全部出た場合）
    if len(unique_hands) == 1 or len(unique_hands) == 3:
        return list(living_hands.keys()), "DRAW (全員残留)"

    # 2. 決着の判定（2種類の手が出た場合）
    # 出ている2種類の手を特定する
    h_set = sorted(list(unique_hands)) # 絵文字順でソートされる (✊, 🖐️, ✌️)
    
    # 勝ち手を決めるロジックをシンプルに全パターン書きます
    # ✊(グー) と ✌️(チョキ) なら ✊(グー) の勝ち
    # ✌️(チョキ) と 🖐️(パー) なら ✌️(チョキ) の勝ち
    # 🖐️(パー) と ✊(グー) なら 🖐️(パー) の勝ち
    
    winning_hand = ""
    if "✊ グー" in unique_hands and "✌️ チョキ" in unique_hands:
        winning_hand = "✊ グー"
    elif "✌️ チョキ" in unique_hands and "🖐️ パー" in unique_hands:
        winning_hand = "✌️ チョキ"
    elif "🖐️ パー" in unique_hands and "✊ グー" in unique_hands:
        winning_hand = "🖐️ パー"
        
    winners = [name for name, hand in living_hands.items() if hand == winning_hand]
    return winners, f"WINNER: {', '.join(winners)}"

# --- セッション状態の初期化 ---
if 'game_id' not in st.session_state:
    st.session_state.game_id = 1
if 'history' not in st.session_state:
    st.session_state.history = []
if 'active_players' not in st.session_state:
    st.session_state.active_players = []
if 'is_finished' not in st.session_state:
    st.session_state.is_finished = False

st.title("JANKEN SURVIVAL")

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    if st.button("♻️ 全リセット"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.divider()
    num_init = st.number_input("参加人数", min_value=2, max_value=10, value=3)
    init_names = []
    for i in range(num_init):
        name = st.text_input(f"プレイヤー {i+1}", value=f"PL {i+1}", key=f"init_n_{i}")
        init_names.append(name)
    
    if st.button("🏁 新ゲーム開始"):
        st.session_state.active_players = init_names
        st.session_state.game_id = 1
        st.session_state.history = []
        st.session_state.is_finished = False
        st.rerun()

# --- メインエリア ---
if st.session_state.is_finished:
    winner_name = st.session_state.active_players[0]
    st.balloons()
    st.markdown(f"""
        <div style="background: linear-gradient(45deg, #ffd700, #ff8c00); padding: 40px; border-radius: 20px; text-align: center;">
            <h1 style="color: white;">👑 CHAMPION 👑</h1>
            <h2 style="color: white;">{winner_name} 様</h2>
        </div>
    """, unsafe_allow_html=True)
elif st.session_state.active_players:
    st.subheader(f"🔥 第 {st.session_state.game_id} 回戦")
    with st.form("battle_form"):
        cols = st.columns(len(init_names))
        current_round_hands = {}
        for i, name in enumerate(init_names):
            with cols[i]:
                if name in st.session_state.active_players:
                    st.markdown(f"**{name}**")
                    hand = st.selectbox("選択", ["✊ グー", "✌️ チョキ", "🖐️ パー"], key=f"h_{name}_{st.session_state.game_id}")
                    current_round_hands[name] = hand
                else:
                    st.markdown(f"<span style='color: #444;'>💀 {name}</span>", unsafe_allow_html=True)
                    current_round_hands[name] = ""
        if st.form_submit_button("判定を実行"):
            living_hands = {k: v for k, v in current_round_hands.items() if v != ""}
            winners, result_msg = judge_winners(living_hands)
            row = {"回戦": f"第{st.session_state.game_id}回", "判定": result_msg}
            row.update(current_round_hands)
            st.session_state.history.append(row)
            st.session_state.active_players = winners
            if len(winners) == 1:
                st.session_state.is_finished = True
            else:
                st.session_state.game_id += 1
            st.rerun()

# --- 履歴表示 ---
st.divider()
st.subheader("履歴")

if st.session_state.history:
    # データフレームの作成
    df = pd.DataFrame(st.session_state.history)
    
    # ① 表の表示：'回戦'列を削除し、インデックス(左の番号)を非表示にする
    display_df = df.drop(columns=['回戦'])
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True
    )

    # --- 【シンプル版】コピー用テキストの作成 ---
    players = [c for c in df.columns if c not in ["回戦", "判定"]]
    
    copy_text = "【JANKEN SURVIVAL 全記録】\\n"
    copy_text += "--------------------------\\n"
    
    for i, row in df.iterrows():
        # 2回目以降のデータには区切り線を入れる
        if i > 0:
            copy_text += "--------------------------\\n"
        
        # DRAWでない時のみ結果を表示
        is_draw = "DRAW" in str(row['判定'])
        if not is_draw:
            copy_text += f"結果: {row['判定']}\\n"
        
        # 手の情報を生成
        hand_list = []
        for p in players:
            h = row[p] if row[p] != "" else "脱落"
            hand_list.append(f"{p}({h})")
        
        copy_text += "手: " + " / ".join(hand_list) + "\\n"

    copy_text += "--------------------------\\n"

    # --- コピーボタン (HTML/JS) ---
    import streamlit.components.v1 as components
    components.html(
        f"""
        <script>
        function copyToClipboard() {{
            const text = `{copy_text}`;
            const formattedText = text.replace(/\\\\n/g, '\\n');
            navigator.clipboard.writeText(formattedText).then(() => {{
                alert('コピーしました！');
            }});
        }}
        </script>
        <button onclick="copyToClipboard()" style="
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        ">
            📋 全結果をコピー
        </button>
        """,
        height=80,
    )

    # 以前のダウンロードボタン（CSV）
    csv = df.to_csv(index=False).encode('utf_8_sig')
    st.download_button(
        label="💾 CSVで保存",
        data=csv,
        file_name=f"janken_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )