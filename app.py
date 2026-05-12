import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
import random

st.set_page_config(
    page_title="LaparoAI Surgical Co-Pilot",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.big-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
}
.subtitle {
    font-size: 18px;
    color: #b0b0b0;
}
.metric-card {
    background-color: #1c1f26;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #333;
    color: white;
}
.warning {
    color: #ff4b4b;
    font-weight: bold;
}
.safe {
    color: #00cc88;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">LaparoAI: Surgical Safety Co-Pilot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered real-time guidance for laparoscopic surgery</div>',
    unsafe_allow_html=True
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload a laparoscopic surgery image",
    type=["jpg", "jpeg", "png"]
)

def draw_transparent_circle(image, center, radius, color, alpha=0.35):
    overlay = image.copy()
    cv2.circle(overlay, center, radius, color, -1)
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

def process_image(image):
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (760, 520))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Basic tissue-color detection placeholder
    lower_tissue = np.array([0, 25, 35])
    upper_tissue = np.array([35, 255, 255])

    mask = cv2.inRange(hsv, lower_tissue, upper_tissue)

    kernel = np.ones((9, 9), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = img.copy()

    confidence = random.randint(82, 96)
    risk_level = "LOW"
    guidance = "No major risk zone detected."
    measurement = "No clear anatomy region detected."

    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        x, y, w, h = cv2.boundingRect(largest)

        # Main detected anatomy box
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 220, 255), 3)
        cv2.putText(
            output,
            "Detected Anatomy Region",
            (x, max(y - 12, 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 220, 255),
            2
        )

        cx = x + w // 2
        cy = y + h // 2

        danger_radius = max(35, min(w, h) // 5)
        safe_radius = max(55, min(w, h) // 3)

        # Safe zone and danger zone
        output = draw_transparent_circle(output, (cx, cy), safe_radius, (0, 180, 80), alpha=0.22)
        output = draw_transparent_circle(output, (cx, cy), danger_radius, (0, 0, 255), alpha=0.45)

        cv2.circle(output, (cx, cy), danger_radius, (0, 0, 255), 4)
        cv2.circle(output, (cx, cy), safe_radius, (0, 255, 100), 3)

        cv2.putText(
            output,
            "DANGER ZONE",
            (cx - 85, cy - danger_radius - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        cv2.putText(
            output,
            "SAFE DISSECTION AREA",
            (cx - 120, cy + safe_radius + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 100),
            2
        )

        # Simulated tool path line
        start_point = (max(20, cx - 230), min(500, cy + 120))
        end_point = (cx - danger_radius - 15, cy + 20)

        cv2.arrowedLine(output, start_point, end_point, (255, 255, 255), 3, tipLength=0.04)
        cv2.putText(
            output,
            "Suggested Safe Tool Path",
            (start_point[0], start_point[1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        if area > 45000:
            risk_level = "HIGH"
            guidance = "Critical area detected. Avoid red zone and verify anatomy before cutting."
        elif area > 22000:
            risk_level = "MEDIUM"
            guidance = "Important structure nearby. Proceed carefully using safe zone guidance."
        else:
            risk_level = "LOW"
            guidance = "Anatomy detected. Continue with standard confirmation."

        measurement = f"Detected region: {int(w)} px × {int(h)} px"

    output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    return output, mask, confidence, risk_level, guidance, measurement

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    with st.spinner("AI analyzing surgical camera view..."):
        time.sleep(0.7)
    with st.spinner("Detecting anatomy and risk zones..."):
        time.sleep(0.7)
    with st.spinner("Generating real-time surgical guidance..."):
        time.sleep(0.7)

    processed, mask, confidence, risk_level, guidance, measurement = process_image(image)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Surgical View")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("LaparoAI Guidance Overlay")
        st.image(processed, use_container_width=True)

    st.divider()

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("AI Confidence", f"{confidence}%")

    with m2:
        st.metric("Risk Level", risk_level)

    with m3:
        st.metric("Mode", "Real-Time Assist")

    with m4:
        st.metric("Role", "Surgeon Co-Pilot")

    st.markdown("### AI Recommendation")

    if risk_level == "HIGH":
        st.error(guidance)
    elif risk_level == "MEDIUM":
        st.warning(guidance)
    else:
        st.success(guidance)

    st.write(f"**Measurement:** {measurement}")

    with st.expander("Show AI Segmentation Mask"):
        st.image(mask, caption="Detected tissue mask", use_container_width=True)

    st.info(
        "Prototype note: This demo uses computer vision and simulated guidance logic. "
        "A real clinical system would use trained models such as YOLO or U-Net on verified surgical datasets."
    )

else:
    st.info("Upload a laparoscopic image to start the demo.")

    st.markdown("""
    ### What this demo will show:
    - AI detection of surgical anatomy region  
    - Red danger zone overlay  
    - Green safe zone overlay  
    - Confidence score  
    - Real-time guidance message  
    """)