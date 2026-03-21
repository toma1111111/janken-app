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

# --- 勝敗判定ロジック関数 ---
def judge_winners(living_hands):
    """
    生き残っているプレイヤーの手(dict)を受け取り、勝ち残ったプレイヤーのリストを返す
    """
    hands_list = list(living_hands.values())
    unique_hands = set(hands_list)
    
    # 1種類（全員同じ）または 3種類（グー・チョキ・パー全部）出た場合は「あいこ」
    if len(unique_hands) == 1 or len(unique_hands) == 3:
        return list(living_hands.keys()), "DRAW (全員残留)"

    # 2種類出た場合のみ決着がつく
    h1, h2 = list(unique_hands)
    
    # どちらが勝つ手か判定
    # ✊ > ✌️,  ✌️ > 🖐️,  🖐️ > ✊
    if (h1[0] == "✊" and h2[0] == "✌️") or \
       (h1[0] == "✌️" and h2[0] == "🖐️") or \
       (h1[0] == "🖐️" and h2[0] == "✊"):
        winning_hand = h1
    else:
        winning_hand = h2
        
    winners = [name for name, hand in living_hands.items() if hand == winning_hand]
    return winners, f"WIN: {', '.join(winners)}"

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

# --- サイドバー：初期設定 ---
with st.sidebar:
    st.header("⚙️ ゲーム設定")
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
    
    if st.button("🏁 このメンバーで新ゲーム開始"):
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
        <div style="background: linear-gradient(45deg, #ffd700, #ff8c00); padding: 40px; border-radius: 20px; text-align: center; border: 5px solid #fff;">
            <h1 style="color: white; font-size: 50px; margin: 0;">👑 CHAMPION 👑</h1>
            <h2 style="color: white; font-size: 40px; margin: 20px 0;">{winner_name} 様</h2>
        </div>
    """, unsafe_allow_html=True)
    st.info("新しいゲームを始めるにはサイドバーから「新ゲーム開始」を押してください。")

elif st.session_state.active_players:
    st.subheader(f"🔥 第 {st.session_state.game_id} 回戦")
    
    with st.form("battle_form"):
        cols = st.columns(len(init_names))
        current_round_hands = {}
        
        for i, name in enumerate(init_names):
            with cols[i]:
                if name in st.session_state.active_players:
                    st.markdown(f"✨ **{name}**")
                    hand = st.selectbox("選択", ["✊ グー", "✌️ チョキ", "🖐️ パー"], key=f"h_{name}_{st.session_state.game_id}")
                    current_round_hands[name] = hand
                else:
                    st.markdown(f"<span style='color: #444;'>💀 {name}</span>", unsafe_allow_html=True)
                    current_round_hands[name] = ""

        submit = st.form_submit_button("判定を実行")

    if submit:
        # 生き残っている人の手だけ抽出
        living_hands = {k: v for k, v in current_round_hands.items() if v != ""}
        
        # 判定関数を呼び出し
        winners, result_msg = judge_winners(living_hands)

        # 履歴に追加
        row = {"回戦": f"第{st.session_state.game_id}回", "判定": result_msg}
        row.update(current_round_hands)
        st.session_state.history.append(row)

        # 生き残りリストの更新
        st.session_state.active_players = winners
        
        # 終了判定（勝者が一人のみになったら終了）
        if len(winners) == 1:
            st.session_state.is_finished = True
        else:
            st.session_state.game_id += 1
        
        st.rerun()
else:
    st.warning("サイドバーで設定を行い「新ゲーム開始」を押してください。")

# --- 履歴表示 ---
st.divider()
st.subheader("📊 サバイバル・ログ")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.table(df)