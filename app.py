import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode, RTCConfiguration
import cv2
import mediapipe as mp
import av
import numpy as np

# MediaPipeの設定
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# じゃんけん判定ロジック
def judge_janken(landmarks):
    # 指の先端と第2関節のy座標を比較して、指が立っているか判定
    # 0: 手首, 4: 親指先, 8: 人差し指先, 12: 中指先, 16: 薬指先, 20: 小指先
    finger_status = []
    
    # 親指 (横方向の動きで判定する場合が多いが、簡易的にx座標で判定)
    if landmarks[4].x < landmarks[3].x: # 右手前提の簡易判定
        finger_status.append(1)
    else:
        finger_status.append(0)

    # 人差し指〜小指
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for tip, pip in zip(tips, pips):
        if landmarks[tip].y < landmarks[pip].y:
            finger_status.append(1) # 立っている
        else:
            finger_status.append(0) # 寝ている

    # 判定
    count = sum(finger_status[1:]) # 人差し指〜小指の立っている数
    if count == 0 and finger_status[0] == 0:
        return "ROCK (グー)"
    elif count == 4:
        return "PAPER (パー)"
    elif count == 1 and finger_status[1] == 1: # 人差し指だけ
        return "SCISSORS (チョキ)"
    elif count == 2 and finger_status[1] == 1 and finger_status[2] == 1: # 人差し指と中指
        return "SCISSORS (チョキ)"
    else:
        return "KEEP MOVING..."

# WebRTCの映像処理クラス
class VideoProcessor:
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # 左右反転（鏡のように表示）
        img = cv2.flip(img, 1)
        
        # MediaPipeで処理するためにRGBに変換
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        label = "No Hand Detected"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 骨組みを描画
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                # じゃんけん判定
                label = judge_janken(hand_landmarks.landmark)
                
                # 結果を画面に描画
                cv2.putText(img, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Streamlit UI
st.set_page_config(page_title="Janken Recorder", layout="centered")
st.title("🖐️ じゃんけん記録アプリ")
st.write("カメラに向かって手を出してください。")

# スマホ対応のためのRTC設定
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

webrtc_streamer(
    key="janken",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    video_processor_factory=VideoProcessor,
    async_processing=True,
)

st.info("※ スマホで動作させる場合、ブラウザのカメラ許可設定を確認してください。")
